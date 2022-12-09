import json
import os.path


class DataBase:
    FILE_NAME = 'database.json'

    @classmethod
    def read_database(cls):
        if not os.path.isfile(DataBase.FILE_NAME):
            DataBase.save_database({})

        with open(DataBase.FILE_NAME, 'r', encoding="utf8") as fp:
            data_base = json.load(fp)
        return data_base

    @classmethod
    def save_database(cls, database):
        with open(DataBase.FILE_NAME, 'w', encoding="utf8") as fp:
            json.dump(database, fp, indent=2, ensure_ascii=False)

    @classmethod
    def update_user_city(cls, user_id, city):
        database = DataBase.read_database()
        str_user_id = str(user_id)
        database['cities'][str_user_id] = city.lower()
        DataBase.save_database(database)

    @classmethod
    def get_user_city(cls, user_id):
        str_user_id = str(user_id)
        database = DataBase.read_database()
        return database['cities'].get(str_user_id)
