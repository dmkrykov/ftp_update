import telebot
from telebot import util
import datetime
from config import Config


class TgBot:
    API_TOKEN = ''
    CHAT_ID = ''  #  Integration Chat  testChannel 
    bot = None

    def __init__(self, cfg: Config):
        self.API_TOKEN = cfg.conn['tg_token']
        self.CHAT_ID = cfg.conn['tg_id']
        self.bot = telebot.TeleBot(self.API_TOKEN, parse_mode='HTML')

    def send_message_tg(self, message):
        messages = util.smart_split(message)
        for message in messages:
            self.bot.send_message(self.CHAT_ID, message)

    def send_msg_stop_update(self, new_test_dict: dict):
        str_add = ''
        str_del = ''
        for i in new_test_dict:
            if i == 'added':
                for j in new_test_dict[i]:
                    print(j)
                    str_add += f'{j} - {datetime.datetime.strptime(new_test_dict[i][j], "%Y-%m-%d %H:%M:%S").date()}\n'
                    print('Add: ', str_add)
            elif i == 'remove':
                for j in new_test_dict[i]:
                    print(j)
                    str_del += f'{j}\n'
                    print('Del: ', str_del)

        message = f'''<b>StopList.xml</b>\n<u><i>Обновление справочника завершено</i></u>\nСписок изменений:\n\nВременно не доступные услуги:\n<code>{str_add}</code>\nУслуги снова доступны:\n<code>{str_del}</code>\n#StopList'''

        self.send_message_tg(message)
