import json
import logging

from selenium import webdriver
import undetected_chromedriver.v2 as uc

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.common.keys import Keys

from helper import helper
from notification import Noti
from xpaths import xpaths
from settings import CONFIG

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)


class OpenTrade:
    def __init__(self, driver, symbol, window_handles_for):
        self.driver = driver
        self.symbol = symbol
        self.window_handles_for = window_handles_for

    def send_margin(self, xpath: str):
        logging.info("Sending margin...")

        sleep(1)
        pos_mode_change__dialog = self.driver.find_element(
            By.CLASS_NAME, "pos-mode-change__dialog"
        )
        by_input__inner = pos_mode_change__dialog.find_elements(
            By.CLASS_NAME, "by-input__inner"
        )
        by_input = by_input__inner[1]

        # input = helper.wait_and_find_element(self.driver, xpath)
        ctrlKey = Keys.COMMAND if CONFIG.OS == "Mac" else Keys.CONTROL
        by_input.send_keys(ctrlKey + "a")
        by_input.send_keys(Keys.DELETE)
        by_input.send_keys(CONFIG.MARGIN)

    def choose_cross(self, isIsolated):
        sleep(1.5)
        # helper.wait_and_find_element(
        #     self.driver, xpaths.OPEN_TRADES_COPY_TRADING_ISOLATED
        # ).click()

        oc_head_mode = self.driver.find_element(By.CLASS_NAME, "oc-head-mode")
        oc_head_mode.click()

        self.send_margin(xpaths.OPEN_TRADES_COPY_TRADING_MARGIN_INPUT)

        # helper.wait_and_find_element(
        #     self.driver, xpaths.OPEN_TRADES_MARGIN_MODE_CONFIRM_BTN
        # ).click()
        by_dialog__foot = self.driver.find_element(By.CLASS_NAME, "by-dialog__foot")
        confirmBtn = by_dialog__foot.find_elements(By.TAG_NAME, "button")
        confirmBtn[0].click()

    def send_TP_SL_value(self, oc_row, kind: str = "TP"):
        # helper.get_element(self.driver, xpaths.OPEN_TRADES_INPUT_KIND[kind]).send_keys(
        #     CONFIG.TP_SL_VALUE[kind]
        # )

        by_input__inner = oc_row.find_element(By.CLASS_NAME, "by-input__inner")
        by_input__inner.send_keys(CONFIG.TP_SL_VALUE[kind])

    def oder_market(self, openSL):
        by_card__body = self.driver.find_elements(By.CLASS_NAME, "by-card__body")
        print("by_card__body")
        trade_body = by_card__body[0]
        print("trade_body")

        # helper.get_element(self.driver, xpaths.OPEN_TRADES_SWITCH_MARKET).click()

        trade_body.find_elements(By.CLASS_NAME, "by-switch__item")[1].click()
        print("click market")

        # helper.get_element(
        #     self.driver, xpaths.OPEN_TRADES_MARKET_ORDER_BY_QTY_INPUT
        # ).send_keys(CONFIG.PRICE[self.symbol])

        trade_body.find_element(By.CLASS_NAME, "by-input__inner").send_keys(
            CONFIG.PRICE[self.symbol]
        )
        print("sent price")
        # sleep(10000)

        if (CONFIG.TP_SL_VALUE["TP"] != 0 or CONFIG.TP_SL_VALUE["SL"]) != 0:
            # openTradeSideCheckBox = helper.get_element(
            #     self.driver, xpaths.OPEN_TRADES_CHECK_BOX[openSL]
            # )

            # openTradeSideCheckBox.click()
            by_checkbox__item = trade_body.find_elements(
                By.CLASS_NAME, "by-checkbox__item"
            )
            checkbox_index = 0 if openSL == "L" else 1
            by_checkbox__item[checkbox_index].click()

            take_profit_class = helper.wait_and_find_element(
                self.driver, by_key=By.CLASS_NAME, by_value="take_profit_class"
            )

            oc__rows = take_profit_class.find_elements(By.CLASS_NAME, "oc__row")
            tpslValue = 0
            for oc_row in oc__rows:
                by_popover = oc_row.find_element(By.CLASS_NAME, "by-popover")
                by_popover.click()
                helper.wait_and_find_element(
                    self.driver, by_key=By.CLASS_NAME, by_value="by-select-option"
                )
                by_select_options = self.driver.find_elements(
                    By.CLASS_NAME, "by-select-option"
                )
                by_select_options[-1].click()

                self.send_TP_SL_value(oc_row, "SL" if tpslValue else "TP")

                tpslValue += 1

            scroll_origin = ScrollOrigin.from_element(by_checkbox__item[checkbox_index])
            ActionChains(self.driver).scroll_from_origin(
                scroll_origin, 0, 300
            ).perform()

            sleep(1)

            # helper.wait_and_find_element(
            #     self.driver, xpaths.OPEN_TRADES_TP_SL_PICK_MODE[CONFIG.TPSL_MODE]
            # ).click()
            # self.send_TP_SL_value("TP")

            # helper.wait_and_find_element(
            #     self.driver, xpaths.OPEN_TRADES_SL_MODE
            # ).click()
            # helper.wait_and_find_element(
            #     self.driver, xpaths.OPEN_TRADES_TP_SL_PICK_MODE[CONFIG.TPSL_MODE]
            # ).click()
            # self.send_TP_SL_value("SL")

        # sleep(2000)
        by_obp = self.driver.find_element(By.CLASS_NAME, "by-obp")
        btns = by_obp.find_elements(By.TAG_NAME, "button")
        if openSL == "S":
            print(btns[-1].text)
            # ActionChains(self.driver).scroll_to_element(btns[-1]).perform()
            btns[-1].click()
            # helper.get_element(self.driver, xpaths.OPEN_TRADES_OPEN_SHORT_BTN).click()
        else:
            print(btns[0].text)
            # ActionChains(self.driver).scroll_to_element(btns[0]).perform()
            btns[0].click()
            # helper.get_element(self.driver, xpaths.OPEN_TRADES_OPEN_LONG_BTN).click()

        # helper.wait_and_find_element(self.driver, xpaths.OPEN_TRADES_CONFIRM).click()

        by_modal__container = helper.wait_and_find_element(
            self.driver, By.CLASS_NAME, "by-modal__container"
        )
        by_obpcd__foot = by_modal__container.find_element(
            By.CLASS_NAME, "by-obpcd__foot"
        )
        modal_btns = by_obpcd__foot.find_elements(By.TAG_NAME, "button")
        modal_btns[0].click()

        # sleep(1000)
        # print("Sleeping")
        # sleep(1000)
        # helper.get_element(self.driver, xpaths.OPEN_TRADES_TRANSFER).click()

    def get_new_order_no(self):
        # order_no = helper.wait_and_find_element(
        #     self.driver, xpaths.COPY_TRADES_ORDER_NO.format(1)
        # ).text
        order_no = 0
        try:
            guidance_anchor_position = self.driver.find_element(
                By.ID, "guidance_anchor_position"
            )
            tbody = guidance_anchor_position.find_element(By.TAG_NAME, "tbody")
            tr = tbody.find_elements(By.TAG_NAME, "tr")
            row1 = tr[0]
            td = row1.find_elements(By.TAG_NAME, "td")
            order_no = td[-2].text
        except Exception as e:
            helper.error_log(
                f"Failed to get_new_order_no\n{e}",
                filename="open_trade.get_new_order_no.log",
            )

        return order_no

    def run(self, isIsolated, openSL):
        # self.driver.get(CONFIG.OPEN_TRADE_URL + self.symbol)
        self.driver.switch_to.window(
            self.driver.window_handles[self.window_handles_for[self.symbol]]
        )

        # helper.wait_and_find_element(
        #     self.driver, xpaths.OPEN_TRADES_COPY_TRADING
        # ).click()

        self.choose_cross(isIsolated)
        self.oder_market(openSL)

        sleep(3)

        order_no = self.get_new_order_no()

        Noti(
            f"Following **{self.symbol}** with side `{openSL}`. Order number: {order_no}."
        ).send()

        return order_no
