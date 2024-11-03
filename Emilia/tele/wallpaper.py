# DONE: Wallpaper

import asyncio
import random

from requests import get

from Emilia import telethn
from Emilia.custom_filter import register
from Emilia.helper.disable import disable
from Emilia.utils.decorators import *


@usage("/wall [query]")
@example("/wall naruto")
@description("This will send desired wallpaper.")
@register(pattern="wall", disable=True)
@disable
@rate_limit(40, 60)
async def some1(event):
    try:
        inpt: str = (
            event.text.split(None, 1)[1]
            if len(event.text) < 3
            else event.text.split(None, 1)[1].replace(" ", "%20")
        )
    except IndexError:
        return await usage_string(event, some1)

    Emievent = await event.reply("Sending please wait...")
    try:
        r = get(
            f"https://bakufuapi.vercel.app/api/wall/wallhaven?query={inpt}&page=1"
        ).json()

        list_id = [r["response"][i]["path"] for i in range(len(r["response"]))]
        item = (random.sample(list_id, 1))[0]
    except BaseException:
        await event.reply("Try again later or enter correct query.")
        await Emievent.delete()
        return

    await telethn.send_file(event.chat_id, item, caption="Preview", reply_to=event)
    await telethn.send_file(
        event.chat_id, file=item, caption="wall", reply_to=event, force_document=True
    )
    await Emievent.delete()
    await asyncio.sleep(5)
