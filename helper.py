import json
import logging
import requests
import time

from datetime import datetime
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.keys import Keys

from _db import database
from notification import Noti
from xpaths import xpaths
from settings import CONFIG


class Helper:
    def error_log(self, msg, filename: str = "error.log"):
        Path("log").mkdir(parents=True, exist_ok=True)
        fn = f"log/{filename}" if CONFIG.OS == "Mac" else f"log\\{filename}"
        if not Path(fn).is_file():
            with open(fn, "w") as f:
                f.write("")

        with open(fn, "a") as f:
            print(f"{msg}\n{'-' * 80}", file=f)

    def get_element(self, driver, XPATH):

        return driver.find_element(
            by=By.XPATH,
            value=XPATH,
        )

    def wait_and_find_element(self, driver, XPATH: str):
        WebDriverWait(driver, CONFIG.DRIVER_WAIT_TIME).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    XPATH,
                )
            )
        )

        return driver.find_element(
            by=By.XPATH,
            value=XPATH,
        )

    def format_key(self, key: str) -> str:
        return key.replace(".", "").replace(",", "").replace(" ", "")

    def close_all_my_tradings(self, driver) -> dict:
        try:
            self.get_element(driver, xpaths.CLOSE_ALL_POSITION).click()
            self.wait_and_find_element(
                driver, xpaths.CLOSE_ALL_POSITION_CONFIRM
            ).click()

        except Exception as e:
            pass

    def get_copy_trades_via_api(self):
        res = {}

        url = CONFIG.COPY_TRADE_API.format(int(time.time()), CONFIG.TRADER_ID)
        response = requests.get(url)

        copyTrades = json.loads(response.text)["result"]["data"]

        for copyTrade in copyTrades:
            key = (
                copyTrade["symbol"]
                + self.format_key(copyTrade["entryPrice"])
                + copyTrade["createdAtE3"]
            )
            res[key] = copyTrade

        return res

    def get_count_copy_trades(self, copyTradesText: str) -> int:
        try:
            count = copyTradesText.split("(")[-1][:-1]
            return int(count)
        except Exception as e:
            self.error_log(
                f"Failed to get count of copy trades\n{e}",
                filename="count_copy_trades.log",
            )

    def get_past_trades_by_row_id(self, driver, rowId, is_closed):
        openSLAndMargin = self.get_element(
            driver, xpaths.PAST_TRADES_OPENSL.format(rowId + 1)
        )

        symbol = self.get_element(driver, xpaths.PAST_TRADES_SYMBOL.format(rowId + 1))

        entryPrice = self.get_element(
            driver, xpaths.PAST_TRADES_ENTRY_PRICE.format(rowId + 1)
        )
        closePrice = self.get_element(
            driver, xpaths.PAST_TRADES_CLOSING_PRICE.format(rowId + 1)
        )
        openTime = self.get_element(
            driver, xpaths.PAST_TRADES_OPEN_TIME.format(rowId + 1)
        )
        closeTime = self.get_element(
            driver, xpaths.PAST_TRADES_CLOSE_TIME.format(rowId + 1)
        )
        copyTradeROI = self.get_element(
            driver, xpaths.PAST_TRADES_ROI.format(rowId + 1)
        )

        res = {
            "openSL": "L"
            if openSLAndMargin.text.split(" ")[0].lower() == "long"
            else "S",
            "margin": openSLAndMargin.text.split(" ")[-1],
            "symbol": symbol.text,
            "entryPrice": entryPrice.text,
            "closePrice": closePrice.text,
            "openTime": openTime.text,
            "closeTime": closeTime.text,
            "copyTradeROI": copyTradeROI.text,
        }

        key = (
            res["openSL"]
            + res["symbol"]
            + res["margin"]
            + res["entryPrice"]
            + res["openTime"]
        )
        key = self.format_key(key)

        data = (key, json.dumps(res), is_closed)
        condition = f"key='{key}'"
        database.select_or_insert(table="past_trade", condition=condition, data=data)

    def get_past_trades(self, driver, is_closed: int = 0):
        logging.info("Getting past trades...")
        for i in range(1, 9):
            try:
                self.get_past_trades_by_row_id(driver, i, is_closed)

            except Exception as e:
                break

    def get_all_copy_trades(self, driver) -> dict:
        logging.info("Getting copy trades...")
        traderUrl = CONFIG.COPY_TRADE_URL + CONFIG.TRADER_ID

        driver.switch_to.window(driver.window_handles[0])
        driver.get(traderUrl)

        time.sleep(CONFIG.COPY_TRADE_WAIT_TIME_BEFORE_CRAWL)

        # print("wait_and_find_element(driver, xpaths.COPY_TRADES)")
        # copyTrades = self.wait_and_find_element(driver, xpaths.COPY_TRADES)

        ant_tabs_nav_list = driver.find_element(By.CLASS_NAME, "ant-tabs-nav-list")
        tabs = ant_tabs_nav_list.find_elements(By.TAG_NAME, "div")
        copyTrades = tabs[2]
        # print("DONE: wait_and_find_element(driver, xpaths.COPY_TRADES)")
        copyTrades.click()

        time.sleep(CONFIG.COPY_TRADE_WAIT_TIME_BEFORE_CRAWL)

        self.get_page_copy_trades(driver)

        for page in range(2, 1000):
            try:
                # ant-pagination-item ant-pagination-item-2
                # #rc-tabs-0-panel-orders > div > div:nth-child(1) > div.order-list-table-box > div > div > div > div > ul > li.ant-pagination-item.ant-pagination-item-3 > a
                # #rc-tabs-0-panel-orders > div > div:nth-child(1) > div.order-list-table-box > div > div > div > div > ul > li.ant-pagination-item.ant-pagination-item-2 > a
                # #rc-tabs-0-panel-orders > div > div:nth-child(1) > div.order-list-table-box > div > div > div > div > ul > li.ant-pagination-item.ant-pagination-item-1.ant-pagination-item-active > a
                # page_element = self.get_element(
                #     driver, xpaths.COPY_TRADES_PAGE_I_BTN.format(page + 1)
                # ).click()
                page_element = driver.find_element(
                    By.CSS_SELECTOR,
                    f"#rc-tabs-0-panel-orders > div > div:nth-child(1) > div.order-list-table-box > div > div > div > div > ul > li.ant-pagination-item.ant-pagination-item-{page} > a",
                )
                # page_element = self.wait_and_find_element(
                #     driver, xpaths.COPY_TRADES_PAGE_I_BTN.format(page + 1)
                # )

                # action = ActionChains(driver)
                # action.scroll_to_element(page_element)
                # action.perform()

                page_element.click()

                self.get_page_copy_trades(driver)
            except Exception as e:
                # logging.error(
                #     f"#rc-tabs-0-panel-orders > div > div:nth-child(1) > div.order-list-table-box > div > div > div > div > ul > li.ant-pagination-item.ant-pagination-item-{page} > a"
                # )
                # logging.error(f"Failed to click on page\n{e}")
                # time.sleep(1000)
                break

    def get_page_copy_trades(self, driver):

        for i in range(1, 9):
            try:
                logging.info(f"Getting copy trade row {i}")
                self.get_row_by_id(driver, i)

            except Exception as e:
                print(e)
                sleep(10)

    def get_row_by_id(self, driver, rowId):
        openSLAndMargin = self.get_element(
            driver, xpaths.COPY_TRADES_OPENSL.format(rowId + 1)
        )
        symbol = self.get_element(driver, xpaths.COPY_TRADES_SYMBOL.format(rowId + 1))
        # margin = self.get_element(driver, xpaths.COPY_TRADES_MARGIN.format(rowId + 1))

        entryPrice = self.get_element(
            driver, xpaths.COPY_TRADES_ENTRY_PRICE.format(rowId + 1)
        )
        # entryPriceCurrency = self.get_element(
        #     driver, xpaths.COPY_TRADES_ENTRY_PRICE_CURRENCY.format(rowId + 1)
        # )
        openTime = self.get_element(
            driver, xpaths.COPY_TRADES_OPEN_TIME.format(rowId + 1)
        )
        copyTradeROI = self.get_element(
            driver, xpaths.COPY_TRADES_ROI.format(rowId + 1)
        )

        res = {
            "openSL": "L"
            if openSLAndMargin.text.split(" ")[0].lower() == "long"
            else "S",
            "margin": openSLAndMargin.text.split(" ")[-1],
            "symbol": symbol.text,
            "entryPrice": entryPrice.text,
            "openTime": openTime.text,
            "copyTradeROI": copyTradeROI.text,
        }

        key = (
            res["openSL"]
            + res["symbol"]
            + res["margin"]
            + res["entryPrice"]
            + res["openTime"]
        )
        key = self.format_key(key)

        data = (key, json.dumps(res), 0, 0)
        print(data)
        condition = f"key='{key}'"
        database.select_or_insert(table="open_trade", condition=condition, data=data)

    def get_open_trades(self) -> dict:
        res = {}

        openTrades = database.select_all_from(
            table="open_trade", condition="is_traded=0"
        )

        for openTrade in openTrades:
            key = openTrade[1]
            trade = json.loads(openTrade[2])

            res[key] = trade

        return res

    def set_is_traded_for(self, key: str):
        set_condition = "is_traded=1"
        where_condition = f"key='{key}'"
        database.update_table(
            table="open_trade", set_cond=set_condition, where_cond=where_condition
        )

    def set_order_no_for(self, key: str, order_no: str):
        set_condition = f"order_no='{order_no}'"
        where_condition = f"key='{key}'"
        database.update_table(
            table="open_trade", set_cond=set_condition, where_cond=where_condition
        )

    def roi_to_float(self, strROI: str) -> float:
        try:
            strROI = strROI.replace("%", "")
            if strROI == "+" or strROI == "-":
                return 0
            return float(strROI)
        except Exception as e:
            self.error_log(f"Failed to convert ROI: {strROI}\n{e}", filename="helper.roi_to_float.log")
            return CONFIG.ROI_TO_FOLLOW + 1

    def isOkToFollow(self, copyTrade: list) -> bool:
        # return True
        try:
            openOn = datetime.strptime(copyTrade["openTime"], "%Y-%m-%d %H:%M:%S")
            isTimeOk = time.time() - openOn.timestamp() <= CONFIG.SECOND_TO_FOLLOW
            isRoiOk = self.roi_to_float(copyTrade["copyTradeROI"]) <= CONFIG.ROI_TO_FOLLOW

            return isTimeOk and isRoiOk
        except Exception as e:
            self.error_log(
                f"Error to check to follow\n{e}", filename="check_follow.log"
            )
            return False

    def get_order_to_close(self) -> list:
        pastTrades = database.select_all_from(
            table="past_trade", condition="is_closed=0"
        )

        return pastTrades

    def find_order_to_close(self, driver, data_index):
        try:
            spans = self.get_element(
                driver, f'//tr[@data-index="{data_index}"]'
            ).find_elements(By.TAG_NAME, "span")
            return spans
        except Exception as e:
            return False

    def get_all_order(self, driver):
        driver.switch_to.window(driver.window_handles[2])
        self.wait_and_find_element(driver, xpaths.OPEN_TRADES_COPY_TRADING).click()

        time.sleep(1)
        copyTrades = self.get_element(driver, xpaths.OPEN_TRADE_COPY_TRADES_SUM).text
        copyTrades = copyTrades.split("(")[-1].replace(")", "").strip("\n").strip()

        # copyTradesTable = driver.find_element(By.CLASS_NAME, "position__table__content")
        # rows = copyTradesTable.find_elements(By.TAG_NAME, "tr")
        # # rows[0].click()
        # scroll_origin = ScrollOrigin.from_element(rows[0])

        # ActionChains(driver).scroll_from_origin(scroll_origin, 0, 50).perform()

        # time.sleep(1000)

        # for i in range(1, 10):
        #     position__table__content = driver.find_element(
        #         By.CLASS_NAME, "position__table__content"
        #     )
        #     rows = position__table__content.find_elements(By.TAG_NAME, "tr")
        #     scroll_origin = ScrollOrigin.from_element(rows[-1])
        #     ActionChains(driver).scroll_from_origin(scroll_origin, 0, 80).perform()
        #     position__table__content = driver.find_element(
        #         By.CLASS_NAME, "position__table__content"
        #     )
        #     rows = position__table__content.find_elements(By.TAG_NAME, "tr")
        #     for row in rows:
        #         print(row.get_attribute("data-index"))
        #         spans = row.find_elements(By.TAG_NAME, "span")
        #         print(spans[-2].text)
        #     time.sleep(1)

        # time.sleep(10000)
        try:
            copyTrades = int(copyTrades)
            if copyTrades <= 0:
                return

            for i in range(int(copyTrades)):
                while not self.find_order_to_close(driver, i):

                    position__table__content = driver.find_element(
                        By.CLASS_NAME, "position__table__content"
                    )
                    rows = position__table__content.find_elements(By.TAG_NAME, "tr")
                    scroll_origin = ScrollOrigin.from_element(rows[-1])
                    ActionChains(driver).scroll_from_origin(
                        scroll_origin, 0, 60
                    ).perform()

                    # time.sleep(1)

                spans = self.find_order_to_close(driver, i)
                print(i, spans[-2].text)
        except Exception as e:
            print(e)

    def close_order_with(
        self, driver, window_handles_for: dict, symbol: str, order_no_to_close: str
    ):
        if symbol not in CONFIG.PRICE.keys():
            return

        driver.switch_to.window(driver.window_handles[window_handles_for[symbol]])
        self.wait_and_find_element(driver, xpaths.OPEN_TRADES_COPY_TRADING).click()

        time.sleep(1)
        copyTrades = self.get_element(driver, xpaths.OPEN_TRADE_COPY_TRADES_SUM).text
        copyTrades = copyTrades.split("(")[-1].replace(")", "").strip("\n").strip()

        try:
            copyTrades = int(copyTrades)
            if copyTrades <= 0:
                return

            for i in range(int(copyTrades)):
                spans = self.find_order_to_close(driver, i)
                while not spans:
                    position__table__content = driver.find_element(
                        By.CLASS_NAME, "position__table__content"
                    )
                    rows = position__table__content.find_elements(By.TAG_NAME, "tr")
                    scroll_origin = ScrollOrigin.from_element(rows[-1])
                    ActionChains(driver).scroll_from_origin(
                        scroll_origin, 0, 60
                    ).perform()

                    spans = self.find_order_to_close(driver, i)

                order_no = spans[-2].text
                if order_no == order_no_to_close:
                    spans[-1].click()
                    self.wait_and_find_element(
                        driver, xpaths.COPY_TRADES_CLOSE_ORDER_CONFIRM
                    ).click()
                    Noti(f"Closed **{symbol}**. Order number: `{order_no}`.").send()
                    time.sleep(0.5)
                    return
        except Exception as e:
            print(e)

    def close_all_orders(self, driver, window_handles_for):
        orders = [
            {"symbol": json.loads(openTrade[2])["symbol"], "order_no": openTrade[4]}
            for openTrade in database.select_all_from(table="open_trade")
        ]
        print(orders)
        for order in orders:
            logging.info(
                f'Processing {order["symbol"]} with order: {order["order_no"]}'
            )
            self.close_order_with(
                driver=driver,
                window_handles_for=window_handles_for,
                symbol=order["symbol"],
                order_no_to_close=order["order_no"],
            )

    def close_orders(self, driver, window_handles_for):
        orders = self.get_order_to_close()
        if not orders:
            return

        for order in orders:
            key = order[1]
            symbol = json.loads(order[2])["symbol"]

            opened_trade = database.select_all_from(
                table="open_trade", condition=f"key='{key}'"
            )
            if not opened_trade:
                continue

            order_no = opened_trade[0][4]
            self.close_order_with(
                driver=driver,
                window_handles_for=window_handles_for,
                symbol=symbol,
                order_no_to_close=order_no,
            )

            sleep(3)


helper = Helper()


if __name__ == "__main__":
    helper.set_is_traded_for(key="LBTCUSDT5x202205USDT2022-09-1413:43:15")
