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
    def __init__(self, user_id, file_path=None,text=None, root_path=None):
        self.user_id = user_id
        self.plant_data = None
        self.db_path = os.path.join(root_path, "sample.db")
        self.file_path = file_path
        self.text = text
        self.root_path = root_path
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()

    def treat_picture(self):
        """
        画像を受けとったらテーブルを生成し､画像の保存先を入力
        """
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
        self.c.execute('INSERT INTO items (user_id, status, name, file_path, memo, localtime) VALUES (?,?,?,?,?,?)', (self.user_id, "start", None, self.file_path, None, datetime.datetime.now()))
        self.conn.commit()

    def input_plant_data(self):
        """
        DBのstatusから入力状況を確認｡入力に進む｡
        受け取ったテキストをDBに入力｡
        """
        if self.text == "キャンセル":
            self.delete_record()
            return "キャンセルしたよ｡"
        status = self.check_status()
        if status == "start":
            self.update_record("name", self.text, "name")
            return f"{self.text}で登録したよ｡\n何かメモがあれば入力してね\n｢キャンセル｣と入力で終了"
        elif status == "name":
            self.update_record("memo", self.text, "finished")
            return "メモの登録が完了したよ"
        elif status == "finished":
            return self.watch_image()

    def update_record(self, colmn, answer, status):
        """
        第一引数(colmn)の列の値を第二引数の値(answer)に更新する
        その後､回答状況statusを第三引数(status)の値に更新する
        """
        sql_for_palm = f"UPDATE items set {colmn} = '{answer}' where user_id = '{self.user_id}' and id = (select max(id) from items)"
        sql_for_update_status = f"UPDATE items set status = '{status}' where user_id = '{self.user_id}' and id = (select max(id) from items)"
        self.c.execute(sql_for_palm)
        self.c.execute(sql_for_update_status)
        self.conn.commit()

    def delete_record(self):
        sql_for_delete = f"DELETE from items where user_id = '{self.user_id}' and id = (select max(id) from items)"
        self.c.execute(sql_for_delete)
        self.conn.commit()

    def check_status(self):
        """
        リクエストのあったユーザーIDの最後のステータスをチェックし､次の入力を行う
        """
        sql_chk_status = f"select status from items where user_id = '{self.user_id}' order by localtime desc limit 1"
        self.c.execute(sql_chk_status)
        return self.c.fetchall()[0][0]

    def watch_image(self):
        sql_for_imagePath = f"select file_path from items where user_id = '{self.user_id}' and name = '{self.text}' order by id desc limit 1"
        self.c.execute(sql_for_imagePath)
        result = self.c.fetchall()
        if result:
            return result[0][0]
        else:
            return None

    def select_SQL2(self):
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
