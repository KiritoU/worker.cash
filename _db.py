import sqlite3
import sys


from settings import CONFIG


class Database:
    def get_conn(self):
        try:
            return sqlite3.connect("bybit.db")
        except Exception as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

    def select_all_from(self, table: str, condition: str = "1=1", cols: str = "*"):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute(f"SELECT {cols} FROM {table} WHERE {condition}")
        res = cur.fetchall()
        cur.close()
        conn.close()

        return res

    def insert_into(self, table: str, data: tuple = None):
        conn = self.get_conn()
        cur = conn.cursor()

        columns = f"({', '.join(CONFIG.INSERT[table])})"
        values = f"({', '.join(['?'] * len(CONFIG.INSERT[table]))})"
        query = f"INSERT INTO {table} {columns} VALUES {values}"
        cur.execute(query, data)
        id = cur.lastrowid

        conn.commit()
        cur.close()
        conn.close()
        return id

    def update_table(
        self, table: str, set_cond: str, where_cond: str, data: tuple = ()
    ):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute(f"UPDATE {table} set {set_cond} WHERE {where_cond}", data)
        conn.commit()
        cur.close()
        conn.close()

    def delete_from(self, table: str = "", condition: str = "1=1"):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE {condition}")
        conn.commit()
        cur.close()
        conn.close()

    def select_or_insert(self, table: str, condition: str, data: tuple):
        res = self.select_all_from(table=table, condition=condition)
        if not res:
            self.insert_into(table, data)
            res = self.select_all_from(table, condition=condition)
        return res


database = Database()


def clear_database():
    tables = ["open_trade", "past_trade"]
    for table in tables:
        database.delete_from(table=table)


if __name__ == "__main__":
    # ID = 85
    # condition = f'ID = "{ID}"'
    # data = (
    #     "LBTCUSDT5x203350USDT2022-09-1410:06:03",
    #     '{"openSL": "L", "margin": "5x", "symbol": "BTCUSDT", "entryPrice": "20,335.0 USDT", "openTime": "2022-09-14 10:06:03", "copyTradeROI": "-4.63%"}',
    #     0,
    # )
    # database.insert_into(table="open_trade", data=("key1", "trade1", 0))
    # be_open_trade = database.select_all_from(table=f"open_trade")

    # print(be_open_trade)
    clear_database()
