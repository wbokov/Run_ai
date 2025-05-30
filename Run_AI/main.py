import asyncio
import datetime
from translate import Translator
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from tokens import API_TOKEN
from alchemy import *
from states import Form
from other_functions import *
from buttons import *
from validators import *


bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()


@router.message(Command("admin2008"))
async def cmd_start(message: types.Message):
    await message.delete()
    await message.answer(
        "Вы вошли в учетную запись администратора.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Сделать рассылку пользователям", callback_data="admin1"
                    )
                ],
                [InlineKeyboardButton(text="Получить отзывы", callback_data="admin2")],
                [InlineKeyboardButton(text="Назад", callback_data="got_it")],
            ]
        ),
    )


@router.message(Command("rate"))
async def cmd_start(message: types.Message):
    recents = await get_recent()
    if str(message.from_user.id) in str(recents):
        await message.answer("Вы уже оставляли отзыв сегодня")
        return
    await add_id(message.from_user.id)
    await message.answer(
        "Что бы вы хотели оценить?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="качество составления планов", callback_data="rate1"
                    )
                ],
                [InlineKeyboardButton(text="функциональность", callback_data="rate2")],
                [InlineKeyboardButton(text="скорость работы", callback_data="rate3")],
            ]
        ),
    )


@router.message(Form.waiting_for_rate1)
async def rate(message: types.Message, state: FSMContext):
    weight = message.text
    if weight not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
        await message.answer("Необходимо ввести число от 1 до 10 включительно")
        return
    topic = "rate1"
    avg = await get_avg_m(topic)
    if avg == 0 or avg is None:
        upd = float(weight)
    else:
        upd = (float(avg) + float(weight)) / 2
    await update_avg_m(upd, topic)
    await message.answer("Спасибо за отзыв!")
    await state.set_state("*")


@router.message(Form.waiting_for_rate2)
async def rate(message: types.Message, state: FSMContext):
    weight = message.text
    if weight not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
        await message.answer("Необходимо ввести число от 1 до 10 включительно")
        return
    topic = "rate2"
    avg = await get_avg_m(topic)
    if avg == 0 or avg is None:
        upd = float(weight)
    else:
        upd = (float(avg) + float(weight)) / 2
    await update_avg_m(upd, topic)
    await message.answer("Спасибо за отзыв!")
    await state.set_state("*")


@router.message(Form.waiting_for_rate3)
async def rate(message: types.Message, state: FSMContext):
    weight = message.text
    if weight not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
        await message.answer("Необходимо ввести число от 1 до 10 включительно")
        return
    topic = "rate3"
    avg = await get_avg_m(topic)
    if avg == 0 or avg is None:
        upd = float(weight)
    else:
        upd = (float(avg) + float(weight)) / 2
    await update_avg_m(upd, topic)
    await message.answer("Спасибо за отзыв!")
    await state.set_state("*")


@router.message(Command("edit_plan"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Что бы вы хотели изменить?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Частота тренировок", callback_data="amo")],
                [InlineKeyboardButton(text="Сложность", callback_data="dif")],
            ]
        ),
    )


@router.message(Form.waiting_for_admin)
async def cmd_edit_weight(message: types.Message, state: FSMContext):
    people = await get_people_ids()
    print(people)
    for i in people:
        await bot.send_message(i, message.text)
    await state.set_state("*")


@router.message(Form.waiting_for_new_weight)
async def cmd_edit_weight(message: types.Message, state: FSMContext):
    weight = message.text
    if check_weight(weight):
        await message.answer(
            "Необходимо ввести одно действительное число, соответствующее вашему весу"
        )
        return
    weight_dict = await get_weight(message.chat.id)
    weight_dict = ast.literal_eval(weight_dict)
    weight_dict[datetime.datetime.today().strftime("%Y-%m-%d")] = weight
    await update_weight(message.chat.id, weight_dict)
    await plot_and_save_accidents(message.chat.id, weight_dict)
    await state.set_state("*")


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    user_nik = message.from_user.username
    await insert_user(user_id, first_name, user_nik)
    await message.answer(
        f"Здравствуйте, {first_name}! Пожалуйста, заполните информацию о себе, чтобы приступить к тренировкам."
    )
    await message.answer("Для начала введите ваш возраст:")
    await state.set_state(Form.waiting_for_age)


@router.message(Form.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    age = message.text
    if check_age(age):
        await message.answer(
            "Необходимо ввести одно натуральное число, соответствующее вашему возрасту"
        )
        return
    await update_age(message.chat.id, age)
    await state.set_state(Form.waiting_for_weight)
    await message.answer("Теперь ваш вес:")


@router.message(Form.waiting_for_weight)
async def process_age(message: types.Message, state: FSMContext):
    weight = message.text
    user_id = message.chat.id
    if check_weight(weight):
        await message.answer(
            "Необходимо ввести одно действительное число, соответствующее вашему весу"
        )
        return
    await update_weight(
        user_id,
        str(
            {
                f"Начало тренировок\n({datetime.datetime.today().strftime('%Y-%m-%d')})": weight
            }
        ),
    )
    await state.set_state(Form.waiting_for_times)
    await message.answer("Сколько раз в неделю вы планируете тренироваться?")


@router.message(Form.waiting_for_times)
async def process_age(message: types.Message, state: FSMContext):
    times = message.text
    if check_times(times):
        await message.answer("Необходимо ввести количество дней в неделю")
        return
    await update_times(message.chat.id, times)
    await message.answer(
        "Ваш пол:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Мужской", callback_data="m")],
                [InlineKeyboardButton(text="Женский", callback_data="f")],
            ]
        ),
    )
    await state.set_state("*")


@router.message(Form.waiting_for_times2)
async def process_age2(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    times = message.text
    if check_times(times):
        await message.answer("Необходимо ввести количество дней в неделю")
        return
    plan = await get_plan_aiosql(user_id)
    text = solve(
        API_GPT,
        "text",
        f"{plan}.Сделать количество дней в этом плане {times}."
        f"Ответ также дать в форме словаря Python вида день недели : тренировка. Вывести в одну сторку без обозначения языка Python",
    )
    try:
        await get_plan(user_id, insert_newline_after_two_words(ast.literal_eval(text)))
        await update_plan(user_id, plan)
    except:
        await get_plan_run(user_id)
    await message.answer("Вот ваш новый план!")
    await state.set_state("*")


@router.callback_query(
    lambda c: c.data
    in [
        "m",
        "f",
        "Начинающий",
        "Средний",
        "Продвинутый",
        "low",
        "mid",
        "up",
        "dif",
        "amo",
        "p",
        "min",
        "ok",
        "complete",
        "got_it",
        "rate1",
        "rate2",
        "rate3",
        "admin1",
        "admin2",
    ]
)
async def process_callback_button(
    callback_query: types.CallbackQuery, state: FSMContext
):
    user_id = callback_query.message.chat.id
    msg_id = callback_query.message.message_id
    if callback_query.data == "admin1":
        await bot.answer_callback_query(callback_query.id)
        await state.set_state(Form.waiting_for_admin)
        await bot.delete_message(
            chat_id=user_id,
            message_id=msg_id,
        )
        await bot.send_message(user_id, "Введите текст рассылки")
    if callback_query.data == "admin2":
        await bot.answer_callback_query(callback_query.id)
        await bot.delete_message(
            chat_id=user_id,
            message_id=msg_id,
        )
        match = await get_avg_match()
        info = await get_avg_info()
        mis = await get_avg_mis()
        await bot.send_message(
            user_id,
            f"Вот рейтинг:"
            f"\n Качество составления плана: {info} "
            f"\n Функциональность: {mis}"
            f"\n Скорость работы: {match}",
        )
    if callback_query.data == "rate1":
        await bot.answer_callback_query(callback_query.id)
        await state.set_state(Form.waiting_for_rate1)
        await bot.delete_message(
            chat_id=user_id,
            message_id=msg_id,
        )
        await bot.send_message(
            user_id,
            "Как бы вы оценили качество составления планов?\nНеобходимо ввести число от 1 до 10",
        )
    if callback_query.data == "rate2":
        await bot.answer_callback_query(callback_query.id)
        await state.set_state(Form.waiting_for_rate2)
        await bot.delete_message(
            chat_id=user_id,
            message_id=msg_id,
        )
        await bot.send_message(
            user_id,
            "Как бы вы оценили функциональность?\nНеобходимо ввести число от 1 до 10",
        )
    if callback_query.data == "rate3":
        await bot.answer_callback_query(callback_query.id)
        await state.set_state(Form.waiting_for_rate3)
        await bot.delete_message(
            chat_id=user_id,
            message_id=msg_id,
        )
        await bot.send_message(
            user_id,
            "Как бы вы оценили скорость работы?\nНеобходимо ввести число от 1 до 10",
        )
    if callback_query.data == "m":
        await bot.answer_callback_query(callback_query.id)
        await update_gender(user_id, "Мужской")
        await bot.delete_message(chat_id=user_id, message_id=msg_id)
        await bot.send_message(
            callback_query.message.chat.id,
            "Ваш уровень подготовки:",
            reply_markup=level(),
        )
    if callback_query.data == "f":
        await bot.answer_callback_query(callback_query.id)
        await update_gender(user_id, "Женский")
        await bot.delete_message(
            chat_id=user_id,
            message_id=msg_id,
        )
        await bot.send_message(user_id, "Ваш уровень подготовки:", reply_markup=level())
    if callback_query.data == "Начинающий":
        await bot.answer_callback_query(callback_query.id)
        await update_level(user_id, "Начинающий")
        await bot.delete_message(chat_id=user_id, message_id=msg_id)
        await bot.send_message(
            callback_query.message.chat.id, "Ваша цель:", reply_markup=target()
        )
    if callback_query.data == "Средний":
        await bot.answer_callback_query(callback_query.id)
        await update_level(user_id, "Средний")
        await bot.delete_message(chat_id=user_id, message_id=msg_id)
        await bot.send_message(
            callback_query.message.chat.id, "Ваша цель:", reply_markup=target()
        )
    if callback_query.data == "Продвинутый":
        await bot.answer_callback_query(callback_query.id)
        await update_level(user_id, "Продвинутый")
        await bot.delete_message(chat_id=user_id, message_id=msg_id)
        await bot.send_message(
            callback_query.message.chat.id, "Ваша цель:", reply_markup=target()
        )
    if callback_query.data == "low":
        await bot.answer_callback_query(callback_query.id)
        await update_target(user_id, "Потеря лишнего веса")
        await bot.delete_message(chat_id=user_id, message_id=msg_id)
        await get_user_data(user_id)
        await bot.send_message(user_id, "Составляем тренировочный план...")
        await state.set_state("*")
        await get_plan_run(user_id)
        user = await get_user_data(user_id)
        kkal = calculate_daily_caloric_intake(
            list(ast.literal_eval(user.weight_gr).values())[0], user.age, user.per_week
        )
        await bot.send_message(
            user_id, f"Ваше суточное потребление калорий: {round(kkal - 500)}"
        )
    if callback_query.data == "mid":
        await bot.answer_callback_query(callback_query.id)
        await update_target(user_id, "Поддержание формы")
        await bot.delete_message(chat_id=user_id, message_id=msg_id)
        await get_user_data(user_id)
        await bot.send_message(user_id, "Составляем тренировочный план...")
        await state.set_state("*")
        await get_plan_run(user_id)
        user = await get_user_data(user_id)
        kkal = calculate_daily_caloric_intake(
            list(ast.literal_eval(user.weight_gr).values())[0], user.age, user.per_week
        )
        await bot.send_message(
            user_id, f"Ваше суточное потребление калорий: {round(kkal)}"
        )
    if callback_query.data == "up":
        await bot.answer_callback_query(callback_query.id)
        await update_target(user_id, "Улучшение результатов")
        await bot.delete_message(chat_id=user_id, message_id=msg_id)
        await get_user_data(user_id)
        await bot.send_message(user_id, "Составляем тренировочный план...")
        await state.set_state("*")
        await get_plan_run(user_id)
        user = await get_user_data(user_id)
        kkal = calculate_daily_caloric_intake(
            list(ast.literal_eval(user.weight_gr).values())[0], user.age, user.per_week
        )
        await bot.send_message(
            user_id, f"Ваше суточное потребление калорий: {round(kkal)}"
        )
    if callback_query.data == "amo":
        await bot.answer_callback_query(callback_query.id)
        await state.set_state(Form.waiting_for_times2)
        await bot.delete_message(chat_id=user_id, message_id=msg_id)
        await bot.send_message(
            user_id, "Сколько раз в неделю вы планируете тренироваться?"
        )
    if callback_query.data == "dif":
        await bot.answer_callback_query(callback_query.id)
        await bot.delete_message(chat_id=user_id, message_id=msg_id)
        await bot.send_message(
            user_id, "Как бы вы хотели изменить план?", reply_markup=dif()
        )
    if callback_query.data == "complete":
        await bot.answer_callback_query(callback_query.id)
        today = datetime.datetime.now().strftime("%A").lower()
        today = Translator(from_lang="english", to_lang="russian").translate(today)
        today = today[0].upper() + today[1:]
        await bot.delete_message(chat_id=user_id, message_id=msg_id)
        await bot.send_message(user_id, "Результаты сохранены")
        ans = await update_train(user_id, today)
        if ans[0] >= 100 and ans[1] < 5:
            await bot.send_message(
                user_id, "Первые 100 км! Ваш уровень: 5. Взгляните на ваши успехи:"
            )
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    stmt = (
                        update(UserSport)
                        .where(UserSport.user_id == user_id)
                        .values(level=5)
                    )
                    await session.execute(stmt)
                    await session.commit()
                    await get_profile(user_id)
        if ans[0] >= 500 and ans[1] < 10:
            await bot.send_message(
                user_id,
                "Вы достигли 500 км! Ваш уровень: 10. Взгляните на ваши успехи:",
            )
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    stmt = (
                        update(UserSport)
                        .where(UserSport.user_id == user_id)
                        .values(level=10)
                    )
                    await session.execute(stmt)
                    await session.commit()
                    await get_profile(user_id)
        if ans[0] >= 2000 and ans[1] < 30:
            await bot.send_message(
                user_id, "Вы преодолели отметку в 2000 км! Ваш уровень: 30"
            )
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    stmt = (
                        update(UserSport)
                        .where(UserSport.user_id == user_id)
                        .values(level=30)
                    )
                    await session.execute(stmt)
                    await session.commit()
        if ans[0] >= 5000 and ans[1] < 40:
            await bot.send_message(user_id, "Вы пробежали 5000 км! Ваш уровень: 40")
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    stmt = (
                        update(UserSport)
                        .where(UserSport.user_id == user_id)
                        .values(level=40)
                    )
                    await session.execute(stmt)
                    await session.commit()
        if ans[0] >= 10000 and ans[1] < 50:
            await bot.send_message(
                user_id, "Вы преодолели целых 10000 км! Ваш уровень: 50"
            )
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    stmt = (
                        update(UserSport)
                        .where(UserSport.user_id == user_id)
                        .values(level=50)
                    )
                    await session.execute(stmt)
                    await session.commit()
    if callback_query.data == "got_it":
        await bot.answer_callback_query(callback_query.id)
        await bot.delete_message(chat_id=user_id, message_id=msg_id)
    if callback_query.data == "ok":
        await bot.answer_callback_query(callback_query.id)
        await bot.delete_message(chat_id=user_id, message_id=msg_id)
        prof = await get_profile1(user_id)
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = (
                    update(UserSport)
                    .where(UserSport.user_id == user_id)
                    .values(amount=prof.amount + 1)
                )
                await session.execute(stmt)
                await session.commit()
        if prof.amount > 0:
            await bot.send_message(
                user_id,
                "Вы уже пропускали предыдущую тренировку. "
                "Вы можете сделать перерыв от занятий или воспользоваться советом помошника задав свой вопрос /ask",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="Понятно", callback_data="got_it")]
                    ]
                ),
            )

    if callback_query.data == "min":
        await bot.answer_callback_query(callback_query.id)
        plan = await get_plan_aiosql(user_id)
        text = solve(
            API_GPT,
            "text",
            f"{plan}.Сделать этот план на 10% легче."
            f"Ответ также дать в форме словаря Python вида день недели : тренировка. Вывести в одну сторку без обозначения языка Python",
        )
        await get_plan(user_id, insert_newline_after_two_words(ast.literal_eval(text)))
        await update_plan(user_id, text)
        await callback_query.message.answer("Вот ваш новый план!")
        await bot.delete_message(chat_id=user_id, message_id=msg_id)
        await state.set_state("*")
    if callback_query.data == "p":
        await bot.answer_callback_query(callback_query.id)
        await bot.answer_callback_query(callback_query.id)
        plan = await get_plan_aiosql(user_id)
        text = solve(
            API_GPT,
            "text",
            f"{plan}.Сделать этот план на 10% сложнее."
            f"Ответ также дать в форме словаря Python вида день недели : тренировка. Вывести в одну сторку без обозначения языка Python",
        )
        await get_plan(user_id, insert_newline_after_two_words(ast.literal_eval(text)))
        await update_plan(user_id, text)
        await callback_query.message.answer("Вот ваш новый план!")
        await bot.delete_message(chat_id=user_id, message_id=msg_id)
        await state.set_state("*")


async def main():
    await create()
    dp.include_router(router)
    start_scheduler()
    await dp.start_polling(bot)


@router.message(Command("get_location"))
async def cmd_edit_weight(message: types.Message):
    await message.answer(
        "Вы можете отправить вашу геолокацию. "
        "Вам будут доступны сведения о погоде и пользователях рядом",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Понятно", callback_data="got_it")]
            ]
        ),
    )


@router.message(Command("edit_weight"))
async def cmd_edit_weight(message: types.Message, state: FSMContext):
    await message.answer("Введите ваш вес на данный момент:")
    await state.set_state(Form.waiting_for_new_weight)


@router.message(Command("profile"))
async def cmd_edit_weight(message: types.Message):
    await get_profile(message.from_user.id)


@router.message(Command("ask"))
async def cmd_edit_weight(message: types.Message, state: FSMContext):
    await message.answer("Что бы вы хотели спросить? \nНапишите ваш вопрос")
    await state.set_state(Form.waiting_for_ask)


@router.message(Form.waiting_for_ask)
async def cmd_edit_weight(message: types.Message, state: FSMContext):
    text_q = message.text
    user = await get_user_data(message.from_user.id)
    text = solve(
        API_GPT,
        "text",
        f"Роль: тренер по бегу. Ответить на вопрос '{text_q}'. "
        f"Параметры спортсмена: возраст {user.age}, вес {list(ast.literal_eval(user.weight_gr).values())[0]}кг, пол {user.gender}, "
        f"уровень спортсмена {user.level}, цель тренировок {user.target}, количество тренировок в неделю {user.per_week}",
    )
    await message.answer(text)
    await state.set_state("*")


@router.message(F.location)
async def handle_location(message: types.Message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    geo = str(str(latitude) + ", " + str(longitude))
    await save_location(message.from_user.id, geo)
    await bot.send_message(message.from_user.id, "Геолокация сохранена")
    list_of_users = await get_people()
    awnser_list = ""
    for i in list_of_users:
        if 1 >= haversine(geo, i.geo) and haversine(geo, i.geo) != 0:
            if i.user_nik != None:
                awnser_list += (
                    str(i.name) + ", " + str(i.age) + " ->   @" + str(i.user_nik) + "\n"
                )
    if awnser_list == "":
        await bot.send_message(
            message.from_user.id,
            f"К сожалению, список пользователей в вашем районе пуст",
        )
    else:
        await bot.send_message(
            message.from_user.id,
            f"Вот список пользователей в вашем районе:\n \n{awnser_list}",
        )


from apscheduler.schedulers.asyncio import AsyncIOScheduler


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(training_day, "cron", hour=7, minute=40)
    scheduler.start()


async def training_day():
    await delete_recent()
    async with AsyncSessionLocal() as session:
        today = datetime.datetime.now().strftime("%A").lower()
        today = Translator(from_lang="english", to_lang="russian").translate(today)
        today = today[0].upper() + today[1:]
        print(today)
        users_with_training_today = await session.execute(
            select(User.user_id).where(User.plan.contains(today))
        )
        users_with_training_today = users_with_training_today.scalars().all()
        print(users_with_training_today)
        for i in users_with_training_today:
            geo = await get_geo(i)
            if geo != None:
                l1, l2 = geo.split(", ")[0], geo.split(", ")[1]
                weather = await get_weather(l1, l2)
                text = f"У вас сегодня тренировка! На улице {weather}. "
            else:
                text = f'У вас сегодня тренировка! {today}, {datetime.datetime.today().strftime("%Y-%m-%d")}.'
            await bot.send_message(
                i,
                text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Тренировка выполнена", callback_data="complete"
                            )
                        ],
                        [InlineKeyboardButton(text="Пропустить", callback_data="ok")],
                    ]
                ),
            )


if __name__ == "__main__":
    asyncio.run(main())
