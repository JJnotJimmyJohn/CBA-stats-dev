import sys
from pathlib import Path
from sqlalchemy import create_engine
import pymysql
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

# TODO: use argparse
DOTENV_PATH = '.'
ENCODING = 'UTF-8'
PARSER = 'html.parser'
HEADERS = {
    'User-Agent': r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
    r'Chrome/41.0.2227.1 Safari/537.36'}
SINA_SCHEDULE_BASE_URL = "http://cba.sports.sina.com.cn/cba/schedule/all/"

# TODO: what if user doesn't need DB access? .env necessary?
# secret variables should be saved in .env files
DB_USERNAME = None
DB_PWD = None
DB_ENDPOINT = None


env_path = Path(DOTENV_PATH) / '.env'
if not (env_path.exists()):
    print('.env file is missing.')
    sys.exit()
load_dotenv(dotenv_path=env_path)

DB_USERNAME = os.getenv('CBADB_USERNAME')
DB_PWD =  os.getenv('CBADB_PWD')
DB_ENDPOINT =  os.getenv('CBADB_ENDPOINT')


class Scraper(object):
    """
    Scraper's base class
    """

    def __init__(self):
        pass

    @classmethod
    def get_page_content(cls, url, encoding, parser, headers):
        session = requests.Session()
        base_url = url
        response = session.get(base_url, headers=headers)
        response.encoding = encoding
        page_content = BeautifulSoup(response.content, parser)
        return page_content


class SinaScraper(Scraper):
    """
    Used to scrape data from sina CBA
    """

    def __init__(self, base_url, encoding, parser, headers):
        """
        docstring
        """
        super().__init__()
        self.encoding = encoding
        self.parser = parser
        self.headers = headers
        self.base_url = base_url
        self.scraper_params = self.get_params(self.base_url,self.encoding,self.parser,self.headers)
        self.db_engine=None

    def get_params(self, base_url, encoding, parser, headers) -> dict:
        """
        从赛程页爬取赛季、月、球队等下拉菜单里的可选值，用在get_url function里

        return:
            return类似这样的dictionary（未列出所有可能值）
            {'qleagueid': {'20-21': '206',
            '19-20': '205'},
            'qmonth': {'全部': '',
            '11': '11',
            '12': '12',
            '01': '01'},
            'qteamid': {'全部': '',
            '广东': '1',
            '江苏': '2',
            '上海': '4'}}
        """
        page_content = self.get_page_content(url=base_url, encoding=encoding, parser=parser, headers=headers)
        param_html_list = page_content.find_all('select')
        param_dict = {}

        for param in param_html_list:
            options = {}
            for option in param.find_all('option'):
                options[option.text] = option['value']
            param_dict[param['name']] = options

        return param_dict

    def compose_url(self,leagueid, month='全部', teamid='全部'):
        """
        此函数用于拼凑想要爬取的网页url。

        链接中有3个参数，qleagueid是赛季，qmonth是月，qteamid是球队。
        qleagueid并不是逐一递增或递减的，如18-19是198,19-20赛季是205。

        """
        try:
            qleagueid = self.scraper_params['qleagueid'][leagueid]
        except KeyError:
            print(f'该赛季不存在。')
        try:
            qmonth = self.scraper_params['qmonth'][month]
        except KeyError:
            print(f'该月份不存在。')
        try:
            qteamid = self.scraper_params['qteamid'][teamid]
        except KeyError:
            print(f'该球队不存在。')
        
        scrape_url = f"http://cba.sports.sina.com.cn/cba/schedule/all/?qleagueid={qleagueid}&qmonth={qmonth}&qteamid={qteamid}"

        return scrape_url

    def scrape_schedule(self, composed_url):
        """
         此函数用于爬取赛程和详细数据的链接
        """
        # 爬取整张页面html
        page_content = self.get_page_content(url=composed_url, encoding=self.encoding, parser=self.parser, headers=self.headers)
        
        # 赛程页面共有两张表
        # 第一张表是当前轮次比赛
        # 第二张表才是该赛季所有比赛

        # 爬取整张表的html
        target_table = page_content.find_all("table")[1]

        # 获取表头
        headers = [th.text for th in target_table.find('thead').find_all('th')]

        # 获取表格数据的html
        tbody = target_table.find('tbody')

        # 获取表格每行的html，存入list
        trs = tbody.find_all('tr')
        
        # 用于存储文本的list
        text_list =[]
        # 用于存储链接的list
        link_list = []

        for tr in trs:
            # 从每行中获取每一单元格的html
            tds = tr.find_all('td')
            for td in tds:
                # 获取每单元格的纯文本内容
                cell_text = str(td.text).strip()
                # 单元格内若无链接则为空字符
                cell_link = ''
                if td.find('a',href=True):
                    # 单元格内存在链接则保存
                    cell_link = td.find('a',href=True)['href'].strip()
                text_list.append(cell_text)
                link_list.append(cell_link)
        
        # 分别将文本和链接保存在两个dataframe中，最后再横向合并
        # 链接的dataframe在column header后加上“_link“后缀
        # 网页本身有空白列，此处不删除是考虑到未来可能会有新内容
        text_list = np.reshape(text_list, [-1, 10])
        link_list = np.reshape(link_list, [-1, 10])
        df_schedule_text = pd.DataFrame(data=text_list, columns=headers)
        df_schedule_link = pd.DataFrame(data=link_list, columns=[header + '_link' for header in headers])

        df_schedule_full = pd.merge(df_schedule_text, df_schedule_link, left_index=True, right_index=True)

        df_schedule_full['SinaGame_ID'] = df_schedule_full['统计_link'].apply(lambda x: re.findall('show[/](\d+)[/]', x)[0])
        df_schedule_full['客队ID'] = df_schedule_full['客队'].apply(lambda x: self.scraper_params['qteamid'][x])
        df_schedule_full['主队ID'] = df_schedule_full['主队'].apply(lambda x: self.scraper_params['qteamid'][x])
        df_schedule_full['日期'] = pd.to_datetime(df_schedule_full['日期'])
        
        return df_schedule_full
    
    def create_db_engine(self,user_name,passcode,endpoint,database=None):
        """
        创建一个database connection，用来execute query
        """
        if database:
            engine = create_engine(f'mysql+pymysql://{user_name}:{passcode}@{endpoint}/{database}')
        else:
            engine = create_engine(f'mysql+pymysql://{user_name}:{passcode}@{endpoint}')
        
        self.engine = engine

    def run_query_db(self,sql_str)->pd.DataFrame:
        """
        对数据库进行查询
        """
        with self.create_db_engine(DB_USERNAME,DB_PWD,DB_ENDPOINT).connect() as connection:
            df = pd.read_sql(sql_str, connection)
        # print(connection.closed)
        return df
    
    def insert_df_db(self,df_to_insert,database_name,table_name)->pd.DataFrame:
        """
        数据insert到表中
        """
        with self.create_db_engine(DB_USERNAME,DB_PWD,DB_ENDPOINT,database_name).connect() as connection:
            with connection.begin() as transaction:
                df_to_insert.to_sql(name=f'{table_name}',con=connection,index=False,if_exists='append')
                transaction.commit()
        # print(connection.closed)
        print('Insertion complete. Success is not garanteed. Check query to make sure.')

    def query_schedule(self):
        """
        查询数据库中的schedule
        """
        return self.run_query_db("select * from CBA_Data.Schedules")
    
    def query_stg_schedule(self):
        """
        查询数据库中的staging schedule(暂存)
        """
        return self.run_query_db("select * from CBA_Staging.Schedules")

    

if __name__ == "__main__":
    print('executing')
    # sys.exit()
    sina_scraper = SinaScraper(
        SINA_SCHEDULE_BASE_URL,ENCODING, PARSER, HEADERS)
    
    ##### testing params #####
    # for key in sina_scraper.scrape_params:
    #     print(key)
    #     for key1 in sina_scraper.scraper_params[key]:
    #         print(f"{key1}---{sina_scraper.scraper_params[key][key1]}")

    ##### testing query schedule #####
    schedule = sina_scraper.query_stg_schedule()
    schedule = schedule.iloc[:5]
    print(len(schedule))
    print('queried schedule')
    print('attempting load data')
    sina_scraper.insert_df_db(schedule,'CBA_Staging','Schedules')
    schedule = sina_scraper.query_stg_schedule()
    print(len(schedule))


    



        
