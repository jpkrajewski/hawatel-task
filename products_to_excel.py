from mysql.connector import Error
import mysql.connector
import datetime as dt
import pandas as pd
import openpyxl

COLUMNS = [
            'ProductID',
            'DepartmentID',
            'Category',
            'IDSKU',
            'ProductName',
            'Quantity',
            'UnitPrice',
            'Ranking',
            'ProductDesc',
            'UnitsInStock',
            'UnitsInOrder',
            'Picture',
            'UnitPriceUSD',
            'UnitPriceEuro'
        ]


class ProductsToExcel:
    def __init__(self, host: str, database: str, user: str, password: str):
        self.settings = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
        }

    def to_excel(self) -> bool:
        try:
            connection = mysql.connector.connect(**self.settings)
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM product")
                records = cursor.fetchall()
                df = pd.DataFrame(records, columns=COLUMNS)
                df.drop('Picture', axis=1, inplace=True)
                df.to_excel(excel_writer=f'products_{dt.datetime.today().strftime("%Y-%m-%d")}.xlsx',
                            sheet_name='Products',
                            columns=df.columns)
                cursor.close()
                connection.close()
                with open('logs.log', 'a+') as file:
                    file.write(f'{dt.datetime.now()}, Excel exported successfully\n')

        except Error as e:
            with open('logs.log', 'a+') as file:
                file.write(f'{dt.datetime.now()}, Excel export error: {e.msg}, SQL State: {e.sqlstate}\n')

