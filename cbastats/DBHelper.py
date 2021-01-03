import sys
from pathlib import Path
from types import ClassMethodDescriptorType
from pymongo.errors import BulkWriteError
import requests
from bs4 import BeautifulSoup
# import lxml.html as lh
import pandas as pd
import datetime
import numpy as np
import re
import time
from pathlib import Path
from dotenv import load_dotenv
import os
from tqdm import tqdm
import pymongo

# TODO: use argparse
DOTENV_PATH = '.'

MONGODB_PWD = None
MONGODB_USERNAME = None
MONGODB_ENDPOINT = None

env_path = Path(DOTENV_PATH) / '.env'
if not (env_path.exists()):
    print('.env file is missing.')
    sys.exit()
load_dotenv(dotenv_path=env_path)

MONGODB_PWD = os.getenv('MONGODB_PWD')
MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_ENDPOINT = os.getenv('MONGODB_ENDPOINT')

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
    docstring
    """
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
    def is_gameid_inDB(self, gameids:list,collection)->dict:
        """
        Take a list of gameIDs, return a dictionary of found gameids and missing gameids in a mongoDB collection
        """
        foundDocs=list(collection.find({ 'GameID_Sina': { "$in": gameids} },{'GameID_Sina':1})) 
        foundIDs=[]
        for foundDoc in foundDocs: 
            foundIDs.append(foundDoc['GameID_Sina'])
        
        return {'InDB':list(set(foundIDs)&set(gameids)),'NotInDB':list(set(foundIDs)^set(gameids))}


    @classmethod
    def update_games(self, scraped_schedule,coll_cbaGames,coll_cbaGamesStaging):
        """
        docstring
        """
        # clean up staging first
        deletemany_result= coll_cbaGamesStaging.delete_many({})
        if deletemany_result.acknowledged:
            print('Staging delete acknowledged!')
        else:
            raise Exception('Staging delete failed!')

        print(f"{coll_cbaGames.name} has {coll_cbaGames.count_documents({})} docs.")
        print(f"{coll_cbaGamesStaging.name} has {coll_cbaGamesStaging.count_documents({})} docs.")
        # insert into staging collection
        coll_cbaGamesStaging.insert_many(scraped_schedule)
        staging_gameids = []
        for game in coll_cbaGamesStaging.find({},{'GameID_Sina':1}):
            staging_gameids.append(game['GameID_Sina'])

        # check what games should be inserted into production
        game_dict = self.is_gameid_inDB(staging_gameids,coll_cbaGames)
        notindb = list(game_dict['NotInDB'])
        if not notindb:
            print('Production is up-to-date')
            print(f"{coll_cbaGames.name} has {coll_cbaGames.count_documents({})} docs.")
            return None
        docs_to_insert = list(coll_cbaGamesStaging.find({'GameID_Sina':{"$in":notindb}},{'_id':0}))

        # insert into production, delete staging
        insertmany_result= coll_cbaGames.insert_many(docs_to_insert)
        deletemany_result= coll_cbaGamesStaging.delete_many({})
        if insertmany_result.acknowledged:
            print('Production insert acknowledged!')
            print(f"{len(insertmany_result.inserted_ids)} records were inserted into production.")
        else:
            raise Exception('Production insert failed!')
        
        if deletemany_result.acknowledged:
            print('Staging delete acknowledged!')
        else:
            raise Exception('Staging delete failed!')

        return insertmany_result