import requests
import mysql.connector
from mysql.connector import Error
import pandas as pd
import datetime as dt


USD_NBP = 'https://api.nbp.pl/api/exchangerates/rates/a/USD/today/'
EUR_NBP = 'https://api.nbp.pl/api/exchangerates/rates/a/EUR/today/'
HEADERS = {'Accept': 'application/json'}
QUERY = ("UPDATE mydb.product SET UnitPriceUSD = %s, UnitPriceEuro = %s WHERE ProductID = %s")


class UpdateForeignCurrency:

    def __init__(self, host: str, database: str, user: str, password: str):
        self.settings = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
        }

    def update(self):
        '''
        wysyłamy requesta i patrzymy na odpowiedź serwera. jesli dostaniemy cos innego niż 200 to kończmymy
        wykonywanie programu i zapisujemy informacje do pliku log

        json()['rates'][0]['mid'] to poprostu wyciagniecie wartosci waluty

        nastepnie łaczymy się do bazy danych, pobieramy dane do 'recordu', potem tworzymy instancje DataFrame i
        dzieki temu mozemy uzywac dzielenia i zaokraglania na calych wierszach

        iterujemy przez wyszskite wiersze i aktualizujemy dane, nastepnie piszemy do pliku logs.log o udanej opreacji
        jesli polaczenie do bazy jest nieudane informujemy o tym w logu
        '''
        try:
            usd_res = requests.get(USD_NBP, headers=HEADERS)
            eur_res = requests.get(EUR_NBP, headers=HEADERS)

            if usd_res.status_code != 200 or eur_res.status_code != 200:
                message_usd = f'USD response status: {usd_res.status_code}. USD NBP Endpoint: {USD_NBP}'
                message_eur = f'EUR response status: {eur_res.status_code}. EUR NBP Endpoint: {EUR_NBP}'
                with open('logs.log', 'a+') as file:
                    file.write(f'{dt.datetime.now()}, NBP API connection error. {message_usd}, {message_eur}\n')
                return

            usd_mid = usd_res.json()['rates'][0]['mid']
            eur_mid = eur_res.json()['rates'][0]['mid']

            connection = mysql.connector.connect(**self.settings)
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT ProductID, UnitPrice FROM product")
                records = cursor.fetchall()
                df_prices = pd.DataFrame(records, columns=['id', 'UnitPrice'])
                df_prices['UnitPrice'] = pd.to_numeric(df_prices.UnitPrice)
                df_prices['UnitPriceUSD'] = df_prices['UnitPrice'] / usd_mid
                df_prices['UnitPriceUSD'] = df_prices['UnitPriceUSD'].round(2)
                df_prices['UnitPriceEuro'] = df_prices['UnitPrice'] / eur_mid
                df_prices['UnitPriceEuro'] = df_prices['UnitPriceEuro'].round(2)
                for index, row in df_prices.iterrows():
                    cursor.execute(QUERY, (row['UnitPriceUSD'], row['UnitPriceEuro'], row['id']))
                    connection.commit()
                cursor.close()
                connection.close()
                with open('logs.log', 'a+') as file:
                    file.write(f'{dt.datetime.now()}, Currencies updated successfully\n')

        except Error as e:
            with open('logs.log', 'a+') as file:
                file.write(f'{dt.datetime.now()}, Updating currencies error: {e.msg}, SQL State: {e.sqlstate}\n')



