from products_to_excel import ProductsToExcel
from update_foreign_currency import UpdateForeignCurrency
import threading
import time


SETTINGS = {
            'host': 'localhost',
            'database': 'mydb',
            'user': 'root',
            'password': 'password',
}


def thread_function():
    while True:
        ufc.update()
        time.sleep(3600)


if __name__ == '__main__':
    ufc = UpdateForeignCurrency(**SETTINGS)
    pte = ProductsToExcel(**SETTINGS)
    update_curr_thread = threading.Thread(target=thread_function)
    update_curr_thread.daemon = True
    update_curr_thread.start()
    while True:
        print('Kliknij 1, aby wyeskportować dane produktów do Excela\n'
              'Kliknij 2, aby zaktualizować cenę produktów\n'
              'Kliknij 3, aby wyjść z programu')
        inp = input()
        if '1' == inp:
            pte.to_excel()
        if '2' == inp:
            ufc.update()
        if '3' == inp:
            exit()


