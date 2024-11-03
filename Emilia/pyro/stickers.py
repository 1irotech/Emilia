import os
import re
import shutil
import tempfile

import cv2
import ffmpeg
from PIL import Image
from pyrogram import Client, emoji, enums, filters
from pyrogram.errors import BadRequest, PeerIdInvalid, StickersetInvalid
from pyrogram.file_id import FileId
from pyrogram.raw.functions.messages import GetStickerSet, SendMedia
from pyrogram.raw.functions.stickers import (
    AddStickerToSet,
    CreateStickerSet,
    RemoveStickerFromSet,
)
from pyrogram.raw.types import (
    DocumentAttributeFilename,
    InputDocument,
    InputMediaUploadedDocument,
    InputStickerSetItem,
    InputStickerSetShortName,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Emilia import EVENT_LOGS as LOG_CHANNEL, BOT_USERNAME
from Emilia import custom_filter, pgram
from Emilia.helper.disable import disable
from Emilia.helper.http import http
from Emilia.utils.decorators import *


@usage("/stickerid [reply to a sticker]")
@example("/stickerid [reply to a sticker]")
@description("Fetches integer id of replied sticker.")
@Client.on_message(custom_filter.command(commands="stickerid", disable=True))
@disable
async def _stickidd(_, me):
    replied = me.reply_to_message
    text = "Sticker ID: `{}`"

    if replied and replied.sticker:
        await me.reply_text(text.format(replied.sticker.file_id))
    else:
        await usage_string(me, _stickidd)
        return


@usage("/getsticker [reply to a sticker]")
@example("/getsticker [reply to a sticker]")
@description("Will send you png file of replied sticker.")
@Client.on_message(custom_filter.command(commands="getsticker", disable=True))
@disable
async def _stickid0(c, m):
    if sticker := m.reply_to_message.sticker:
        if sticker.is_animated:
            await m.reply_text("Animated sticker is not supported!")
        else:
            with tempfile.TemporaryDirectory() as tempdir:
                path = os.path.join(tempdir, "getsticker")
            sticker_file = await c.download_media(
                message=m.reply_to_message,
                file_name=f"{path}/{sticker.set_name}.png",
            )
            await m.reply_to_message.reply_document(
                document=sticker_file,
                caption=(
                    f"<b>Emoji</b>: {sticker.emoji}\n"
                    f"<b>Sticker ID</b>: <code>{sticker.file_id}</code>\n\n"
                ),
            )
            shutil.rmtree(tempdir, ignore_errors=True)
    else:
        await usage_string(m, _stickid0)
        return


@usage("/getvidsticker [reply to an animated sticker]")
@example("/getvidsticker [reply to an animated sticker]")
@description("Will send you mp4 file of replied animated/video sticker.")
@Client.on_message(custom_filter.command(commands="getvidsticker", disable=True))
@disable
async def _vidstick(_, message):
    chat_id = message.chat.id
    replied = message.reply_to_message
    if replied and replied.sticker:
        if not replied.sticker.is_video:
            return await message.reply_text(
                "Use /getsticker if sticker is not a video!"
            )
        file_id = replied.sticker.file_id
        new_file = await _.download_media(file_id, file_name="sticker.mp4")
        await _.send_animation(chat_id, new_file)
        os.remove(new_file)
    else:
        await usage_string(message, _vidstick)
        return


@usage("/getvideo [reply to a GIF file]")
@example("/getvidsticker [reply to a GIF file]")
@description("Will send you mp4 file of replied GIF media.")
@Client.on_message(custom_filter.command(commands="getvideo", disable=True))
@disable
async def _vidstick0(_, message):
    chat_id = message.chat.id
    replied = message.reply_to_message
    if replied and replied.animation:
        file_id = replied.animation.file_id
        new_file = await _.download_media(file_id, file_name="video.mp4")
        print(new_file)
        await _.send_video(chat_id, video=open(new_file, "rb"))
        os.remove(new_file)
    else:
        await usage_string(message, _vidstick0)
        return


def get_emoji_regex():
    e_list = [
        getattr(emoji, e).encode("unicode-escape").decode("ASCII")
        for e in dir(emoji)
        if not e.startswith("_")
    ]
    # to avoid re.error excluding char that start with '*'
    e_sort = sorted([x for x in e_list if not x.startswith("*")], reverse=True)
    # Sort emojis by length to make sure multi-character emojis are
    # matched first
    pattern_ = f"({'|'.join(e_sort)})"
    return re.compile(pattern_)


EMOJI_PATTERN = get_emoji_regex()


@usage("/unkang [reply to a sticker]")
@example("/unkang [reply to a sticker]")
@description(
    "Will remove the sticker from your pack which has been created by @Elf_Robot."
)
@Client.on_message(
    custom_filter.command(commands=["unkang", "delsticker"], disable=True)
    & filters.reply
)
@disable
async def unkang(c, m):
    if m.reply_to_message.sticker:
        try:
            decoded = FileId.decode(m.reply_to_message.sticker.file_id)
            sticker = InputDocument(
                id=decoded.media_id,
                access_hash=decoded.access_hash,
                file_reference=decoded.file_reference,
            )
            await pgram.invoke(RemoveStickerFromSet(sticker=sticker))
            await m.reply("💌 Sticker has been removed from your pack.")
        except Exception as e:
            await m.reply(f"Failed to remove sticker from your pack.\n\n**Error**: {e}")
    else:
        await usage_string(m, unkang)
        return


@usage("/kang [reply to a sticker]")
@example("/kang [reply to a sticker]")
@description("Will add the sticker to your pack.")
@Client.on_message(custom_filter.command(commands="kang", disable=True))
@disable
async def kang_sticker(c, m):
    if m.sender_chat:
        return await m.reply_text("You are anonymous, please kang in my PM.")
    sticker_emoji = "🤔"
    packnum = 0
    packname_found = False
    resize = False
    animated = False
    videos = False
    convert = False
    reply = m.reply_to_message
    user = await c.resolve_peer(m.from_user.username or m.from_user.id)
    if reply and reply.media:
        if reply.photo:
            resize = True
        elif reply.animation:
            videos = True
            convert = True
        elif reply.video:
            convert = True
            videos = True
        elif reply.document:
            if "image" in reply.document.mime_type:
                # mime_type: image/webp
                resize = True
            elif reply.document.mime_type in (
                enums.MessageMediaType.VIDEO,
                enums.MessageMediaType.ANIMATION,
            ):
                # mime_type: application/video
                videos = True
                convert = True
            elif "tgsticker" in reply.document.mime_type:
                # mime_type: application/x-tgsticker
                animated = True
        elif reply.sticker:
            if not reply.sticker.file_name:
                return await m.reply("The sticker has no name.")
            if reply.sticker.emoji:
                sticker_emoji = reply.sticker.emoji
            animated = reply.sticker.is_animated
            videos = reply.sticker.is_video
            if videos:
                convert = False
            elif not reply.sticker.file_name.endswith(".tgs"):
                resize = True
        else:
            return

        pack_prefix = "anim" if animated else "vid" if videos else "a"
        packname = f"{pack_prefix}_{m.from_user.id}_by_{c.me.username}"

        if len(m.command) > 1 and m.command[1].isdigit() and int(m.command[1]) > 0:
            # provide pack number to kang in desired pack
            packnum = m.command.pop(1)
            packname = f"{pack_prefix}{packnum}_{m.from_user.id}_by_{c.me.username}"
        if len(m.command) > 1:
            # matches all valid emojis in input
            sticker_emoji = (
                "".join(set(EMOJI_PATTERN.findall("".join(m.command[1:]))))
                or sticker_emoji
            )
        filename = await c.download_media(m.reply_to_message)
        if not filename:
            # Failed to download
            return
    elif m.entities and len(m.entities) > 1:
        pack_prefix = "a"
        filename = "sticker.png"
        packname = f"c{m.from_user.id}_by_{c.me.username}"
        img_url = next(
            (
                m.text[y.offset : (y.offset + y.length)]
                for y in m.entities
                if y.type == "url"
            ),
            None,
        )

        if not img_url:
            return
        try:
            r = await http.get(img_url)
            if r.status_code == 200:
                with open(filename, mode="wb") as f:
                    f.write(r.read())
        except Exception as r_e:
            return await m.reply(f"{r_e.__class__.__name__} : {r_e}")
        if len(m.command) > 2:
            # m.command[1] is image_url
            if m.command[2].isdigit() and int(m.command[2]) > 0:
                packnum = m.command.pop(2)
                packname = f"a{packnum}_{m.from_user.id}_by_{c.me.username}"
            if len(m.command) > 2:
                sticker_emoji = (
                    "".join(set(EMOJI_PATTERN.findall("".join(m.command[2:]))))
                    or sticker_emoji
                )
            resize = True
    else:
        await usage_string(m, kang_sticker)
        return
    try:
        if resize:
            filename = resize_image(filename)
        elif convert:
            filename = await convert_video(filename)
            if filename is False:
                return await m.reply("Error")
        max_stickers = 50 if animated else 120
        while not packname_found:
            try:
                stickerset = await c.invoke(
                    GetStickerSet(
                        stickerset=InputStickerSetShortName(short_name=packname),
                        hash=0,
                    )
                )
                if stickerset.set.count >= max_stickers:
                    packnum += 1
                    packname = (
                        f"{pack_prefix}_{packnum}_{m.from_user.id}_by_{c.me.username}"
                    )
                else:
                    packname_found = True
            except StickersetInvalid:
                break
        file = await c.save_file(filename)
        media = await c.invoke(
            SendMedia(
                peer=(await c.resolve_peer(LOG_CHANNEL)),
                media=InputMediaUploadedDocument(
                    file=file,
                    mime_type=c.guess_mime_type(filename),
                    attributes=[DocumentAttributeFilename(file_name=filename)],
                ),
                message=f"#Sticker kang by UserID -> {m.from_user.id}",
                random_id=c.rnd_id(),
            ),
        )
        msg_ = media.updates[-1].message
        stkr_file = msg_.media.document
        if packname_found:
            await c.invoke(
                AddStickerToSet(
                    stickerset=InputStickerSetShortName(short_name=packname),
                    sticker=InputStickerSetItem(
                        document=InputDocument(
                            id=stkr_file.id,
                            access_hash=stkr_file.access_hash,
                            file_reference=stkr_file.file_reference,
                        ),
                        emoji=sticker_emoji,
                    ),
                )
            )
        else:
            stkr_title = f"{m.from_user.first_name}'s"
            if animated:
                stkr_title += "AnimPack"
            elif videos:
                stkr_title += "VidPack"
            if packnum != 0:
                stkr_title += f" v{packnum}"
            try:
                await c.invoke(
                    CreateStickerSet(
                        user_id=user,
                        title=stkr_title,
                        short_name=packname,
                        stickers=[
                            InputStickerSetItem(
                                document=InputDocument(
                                    id=stkr_file.id,
                                    access_hash=stkr_file.access_hash,
                                    file_reference=stkr_file.file_reference,
                                ),
                                emoji=sticker_emoji,
                            )
                        ],
                        animated=animated,
                        videos=videos,
                    )
                )
            except PeerIdInvalid:
                return await m.reply(
                    "It looks like you've never interacted with me in private chat, you need to do that first..",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Click Me",
                                    url=f"https://t.me/{BOT_USERNAME}?start",
                                )
                            ]
                        ]
                    ),
                )

    except BadRequest as e:
        print(e)
        return await m.reply(
            "Your Sticker Pack is full if your pack is not in v1 Type /kang 1, if it is not in v2 Type /kang 2 and so on."
        )
    else:
        markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="View Your Pack",
                        url=f"https://t.me/addstickers/{packname}",
                    )
                ]
            ]
        )
        await m.reply(
            f"<b>Sticker successfully stolen!</b>\n<b>Emoji:</b> {sticker_emoji}",
            reply_markup=markup,
        )
        # Cleanup
        await c.delete_messages(chat_id=LOG_CHANNEL, message_ids=msg_.id, revoke=True)
        try:
            os.remove(filename)
        except OSError:
            pass


def resize_image(filename: str) -> str:
    im = Image.open(filename)
    maxsize = 512
    scale = maxsize / max(im.width, im.height)
    sizenew = (int(im.width * scale), int(im.height * scale))
    im = im.resize(sizenew, Image.NEAREST)
    downpath, f_name = os.path.split(filename)
    # not hardcoding png_image as "sticker.png"
    png_image = os.path.join(downpath, f"{f_name.split('.', 1)[0]}.png")
    im.save(png_image, "PNG")
    if png_image != filename:
        os.remove(filename)
    return png_image


async def convert_video(input):
    vid = cv2.VideoCapture(input)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)

    # check height and width to scale
    if width > height:
        width = 512
        height = -1
    elif height > width:
        height = 512
        width = -1
    elif width == height:
        width = 512
        height = 512

    converted_name = "kangsticker.webm"

    (
        ffmpeg.input(input)
        .filter("fps", fps=30, round="up")
        .filter("scale", width=width, height=height)
        .trim(start="00:00:00", end="00:00:03", duration="3")
        .output(
            converted_name,
            vcodec="libvpx-vp9",
            **{
                # 'vf': 'scale=512:-1',
                "crf": "30"
            },
        )
        .overwrite_output()
        .run()
    )

    return converted_name
