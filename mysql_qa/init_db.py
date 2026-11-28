from pathlib import Path

from mysql_qa.db.mysql_client import MySQLClient


def main():
    csv_path = (
        Path(__file__).resolve().parent
        / "data"
        / "JP学科知识问答.csv"
    )

    mysql_client = MySQLClient()

    try:
        # 创建 jpkb 表
        mysql_client.create_table()

        # 检查表中是否已经有数据
        mysql_client.cursor.execute("SELECT COUNT(*) FROM jpkb")
        count = mysql_client.cursor.fetchone()[0]

        if count > 0:
            print(f"jpkb 表中已有 {count} 条数据，跳过导入")
            return

        # 表为空时导入 CSV
        mysql_client.insert_data(csv_path)
        print("CSV 数据导入完成")

    finally:
        mysql_client.close()


if __name__ == "__main__":
    main()