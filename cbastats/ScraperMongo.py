import sys
from pathlib import Path
from types import ClassMethodDescriptorType
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
ENCODING = 'UTF-8'
PARSER = 'html.parser'

HEADERS = {
    'User-Agent': r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
    r'Chrome/41.0.2227.1 Safari/537.36'}
SINA_SCHEDULE_BASE_URL = "http://cba.sports.sina.com.cn/cba/schedule/all/"

# TODO: what if user doesn't need DB access? .env necessary?
# secret variables should be saved in .env files

env_path = Path(DOTENV_PATH) / '.env'
if not (env_path.exists()):
    print('.env file is missing.')
    sys.exit()
load_dotenv(dotenv_path=env_path)



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
    Class for scraping data from sina CBA
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
        self.scraper_params = self.get_params(
            self.base_url, self.encoding, self.parser, self.headers)
        self.current_season=sorted(self.scraper_params['qleagueid'].items(), key=lambda item: int(item[1]), reverse=True)[0][0]
        self.db_engine = None

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
        page_content = self.get_page_content(
            url=base_url, encoding=encoding, parser=parser, headers=headers)
        param_html_list = page_content.find_all('select')
        param_dict = {}

        for param in param_html_list:
            options = {}
            for option in param.find_all('option'):
                options[option.text] = option['value']
            param_dict[param['name']] = options

        return param_dict

    def scrape_schedule(self, season=None, month='全部', team='全部'):
        """
        此函数用于爬取赛程和详细数据的链接
        
        params:
            season defaults to current_season

        """
        if season is None:
            season=self.current_season

        try:
            qleagueid = self.scraper_params['qleagueid'][season]
        except KeyError:
            print(f'该赛季不存在。')
        try:
            qmonth = self.scraper_params['qmonth'][month]
        except KeyError:
            print(f'该月份不存在。')
        try:
            qteamid = self.scraper_params['qteamid'][team]
        except KeyError:
            print(f'该球队不存在。')

        composed_url = f"http://cba.sports.sina.com.cn/cba/schedule/all/?qleagueid={qleagueid}&qmonth={qmonth}&qteamid={qteamid}"

        # 爬取整张页面html
        page_content = self.get_page_content(
            url=composed_url, encoding=self.encoding, parser=self.parser, headers=self.headers)

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
        
        # 分别提取每行的数据和link
        rows = []
        for tr in trs:
            row = {}
            tds = tr.find_all('td')
            for td in zip(headers,tds):
                header=td[0]
                cell_content=td[1]
                cell_text = str(cell_content.text).strip()
                cell_link = None   
                # 提取link
                if cell_content.find('a',href=True):
                        cell_link=cell_content.find('a',href=True)['href'].strip()
                
                # 如果不含link        
                if not cell_link:
                    row[header]=cell_text
                    continue
                else:
                    # there is link
                    # 并且表头和单元格内容不一样
                    # 比如表头是”比分“，单元格内容是”116：131“，且有链接
                    # 那么该cell的数据是{'比分':{'比分':'116:131','url':'https://xxx.xxx.xxx'}}
                    if (cell_text!=header):
                        cell={}
                        cell[header]=cell_text
                        cell['url']=cell_link
                        row[header]=cell
                        continue
                    # 如果有link，但标题和单元格文本一样
                    # 比如标题是“战报”，单元格文本也是“战报”，则没必要再列一遍“战报”
                    else:
                        row[header]=cell_link
            rows.append(row)

        for row in rows:
            row['赛季']=season
            row['GameID_Sina']=re.findall('schedule[/]show[/](\d+)[/]',row['比分']['url'])[0]
            # FIXME: fix gameID,主队ID，客队ID issue in stats calculation
            row['主队']['TeamID_Sina']=re.findall('team[/]show[/](\d+)[/]',row['主队']['url'])[0]
            row['客队']['TeamID_Sina']=re.findall('team[/]show[/](\d+)[/]',row['客队']['url'])[0]
            row['GameStats']=[]
            row['PlayByPlay']=[]
        return rows


    def update_schedule(self, season,collection,update_game_stats=False,update_playbyplay=False):
        """
        docstring
        """
        inserted_objs = []
        print('start scraping')
        scraped_schedule = sina_scraper.scrape_schedule(season=season, month='全部', team='全部')
        print('scrape complete')
        for game in scraped_schedule[:10]:
            if is_record_found({'GameID_Sina':game['GameID_Sina']},collection):
                continue
            x+=1
        pass

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

    def clean_staging_schedule(self):
        """
        清理刚scrape到CBA_Staging的table
        """
        # query to clean-up staging schedule
        with self.create_db_engine(DB_USERNAME, DB_PWD, DB_ENDPOINT).connect() as connection:
            with connection.begin():
                # delete未开始，没比分的比赛
                connection.execute("""
                DELETE FROM CBA_Staging.Schedules
                WHERE 比分='VS';
                                """)

                # delete已经scrape过的比赛
                connection.execute("""
                DELETE
                FROM CBA_Staging.Schedules
                WHERE CBA_Staging.Schedules.SinaGame_ID IN (
                SELECT SinaGame_ID
                FROM CBA_Data.Schedules
                );

                                """)

                # delete重复比赛
                connection.execute("""
                DELETE
                FROM CBA_Staging.Schedules
                WHERE EXISTS (
                SELECT 1
                FROM  CBA_Data.Schedules prod
                WHERE prod.主队=CBA_Staging.Schedules.主队
                AND prod.主队=CBA_Staging.Schedules.主队
                AND prod.日期=CBA_Staging.Schedules.日期
                );
                                """)

                # scrape完的比赛insert到CBA_Data.Schedules
                connection.execute("""
                INSERT into CBA_Data.Schedules
                SELECT *
                FROM CBA_Staging.Schedules
                WHERE SinaGame_ID not in (
                SELECT SinaGame_ID
                FROM CBA_Data.Schedules
                ) and 
                SinaGame_ID in (
                SELECT SinaGame_ID
                FROM CBA_Data.PlayerStatsPerGame
                );
                                """)
                # 删除已scrape完的比赛，且已经insert到CBA_Data.Schedules的比赛
                connection.execute("""
                DELETE FROM  CBA_Staging.Schedules
                WHERE SinaGame_ID in (
                SELECT SinaGame_ID
                FROM CBA_Data.Schedules
                ) and 
                SinaGame_ID in (
                SELECT SinaGame_ID
                FROM CBA_Data.PlayerStatsPerGame
                );
                                """)

    def split_made_attempt(self, scraped_stats):
        """
        用于删除投篮命中率,并把”2分中-投“分离成“2分中”，“2分投”两列
        """
        for col_name in list(filter(lambda x: '-' in x, scraped_stats.columns.tolist())):
            orig_col = col_name
            col_made = re.findall('(.*)中-投', col_name)[0] + '中'
            col_attempt = re.findall('(.*)中-投', col_name)[0] + '投'
            scraped_stats[[col_made, col_attempt]
                          ] = scraped_stats[orig_col].str.split('-', expand=True)
            scraped_stats[col_attempt] = scraped_stats[col_attempt].apply(
                lambda x: re.sub('[(].*[)]', '', x))

            scraped_stats[col_made] = pd.to_numeric(scraped_stats[col_made])
            scraped_stats[col_attempt] = pd.to_numeric(
                scraped_stats[col_attempt])

            scraped_stats.drop(columns=orig_col, inplace=True)
        return scraped_stats

    def scrape_games(self, schedule_to_scrape):
        """
        爬取schedule_to_scrape里的每一场比赛的详细比赛数据统计
        """
        assert len(schedule_to_scrape) > 0, "no game to scrape"
        df_list = []

        progress_bar = tqdm(total=len(schedule_to_scrape))
        for index, row in schedule_to_scrape.iterrows():

            # progress_bar.update(1)

            detail_url = row['统计_link']
            page_content = self.get_page_content(
                detail_url, encoding='GB2312', parser=PARSER, headers=HEADERS)

            for table_num, table in enumerate(page_content.find_all("table")[:2]):
                stats_headers = [th.text for th in table.find(
                    'thead').find_all('th')]
                stats_headers.insert(0, '球员_link')
                # extract details
                all_trs = []
                for tr in table.find('tbody').find_all('tr'):
                    # 抓取行(tr)
                    all_tds = []
                    # 在每一行中抓取每一格(td)
                    for td in tr.find_all('td'):
                        # get 球员link
                        if td.find('a', href=True):
                            all_tds.append(td.find('a', href=True)[
                                           'href'].strip())
                        all_tds.append(td.text.strip().replace(
                            ' ', '').replace('\n', ''))
                    all_trs.append(all_tds)

                team_df = pd.DataFrame(all_trs, columns=stats_headers)

                # 删除球队行
                team_df.drop(team_df.loc[team_df['号码']
                                         == '--'].index, inplace=True)

                # clean data frame

                # get 球员ID
                # 暂不提取球员ID，有时新球员加入，新浪更新不及时，可能会没有球员ID，导致error
                # team_df['球员ID'] = team_df['球员_link'].apply(lambda x: int(re.findall('show[/](\d+)[/]', x)[0]))

                # team_df['号码'] = team_df['号码'].astype(str)
                team_df['轮次'] = row['轮次']
                team_df['SinaGame_ID'] = row['SinaGame_ID']
                if table_num == 0:
                    # 主队table
                    team_df['球队ID'] = row['主队ID']
                    team_df['对手ID'] = row['客队ID']
                    team_df['球队'] = row['主队']
                    team_df['对手'] = row['客队']
                else:
                    # 客队table
                    team_df['球队ID'] = row['客队ID']
                    team_df['对手ID'] = row['主队ID']
                    team_df['球队'] = row['客队']
                    team_df['对手'] = row['主队']

                team_df['地点'] = row['地点']

                df_list.append(team_df)

            progress_bar.update(1)
            time.sleep(np.random.rand() * 4)

        progress_bar.close()
        games_stats = pd.concat(df_list, ignore_index=True)
        games_stats = self.split_made_attempt(games_stats)
        games_stats[['出场时间', '进攻篮板', '防守篮板', '助攻', '犯规', '抢断',
                     '失误', '盖帽', '扣篮', '被侵', '2分中', '2分投',
                     '3分中', '3分投', '罚球中',
                     '罚球投']] = games_stats[['出场时间', '进攻篮板', '防守篮板', '助攻', '犯规', '抢断',
                                            '失误', '盖帽', '扣篮', '被侵', '2分中', '2分投',
                                            '3分中', '3分投', '罚球中', '罚球投']].astype(int)
        # 计算得分
        games_stats['得分'] = games_stats['2分中']*2 + \
            games_stats['3分中']*3+games_stats['罚球中']
        games_stats['号码'] = games_stats['号码'].astype(str)
        # games_stats['球队ID'] = games_stats['球队ID'].astype(str)
        # games_stats['对手ID'] = games_stats['对手ID'].astype(str)
        games_stats['首发'] = games_stats['首发'].apply(
            lambda x: re.sub('是', '1', x))
        games_stats['首发'] = games_stats['首发'].apply(
            lambda x: re.sub('否', '0', x))
        games_stats['首发'] = games_stats['首发'].astype(int)

        return games_stats

    def scrape_sina(self, season):
        """
        shorcut function to scrape from sina CBA
        """
        ##### scrape schedule #####
        # compose the url you want to scrape
        print('-'*40)
        print('Composing url')
        print('-'*40)
        composed_url = self.compose_url(
            leagueid=season, month='全部', teamid='全部')
        # scrape the schedule
        print('Scraping Schedule')
        print('-'*40)
        scraped_schedule = self.scrape_schedule(composed_url)
        # insert/replace df into CBA_Staging.schedules
        print('Insert Schedule to CBA_Staging.Schedules')
        print('-'*40)
        self.insert_df_into_db(
            scraped_schedule, 'CBA_Staging', 'Schedules')
        # clean up CBA_Staging.schedules
        print('Cleaning up CBA_Staging.Schedules')
        print('-'*40)
        self.clean_staging_schedule()
        # check CBA_Staging.schedules
        print('Pulling schedule from CBA_Staging.Schedules')
        print('-'*40)
        schedule_to_scrape = self.query_stg_schedule()
        # scrape stats for each game
        print('Scraping game stats')
        print('-'*40)
        games_stats = self.scrape_games(schedule_to_scrape)
        # append stats to CBA_data.
        print('Append game stats to CBA_Data.PlayerStatsPerGame')
        print('-'*40)
        self.append_df_to_table(
            games_stats, 'CBA_Data', 'PlayerStatsPerGame')
        # clean up CBA_Staging.schedules
        # there should't be anything left in CBA_Staging.Schedules at this point
        print('Final clean up of the staging schedules')
        print('-'*40)
        self.clean_staging_schedule()

if __name__ == "__main__":
    print('executing')
    # sys.exit()

    ##### testing SinaScraper #####
    sina_scraper = SinaScraper(
        SINA_SCHEDULE_BASE_URL, ENCODING, PARSER, HEADERS)
    # sina_scraper.scrape_sina(season='20-21')
    ##### testing params #####
    # for key in sina_scraper.scrape_params:
    #     print(key)
    #     for key1 in sina_scraper.scraper_params[key]:
    #         print(f"{key1}---{sina_scraper.scraper_params[key][key1]}")

    # ##### scrape schedule #####
    # # compose the url you want to scrape
    print('-'*40)
    # print('Composing url')
    # print('-'*40)
    # composed_url = sina_scraper.compose_url(
    #     leagueid='20-21', month='全部', teamid='全部')
    # # scrape the schedule
    # print('Scraping Schedule')
    # print('-'*40)
    # scraped_schedule = sina_scraper.scrape_schedule(composed_url)
    # # insert/replace df into CBA_Staging.schedules
    # print('Insert Schedule to CBA_Staging.Schedules')
    # print('-'*40)
    # sina_scraper.insert_df_into_db(
    #     scraped_schedule, 'CBA_Staging', 'Schedules')
    # # clean up CBA_Staging.schedules
    # print('Cleaning up CBA_Staging.Schedules')
    # print('-'*40)
    # sina_scraper.clean_staging_schedule()
    # # check CBA_Staging.schedules
    # print('Pulling schedule to scape from CBA_Staging.Schedules')
    # print('-'*40)
    # schedule_to_scrape = sina_scraper.query_stg_schedule()
    # # scrape stats for each game
    # print('Scraping game stats')
    # print('-'*40)
    # games_stats = sina_scraper.scrape_games(schedule_to_scrape)
    # # append stats to CBA_data.
    # print('Append game stats to CBA_Data.PlayerStatsPerGame')
    # print('-'*40)
    # sina_scraper.append_df_to_table(
    #     games_stats, 'CBA_Data', 'PlayerStatsPerGame')
    # # clean up CBA_Staging.schedules
    # # there should't be anything left in CBA_Staging.Schedules at this point
    # print('Final clean up of the staging schedules')
    # print('-'*40)
    # sina_scraper.clean_staging_schedule()
