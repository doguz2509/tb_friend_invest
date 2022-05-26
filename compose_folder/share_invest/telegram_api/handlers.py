import logging
import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from googletrans import Translator

from .service import Service
try:
    from ..share_calculator import ShareCalculator
except (ImportError, ModuleNotFoundError):
    from compose_folder.share_invest.share_calculator import ShareCalculator


logger = logging.getLogger(os.path.split(__file__)[-1])


def tx(t, message: types.Message):
    return Translator().translate(t, dest=message.from_user.language_code).text


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
    await message.reply(tx(f"""Enter overall price""", message))


@Service.dp.message_handler(lambda mes: mes.text.isnumeric(),
                            state=SetAmounts.amount)
async def add_participant_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['invoice'].set_amount(float(message.text))
        await SetAmounts.next()
        await message.reply(tx("Count of units?", message))


@Service.dp.message_handler(lambda message: message.text.isnumeric(),
                            state=SetAmounts.units)
async def set_amount_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['invoice'].set_units(float(message.text))
        msg = tx("""Purchasing: {}
    Add participants with /{} ,
    generate invoice with /{}
    or cancel purchase with /{} purchase""", message)

        await message.reply(msg.format(data['invoice'].purchase, 'participant', 'invoice', 'cancel'))


@Service.dp.message_handler(commands=['participant'], state='*')
async def add_participant_handler(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            assert 'invoice' in data.keys()
        await AddParticipant.name.set()
        await message.reply(tx(f"Enter person name?", message))
    except AssertionError:
        await message.reply(tx("/{} session first", message).format('start'))


@Service.dp.message_handler(state=AddParticipant.name)
async def add_participant_name_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        await AddParticipant.next()
        await message.reply(tx(f"{data['name']}'s personal involvement?", message))


@Service.dp.message_handler(state=AddParticipant.amount)
async def set_participant_involvement_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['invoice'].add_amount_per_participant(data['name'], float(message.text))
        await state.finish()
        if data['invoice'].invoice_ready:
            msg = tx("""Purchasing: {}
                    You are ready for generate /{}
                    or /{} purchase""", message).format(data['invoice'].purchase['price'], 'invoice', 'cancel')
        else:
            msg = tx("""Purchasing: {}
                    Continue /{} adding 
                    or /{} purchase""", message).format(data['invoice'].purchase['price'], 'participant', 'cancel')
        await message.reply(msg)


@Service.dp.message_handler(commands=['invoice'], state='*')
async def generate_invoice(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            result = data['invoice'].invoice
            res_txt = tx("Overall price is: {}; Count are: {}", message).format(
                data['invoice'].purchase.get('price'),
                data['invoice'].purchase.get('count')
            ) + "\n------------------------\n"
            del data['invoice']
            await state.finish()

        for name, item in result.items():
            res_txt += f"\n{name:10s} involved for {item.Spend:0.2f} should get {item.Units:0.2f}" + \
                       (f"; Change: {item.Change:0.2f}" if item.Change > 0 else '') + '\n'
        m_id = await message.reply(tx(f"{res_txt}", message))
        await message.chat.pin_message(m_id.message_id)
    except AssertionError as e:
        await message.reply(tx("{}\nContinue add/update /{}", message).format(e, 'participant'))


@Service.dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        del data['invoice']
        await state.finish()
    await message.reply('ОК')


@Service.dp.message_handler()
async def handler_all(message: types.Message):
    await message.reply(tx("""Start invoice for user {}
    Click /{} for initiate new calculation""", message).format(message.from_user.username, 'start'))


