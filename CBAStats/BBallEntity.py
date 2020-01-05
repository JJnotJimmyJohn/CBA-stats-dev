import pandas as pd
from tabulate import tabulate


def stats_output(df):
    print(tabulate(df, headers='keys', tablefmt='psql'))


class BBallEntity(object):
    def __init__(self):
        self.__raw_stats = self.__games_stats()



    @staticmethod
    def __games_stats(path=r'~/Documents/CBA_Stats/StatsData/All_Games_Stats_2020-01-01.csv'):
        games_stats = pd.read_csv(path, encoding='UTF-8',
                                  dtype={'Game_ID': object,'号码':object})
        # as of 2020-01-01, 10 is 田宇恒
        games_stats.loc[games_stats['球员'] == '10', '球员'] = '田宇恒'
        return games_stats

