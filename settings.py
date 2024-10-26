import os

SAVE_LATEST_MESSAGE = True
ADMIN_GROUP = os.getenv("ADMIN_GROUP", "").split(",")
HIDERS_CHECKER = 'hider_checker.TTKHidersChecker'
TOKEN = os.getenv('TOKEN', '')
