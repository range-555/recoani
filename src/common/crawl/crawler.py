import chromedriver_binary
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class Crawler:
    def __init__(self):
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--start-maximized")
        options.add_argument('--headless')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("disable-infobars")
        self.driver = webdriver.Chrome(options=options)

    def get(self, url):
        time.sleep(1)
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located)
        except TimeoutException as te:
            raise te

    def click(self, target):
        time.sleep(1)
        target.click()

    # ページを下までスクロール
    def scroll_to_bottom(self):
        html_tmp_1 = self.driver.page_source
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            html_tmp_2 = self.driver.page_source
            if html_tmp_1 != html_tmp_2:
                html_tmp_1 = html_tmp_2
            else:
                return self.driver

    # driver終了
    def __del__(self):
        try:
            self.driver.close()
            self.driver.quit()
            print("driver Delete!!")
        except Exception as e:
            print(e)
            raise
