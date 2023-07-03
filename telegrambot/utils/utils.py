import asyncio
import os.path

import pandas as pd
from telegrambot.models import *
import json
from telegrambot.repository.repository import Repository, SQL


class Utils:
    repository = Repository
    sql = SQL

    # Надо брать с [1:]

    @staticmethod
    def excel_to_json(path_to_excel):
        excel_table = pd.read_excel(path_to_excel)
        if os.path.exists('moving_db.json'):
            os.rename('moving_db.json', 'moving_db_new.json')
            excel_table.to_json('moving_db.json', orient='records')
            os.remove('moving_db_new.json')
        else:
            excel_table.to_json('moving_db.json', orient='records')

        return 'moving_db.json'

    @staticmethod
    def create_table():
        return Utils.sql.create_table()

    @staticmethod
    def insert_data_from_json(path):
        return Utils.sql.insert_data_from_json(path)

    @staticmethod
    def delete_table():
        return Utils.sql.delete_table()

    @staticmethod
    def rename_table():
        return Utils.sql.rename_table()

    @staticmethod
    def drop_json():
        pass

    @staticmethod
    def rename_json(path):
        if os.path.exists('moving_db.json'):
            os.remove('moving_db.json')
            os.rename(path, 'moving_db.json')
        else:
            os.rename(path, 'moving_db.json')
