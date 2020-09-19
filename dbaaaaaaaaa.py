import sqlite3
import os
import datetime

#データベース接続とカーソル生成
#print(os.getcwd())
#db_path = os.path.join(os.getcwd(),"sample.db")

class DB():
    def __init__(self):
        self.plant_data = None
        self.db_path = r"C:\Users\syoka\python project\LINE-plant-log\sample.db"
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
        #テーブルの生成
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            file_path TEXT,
            memo TEXT,
            localtime DATETIME
            )""")

    def select_command(self):
        while True:
            self.command = int(input("何を行いますか?数字を選んでEnterキーを押してください\n1. 画像を登録\n2. 画像を閲覧\n3. 終了\n--→"))
            print()
            if self.command == 3:
                print("---終了します｡ばいばい｡")
                self.close_data()
                break
            elif self.command == 1:
                self.insert_data()
                print("---登録が完了しました\n\n")
            elif self.command == 2:
                self.select_SQL()
                print("\n\n")
            else:
                print("---メニューの数字から選んでください")


    def input_plant_data(self):
        print("植物データの入力を開始します｡")
        self.plant_name = input("植物名を入力してください:")
        self.plant_photo_path = input("次にファイルの保存場所を入力してください:")
        self.plant_memo = input("メモ書きがあれば入力してください:\n")

        return (self.plant_name, self.plant_photo_path, self.plant_memo)

    def insert_data(self):
        self.plant_data = self.input_plant_data()
        self.insert_data = (self.plant_data[0], self.plant_data[1], self.plant_data[2], datetime.datetime.now())
        self.c.execute('INSERT INTO items (name, file_path, memo, localtime) VALUES (?,?,?,?)', (self.insert_data))
        self.conn.commit()

    def select_SQL(self):
        print("現在は下記の植物が登録されています:")
        self.c.execute('select distinct name from items order by localtime desc')
        for item in self.c.fetchall():
            print(item[0])
        print()
        self.requested_item_name = input("閲覧したい植物名を選択してください:")
        print()
        print(self.requested_item_name)
        self.c.execute('select * from items where name = ? order by localtime desc', (self.requested_item_name,))
        print(self.c.fetchall())


    def close_data(self):
        self.conn.close()


db = DB()
db.select_command()
