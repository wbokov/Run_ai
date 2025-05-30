import matplotlib.pyplot as plt
from aiogram.types import FSInputFile
from main import bot
import os
import ast
import math
from PIL import Image, ImageDraw, ImageFont
from alchemy import get_user_data, update_plan
from gpt_work import solve
from tokens import API_GPT
import aiohttp
import re
from alchemy import get_profile1


async def get_weather(l1, l2):
    url = f"https://yandex.ru/pogoda/ru-RU/details/auto/today?lat={l1}&lon={l2}&lang=ru&via=dnav"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            res = await response.text()
            pattern = (
                r'<p class="A11Y_visuallyHidden__y0sw0 visuallyHidden">0:00:s*(.*?)</p>'
            )
            match = re.search(pattern, res)
            if match:
                return match.group(1)
            else:
                return None


def insert_newline_after_two_words(input_dict):
    output_dict = {}

    for key, value in input_dict.items():
        # Разделяем строку на слова
        words = value.split()
        # Создаем новый список для хранения измененных слов
        modified_words = []

        # Проходим по словам и добавляем \n после каждых двух
        for i in range(len(words)):
            modified_words.append(words[i])
            # Проверяем, нужно ли добавить \n
            if (i + 1) % 2 == 0:
                modified_words.append("\n")

        # Объединяем слова обратно в строку
        output_dict[key] = " ".join(modified_words)

    return output_dict


async def plot_and_save_accidents(id, data, filename="accidents_plot.png"):
    years = list(data.keys())
    accidents = [float(i) for i in list(data.values())]

    # Создаем график
    plt.figure(figsize=(10, 5))
    plt.plot(years, accidents, marker="o", linestyle="-", color="b")

    # Добавляем заголовок и метки осей
    plt.title("График изменений массы тела")
    plt.xlabel("Число")
    plt.ylabel("Вес (кг)")

    # Добавляем сетку для удобства восприятия
    plt.grid()

    # Сохраняем график как изображение
    plt.savefig(filename)
    photo_file = FSInputFile(filename)
    await bot.send_photo(chat_id=id, photo=photo_file)
    # Закрываем график, чтобы освободить память
    plt.close()
    if os.path.exists("accidents_plot.png"):
        os.remove("accidents_plot.png")


def calculate_daily_caloric_intake(weight, age, training_sessions_per_week):

    bmr = 633 + (13.397 * float(weight)) - (5.677 * int(age))

    # Определяем коэффициент активности
    if training_sessions_per_week == 0:
        activity_multiplier = 1.2  # Малоподвижный образ жизни
    elif training_sessions_per_week <= 2:
        activity_multiplier = 1.375  # Легкие тренировки
    elif training_sessions_per_week <= 5:
        activity_multiplier = 1.55  # Умеренные тренировки
    else:
        activity_multiplier = 1.725  # Активные тренировки

    # Рассчитываем суточное потребление калорий
    daily_caloric_intake = bmr * activity_multiplier
    return daily_caloric_intake


async def get_plan(id, list_from_ai):

    data = [[], []]
    data[0] = list_from_ai.keys()
    data[1] = list_from_ai.values()
    # Настройки изображения
    cell_width = 270
    cell_height = 350
    table_width = cell_width * len(data[0])
    table_height = cell_height * len(data)

    # Загрузка фона (укажите путь к вашему изображению фона)
    background_path = "Picture.png"  # Замените на путь к вашему изображению фона
    background = Image.open(background_path).resize((table_width, table_height))

    # Создание нового изображения с фоном
    image = Image.new("RGB", (table_width, table_height))
    image.paste(background, (0, 0))

    draw = ImageDraw.Draw(image)

    # Загрузка шрифта (укажите путь к вашему .ttf файлу)
    font_path = "arial.ttf"  # Убедитесь, что файл находится в той же папке или укажите полный путь
    font_size = 20
    font = ImageFont.truetype(font_path, font_size)

    # Рисуем таблицу
    for i, row in enumerate(data):
        for j, value in enumerate(row):
            x0 = j * cell_width
            y0 = i * cell_height
            x1 = x0 + cell_width
            y1 = y0 + cell_height

            # Рисуем прямоугольник для ячейки
            draw.rectangle([x0, y0, x1, y1], outline="black")

            # Рисуем текст в ячейке
            draw.text((x0 + 5, y0 + 5), str(value), fill="black", font=font)

    image.save("table_pillow.jpg")

    # Сохранение изображения в файл
    photo_file = FSInputFile("table_pillow.jpg")
    await bot.send_photo(chat_id=id, photo=photo_file)

    if os.path.exists("table_pillow.jpg"):
        os.remove("table_pillow.jpg")

    return


async def get_profile(id):
    prof = await get_profile1(id)
    name_table = await get_user_data(id)
    await bot.send_message(
        id,
        f"Профиль - {name_table.name}"
        f"({list(ast.literal_eval(name_table.weight_gr).values())[len(list(ast.literal_eval(name_table.weight_gr).values()))-1]}кг)\n"
        f"уровень: {prof.level}\n"
        f"общее расстояние: {prof.km}\n"
        f"количество тренировок: {prof.amount_at}",
    )


async def get_plan_run(id):
    user = await get_user_data(id)
    text = solve(
        API_GPT,
        "text",
        f"Составить план тренировок на {user.per_week} дней в неделю по бегу включая параметры:"
        f" возраст {user.age}л, вес {list(ast.literal_eval(user.weight_gr).values())[0]}кг, пол {user.gender}, "
        f"уровень спортсмена {user.level}, цель тренировок {user.target}. Ответ дать в форме словаря Python вида 'день недели (всего Хкм) : тренировка'. Вывести в одну сторку без обозначения языка Python. "
        f"Дни без тренировок не писать",
    )
    try:
        if len(ast.literal_eval(text).keys()) != user.per_week:
            raise ValueError
        await get_plan(id, insert_newline_after_two_words(ast.literal_eval(text)))
        await update_plan(id, text)
    except:
        await get_plan_run(id)


def haversine(coord1, coord2):
    # Радиус Земли в километрах
    R = 6371.0

    lat1, lon1 = coord1.split(", ")
    lat2, lon2 = coord2.split(", ")
    lat1, lat2, lon1, lon2 = float(lat1), float(lat2), float(lon1), float(lon2)

    # Преобразуем градусы в радианы
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Разница координат
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Формула haversine
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance
