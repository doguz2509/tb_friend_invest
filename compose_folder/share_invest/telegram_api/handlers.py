import logging
import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from .service import Service
from .. import ShareCalculator

logger = logging.getLogger(os.path.split(__file__)[-1])


class AddParticipant(StatesGroup):
    name = State()
    amount = State()


class SetAmounts(StatesGroup):
    amount = State()
    units = State()


@Service.dp.message_handler(commands='start')
async def start_handler(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['invoice'] = ShareCalculator()
    await SetAmounts.amount.set()
    await message.reply(f"""Enter overall price""")


@Service.dp.message_handler(lambda message: message.text.isnumeric(),
                            state=SetAmounts.amount)
async def add_participant_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['invoice'].set_amount(float(message.text))
        await SetAmounts.next()
        await message.reply("Purchase count?")


@Service.dp.message_handler(lambda message: message.text.isnumeric(),
                            state=SetAmounts.units)
async def set_amount_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['invoice'].set_units(float(message.text))
        await message.reply(f"""Purchasing: {data['invoice'].purchase}
        Add participants with /participant ,
        generate /invoice
        or /cancel purchase""")


@Service.dp.message_handler(commands=['participant'], state='*')
async def add_participant_handler(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            assert 'invoice' in data.keys()
        await AddParticipant.name.set()
        await message.reply(f"Enter person name?")
    except AssertionError:
        await message.reply("/start session first")


@Service.dp.message_handler(state=AddParticipant.name)
async def add_participant_name_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        await AddParticipant.next()
        await message.reply(f"{data['name']}'s personal involvement?")


@Service.dp.message_handler(state=AddParticipant.amount)
async def set_participant_involvement_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['invoice'].add_amount_per_participant(data['name'], float(message.text))
        await state.finish()
        await message.reply(f"""Purchasing: {data['invoice'].purchase}
                Add participants with /participant 
                or generate /invoice
                or /cancel purchase""")


@Service.dp.message_handler(commands=['invoice'], state='*')
async def generate_invoice(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            result = data['invoice'].invoice
            del data['invoice']
            await state.finish()
        res_txt = ''
        for name, item in result.items():
            res_txt += f"{name:10s} involved for {item.Spend:0.2f} should get {item.Units:0.2f}" + \
                       (f"; Change: {item.Change:0.2f}" if item.Change > 0 else '') + '\n'
        await message.reply(f"{res_txt}")
    except AssertionError as e:
        await message.reply(f"{e}\nContinue add/update /participant")


# Добавляем возможность отмены, если пользователь передумал заполнять
@Service.dp.message_handler(state='*', commands='cancel')
@Service.dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        del data['invoice']
        await state.finish()
    await message.reply('ОК')


@Service.dp.message_handler()
async def handler_all(message: types.Message):
    await message.reply("""Start purchase invoice for user {username}
    Type /start for initiate new calculation""".format(username=message.from_user.username))

