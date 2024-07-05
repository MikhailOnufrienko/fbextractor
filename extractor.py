"""Достает из Facebook ссылки на страницы участников сообщества.
При запуске скрипта из командной строки требует передачи трех аргументов (через пробел):
- ссылка на страницу со списком участников сообщества
(например, https://www.facebook.com/groups/426674414052346/members);
- email пользователя;
- пароль пользователя.
"""

import sys
import time
from typing import Optional

import openpyxl
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from webdriverfactory import WebDriverAbstractFactory, ChromeWebDriverFactory


class Extractor:
    def __init__(self, driver_factory: WebDriverAbstractFactory):
        self.driver_factory = driver_factory

    def main(self, args: list[str]) -> None:
        with self.driver_factory.create_driver() as driver:
            driver.get(args[0])
            try:
                email_input, password_input = Extractor._get_input_fields(driver)
                if not email_input or not password_input:
                    return
                email_input.send_keys(args[1])
                password_input.send_keys(args[2])
                password_input.send_keys(Keys.RETURN)
                time.sleep(5) # Ждем загрузку страницы
                links = Extractor._scroll_and_parse(driver)
                if not links:
                    return
                Extractor._save_to_excel(links)
            except Exception as e:
                print(f'Произошла ошибка: {e}')
                return

    @staticmethod
    def _get_input_fields(driver, timeout=10) -> tuple[Optional[WebElement]]:
        try:
            email_input = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.ID, 'email'))
            )
            password_input = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.ID, 'pass'))
            )
            return email_input, password_input
        except TimeoutException as e:
            print(f'Ошибка таймаут при загрузке полей для входа: {e}')
            return None, None
        except Exception as e:
            print(f'Произошла непредвиденная ошибка при обработке полей для входа: {e}')
            return None, None

    @staticmethod
    def _scroll_and_parse(driver) -> list[Optional[WebElement]]:
        try:
            # Прокручиваем страницу вниз для загрузки участников
            last_height = driver.execute_script("return document.body.scrollHeight")
            max_iterations = 10  # Ограничил количество итераций на случай, если в группе много участников
            for _ in range(max_iterations):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Ждем загрузку новой порции данных
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            return driver.find_elements(By.CLASS_NAME, 'xt0psk2')
        except WebDriverException as e:
            print(f'Произошла ошибка при парсинге страницы: {e}')
            return []
        except Exception as e:
            print(f'Произошла непредвиденная ошибка при парсинге страницы: {e}')
            return []

    @staticmethod
    def _save_to_excel(links: list[WebElement], filename='links.xlsx'):
        wb = openpyxl.Workbook()
        wb_active = wb.active
        wb_active.title = 'FB group members links'
        wb_active.append(['Links:'])
        for link in links:
            href = link.get_attribute('href')
            if href and '/user/' in href:
                wb_active.append([href])
        wb.save(filename)
        print(f"Ссылки сохранены в файл {filename}.")


if __name__ == '__main__':
    webdriver_factory = ChromeWebDriverFactory()
    extractor = Extractor(webdriver_factory)
    extractor.main(sys.argv[1:])
