import logging
import undetected_chromedriver.v2 as uc

from multiprocessing import freeze_support
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

from helper import helper
from notification import Noti
from open_trade import OpenTrade
from settings import CONFIG
from xpaths import xpaths

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)


class ByBit:
    def __init__(self):
        self.window_handles_for = {}
        self.options = uc.ChromeOptions()
        self.options.add_argument("--start-maximized")

        # setting profile
        # self.options.user_data_dir = f"{CONFIG.CHROME_PROFILE_PATH}"
        self.options.add_argument(f"--user-data-dir={CONFIG.USER_DATA_DIR}")
        self.options.add_argument(f"--profile-directory={CONFIG.PROFILE_DIRECTORY}")

        self.options.add_argument(
            "--no-first-run --no-service-autorun --password-store=basic"
        )
        self.driver = uc.Chrome(
            options=self.options, executable_path=CONFIG.CHROME_DRIVER
        )

        keys = list(CONFIG.PRICE.keys())
        for i in range(len(keys)):
            self.driver.execute_script("window.open('');")
            # print(len(self.driver.window_handles))
            # self.driver.switch_to.window(self.driver.window_handles[len(self.driver.window_handles) - 1])
            # sleep(2)
            self.window_handles_for[keys[i]] = len(self.driver.window_handles) - 1
            self.driver.switch_to.window(
                self.driver.window_handles[self.window_handles_for[keys[i]]]
            )
            self.driver.get(CONFIG.OPEN_TRADE_URL + keys[i])
            # sleep(10000)
            # helper.wait_and_find_element(
            #     self.driver, xpaths.OPEN_TRADES_COPY_TRADING
            # ).click()

            sleep(1)
            try:
                oc__trade_model_box = self.driver.find_element(
                    By.CLASS_NAME, "oc__trade-model-box"
                )
                by_switch__item = oc__trade_model_box.find_elements(
                    By.CLASS_NAME, "by-switch__item"
                )
                copyTradingButton = by_switch__item[-1]
                copyTradingButton.click()

            except Exception as e:
                print("Copy trading button not found")

            # helper.wait_and_find_element(
            #     self.driver, xpaths.OPEN_TRADES_COPY_TRADING
            # ).click()

        self.driver.switch_to.window(self.driver.window_handles[0])

    def login(self):
        self.driver.get(CONFIG.LOGIN_URL)
        loggedIn = helper.wait_and_find_element(self.driver, xpaths.LOGIN_ICON)
        logging.info("Logged in")

        # sleep(10000)

    def make_trading(self):
        currentTrades = helper.get_open_trades()
        if not currentTrades:
            return

        logging.info("Following trader...")

        for key, copyTrade in currentTrades.items():
            symbol = copyTrade["symbol"]
            helper.set_is_traded_for(key=key)
            if symbol not in CONFIG.PRICE.keys():
                continue

            if helper.isOkToFollow(copyTrade):

                try:
                    if "openSL" in copyTrade.keys():
                        openSL = copyTrade["openSL"]
                    else:
                        side = copyTrade["side"]
                        openSL = "S" if side == "Sell" else "L"
                    symbol = copyTrade["symbol"]

                    order_no = OpenTrade(
                        self.driver, symbol, self.window_handles_for
                    ).run(CONFIG.IS_ISOLATED, openSL)

                    helper.set_order_no_for(key=key, order_no=order_no)

                    sleep(1.5)
                    # logging.info("sleeping")
                    # sleep(1000)

                except Exception as e:
                    logging.error(f"Failed to follow {openSL} {symbol}")
                    print(e)

                    # logging.info("sleeping")
                    # sleep(1000)

    def test_new_tab(self):
        self.driver.get("https://1.1.1.1/")

        self.driver.execute_script("window.open('');")

        print(self.driver.window_handles)

        while True:
            # ctrlKey = Keys.COMMAND if CONFIG.OS == "Mac" else Keys.CONTROL

            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get("https://google.com")
            sleep(5)

            self.driver.switch_to.window(self.driver.window_handles[0])
            sleep(5)


def main():
    byBit = ByBit()
    # helper.close_orders(
    #     driver=byBit.driver, window_handles_for=byBit.window_handles_for
    # )
    # byBit.make_trading()

    # helper.get_all_order(byBit.driver)
    # helper.close_all_orders(byBit.driver, byBit.window_handles_for)
    # sleep(100000)

    try:

        helper.get_all_copy_trades(byBit.driver)

        helper.get_past_trades(byBit.driver, is_closed=1)

        byBit.make_trading()
    except Exception as e:
        helper.error_log(f"Error in main def\n{e}")

    while True:
        try:
            helper.get_all_copy_trades(byBit.driver)
            byBit.make_trading()

            helper.get_past_trades(byBit.driver)

            helper.close_orders(
                driver=byBit.driver, window_handles_for=byBit.window_handles_for
            )

            sleep(CONFIG.FOLLOW_INTERVAL)
        except Exception as e:
            helper.error_log(
                f"Error while crawling new copy trades/past trades and follow\n{e}",
                filename="crawling_new.log",
            )


if __name__ == "__main__":

    freeze_support()
    main()
