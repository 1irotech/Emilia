import json
import os


def get_user_list(config, key):
    with open("{}/Emilia/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]


class Config(object):
    API_HASH = "45aabfac" # API_HASH from my.telegram.org
    API_ID = 62 # API_ID from my.telegram.org

    BOT_ID = 521 # BOT_ID
    BOT_USERNAME = "irowriterobot" # BOT_USERNAME

    MONGO_DB_URL = "mongodb://username:password@localhost:27017/emi?directConnection=true&authSource=admin" # MongoDB URL from MongoDB Atlas

    SUPPORT_CHAT = "ironmanhindigming" # Support Chat Username
    UPDATE_CHANNEL = "ironmanhindigaming11" # Update Channel Username
    START_PIC = "https://iili.io/2wrEKlt.jpg" # Start Image
    DEV_USERS = [6040984893, 6461051572, 7107018652] # Dev Users
    TOKEN = "7575301138:AAGxh6m_zmkMVF68WVOwvoEjrDSpyDon2bk" # Bot Token from @BotFather

    EVENT_LOGS = -10093 # Event Logs Chat ID
    OWNER_ID = 6040984893 # Owner ID
 
    TEMP_DOWNLOAD_DIRECTORY = "./" # Temporary Download Directory
    BOT_NAME = "IRO WRITER" # Bot Name
    WALL_API = "6950f53" # Wall API from wall.alphacoders.com
    ORIGINAL_EVENT_LOOP = True # Do not Change


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
