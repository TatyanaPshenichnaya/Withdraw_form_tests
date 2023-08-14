import pytest
#import time
from selenium import webdriver
#from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base_url = 'https://groall.noda.pro/test_qa'


@pytest.fixture(autouse=True)
def driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)  # ставим величину неявного ожидания элементов в 10 секунд
    # Переходим на страницу
    driver.get(base_url)

    # при первом открытии сайта появляется окно выбора локации, закроем его:
    location_btn = driver.find_element(By.XPATH, '//a[@class="franchiseeListLink active gkOffice"]')
    if location_btn:
        location_btn.click()

    yield driver

    driver.quit()



# создадим переменную для кнопки "Вывести"
# btn_withdraw = driver.find_element(By.XPATH, '//input[@type="button"]')


def test_form_elements(driver):
    # Тест-кейс №1. Проверим наличие элементов на странице
    assert (driver.find_element(By.XPATH, '//h1').text == "Вывод средств со счета" and
            driver.find_element(By.XPATH, '//p[contains(text(), "Баланс")]') and
            driver.find_element(By.ID, 'all') and
            driver.find_element(By.XPATH, '//p[contains(text(), "= 1 коин")]') and
            driver.find_element(By.XPATH, '//input[@type="button"]') )

            #btn_withdraw)


def test_form_currency(driver):
    # Тест-кейс №2. Проверка валюты баланса и выводимой валюты.
    assert (driver.find_element(By.XPATH, '//p[contains(text(), "токен")]') and
            driver.find_element(By.XPATH, '//form[@id="sendTokenForm"]').text == 'Вывести токенов\nВывести всё\n100 токенов = 1 коин' )

'''                                          
def test_form_alert(driver):
    # Тест-кейс №2. Проверим, какая валюта указана в окне предупреждения (алерте)
    driver.find_element(By.XPATH, '//form/input[@type="text"]').send_keys(100)
    driver.find_element(By.XPATH, '//input[@type="button"]').click()

    #активируем явное ожидание на присутствие окна алерта
    alert1 = WebDriverWait(driver, 10).until(EC.alert_is_present())
    #alert1 = driver.switch_to.alert()
    text = alert1.text
    assert "Токены списаны" in text
'''

# функция, возвращающая текст окна предупреджения,
# которое появляется после ввода количества выводимой валюты и клика на кнопку "Вывести"
def operation_fun(driver, value):
    driver.find_element(By.XPATH, '//form/input[@type="text"]').send_keys(value)
    driver.find_element(By.XPATH, '//input[@type="button"]').click()
    # активируем явное ожидание на присутствие окна алерта
    alert1 = WebDriverWait(driver, 10).until(EC.alert_is_present())
    # alert1 = driver.switch_to.alert()
    return alert1.text

def test_form_alert_new(driver):
    # Тест-кейс №2. Проверим, какая валюта указана в окне предупреждения (алерте)
    text = operation_fun(driver, 100)
    assert "Токены списаны" in text


@pytest.mark.parametrize("params", [ (100, 121900), (2000.59, 119999.41), (122000, 0) ]) # ids=[])
def test_form_positive(driver, params):
    # Тест-кейс №3. Позитивный тест формы вывода средств со счёта
    (input_, expected_output) = params
    actual_output = operation_fun(driver, input_)
    assert (' ' + str(expected_output)) in actual_output  # добавление пробела позволит проверить, что остаток не отрицательный

def test_form_positive_all(driver):
    # Тест-кейс №3. Позитивный тест - операция "вывести всё" с помощью флажка
    driver.find_element(By.ID, 'all').click()
    driver.find_element(By.XPATH, '//input[@type="button"]').click()
    alert1 = WebDriverWait(driver, 10).until(EC.alert_is_present())
    text = alert1.text
    assert "осталось 0" in text


@pytest.mark.parametrize("params", [ (0, 'Введеное кол-во коинов должно быть больше 0'),
                                     (3000000, 'Недостаточно средств'),
                                     (-600, 'Введеное кол-во коинов должно быть больше 0')
                                     ] )
def test_form_negative_part1(driver, params):
    # Тест-кейс №4. Негативный тест  формы вывода средств со счёта - появление алертов.
    (input_, expected_output) = params
    text = operation_fun(driver, input_)
    assert expected_output == text



@pytest.mark.parametrize("params", [ ('', 'Поле обязательно для заполнения'),
                                     ('203K', 'Поле должно содержать только цифры!'),
                                     ('Hh', 'Поле должно содержать только цифры!'),
                                     ('%)),', 'Поле должно содержать только цифры!')],
                         ids=['empty',  '203K', 'Hh', '%)),'] )
def test_form_negative_part2(driver, params):
    # Тест-кейс №4. Негативный тест  формы вывода средств со счёта - форма не принята, появление подсказок.
    (input_, expected_output) = params
    driver.find_element(By.XPATH, '//form/input[@type="text"]').send_keys(input_)
    driver.find_element(By.XPATH, '//input[@type="button"]').click()
    assert driver.find_element(By.ID, 'value-error').text == expected_output


def test_balance(driver):
    # Тест-кейс №5. Проверка отображение баланса после операции по выводу средств.
    driver.find_element(By.XPATH, '//form/input[@type="text"]').send_keys(22000)
    driver.find_element(By.XPATH, '//input[@type="button"]').click()
    # активируем явное ожидание на присутствие окна алерта
    alert1 = WebDriverWait(driver, 10).until(EC.alert_is_present())
    alert1.accept() # закрытие алерта
    # равним текущий показатель баланса с ожидаемым:
    assert driver.find_element(By.XPATH, '//div[@class="baseContent"]/p').text == 'Баланс: 100000 токенов'
