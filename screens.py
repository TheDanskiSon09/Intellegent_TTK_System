import settings
from hammett.core.mixins import StartMixin
from hammett.core.screen import Screen
from hammett.core.constants import SourcesTypes
from hammett.core import Button
from hammett.core.handlers import register_typing_handler, register_button_handler
from pymystem3 import Mystem
import constants as con
import sqlite3

connection = sqlite3.connect('TTK_database.db')
cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
agreement_number TEXT PRIMARY KEY,
role TEXT,
phone_number TEXT,
email INTEGER,
id INTEGER
)
''')


class Global:
    input = bool
    action = ''
    mystem = Mystem()
    agr_num = ''
    phone_number = ''
    email = ''


class BaseScreen(Screen):
    hide_keyboard = True
    cache_covers = False


async def show_bad_request(text: str, _update, _context):
    BadRequest.description = text
    return await BadRequest().jump(_update, _context)


async def get_clean_var(var):
    var = str(var)
    for symbols in con.REMOVE_SYMBOLS:
        var = var.replace(symbols, '')
    return var


async def get_request(_update, _context, media_type, action_type):
    global connection, cursor
    if media_type == "text":
        if action_type == "get_action":
            request = [_update.message.text]
            print(request)
            for i in request:
                if i in con.WORDS:
                    if i == "Договор":
                        return await Authorisation().jump(_update, _context)
                    if i == "Администрирование":
                        if str(_update.message.chat.id) in str(settings.ADMIN_GROUP):
                            return await Admin().jump(_update, _context)
                else:
                    await show_bad_request("<strong>Извините, я не понял Вашу команду - "
                                           "повторите попытку</strong>", _update, _context)
        if action_type == "get_agr_num":
            request = _update.message.text
            print(request)
            if len(request) == 9:
                cursor.execute("SELECT agreement_number FROM Users WHERE agreement_number = ?",
                               (request,))
                check = cursor.fetchall()
                check = await get_clean_var(check)
                if len(check) > 0:
                    cursor.execute("SELECT id FROM Users WHERE agreement_number = ?",
                                   (check,))
                    check_id = cursor.fetchall()
                    check_id = await get_clean_var(check_id)
                    if str(_update.message.chat.id) == str(check_id):
                        Global.agr_num = check
                        Global.action = "get_action"
                        await show_bad_request("<strong>Вход прошёл успешно!</strong>", _update, _context)
                else:
                    await show_bad_request("<strong>Извините, но данный договор не зарегистрирован", _update, _context)
            else:
                await show_bad_request("<strong>Извините, но номер договора должен быть девятизначным числом - "
                                       "повторите попытку</strong>", _update, _context)
        if action_type == "get_mobile":
            try:
                check = int(_update.message.text)
                request = str(_update.message.text)
                if len(request) == 11:
                    cursor.execute("SELECT phone_number FROM Users WHERE phone_number = ?", (request,))
                    check1 = str(cursor.fetchall())
                    check1 = await get_clean_var(check1)
                    if len(check1) > 0:
                        await show_bad_request("<strong>Извините, но на данный номер телефона уже "
                                               "зарегистрирован договор</strong>",
                                               _update, _context)
                    else:
                        Global.phone_number = request
                        SignUp.description = "<strong>Пожалуйста, введите Вашу электронную почту</strong>"
                        Global.action = "get_email"
                        return await SignUp().jump(_update, _context)
                else:
                    await show_bad_request("<strong>Извините, но Вы должны ввести 11 значный номер телефона - "
                                           "повторите попытку</strong>", _update, _context)
            except ValueError:
                await show_bad_request("<strong>Извините, но Вы должны ввести 11 значный номер телефона - "
                                       "повторите попытку</strong>", _update, _context)
        if action_type == "get_email":
            request = _update.message.text
            cursor.execute("SELECT email FROM Users WHERE email = ?", (request,))
            check1 = str(cursor.fetchall())
            check1 = await get_clean_var(check1)
            if len(check1) > 0:
                await show_bad_request("<strong>Извините, но на данную почту уже зарегистрирован договор</strong>",
                                       _update, _context)
            else:
                Global.email = request
                SignUp.description = "<strong>Пожалуйста, введите свой девятизначный номер Вашего договора</strong>"
                Global.action = "set_custom_agr"
                return await SignUp().jump(_update, _context)
        if action_type == "set_custom_agr":
            try:
                check = int(_update.message.text)
                request = _update.message.text
                if len(request) == 9:
                    cursor.execute("SELECT agreement_number FROM Users WHERE agreement_number = ?",
                                   (request,))
                    check1 = str(cursor.fetchall())
                    check1 = await get_clean_var(check1)
                    if len(check1) > 0:
                        await show_bad_request("<strong>Извините, но данное число договора уже "
                                               "зарегистрировано</strong>",
                                               _update, _context)
                    else:
                        Global.agr_num = request
                        cursor.execute("INSERT INTO Users (agreement_number, role, phone_number, email, id) VALUES "
                                       "(?, ?, ?, ?, ?)", (Global.agr_num, "Anonim", Global.phone_number, Global.email,
                                                           _update.message.chat.id,))
                        connection.commit()
                        await show_bad_request("<strong>Регистрация прошла успешно!</strong>", _update, _context)
                        Global.action = "get_action"
                        Global.agr_num = ''
                        Global.phone_number = ''
                        Global.email = ''
                else:
                    await show_bad_request(
                        "<strong>Извините, но Вы должны ввести девятизначный номер Вашего договора - "
                        "повторите попытку</strong>", _update, _context)
            except ValueError:
                await show_bad_request("<strong>Извините, но Вы должны ввести девятизначный номер Вашего договора - "
                                       "повторите попытку</strong>", _update, _context)


class MainMenu(StartMixin, BaseScreen):

    async def get_description(self, _update, _context):
        Global.input = True
        Global.action = "get_action"
        return '<strong>Здравствуйте! Это бот-ассистент компании ТТК!\nЧем я могу Вам помочь? </strong>'

    @register_typing_handler
    async def get_request(self, _update, _context):
        await get_request(_update, _context, "text", Global.action)


class Login(BaseScreen):

    async def get_description(self, _update, _context):
        Global.action = "get_agr_num"
        Global.input = True
        return '<strong>Пожалуйста, введите свой девятизначный номер договора</strong>'


class SignUp(BaseScreen):
    description = "_"


class YetAnotherScreen(BaseScreen):
    description = (
        'This is just another screen to demonstrate the built-in '
        'capability to switch between screens.'
    )

    async def add_default_keyboard(self, _update, _context):
        return [[
            Button(
                '⬅️ Back',
                MainMenu,
                source_type=SourcesTypes.GOTO_SOURCE_TYPE,
            )
        ]]


class BadRequest(BaseScreen):
    description = "_"


class Authorisation(BaseScreen):

    async def get_description(self, _update, _context):
        Global.input = False
        Global.action = ''
        return "<strong>Выберите одно из следующих действий:</strong>"

    async def add_default_keyboard(self, _update, _context):
        return [
            [
                Button("Войти как клиент ТТК", Login, source_type=SourcesTypes.GOTO_SOURCE_TYPE
                       )
            ],
            [
                Button("Заключить новый договор", self.start_sign_up, source_type=SourcesTypes.HANDLER_SOURCE_TYPE)
            ]
        ]

    @register_button_handler
    async def start_sign_up(self, _update, _context):
        Global.action = "get_mobile"
        SignUp.description = '<strong>Пожалуйста, введите свой номер телефона</strong>'
        return await SignUp().jump(_update, _context)


class TarrifList(BaseScreen):
    description = ''


class Admin(BaseScreen):
    description = ("<strong>Ссылка на сайт: http://192.168.31.213:5000/\nПароль для непосредственного доступа: "
                   "*****</strong>")


class AddService(BaseScreen):

    async def get_description(self, _update, _context):
        Global.action = "get_service"
