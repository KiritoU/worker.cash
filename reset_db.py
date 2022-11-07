from _db import database


def main():
    database.update_table(table="open_trade", set_cond="is_traded=0", where_cond="1=1")
    database.update_table(table="open_trade", set_cond="order_no=0", where_cond="1=1")


if __name__ == "__main__":
    main()
