# import sys
# from pathlib import Path
# import requests
# from bs4 import BeautifulSoup
# import lxml.html as lh
# import pandas as pd
# import datetime
# import re
# import time
# import numpy as np
from logging import raiseExceptions
import logging
import os
from pathlib import Path
import pymongo
from dotenv import load_dotenv
from tqdm import tqdm
import sys
# TODO: shortcut function to get detailed stats
# TODO: use argparse
# DOTENV_PATH = '.'

# MONGODB_PWD = None
# MONGODB_USERNAME = None
# MONGODB_ENDPOINT = None
# CURRENT_TIMEZONE = None

# env_path = Path(DOTENV_PATH) / '.env'
# if not (env_path.exists()):
#     print('.env file is missing.')
#     sys.exit()
# load_dotenv(dotenv_path=env_path)

# MONGODB_PWD = os.getenv('MONGODB_PWD')
# MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
# MONGODB_ENDPOINT = os.getenv('MONGODB_ENDPOINT')
# CURRENT_TIMEZONE = os.getenv('CURRENT_TIMEZONE ')

class DBHelper(object):
    """
    docstring
    """
    def __init__(self):
        """
        placeholder for init
        """
        pass

    def create_connection(self, user_name, passcode, endpoint):
        """
        template method to create database connection
        """
        pass

    def get_games(self, parameter_list):
        """
        docstring
        """
        pass



class MongoDBHelper(DBHelper):
    """
    Just a bunch of helper functions for MongoDB database I/O
    """
    # TODO: maybe it's better to create client in init??
    def __init__(self):
        """
        placeholder for init
        """
        pass
    
    @classmethod
    def create_connection(self, user_name, passcode, endpoint):
        """
        创建一个Mongo client, connect to the cluster 
        """
        try:
            client =pymongo.MongoClient(f'mongodb+srv://{user_name}:{passcode}@{endpoint}')
        except:
            print("connection failed!")
            return None
        print("existing database " + str(client.list_database_names()))
        return client

    @classmethod
    def is_gameid_inDB(self, gameids:list,collection,id_col_name="GameID_Sina")->dict:
        """
        Take a list of gameIDs, return a dictionary of found gameids and missing gameids in a mongoDB collection
        """
        foundDocs=list(collection.find({ id_col_name: { "$in": gameids} },{id_col_name:1})) 
        foundIDs=[]
        for foundDoc in foundDocs: 
            foundIDs.append(foundDoc[id_col_name])
        
        return {'InDB':list(set(foundIDs)&set(gameids)),'NotInDB':list(set(foundIDs)^set(gameids))}
    # TODO: use decorator
    # def insert_hint(insert_func):
    #     def wrapper_func(self,records,collection):
    #         results = insert_func(self,records,collection)
    #         if results.acknowledged:
    #             print(f'{collection.name} operation acknowledged!')
    #             print(f"{len(results.inserted_ids)} records were changed.")
    #         else:
    #             raise Exception('Staging delete failed!')
    #         return results
    #     return wrapper_func

    @classmethod
    def insert_records(self,collection,records:dict):
        """
        Insert one or more records into the collection. Return the result Mongo returned.
        """
        results = collection.insert_many(records)
        if results.acknowledged:
            print(f'{collection.name} operation acknowledged!')
            print(f"{len(results.inserted_ids)} records were inserted into {collection.name}.")
        else:
            raise Exception('Operation failed!')
        return results

    @classmethod
    def delete_records(self,collection,filter:dict):
        results = collection.delete_many(filter)
        if results.acknowledged:
            print(f'{collection.name} operation acknowledged!')
            print(f"{results.deleted_count} records were deleted from {collection.name} .")
        else:
            raise Exception('Operation failed!')
        return results
    
    @classmethod
    def update_records(self):
        raise NotImplementedError

    @classmethod
    def select_records(self,collection,filter:dict={},field:dict={},nlimit:int=None)->dict:
        """
        select records from mongodb, using filter, limit to n records. If nlimit is None, then 
        all the records will b

        example:
        >> mongohelper.select_records(collection,filter={'主队': '广东'},field={'GameID_Sina':1},nlimit=5)
           This will select 5 documents from the db, where 主队=广东, also it only pulls out filed "GameID_Sina"
        """
        if field:
            if nlimit:
                results = collection.find(filter,field).limit(nlimit)
            else:
                results = collection.find(filter,field)
        else:
            if nlimit:
                results = collection.find(filter).limit(nlimit)
            else:
                results = collection.find(filter)
        return list(results)


    @classmethod
    def insert_new_games(self, scraped_schedule, coll_productionGames, coll_stagingGames,id_col_name="GameID_Sina"):
        """
        insert new games into collproductionaGames
        
        """
        logger = logging.getLogger()
        # delete all the records in staging first
        logger.info('----------delete all records staging collection----------')
        self.delete_records(coll_stagingGames,filter={})

        print(f"{coll_productionGames.name} has {coll_productionGames.count_documents({})} docs.")
        print(f"{coll_stagingGames.name} has {coll_stagingGames.count_documents({})} docs.")
        # insert into staging collection
        print('----------insert records into staging collection----------')
        self.insert_records(coll_stagingGames,scraped_schedule)
        staging_gameids = []
        for game in self.select_records(coll_stagingGames,{}):
            staging_gameids.append(game[id_col_name])

        # check what games should be inserted into production
        print('----------checking what records to insert into production----------')
        game_dict = self.is_gameid_inDB(staging_gameids,coll_productionGames,id_col_name="game_id")
        notindb = list(game_dict['NotInDB'])
        if not notindb:
            print('Production is up-to-date')
            print(f"{coll_productionGames.name} has {coll_productionGames.count_documents({})} docs.")
            return None
        docs_to_insert = list(coll_stagingGames.find({id_col_name:{"$in":notindb}},{'_id':0}))

        # insert into production, delete staging

        print('----------insert records into production collection----------')
        insertmany_results= self.insert_records(coll_productionGames,docs_to_insert)
        self.delete_records(coll_stagingGames,filter={})

        print(f"{coll_productionGames.name} has {coll_productionGames.count_documents({})} docs.")
        print(f"{coll_stagingGames.name} has {coll_stagingGames.count_documents({})} docs.")

        return insertmany_results
