import ftplib
from ftplib import FTP_TLS
import xml.etree.ElementTree as ET
import os
import csv
from typing import List
from datetime import date
import hashlib
import pathlib


class ListsUpdate:
    'Класс для работы с ftp, обновления справочников интеграции'
    ftp = None
    outDir = str(pathlib.Path(pathlib.Path.cwd(), 'files', 'temp'))
    'Путь к временной папке'
    uploadDir = str(pathlib.Path(pathlib.Path.cwd(), 'files', 'upload'))
    'Путь к файлам для загрузки'
    msg_gui = None

    def __init__(self, gui_msg, host: str, port: int, user: str, pwd: str, encode='CP1251'):
        try:
            self.msg_gui = gui_msg
            self.ftp = FTP_TLS(host=host, encoding=encode)
            self.ftp.connect(host, port)
            self.ftp.login(user=user, passwd=pwd)
            # #Вызывает ошибку conn.unwrap() в модуле ftplib, ожидает ответ от сервара которого нет
            # self.ftp.prot_p()
            self.msg_gui.add_log(self.ftp.welcome)
        except ftplib.all_errors as e:
            self.msg_gui.add_log(f'Error: {e}')

    def __del__(self):
        try:
            self.ftp.close()
            self.msg_gui.add_log('FTP connection close')
        except ftplib.all_errors as e:
            self.msg_gui.add_log(f'Error: {e}')

    def get_LoadList(self, dir: str):
        'Возвращает список в указанной директории'
        curr_dir = self.ftp.pwd()
        self.set_CurrentDir(dir)
        li = self.ftp.nlst()
        self.set_CurrentDir(curr_dir)
        return li

    def set_CurrentDir(self, dir: str):
        'Устанавливает текущую директорию'
        self.ftp.cwd(dir)

    def backup_ftp(self, bkp_folder: str = '!backup',  folder: str = '!Template Folder'):
        '''Создает бэкап на ftp сервере\n
        bkp_folder- папка для бэкапа default = !backup\n
        folder- папка из которой берутся файлы для бэкапа с сервера'''
        self.msg_gui.add_log('Backup files:')
        li = self.ftp.nlst()
        li_backup = self.get_LoadList(f'/{folder}/Lists')
        if folder in li:
            for i in li_backup:
                self.msg_gui.add_log(i)
                self.msg_gui.window.update()
                self.download_file(f'/{folder}/Lists', i, i)
        dir_name = date.today()
        if str(dir_name) not in self.get_LoadList(f'/{bkp_folder}'):
            self.ftp.mkd(f'/{bkp_folder}/{str(dir_name)}')

        li_upload = []
        with os.scandir(f'{self.outDir}') as files:
            for file in files:
                if file.is_file():
                    li_upload.append(file.name)
        for i in li_upload:
            self.upload_file(f'/{bkp_folder}/{str(dir_name)}/', i)
            os.remove(f'{pathlib.Path(self.outDir, i)}')

    def upload_lists(self, dir: str, fNames: List[str], exception: List[str] = []):
        '''Основная функция загрузки списка на ftp'''
        try:
            if not fNames:
                self.msg_gui.add_log('No files to update')
                return 0
            self.set_CurrentDir(dir)
            li = self.ftp.nlst()

            for i in exception:
                if i in li:
                    li.remove(i)

            bar_iter = 100 / len(li)
            self.msg_gui.bar['value'] = 0

            for i in li:
                li2 = self.get_LoadList(f'/{i}')
                self.msg_gui.bar['value'] = self.msg_gui.bar['value'] + bar_iter
                self.msg_gui.window.update()
                for j in li2:
                    if j == 'Lists':
                        self.msg_gui.add_log(f'Update files in folder {i}')
                        self.msg_gui.window.update()
                        li3 = self.get_LoadList(f'/{i}/{j}')
                        li4 = []
                        for sha in li3: # список с добавлением к имени файла расширения.sha256
                            li4.append(sha)
                            li4.append(f'{sha}.sha256')
                        for file in fNames:
                            if file in li4:
                                self.upload_file(f'/{i}/Lists/', file, self.uploadDir)
        except ftplib.all_errors as e:
            self.msg_gui.add_log(f'Error: {e}')
            self.msg_gui.window.update()

    def upload_file(self, dir: str, fName: str, local_dir: str = outDir):
        self.set_CurrentDir(dir)
        with open(f'{pathlib.Path(local_dir, fName)}', 'rb') as file:
            self.ftp.storbinary(f'STOR {fName}', file)
            file.close()

    def download_file(self, dir: str, fNameOut: str, fNameIn: str):
        '''Скачивает файл с сервера\n
        dir- директория на ftp\n
        fNameOut - имя сохраненного файла\n
        fNameIn - имя скачиваемого файла;'''
        self.set_CurrentDir(dir)
        with open(f'{pathlib.Path(self.outDir, fNameOut)}', 'wb') as file:
            self.ftp.retrbinary(f'RETR {fNameIn}', file.write)
            file.close()

    def ftp_scan_price_type(self):
        '''Сканирует структуру ftp на наличие файла .\/*\/Lists\/price.xml\n
         определяет язык (ru, en) тегов в файле. Итоговый список сохраняется в CSV'''
        dictCsv = {}
        try:
            li = self.ftp.nlst()
            bar_iter = 100 / len(li)
            self.msg_gui.bar['value'] = 0
            for i in li:
                li2 = self.get_LoadList(f'/{i}')
                self.msg_gui.bar['value'] = self.msg_gui.bar['value'] + bar_iter
                self.msg_gui.window.update()
                for j in li2:
                    if j == 'Lists':
                        li3 = self.get_LoadList(f'/{i}/{j}')
                        if 'price.xml' in li3:
                            self.msg_gui.add_log(f'Ftp Path:/{i}/{j}/-Temp file name:{i}_price.xml-Analise file:price.xml')
                            self.msg_gui.window.update()
                            self.download_file(f'/{i}/Lists/', f'{i}_price.xml', 'price.xml')
                            tree = ET.parse(f'{pathlib.Path(self.outDir, i)}_price.xml')
                            root = tree.getroot()
                            if root.tag == 'root':
                                dictCsv.update({f'{i}': 'english tag'})
                            else:
                            #elif root.tag == 'Корневой Выгрузка':
                                dictCsv.update({f'{i}': 'russian tag'})

                            os.remove(f'{pathlib.Path(self.outDir, i)}_price.xml')

        except ftplib.all_errors as e:
            self.msg_gui.add_log(f'Error: {e}')
            self.msg_gui.window.update()

        with open('priceInfo.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=':', quotechar=';', quoting=csv.QUOTE_MINIMAL)
            for key in dictCsv:
                csvwriter.writerow([key, dictCsv[key]])
            csvfile.close()

    def hash_calc(self, path: str, save: bool = True):
        '''Расчитывает хэш файла\n
        path - полный путь к файлу\n
        save - сохранить в файл path .sha256\n
        return str hash'''
        with open(path, 'rb') as file:
            hsh = hashlib.sha256()
            while True:
                data = file.read(2048)
                if not data:
                    break
                hsh.update(data)
            file.close()
            res = hsh.hexdigest()
        if save:
            with open(f'{path}.sha256', 'w') as file:
                file.write(res)
                file.close()
            return res
        else:
            return res

    def check_hash(self, folder: str = '!Template Folder'):
        '''Проверяет хэши файлов с ftp и файлов на загрузку. Составляет список измененных. Возвращает список.
        Скачиваем с фтп хэши, '''
        self.set_CurrentDir('/')
        if folder in self.ftp.nlst():
            upload_list = {}
            ftp_list = {}
            res = []

            for ftp_file in self.get_LoadList(f'/{folder}/Lists'):
                if '.sha256' in ftp_file:
                    self.download_file(f'/{folder}/Lists', ftp_file, ftp_file)
                    with open(f'{pathlib.Path(self.outDir, ftp_file)}', 'r') as file:
                        ftp_list.update({ftp_file[:ftp_file.find('.sha256')]: file.read()})
                        file.close()

            li_upload = os.listdir(self.uploadDir)
            for local_file in li_upload:
                if '.sha256' not in local_file:
                    hash_res = self.hash_calc(f'{pathlib.Path(self.uploadDir, local_file)}')
                    upload_list.update({local_file: hash_res})

            for key_local in upload_list:
                if key_local in ftp_list:
                    if upload_list[key_local] != ftp_list[key_local]:
                        res.append(key_local)
                        res.append(f'{key_local}.sha256')

            return res
