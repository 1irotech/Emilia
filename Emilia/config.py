import json
import os


def get_user_list(config, key):
    with open("{}/Emilia/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]


class Config(object):
    API_HASH = "cb5d60ad1402ce922d53bc500abd20df" # API_HASH from my.telegram.org
    API_ID = 22169867 # API_ID from my.telegram.org

    BOT_ID = 7575301138 # BOT_ID
    BOT_USERNAME = "irowriterobot" # BOT_USERNAME

    MONGO_DB_URL = "mongodb+srv://vikashgup87:EDRIe3bdEq85Pdpl@cluster0.pvoygcu.mongodb.net/?retryWrites=true&w=majority" # MongoDB URL from MongoDB Atlas

    SUPPORT_CHAT = "ironmanhindigming" # Support Chat Username
    UPDATE_CHANNEL = "irotechbotz0" # Update Channel Username
    START_PIC = "https://iili.io/2wrEKlt.jpg" # Start Image
    DEV_USERS = [7086360370] # Dev Users
    TOKEN = "7575301138:AAGxh6m_zmkMVF68WVOwvoEjrDSpyDon2bk" # Bot Token from @BotFather

    EVENT_LOGS = -1002471941785 # Event Logs Chat ID
    OWNER_ID = 7086360370 # Owner ID
 
    TEMP_DOWNLOAD_DIRECTORY = "./" # Temporary Download Directory
    BOT_NAME = "IRO WRITER" # Bot Name
    WALL_API = "6950f53" # Wall API from wall.alphacoders.com
    ORIGINAL_EVENT_LOOP = True # Do not Change


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
