import asyncio
import logging
import sys
from config import B_TOKEN as TOKEN
from API import FOURSQUARE_API_KEY, FLICKR_API_KEY
import requests

from funcs import get_venue_photo
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F
from state import CityForm
from keyboards import origin_button, origin_pois, pois_buttons, return_button
from Commands import (
    Search_Command_Bot,
    Search_Command,

)

storage = MemoryStorage()
dp = Dispatcher()
@dp.message(Search_Command)  # пошукова команда
async def search(message: Message, state: FSMContext) -> None:
    await state.set_state(CityForm.city)
    await message.answer("Введіть назву міста, про яке Ви хочете дізнатися 🌏", reply_markup=ReplyKeyboardRemove())
@dp.message(CityForm.city)  # код команди
async def CityInfo(message: Message, state: FSMContext) -> None:
    city = message.text

    FLICKRURL = url = "https://www.flickr.com/services/rest/"
    WIKIURL = f"https://uk.wikipedia.org/api/rest_v1/page/summary/{city}"  # параметри
    FSURL = 'https://api.foursquare.com/v3/places/search'

    flikrparams = {
        "method": "flickr.photos.search",
        "api_key": FLICKR_API_KEY,
        "text": city,
        "format": "json",
        "nojsoncallback": 1,
        "per_page": 1,
        "media": "photos",
        "content_type": 1,
        "sort": "relevance",
        "lang": "uk"
    }
    headers = {
        "Accept": 'application/json',
        'Authorization': FOURSQUARE_API_KEY
    }
    params = {
        'near': city,
        'locale': 'uk',
        'limit': 1
    }

    markup = origin_button()
    markupback = return_button()

    flickr = requests.get(FLICKRURL, params=flikrparams)
    wiki = requests.get(WIKIURL)
    forsquare = requests.get(FSURL, headers=headers, params=params)
    if forsquare.status_code == 200:  # головний код
        if wiki.status_code == 200:
            flickdata = flickr.json()
            wdata = wiki.json()
            photo = flickdata['photos']['photo'][0]
            photo_url = f"https://live.staticflickr.com/{photo['server']}/{photo['id']}_{photo['secret']}.jpg"
            name = wdata.get("title", "Назву не знайдено")
            description = wdata.get("extract", "Опис не знайдено")
            await state.update_data(city=city)
            await message.answer_photo(f"{photo_url}\n", caption=f"🔎{name}🔍\n{description}", reply_markup=markup)
        else:
            await message.answer("Здається, в нашій базі немає інформації про це місто 😅")
    else:
        await message.answer(f"❌ Здається, такого міста не існує, перевірте чи правильно ви вказали назву міста.", reply_markup=markupback)

@dp.callback_query(origin_pois.filter(F.action=="poits")) #пошук точок інтересу
async def location_pois_hello(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    city = data.get("city")

    fsurl = 'https://api.foursquare.com/v3/places/search'
    headers = {
        "Accept": 'application/json',
        'Authorization': FOURSQUARE_API_KEY
    }
    params = {
        'near': city,
        'limit': 5,
        'locale': 'uk'
    }

    forsquare = requests.get(fsurl, headers=headers, params=params)
    fsdata = forsquare.json()
    pois_list = {}
    url_list = {}
    place = fsdata.get('results', [])
    for i in place:
        place_id = i.get("fsq_id")
        photo_url = get_venue_photo(place_id)
        name = i.get("name", "Ім'я не знайдено")
        location = i.get("location", {})
        address = location.get("formatted_address", "Адреса не знайдена")
        category = i.get("categories", [{"name": "Тип місця невідомий"}])[0].get("name", "Тип місця невідомий")
        venue_url = f"https://foursquare.com/v/{place_id}"
        short_name = name[:28]
        url_list[short_name + "url"] = photo_url
        pois_list[short_name] = f"{name}\n{category}\nАдреса: {address}\nПосилання: {venue_url}"
    markup = pois_buttons(pois_list)

    await state.update_data(url_list=url_list)
    await state.update_data(pois_list=pois_list)
    await callback_query.answer()
    await callback_query.message.answer("Ось список точок інтересу вказаного місця:", reply_markup=markup)

@dp.callback_query(origin_pois.filter(F.action=='end')) #повернутися до пошуку
async def location_pois_bye(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await search(callback_query.message, state)

@dp.callback_query() #вивід інформації
async def poi_selection(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    markup = origin_button()
    url_list = data.get("url_list")
    pois_list = data.get("pois_list")
    poi_name = callback_query.data
    info = pois_list.get(poi_name, "Інформація не знайдена")
    await callback_query.answer()
    await callback_query.message.answer_photo(photo=url_list[poi_name + "url"], caption=info, reply_markup=markup)

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await bot.set_my_commands([
        Search_Command_Bot,

    ])

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
