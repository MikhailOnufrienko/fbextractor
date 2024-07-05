from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWD


class WebDriverAbstractFactory(ABC):
    """Абстрактная фабрика для создания вебдрайвера."""
    @abstractmethod
    def create_driver(self):
        pass


class ChromeWebDriverFactory(WebDriverAbstractFactory):
    def create_driver(self) -> ChromeWD:
        chrome_options = Options()
        chrome_options.add_argument('--disable-notifications')
        return webdriver.Chrome(options=chrome_options)
