import sqlite3
import os
import datetime

"""
目的:ステートフルな会話を目指す
手段:会話の状態をデータベースに状態を保存する
手段2:会話が始まるとDBに保存(user id的なので識別)､1つの会話を1レコードに保存し､どんどん更新していく
(進捗状況はstatuに記録し､どんどん更新していく)

↓

すべての項目が揃ったら､最後の処理を行う､statusを完了にする

"""

#データベース接続とカーソル生成
#print(os.getcwd())
#db_path = os.path.join(os.getcwd(),"sample.db")

class DB():
    def __init__(self, user_id):
        self.user_id = user_id
        self.plant_data = None
        self.db_path = r"C:\Users\syoka\python project\LINE-plant-log\sample2.db"
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
        #テーブルの生成
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            status TEXT,
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
                exit(

                )
            elif self.command == 1:
                self.input_plant_data()
                print("---登録が完了しました\n\n")
            elif self.command == 2:
                self.select_SQL()
                print("\n\n")
            else:
                print("---メニューの数字から選んでください")


    def input_plant_data(self):
        """
        データを入力していく､入力したデータはDBに保存される｡
        どこまで入力したかの状況はDBのstatusに保存される｡

        ↓ここを起動のたびにstatusの状況からルートを変更するように修正

        起動
        →user_id確認
        →そのユーザーの状況確認(やりかけの情報はレコードの有無)
        →なし→新規レコード作成
        →あり→statusの内容に応じて次の質問を投げかける

        """
        status = self.check_status()
        print(status)
        if status == "finished":
            self.insert_record()
            print("植物データの入力を開始します｡")
            self.plant_name = input("植物名を入力してください:")
            self.update_record("name", self.plant_name, "name")

        elif status == "name":
            self.plant_file_path = input("ファイルの保存場所を入力してください:")
            self.update_record("file_path", self.plant_file_path, "file_path")

        elif status == "file_path":
            self.plant_memo = input("メモ書きがあれば入力してください:\n")
            self.update_record("memo", self.plant_memo, "finished")

    def check_status(self):
        """
        リクエストのあったユーザーIDの最後のステータスをチェックする
        """
        sql_chk_status = f"select status from items where user_id = {self.user_id} order by localtime desc limit 1"
        self.c.execute(sql_chk_status)
        return self.c.fetchall()[0][0]

    def insert_record(self):
        """
        処理の最初にuser_id以外が空のレコードを挿入する
        """
        self.c.execute('INSERT INTO items (user_id, status, name, file_path, memo, localtime) VALUES (?,?,?,?,?,?)', (self.user_id, None, None, None, None, datetime.datetime.now()))
        self.conn.commit()
        print("新規のレコードを作成しました")

    def update_record(self, colmn, answer, status):
        """
        第一引数(colmn)の列の値を第二引数の値(answer)に更新する
        その後､回答状況statusを第三引数(status)の値に更新する
        """
        sql_for_palm = f"UPDATE items set {colmn} = '{answer}' where user_id = {self.user_id} and id = (select max(id) from items)"
        sql_for_update_status = f"UPDATE items set 'status' = '{status}' where user_id = {self.user_id} and id = (select max(id) from items)"
        self.c.execute(sql_for_palm)
        self.c.execute(sql_for_update_status)
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

"""
user_idを取得しする方法を考える必要あり
"""
if __name__ == "__main__":
    user_id = 1192
    db = DB(user_id)
    db.select_command()
