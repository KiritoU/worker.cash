import json

from selenium import webdriver
import undetected_chromedriver.v2 as uc

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.common.keys import Keys

from helper import helper
from notification import Noti
from xpaths import xpaths
from settings import CONFIG


class OpenTrade:
    def __init__(self, driver, symbol, window_handles_for):
        self.driver = driver
        self.symbol = symbol
        self.window_handles_for = window_handles_for

    def send_margin(self, xpath: str):
        input = helper.wait_and_find_element(self.driver, xpath)
        ctrlKey = Keys.COMMAND if CONFIG.OS == "Mac" else Keys.CONTROL
        input.send_keys(ctrlKey + "a")
        input.send_keys(Keys.DELETE)
        input.send_keys(CONFIG.MARGIN)

    def choose_cross(self, isIsolated):
        sleep(1.5)
        helper.wait_and_find_element(
            self.driver, xpaths.OPEN_TRADES_COPY_TRADING_ISOLATED
        ).click()

        self.send_margin(xpaths.OPEN_TRADES_COPY_TRADING_MARGIN_INPUT)
        helper.wait_and_find_element(
            self.driver, xpaths.OPEN_TRADES_MARGIN_MODE_CONFIRM_BTN
        ).click()

    def send_TP_SL_value(self, kind: str = "TP"):
        helper.get_element(self.driver, xpaths.OPEN_TRADES_INPUT_KIND[kind]).send_keys(
            CONFIG.TP_SL_VALUE[kind]
        )

    def oder_market(self, openSL):
        helper.get_element(self.driver, xpaths.OPEN_TRADES_SWITCH_MARKET).click()
        helper.get_element(
            self.driver, xpaths.OPEN_TRADES_MARKET_ORDER_BY_QTY_INPUT
        ).send_keys(CONFIG.PRICE[self.symbol])

        if (CONFIG.TP_SL_VALUE["TP"] != 0 or CONFIG.TP_SL_VALUE["SL"]) != 0:

            openTradeSideCheckBox = helper.get_element(
                self.driver, xpaths.OPEN_TRADES_CHECK_BOX[openSL]
            )

            openTradeSideCheckBox.click()

            helper.wait_and_find_element(
                self.driver, xpaths.OPEN_TRADES_TP_MODE
            ).click()
            helper.wait_and_find_element(
                self.driver, xpaths.OPEN_TRADES_TP_SL_PICK_MODE[CONFIG.TPSL_MODE]
            ).click()
            self.send_TP_SL_value("TP")

            helper.wait_and_find_element(
                self.driver, xpaths.OPEN_TRADES_SL_MODE
            ).click()
            helper.wait_and_find_element(
                self.driver, xpaths.OPEN_TRADES_TP_SL_PICK_MODE[CONFIG.TPSL_MODE]
            ).click()
            self.send_TP_SL_value("SL")

        if openSL == "S":
            helper.get_element(self.driver, xpaths.OPEN_TRADES_OPEN_SHORT_BTN).click()
        else:
            helper.get_element(self.driver, xpaths.OPEN_TRADES_OPEN_LONG_BTN).click()

        helper.wait_and_find_element(self.driver, xpaths.OPEN_TRADES_CONFIRM).click()

        # print("Sleeping")
        # sleep(1000)
        # helper.get_element(self.driver, xpaths.OPEN_TRADES_TRANSFER).click()

    def get_new_order_no(self):
        order_no = helper.wait_and_find_element(
            self.driver, xpaths.COPY_TRADES_ORDER_NO.format(1)
        ).text

        return order_no

    def run(self, isIsolated, openSL):
        # self.driver.get(CONFIG.OPEN_TRADE_URL + self.symbol)
        self.driver.switch_to.window(
            self.driver.window_handles[self.window_handles_for[self.symbol]]
        )

        helper.wait_and_find_element(
            self.driver, xpaths.OPEN_TRADES_COPY_TRADING
        ).click()

        self.choose_cross(isIsolated)
        self.oder_market(openSL)

        sleep(3)

        order_no = self.get_new_order_no()
        Noti(
            f"Following **{self.symbol}** with side `{openSL}`. Order number: {order_no}."
        ).send()

        return order_no
