#!/usr/bin/env python
# coding: utf-8

# In[1]:


# from CBAStats.Player import *
# from CBAStats.Team import *
# from CBAStats.Player import stats_output
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


# In[2]:


def get_page_content(url, encoding='UTF-8', header={
            'User-Agent': r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                          r'Chrome/41.0.2227.1 Safari/537.36'}):
    session = requests.Session()
    base_url = url
    response = session.get(base_url, headers=header)
    response.encoding = encoding
    page_content = BeautifulSoup(response.content, "html.parser")
    return page_content


# In[3]:


# 链接中有几个参数，qleagueid是赛季，qmonth是月，qteamid是球队
# 空出qmonth和qteamid则可以无差别选取某赛季的所有比赛
# qleagueid并不是逐一递增或递减的，如20192020赛季是205，20182019是198

def get_params(default_schedule_url = "http://cba.sports.sina.com.cn/cba/schedule/all/"):
    """
    从赛程页爬取赛季，月，球队的可能参数值。
    从可能的参数值里选取想要爬取的赛季，月，球队等，并用get_url函数拼凑出目标url。
    """
    param_html_list = get_page_content(url=default_schedule_url).find_all('select')
    param_dict = {}

    for param in param_html_list:
        options = {}
        for option in param.find_all('option'):
            options[option.text] = option['value']
        param_dict[param['name']] = options
    
    return param_dict


# In[4]:


def get_url(leagueid = '19-20',month = '全部',teamid ='全部'):

    """
    此函数用于拼凑想要爬取的目标url。
    
    链接中有几个参数，qleagueid是赛季，qmonth是月，qteamid是球队。
    qleagueid并不是逐一递增或递减的，如20192020赛季是205，20182019是198。
    
    """
    param_dict = get_params(default_schedule_url = "http://cba.sports.sina.com.cn/cba/schedule/all/")
    qleagueid=param_dict['qleagueid'][leagueid]
    qmonth=param_dict['qmonth'][month]
    qteamid=param_dict['qteamid'][teamid]
    scrape_url = f"http://cba.sports.sina.com.cn/cba/schedule/all/?qleagueid={qleagueid}&qmonth={qmonth}&qteamid={qteamid}"
    
    return scrape_url


# In[5]:


def scrape_schedule(season = '19-20',month = '全部',teamid ='全部', 
                    only_show_params = False,param_url = "http://cba.sports.sina.com.cn/cba/schedule/all/"):
    """
    此函数用于爬取赛程和详细数据的链接，并存入CBA_Data.Staging_Schedules
    
    请注意，season(网页使用的参数是qleagueid)，month，team参数值是有限定值的。
    可通过运行scrape_schedule(only_show_params = False)来查询可用的参数。如果only_show_params=True那么本函数不会爬取赛程数据，只会显示可用参数。
    
    参数中，season(qleagueid)是赛季，qmonth是月，qteamid是球队。
    season(qleagueid)，如20192020赛季是205，20182019是198。
    
    Parameters: 
    
    season:
    month:
    teamid:
    only_show_params:
    param_url:
    """
    
    param_dict = get_params(default_schedule_url = param_url)
    
    if only_show_params:
        return param_dict
    
    # 拼凑出目标url
    schedule_url = get_url(leagueid = season,month = month,teamid =teamid)
    
    # 爬取整张页面html
    page_content = get_page_content(url=schedule_url)

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
    # 因此会有空白列，此处不删除是考虑到未来可能会有新内容
    text_list = np.reshape(text_list, [-1, 10])
    link_list = np.reshape(link_list, [-1, 10])
    df_schedule_text = pd.DataFrame(data=text_list, columns=headers)
    df_schedule_link = pd.DataFrame(data=link_list, columns=[header + '_link' for header in headers])

    df_schedule_full = pd.merge(df_schedule_text, df_schedule_link, left_index=True, right_index=True)

    df_schedule_full['SinaGame_ID'] = df_schedule_full['统计_link'].apply(lambda x: re.findall('show[/](\d+)[/]', x)[0])
    df_schedule_full['客队ID'] = df_schedule_full['客队'].apply(lambda x: param_dict['qteamid'][x])
    df_schedule_full['主队ID'] = df_schedule_full['主队'].apply(lambda x: param_dict['qteamid'][x])
    df_schedule_full['日期'] = pd.to_datetime(df_schedule_full['日期'])
       
    return df_schedule_full


# In[6]:


def get_schedule():
    
    user_name = 'master'
    passcode = 'Pw#cbashuju0131'
    endpoint = 'cbashuju.ctkaehd5rxxe.us-east-1.rds.amazonaws.com'
    database = 'CBA_Data'
    engine = create_engine(f'mysql+pymysql://{user_name}:{passcode}@{endpoint}/{database}')
    connection= engine.connect()

    # df.to_sql(name='Schedules',con=connection,index=False,if_exists='replace')
    df = pd.read_sql("select * from CBA_Data.Schedules", connection)
    connection.close()
    return df

def get_staging_schedule():
    
    user_name = 'master'
    passcode = 'Pw#cbashuju0131'
    endpoint = 'cbashuju.ctkaehd5rxxe.us-east-1.rds.amazonaws.com'
    database = 'CBA_Staging'
    engine = create_engine(f'mysql+pymysql://{user_name}:{passcode}@{endpoint}/{database}')
    connection= engine.connect()

    # df.to_sql(name='Schedules',con=connection,index=False,if_exists='replace')
    df = pd.read_sql("select * from CBA_Staging.Schedules", connection)
    connection.close()
    return df

def load_schedule_into_staging(scraped_schedule):
    # 写入数据库Staging_Schedule
    user_name = 'master'
    passcode = 'Pw#cbashuju0131'
    endpoint = 'cbashuju.ctkaehd5rxxe.us-east-1.rds.amazonaws.com'
#     database = 'CBA_Data'
    database = 'CBA_Staging'
    engine = create_engine(f'mysql+pymysql://{user_name}:{passcode}@{endpoint}/{database}')
    connection= engine.connect()

    scraped_schedule.to_sql(name='Schedules',con=connection,index=False,if_exists='replace')
    connection.close()

def clean_staging_schedule():
    
    # query to clean-up staging schedule
    
    user_name = 'master'
    passcode = 'Pw#cbashuju0131'
    endpoint = 'cbashuju.ctkaehd5rxxe.us-east-1.rds.amazonaws.com'
    database = 'CBA_Staging'
    engine = create_engine(f'mysql+pymysql://{user_name}:{passcode}@{endpoint}/{database}')
    with engine.connect() as connection:
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


# In[7]:


def get_coach(html):
    coach = re.findall('主教练：(.*?)领队', html)
    return coach


def get_lingdui(html):
    lingdui = re.findall('领队：(.*?)<', html)
    return lingdui


# In[8]:


def split_made_attempt(df_orig):
    """
    函数用于删除投篮命中率,split ”2分中-投“
    """
    df = df_orig.copy()
    for col_name in list(filter(lambda x: '-' in x, df.columns.tolist())):
        orig_col = col_name
        col_made = re.findall('(.*)中-投', col_name)[0] + '中'
        col_attempt = re.findall('(.*)中-投', col_name)[0] + '投'
        df[[col_made, col_attempt]] = df[orig_col].str.split('-', expand=True)
        df[col_attempt] = df[col_attempt].apply(lambda x: re.sub('[(].*[)]', '', x))
        
        df[col_made] = pd.to_numeric(df[col_made])
        df[col_attempt] = pd.to_numeric(df[col_attempt])
        
        df.drop(columns=orig_col, inplace=True)
    return df


# In[17]:


def scrape_games(schedule_to_scrape):
    assert len(schedule_to_scrape)>0,"no game to scrape"
    df_list = []

    for index,row in schedule_to_scrape.iterrows():

        detail_url = row['统计_link']
        page_content = get_page_content(detail_url, encoding='GB2312')

        for table_num,table in enumerate(page_content.find_all("table")[:2]):
            stats_headers = [th.text for th in table.find('thead').find_all('th')]
            stats_headers.insert(0,'球员_link')
            # extract details
            all_trs = []
            for tr in table.find('tbody').find_all('tr'):
                # 抓取行(tr)
                all_tds=[]
                # 在每一行中抓取每一格(td)
                for td in tr.find_all('td'):
                    # get 球员link
                    if td.find('a',href=True):
                        all_tds.append(td.find('a',href=True)['href'].strip())
                    all_tds.append(td.text.strip().replace(' ','').replace('\n',''))
                all_trs.append(all_tds)

            team_df =pd.DataFrame(all_trs,columns=stats_headers)

            # 删除球队行
            team_df.drop(team_df.loc[team_df['号码'] == '--'].index, inplace=True)

            # clean data frame

            # get 球员ID 
            # 暂不提取球员ID，有时新球员加入，新浪更新不及时，可能会没有球员ID，导致error
            # team_df['球员ID'] = team_df['球员_link'].apply(lambda x: int(re.findall('show[/](\d+)[/]', x)[0]))

            # team_df['号码'] = team_df['号码'].astype(str)
            team_df['轮次'] = row['轮次']
            team_df['SinaGame_ID']=row['SinaGame_ID']
            if table_num==0:
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
        if ((index+1)%10==0)|(index==0):
            print('已爬取', index+1,'场比赛', datetime.datetime.now())
        time.sleep(np.random.rand() * 4)

    print('完成！')
    games_stats = pd.concat(df_list, ignore_index=True)
    games_stats = split_made_attempt(games_stats)
    games_stats[['出场时间', '进攻篮板', '防守篮板', '助攻', '犯规', '抢断',
               '失误', '盖帽', '扣篮', '被侵', '2分中', '2分投', 
               '3分中', '3分投', '罚球中',
               '罚球投']] = games_stats[['出场时间', '进攻篮板', '防守篮板', '助攻', '犯规', '抢断',
                                   '失误', '盖帽', '扣篮', '被侵', '2分中', '2分投', 
                                   '3分中', '3分投', '罚球中','罚球投']].astype(int)
    # 计算得分
    games_stats['得分'] = games_stats['2分中']*2+games_stats['3分中']*3+games_stats['罚球中']
    games_stats['号码'] = games_stats['号码'].astype(str)
    # games_stats['球队ID'] = games_stats['球队ID'].astype(str)
    # games_stats['对手ID'] = games_stats['对手ID'].astype(str)
    games_stats['首发'] = games_stats['首发'].apply(lambda x: re.sub('是', '1', x))
    games_stats['首发'] = games_stats['首发'].apply(lambda x: re.sub('否', '0', x))
    games_stats['首发'] = games_stats['首发'].astype(int)
    
    return games_stats


# In[10]:


def append_details(df):
    # 写入数据库Staging_Schedule
    user_name = 'master'
    passcode = 'Pw#cbashuju0131'
    endpoint = 'cbashuju.ctkaehd5rxxe.us-east-1.rds.amazonaws.com'
    database = 'CBA_Data'
    engine = create_engine(f'mysql+pymysql://{user_name}:{passcode}@{endpoint}/{database}')
    connection= engine.connect()

    df.to_sql(name='PlayerStatsPerGame',con=connection,index=False,if_exists='append')

    connection.close()


# In[15]:


# scraped_schedule = scrape_schedule()
# load_schedule_into_staging(scraped_schedule)
# clean_staging_schedule()
# schedule_to_scrape = get_staging_schedule()
# schedule_to_scrape


# In[18]:


# games_stats=scrape_games(schedule_to_scrape)


# In[13]:


# games_stats


# In[13]:


# append_details(games_stats)


# In[14]:


# clean_staging_schedule()

