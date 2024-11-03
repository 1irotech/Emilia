from Emilia import db
from Emilia.functions.admins import is_owner
from Emilia.custom_filter import register
import Emilia.strings as strings
from Emilia.utils.decorators import rate_limit
from Emilia.pyro.connection.connection import connection
import json
import os
from bson import ObjectId

# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(JSONEncoder, self).default(obj)

# Define collections for different settings
collections = {
    'blocklists': db['blocklists'],
    'disable': db['disable'],
    'filters': db['filters'],
    'locks': db['locks'],
    'notes': db['notes'],
    'rules': db['rules'],
    'warnings': db['warnings'],
    'welcome': db['welcome']
}

@register(pattern="export")
@rate_limit(3, 1800)
async def export_settings(event):
    chat_id = await connection(event) if await connection(event) else event.chat_id
    if event.is_private and not str(chat_id).startswith('-100'):
        return await event.reply(strings.is_pvt)
    
    if not await is_owner(event, event.sender_id, chat_id):
        await event.reply("Only the chat owner can export settings.")
        return

    args = event.raw_text.split()[1:]

    # If no arguments, export all settings
    exported_data = {}
    if not args:
        for key, collection in collections.items():
            settings = await collection.find_one({'chat_id': chat_id})
            if settings:
                # Remove '_id' and 'chat_id' before exporting
                settings.pop('_id', None)
                settings.pop('chat_id', None)
                exported_data[key] = settings
    else:
        for arg in args:
            collection = collections.get(arg)
            if collection:
                settings = await collection.find_one({'chat_id': chat_id})
                if settings:
                    # Remove '_id' and 'chat_id' before exporting
                    settings.pop('_id', None)
                    settings.pop('chat_id', None)
                    exported_data[arg] = settings

    if not exported_data:
        await event.reply("No settings found.")
        return

    # Use the custom JSON encoder to handle ObjectId
    settings_json = json.dumps(exported_data, indent=4, cls=JSONEncoder)
    file_name = f"chat_settings_{chat_id}.json"
    
    with open(file_name, 'w') as file:
        file.write(settings_json)
    
    await event.respond(file=file_name)
    os.remove(file_name)


@register(pattern="import")
@rate_limit(3, 1800)
async def import_settings(event):
    chat_id = await connection(event) if await connection(event) else event.chat_id
    if event.is_private and not str(chat_id).startswith('-100'):
        return await event.reply(strings.is_pvt)

    if not await is_owner(event, event.sender_id, chat_id):
        await event.reply("Only the chat owner can import settings.")
        return

    if not event.is_reply:
        await event.reply("Reply to the JSON file containing settings.")
        return

    message = await event.get_reply_message()
    if not message.file or not message.file.name.endswith('.json'):
        await event.reply("Please reply to a valid JSON file.")
        return

    file_path = await message.download_media()

    with open(file_path, 'r') as file:
        settings = json.load(file)

    for key, value in settings.items():
        collection = collections.get(key)
        if collection is not None:
            # Remove existing '_id' if present and set the new 'chat_id'
            value.pop('_id', None)
            value['chat_id'] = chat_id
            
            # Check if the collection item already exists and update it or insert as needed
            existing_item = await collection.find_one({'chat_id': chat_id})
            if existing_item:
                # Update only the provided settings while preserving other fields
                await collection.update_one({'chat_id': chat_id}, {'$set': value})
            else:
                # Insert the new settings
                await collection.insert_one(value)

    await event.reply("Settings imported successfully.")
    os.remove(file_path)


@register(pattern="reset")
@rate_limit(3, 1800)
async def reset_settings(event):
    chat_id = await connection(event) if await connection(event) else event.chat_id
    if event.is_private and not str(chat_id).startswith('-100'):
        return await event.reply(strings.is_pvt)

    if not await is_owner(event, event.sender_id, chat_id):
        await event.reply("Only the chat owner can reset settings.")
        return

    for collection in collections.values():
        await collection.delete_one({'chat_id': chat_id})

    await event.reply("All chat settings have been reset.")
