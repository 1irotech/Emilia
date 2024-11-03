from pyrogram import Client
from requests import get

from Emilia import custom_filter
from Emilia.helper.disable import disable
from Emilia.utils.decorators import *


@Client.on_message(
    custom_filter.command(commands=["joke", "jokes", "funny"], disable=True)
)
@rate_limit(10, 60)
@disable
async def joke(client, message):
    try:
        joke = get("https://v2.jokeapi.dev/joke/Any").json()
        try:
            get1 = joke["setup"]
            get2 = joke["delivery"]
            await message.reply(f"{get1}\n{get2}")
        except BaseException:
            get3 = joke["joke"]
            await message.reply(get3)
    except Exception as e:
        return await message.reply(
            str(e) + "\nPlease report to support chat @SpiralTechDivision"
        )
