import asyncio
import json
import logging
from abc import ABC
from typing import Callable, Dict, Any, Awaitable

import requests
from aiogram import BaseMiddleware
from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, TelegramObject
from config import config


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class AccessMiddleware(BaseMiddleware, ABC):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = data["event_from_user"]
        data['whitelist'] = True
        if user.username not in self.allowed_users:
            data['whitelist'] = False
        return await handler(event, data)

    def __init__(self, allowed_users: list):
        super().__init__()
        self.allowed_users = allowed_users


bot = Bot(token=config.telegram_bot_token)
dp = Dispatcher()

allowed_users = ['alissali']
dp.update.outer_middleware(AccessMiddleware(allowed_users))

results = asyncio.Queue()


@dp.message(F.text, Command('imei'))
async def extract_data(message: Message, command: CommandObject, whitelist: bool):

    if whitelist:
        if command.args is None:
            await message.answer("Ошибка: укажи свой токен/imei")
            return
        try:
            token, imei = command.args.split('/', maxsplit=1)
        except ValueError:
            await message.answer("Ошибка: укажи свой токен и imei через / ")
            return

        # headers = {
        #     'Authorization': 'Bearer ' + token,
        #     'Content-Type': 'application/json'
        # }
        # body = json.dumps({
        #     "deviceId": imei,
        #     "serviceId": 12
        # })
        headers, body = headers_body(imei)
        try:
            response = requests.post(config.external_api_url, headers=headers, data=body)
            data = response.json()
            answer = json.dumps(data, indent=3, separators=(';', '- '))
            await message.reply(answer)
        except:
            await message.reply('Bad data')
    else:
        await message.answer("У вас нет доступа к этому боту.")
        raise CancelHandler()


def headers_body(imei: str) -> tuple:
    headers = {
        'Authorization': 'Bearer ' + config.api_token,
        'Content-Type': 'application/json'
    }
    body = json.dumps({
        "deviceId": imei,
        "serviceId": 12
    })
    return headers, body


@dp.message(F.text)
async def check_imei_tg_from_api(text: str):
    imei = text
    headers, body = headers_body(imei)
    try:
        response = requests.post(config.external_api_url, headers=headers, data=body)
        data = response.json()
        await results.put(data)
    except:
        await results.put({'error': 'Что-то пошло не так, попробуйте еще раз'})


async def run_bot():
    await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(run_bot())
