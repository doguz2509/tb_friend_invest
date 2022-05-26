import logging
import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from .service import Service
try:
    from ..share_calculator import ShareCalculator
except (ImportError, ModuleNotFoundError):
    from compose_folder.share_invest.share_calculator import ShareCalculator


logger = logging.getLogger(os.path.split(__file__)[-1])


class AddParticipant(StatesGroup):
    name = State()
    amount = State()


class SetAmounts(StatesGroup):
    amount = State()
    units = State()


# @Service.dp.chat_join_request_handler()
@Service.dp.message_handler(commands='start')
async def start_handler(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['order'] = ShareCalculator()
        data['order_id'] = id(data['order'])
        logger.info(f"Order: {id(data['order'])}")
    await SetAmounts.amount.set()
    await message.reply(f"""Enter overall price""")


@Service.dp.message_handler(lambda message: message.text.isnumeric(),
                            state=SetAmounts.amount)
async def add_participant_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['order'].set_amount(float(message.text))
        logger.info(f"Order price: {float(message.text)}")
        await SetAmounts.next()
        await message.reply("Purchase count?")


@Service.dp.message_handler(lambda message: message.text.isnumeric(),
                            state=SetAmounts.units)
async def set_amount_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['order'].set_units(float(message.text))
        await message.reply(f"""Purchasing: {data['order'].purchase}
        Add participants with /participant ,
        generate /invoice
        or /cancel purchase""")


@Service.dp.message_handler(commands=['participant'], state='*')
async def add_participant_handler(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            assert 'order' in data.keys()
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
        data['order'].add_amount_per_participant(data['name'], float(message.text))
        if data['order'].invoice_ready:
            await message.reply(f"""Purchasing: {data['order'].purchase['price']}
                    You are ready for generate /invoice
                    or /cancel purchase""")
        else:
            await message.reply(f"""Purchasing: {data['order'].purchase['price']}
                    Continue /participant adding 
                    or /cancel purchase""")
    await state.finish()
    assert data.get('order', False), "No order placed"
    assert data.get('order_id', 0) == id(data.get('order', False)), \
        f"Wrong order placed ({data.get('order_id', 0)} !=? {id(data.get('order', False))})"


@Service.dp.message_handler(commands=['order'], state='*')
async def generate_invoice(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            order = data['order']
            result = order.invoice
            res_txt = "Overall price is: {price}; Count are: {count}\n------------------------\n".format(
                **order.purchase
            )
            del data['order']
            await state.finish()

        for name, item in result.items():
            res_txt += f"{name:10s} involved for {item.Spend:0.2f} should get {item.Units:0.2f}" + \
                       (f"; Change: {item.Change:0.2f}" if item.Change > 0 else '') + '\n'
        m_id = await message.reply(f"{res_txt}")
        await message.chat.pin_message(m_id.message_id)
    except AssertionError as e:
        await message.reply(f"{e}\nContinue add/update /participant")


@Service.dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        del data['order']
        await state.finish()
    await message.reply('ОК')


@Service.dp.message_handler()
async def handler_all(message: types.Message):
    await message.reply("""Start purchase invoice for user {username}
    Type /start for initiate new calculation""".format(username=message.from_user.username))

