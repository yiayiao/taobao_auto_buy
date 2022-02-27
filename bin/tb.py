from lib.base import *


class Taobao(AutoBuyBase):

    def __init__(self, target_url, buy_time):
        super().__init__(target_url, buy_time)

    def _login(self):
        self._browser.get(self._main_url)
        self._browser.find_element_by_link_text("亲，请登录").click()

        current_url = self._browser.current_url
        self._wait_redirect(current_url)

    def _goto_detail(self):
        self._browser.get(self._target_url)

    def _buy(self):
        self._logger.info("正在倒计时")
        self._timer(self._buy_time)
        self._logger.info(f"开始抢购")
        choose_element = WebDriverWait(self._browser, 60).until(self._choose_element)
        choose_element.click()
        buy_element = WebDriverWait(self._browser, 60).until(EC.element_to_be_clickable((By.CLASS_NAME, "tb-btn-buy")))
        self._click_until_redirect(buy_element, self._browser.current_url)
        self._checkout()

    @staticmethod
    def _choose_element(driver: Chrome):
        element_box = driver.find_element(By.CLASS_NAME, "J_TSaleProp")
        elements_li = element_box.find_elements(By.TAG_NAME, "li")
        while len(elements_li) == 1:
            driver.refresh()
            element_box = driver.find_element(By.CLASS_NAME, "J_TSaleProp tb-img tb-clearfix")
            elements_li = element_box.find_elements(By.TAG_NAME, "li")
        else:
            return elements_li[1]

    def _checkout(self):
        sumit_element = WebDriverWait(self._browser, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "go-btn")))
        self._click_until_redirect(sumit_element, self._browser.current_url)
        self._logger.info("抢购结束")

    def start(self):
        # self._logger.info("主程序启动")
        # self._login()
        # self._logger.info("登陆成功")
        self._goto_detail()
        self._logger.info("进入商品页面 请在抢购时间前完成填写选项")
        self._buy()
