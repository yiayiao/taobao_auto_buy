import logging
import platform
import os
from datetime import datetime
from lib.exceptions import SystemUnsupported, InvalidInputUrl, InvalidInputTime, SubClassInvaild
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchAttributeException
from selenium.webdriver import Chrome, ChromeOptions
from urllib.parse import urlparse
from functools import wraps
import pickle
from selenium.webdriver.common.action_chains import ActionChains

class AutoBuyBase(object):

    __slots__ = ["_main_url", "_target_url", "_logger", "_browser", "_buy_time"]

    def __init__(self, target_url, buy_time):

        self._main_url = "https://www.taobao.com/"
        self._target_url = target_url
        self._buy_time = buy_time

        # validation
        self._validate_input()
        # end

        self._logger = self._get_logger()
        self._browser = None
        # self._browser = self._config_login_browser()

    @staticmethod
    def delay(min, max):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return result
            return wrapper
        return decorator

    def __repr__(self):

        class_name = self.__class__.__name__
        return f"{class_name}"

    def _is_url(self, url):

        try:
            result = urlparse(url)
            return True
        except ValueError:
            return False

    def _validate_url(self, url):

        accepted_url_keyword = ["taobao", "tmall"]

        if self._is_url(url) and any([x in url for x in accepted_url_keyword]):
            return 0
        else:
            raise InvalidInputUrl()

    def _validate_time(self, time):

        try:
            datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        except:
            raise InvalidInputTime()

    def _validate_input(self):

        self._validate_url(self._main_url)
        self._validate_url(self._target_url)
        self._validate_time(self._buy_time)

    def _get_logger(self):

        logger = logging.getLogger(name = self.__class__.__name__)
        logger.setLevel(logging.INFO)
        return logger

    def _get_driver_dir(self):

        os_type = platform.system()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        driver_dir = os.path.join(base_dir, "../drivers")

        if os_type == "Linux":
            return os.path.join(driver_dir, "chromedriver_linux")
        elif os_type == "Darwin":
            return os.path.join((driver_dir, "chromedriver_mac"))
        elif os_type == "Windows":
            return os.path.join(driver_dir, "chromedriver_win.exe")
        return None

    def _config_browser(self):

        opts = ChromeOptions()
        opts.add_experimental_option("detach", True)

        # disable image render
        prefs = {"profile.managed_default_content_settings.images": 2}
        opts.add_experimental_option("prefs", prefs)
        # end

        # max window
        opts.add_argument("--start-maximized")
        # end

        # avoid detection
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        # opts.add_argument("--disable-blink-features")
        # opts.add_argument("--disable-blink-features=AutomationControlled")
        # opts.add_argument("--headless")
        # end

        driver_dir = self._get_driver_dir()
        self._logger.info(f"using {driver_dir}")
        return Chrome(driver_dir, chrome_options=opts)

    def _config_login_browser(self):

        opts = ChromeOptions()
        opts.add_experimental_option("detach", True)
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        opts.add_argument("--start-maximized")
        return Chrome(self._get_driver_dir(), chrome_options = opts)

    def _dump_login_cookies(self, cookies):

        pickle.dump(cookies, open("cookies.pkl", "wb"))

    def _load_login_cookies(self):

        self._browser = self._config_browser()
        self._browser.get("https://www.taobao.com")
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            if 'expiry' in cookie:
                del cookie['expiry']
            self._browser.add_cookie(cookie)

    def _wait_redirect(self, current_url):

        wait = WebDriverWait(self._browser, 60)
        try:
            wait.until_not(lambda _browser: _browser.current_url == current_url)
        except TimeoutException as e:
            raise e

    def _wait_until_login(self, browser):

        wait = WebDriverWait(browser, 60)
        try:
            wait.until_not(lambda _browser: _browser.current_url == "https://www.taobao.com")
        except TimeoutException as e:
            raise e

    def _click_until_redirect(self, element, current_url):

        while current_url == self._browser.current_url:
            try:
                element.click()
            except:
                continue

    def _add_random_wait_time(self):
        pass

    def _add_human_action(self):
        pass

    def _wait_for_load_page(self, timeout):
        self._browser.implicitly_wait(timeout)

    def _click_until_new_tab(self, element):

        while len(self._browser.window_handles) == 1:
            try:
                element.click()
            except:
                continue

        self._browser.switch_to.window(self._browser.window_handles[1])

    def _login(self):

        browser = self._config_login_browser()
        browser.get("https://login.taobao.com")
        # browser.implicitly_wait(20)
        # current_url = browser.current_url
        # print(current_url)
        self._wait_until_login(browser)

        # self._wait_redirect(current_url, browser)
        # browser.find_element_by_link_text("亲，请登录").click()
        # login_element = WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.LINK_TEXT, "亲，请登录")))

        cookies = browser.get_cookies()
        browser.quit()

        # start new session
        self._logger.info("Disable Image Render")
        self._dump_login_cookies(cookies)
        self._load_login_cookies()
        # end
        return cookies

    def start(self):

        raise SubClassInvaild()

    def _timer(self, buy_time):

        buy_time_raw = datetime.strptime(buy_time, "%Y-%m-%d %H:%M:%S")
        offsetSecond = 5

        while (buy_time_raw - datetime.now()).total_seconds() > offsetSecond:
            self._timer_printer(buy_time_raw)

    def _timer_printer(self, buy_time):

        print(f"{buy_time - datetime.now()}", end = "\r")
