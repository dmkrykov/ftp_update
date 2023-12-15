import listupdate
import xmlgenerator
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.ttk import Checkbutton
from tkinter import scrolledtext
from tkinter.ttk import Progressbar
from config import Config
import base64
import datetime
import pathlib
from tgBot import TgBot
import os


class Gui(object):
    'Pattern class is a singleton'
    _instance = None
    window = None
    cfg: Config

    def __new__(cls, config: Config):
        if Gui._instance is None:
            Gui._instance = super().__new__(cls)
        return Gui._instance

    def __init__(self, config: Config):
        self.cfg = config
        self.window = Tk()
        self.window.title('Управление справочниками v.1.0.2')
        self.window.geometry('740x480')
        self.window.resizable(FALSE, FALSE)

        Label(self.window, text='Настройки подключения', font=('Bookman Old Style', 12), pady=10).grid(column=0, row=0, columnspan=6)
        upd_cfg = Button(self.window, text='Обновить настройки', command=self.btn_upd_config)
        upd_cfg.grid(column=4, row=0)

        Label(self.window, text='SQL Config |->', font=('Bookman Old Style', 10)).grid(column=0, row=1, rowspan=2)
        Label(self.window, text='Login').grid(column=1, row=1)
        self.sq_log = Entry(self.window, width=30)
        self.sq_log.grid(column=2, row=1)
        self.sq_log.insert(INSERT, base64.b85decode(self.cfg.conn['sq_user']).decode('utf-8'))
        Label(self.window, text='Password').grid(column=3, row=1)
        self.sq_pwd = Entry(self.window, width=30, show='*')
        self.sq_pwd.grid(column=4, row=1)
        self.sq_pwd.insert(INSERT, base64.b85decode(self.cfg.conn['sq_pwd']).decode('utf-8'))
        Label(self.window, text='SQL Host').grid(column=1, row=2)
        self.sq_host = Entry(self.window, width=30)
        self.sq_host.grid(column=2, row=2)
        self.sq_host.insert(INSERT, self.cfg.conn['sq_host'])
        Label(self.window, text='DB Name').grid(column=3, row=2)
        self.sq_db = Entry(self.window, width=30)
        self.sq_db.grid(column=4, row=2)
        self.sq_db.insert(INSERT, self.cfg.conn['sq_db'])
        ttk.Separator(self.window, orient=HORIZONTAL, style='TSeparator', takefocus= 1, cursor='plus').grid(row=3, sticky=EW, columnspan=6, pady=8)

        Label(self.window, text='FTP Config |->', font=('Bookman Old Style', 10)).grid(column=0, row=4, rowspan=2)
        Label(self.window, text='Login').grid(column=1, row=4)
        self.ftp_log = Entry(self.window, width=30)
        self.ftp_log.grid(column=2, row=4)
        self.ftp_log.insert(INSERT, base64.b85decode(self.cfg.conn['f_user']).decode('utf-8'))
        Label(self.window, text='Password').grid(column=3, row=4)
        self.ftp_pwd = Entry(self.window, width=30, show='*')
        self.ftp_pwd.grid(column=4, row=4)
        self.ftp_pwd.insert(INSERT, base64.b85decode(self.cfg.conn['f_pwd']).decode('utf-8'))
        Label(self.window, text='FTP Host').grid(column=1, row=5)
        self.ftp_host = Entry(self.window, width=30)
        self.ftp_host.grid(column=2, row=5)
        self.ftp_host.insert(INSERT, self.cfg.conn['f_host'])
        Label(self.window, text='FTP Port').grid(column=3, row=5)
        self.ftp_port = Entry(self.window, width=30)
        self.ftp_port.grid(column=4, row=5)
        self.ftp_port.insert(INSERT, self.cfg.conn['f_port'])
        ttk.Separator(self.window, orient=HORIZONTAL, style='TSeparator', takefocus=1, cursor='plus').grid(row=6, sticky=EW, columnspan=6, pady=8)

        Label(self.window, text='Telegram Config |->', font=('Bookman Old Style', 10)).grid(column=0, row=7, rowspan=2)
        Label(self.window, text='API Token').grid(column=1, row=7)
        self.tg_token = Entry(self.window, width=30)
        self.tg_token.grid(column=2, row=7)
        self.tg_token.insert(INSERT, self.cfg.conn['tg_token'])
        Label(self.window, text='Chat ID').grid(column=3, row=7)
        self.tg_id = Entry(self.window, width=30)
        self.tg_id.grid(column=4, row=7)
        self.tg_id.insert(INSERT, self.cfg.conn['tg_id'])
        ttk.Separator(self.window, orient=HORIZONTAL, style='TSeparator', takefocus=1, cursor='plus').grid(row=8, sticky=EW, columnspan=6, pady=8)

        Label(self.window, text='Обновление справочников', font=('Bookman Old Style', 12), pady=10).grid(column=0, row=9, columnspan=6)
        Label(self.window, text='StopList.xml |->', font=('Bookman Old Style', 10)).grid(column=0, row=10)
        upd_stop = Button(self.window, text='Обновить', command=self.btn_upd_stop)
        upd_stop.grid(column=1, row=10)
        self.chk_post_tg_st = BooleanVar()
        self.chk_post_tg_st.set(True)
        chk_post_tg = Checkbutton(self.window, text='POST TG', variable=self.chk_post_tg_st)
        chk_post_tg.grid(column=2, row=10)
        Label(self.window, text='Выгрузить за N дней').grid(column=3, row=10)
        self.stp_days = Entry(self.window, width=10)
        self.stp_days.grid(column=4, row=10)
        self.stp_days.insert(INSERT, self.cfg.conn['stp_days'])
        self.get_stop = Button(self.window, text='Выгрузить из SQL без обновления на FTP', command=self.btn_get_stop)
        self.get_stop.grid(column=1, row=11, columnspan=2)
        self.stp_force = Button(self.window, text='Принудительно обновить', command=self.btn_force_stop)
        self.stp_force.grid(column=3, row=11, columnspan=2)
        ttk.Separator(self.window, orient=HORIZONTAL, style='TSeparator', takefocus=1, cursor='plus').grid(row=12, sticky=EW, columnspan=6, pady=8)
        Label(self.window, text='Справочники |->', font=('Bookman Old Style', 10)).grid(column=0, row=13)
        upd_list = Button(self.window, text='Обновить', command=self.btn_upd_list)
        upd_list.grid(column=1, row=13)
        self.chk_post_tg_lst = BooleanVar()
        self.chk_post_tg_lst.set(True)
        chk_post_list = Checkbutton(self.window, text='POST TG', variable=self.chk_post_tg_st)
        chk_post_list.grid(column=2, row=13)
        upd_list_force = Button(self.window, text='Принудительно обновить', command=self.btn_force_list)
        upd_list_force.grid(column=3, row=13)
        Label(self.window, text='↓Исключения (через пробел)↓').grid(column=4, row=13)
        self.except_list = Entry(self.window, width= 30)
        self.except_list.grid(column=4, row=19)
        self.except_list.insert(INSERT, self.cfg.conn['exception'])

        upl_csv = Button(self.window, text='Выгрузить CSV с тегами', command=self.btn_upl_csv)
        upl_csv.grid(column=2, row=19)
        cls_logs = Button(self.window, text='Очистить логи', command=self.btn_cls_logs)
        cls_logs.grid(column=0, row=19)

        self.txt_logs = scrolledtext.ScrolledText(self.window, width=88, height=5, state=tk.NORMAL)
        self.txt_logs.grid(column=0, row=20, columnspan=6, padx=5)
        self.txt_logs.insert(INSERT, 'Поле вывода логов')

        self.bar = Progressbar(self.window, length=720)
        self.bar.grid(column=0, row=21, columnspan=6, padx=5)
        self.bar['value'] = 0

        self.window.mainloop()

    def btn_upd_config(self):
        self.cfg.conn['f_host'] = self.ftp_host.get()
        self.cfg.conn['f_user'] = base64.b85encode(str(self.ftp_log.get()).encode('utf-8'))
        self.cfg.conn['f_pwd'] = base64.b85encode(str(self.ftp_pwd.get()).encode('utf-8'))
        self.cfg.conn['f_port'] = self.ftp_port.get()
        self.cfg.conn['sq_host'] = self.sq_host.get()
        self.cfg.conn['sq_db'] = self.sq_db.get()
        self.cfg.conn['sq_user'] = base64.b85encode(str(self.sq_log.get()).encode('utf-8'))
        self.cfg.conn['sq_pwd'] = base64.b85encode(str(self.sq_pwd.get()).encode('utf-8'))
        self.cfg.conn['tg_token'] = self.tg_token.get()
        self.cfg.conn['tg_id'] = self.tg_id.get()
        self.cfg.conn['stp_days'] = self.stp_days.get()
        self.cfg.conn['exception'] = self.except_list.get()
        self.cfg.save_config()

        messagebox.showinfo('Status', 'Конфигурация сохранена в config.dat')

    def btn_cls_logs(self):
        self.txt_logs.delete(1.0, END)

    def btn_upl_csv(self):
        self.txt_logs.focus()
        self.btn_cls_logs()
        lu = listupdate.ListsUpdate(self, self.cfg.conn['f_host'], int(self.cfg.conn['f_port']),
                                    base64.b85decode(self.cfg.conn['f_user']).decode('utf-8'),
                                    base64.b85decode(self.cfg.conn['f_pwd']).decode('utf-8'))
        lu.ftp_scan_price_type()
        messagebox.showinfo('Status', 'Операция успешно завершена')

    def btn_force_list(self):
        self.txt_logs.focus()
        self.btn_cls_logs()
        time_start = datetime.datetime.now()
        self.add_log(f'Start date: {time_start}')
        lu = listupdate.ListsUpdate(self, self.cfg.conn['f_host'], int(self.cfg.conn['f_port']),
                                    base64.b85decode(self.cfg.conn['f_user']).decode('utf-8'),
                                    base64.b85decode(self.cfg.conn['f_pwd']).decode('utf-8'))
        lu.backup_ftp()
        upload_list = os.listdir(str(pathlib.Path(pathlib.Path.cwd(), 'files', 'upload')))
        # m_6751 - medsi folder
        exception_list = self.except_list.get().split()
        self.add_log(f'Lists for update: {str(upload_list)}')
        lu.upload_lists('/', upload_list, exception_list)
        self.add_log(f'Updating time: {datetime.datetime.now() - time_start}')
        messagebox.showinfo('Status', 'Операция успешно завершена')

    def btn_upd_list(self):
        self.txt_logs.focus()
        self.btn_cls_logs()
        time_start = datetime.datetime.now()
        self.add_log(f'Start date: {time_start}')
        lu = listupdate.ListsUpdate(self, self.cfg.conn['f_host'], int(self.cfg.conn['f_port']),
                                            base64.b85decode(self.cfg.conn['f_user']).decode('utf-8'),
                                            base64.b85decode(self.cfg.conn['f_pwd']).decode('utf-8'))
        lu.backup_ftp()
        # m_6751 - medsi folder
        exception_list = self.except_list.get().split()
        hash_list = lu.check_hash()
        lu.upload_lists('/', hash_list, exception_list)
        self.add_log(f'Updating time: {datetime.datetime.now() - time_start}')
        if hash_list and self.chk_post_tg_lst.get():
            tg = TgBot(self.cfg)
            tg.send_message_tg(f'''<b>Справочники</b>\n<u><i>Обновление справочников завершено</i></u>\nСписок файлов:\n
                                \n<code>{hash_list}</code>\n#справочники''')
        messagebox.showinfo('Status', 'Операция успешно завершена')

    def btn_get_stop(self):
        self.txt_logs.focus()
        self.btn_cls_logs()
        # за сколько дней выгружать стоп лист
        old_date = datetime.date.today() - datetime.timedelta(days=int(self.stp_days.get()))

        stp = xmlgenerator.XmlGenerator(self, self.cfg.conn['sq_host'], self.cfg.conn['sq_db'],
                                        base64.b85decode(self.cfg.conn['sq_user']).decode('utf-8'),
                                        base64.b85decode(self.cfg.conn['sq_pwd']).decode('utf-8'))
        stp.generate_stoplist(str(old_date))
        upload_ftp = listupdate.ListsUpdate(self, self.cfg.conn['f_host'], int(self.cfg.conn['f_port']),
                                            base64.b85decode(self.cfg.conn['f_user']).decode('utf-8'),
                                            base64.b85decode(self.cfg.conn['f_pwd']).decode('utf-8'))
        upload_ftp.uploadDir = pathlib.Path(pathlib.Path.cwd(), 'files', 'stop')
        stp_list = upload_ftp.check_hash()
        self.add_log(f'Check hash sum: {stp_list}')
        self.add_log(f'Generate complete StopList.xml -> /files/stop')
        messagebox.showinfo('Status', 'Операция успешно завершена')

    def btn_force_stop(self):
        self.txt_logs.focus()
        self.btn_cls_logs()

        time_start = datetime.datetime.now()
        self.add_log(f'Start time: {time_start}')
        # за сколько дней выгружать стоп лист
        old_date = datetime.date.today() - datetime.timedelta(days=int(self.stp_days.get()))

        stp = xmlgenerator.XmlGenerator(self, self.cfg.conn['sq_host'], self.cfg.conn['sq_db'],
                                        base64.b85decode(self.cfg.conn['sq_user']).decode('utf-8'),
                                        base64.b85decode(self.cfg.conn['sq_pwd']).decode('utf-8'))
        stp.generate_stoplist(str(old_date))
        upload_ftp = listupdate.ListsUpdate(self, self.cfg.conn['f_host'], int(self.cfg.conn['f_port']),
                                            base64.b85decode(self.cfg.conn['f_user']).decode('utf-8'),
                                            base64.b85decode(self.cfg.conn['f_pwd']).decode('utf-8'))
        upload_ftp.uploadDir = pathlib.Path(pathlib.Path.cwd(), 'files', 'stop')
        stp_list = upload_ftp.check_hash()
        self.add_log(f'Check hash sum: {stp_list}')
        upload_ftp.upload_lists('/', ['StopList.xml', 'StopList.xml.sha256'])
        self.add_log(f'Updating time: {datetime.datetime.now() - time_start}')
        messagebox.showinfo('Status', 'Операция успешно завершена')

    def btn_upd_stop(self):
        self.txt_logs.focus()
        self.btn_cls_logs()

        time_start = datetime.datetime.now()
        self.add_log(f'Start time: {time_start}')
        # за сколько дней выгружать стоп лист
        old_date = datetime.date.today() - datetime.timedelta(days=int(self.stp_days.get()))

        stp = xmlgenerator.XmlGenerator(self, self.cfg.conn['sq_host'], self.cfg.conn['sq_db'],
                           base64.b85decode(self.cfg.conn['sq_user']).decode('utf-8'),
                           base64.b85decode(self.cfg.conn['sq_pwd']).decode('utf-8'))
        stp.generate_stoplist(str(old_date))

        upload_ftp = listupdate.ListsUpdate(self, self.cfg.conn['f_host'], int(self.cfg.conn['f_port']),
                                 base64.b85decode(self.cfg.conn['f_user']).decode('utf-8'),
                                 base64.b85decode(self.cfg.conn['f_pwd']).decode('utf-8'))
        upload_ftp.uploadDir = pathlib.Path(pathlib.Path.cwd(), 'files', 'stop')
        stp_list = upload_ftp.check_hash()
        new_test = stp.compare_stoplist(upload_ftp, str(old_date))
        self.add_log(new_test)

        empty = True
        for i in new_test:
            if new_test[i]:
                empty = False

        upload_ftp.upload_lists('/', stp_list)

        if not empty and self.chk_post_tg_st.get():
            # send message in telegram
            tg = TgBot(self.cfg)
            tg.send_msg_stop_update(new_test)

        self.add_log(f'Updating time: {datetime.datetime.now() - time_start}')
        messagebox.showinfo('Status', 'Операция успешно завершена')

    def add_log(self, txt: str):
        sep_txt = f'{txt}\n'
        self.txt_logs.insert(INSERT, sep_txt)
