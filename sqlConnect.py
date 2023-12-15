import pyodbc
from pyodbc import Connection, Cursor
from typing import Tuple


class SqlCache:
    cnxn: Connection = None
    cursor: Cursor = None
    db: str = None
    msg_gui = None

    def __init__(self, gui_msg, server: str, db_name: str, user: str, pwd: str):
        # ENCRYPT defaults to yes starting in ODBC Driver 18. It's good to always specify
        # ENCRYPT=yes on the client side to avoid MITM attacks.
        try:
            self.msg_gui = gui_msg
            self.db = db_name
            driver = 'ODBC Driver 18 for SQL Server'
            self.cnxn = pyodbc.connect(
                f"DRIVER={driver};SERVER={server};DATABASE={db_name};TrustServerCertificate=Yes;sslverify=0;UID={user};PWD={pwd}")
            self.cursor = self.cnxn.cursor()
            # print(f'SQL connected from {self.db}')
            self.msg_gui.add_log(f'SQL connected from {self.db}')
        except AttributeError as e:
            # print('Error connection SQL DB: ', e)
            self.msg_gui.add_log('Error connection SQL DB: ', e)

    def __del__(self):
        self.cnxn.close()
        self.msg_gui.add_log(f'SQL connection close with {self.db}')

    def select_data(self, query: str):
        li = []
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        while row:
            li.append(row)
            row = self.cursor.fetchone()
        return li

    def __select_export_test(self, li: Tuple):
        res = self.select_data(f'''select* FROM [OrdersFromCACHE].[dbo].[OrdersToExportTests]
        where OrderAid in {li}''')
        return res
