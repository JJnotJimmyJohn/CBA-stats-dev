from CBAStats.BBallEntity import *

# todo: convert total_stats and something else to arrays, then convert back to df
# todo: all the output should be pandas dataframe


class Player(BBallEntity):
    def __init__(self, name):
        BBallEntity.__init__(self)
        self.__name = name
        pass

    @property
    def plr_name(self):
        return self.plr_raw_stats['球员'].unique()[0]

    @property
    def plr_tm_name(self):
        # used a list in case in the future player can be traded during season
        return self.plr_raw_stats['球队'].unique().tolist()

    @property
    def plr_raw_stats(self):
        raw_stats = self._BBallEntity__raw_stats.loc[self._BBallEntity__raw_stats['球员'] == self.__name, :].copy()
        if raw_stats.empty:
            print('No such Player. Please check name entered.')
            exit()
        raw_stats.loc[:, '出场'] = 0
        raw_stats.loc[raw_stats['出场时间'] > 0, '出场'] = 1
        return raw_stats

    @property
    def plr_total_stats(self):
        return self.plr_raw_stats.groupby(['球员', '号码']).sum().reset_index()

    @property
    def plr_avg_stats(self):
        # only calculates appearance
        all_games = self.plr_raw_stats.loc[self.plr_raw_stats['出场'] == 1]
        avg_stats = all_games.groupby(['球员', '号码']).sum().reset_index()
        return avg_stats

    @property
    def tm_raw_stats(self):
        # get game stats using game_ID and team names instead of only team names in case
        # player can be traded in the future
        # use df to filter games
        filter_df = self.plr_raw_stats[['Game_ID','球队']].copy().drop_duplicates()
        raw_stats = self._BBallEntity__raw_stats.copy()
        return raw_stats.merge(filter_df, on=['Game_ID', '球队'])

    @property
    def tm_total_stats(self):
        team_total_stats = self.tm_raw_stats.sum(numeric_only=True)
        return team_total_stats

    @property
    def tm_avg_stats(self):
        return self.tm_total_stats/(self.tm_total_stats['首发']/5)

    @property
    def op_tm_raw_stats(self):
        # get game stats using game_ID and team names instead of only team names in case
        # player can be traded in the future
        # use df to filter games
        filter_df = self.plr_raw_stats[['Game_ID','对手']].copy().drop_duplicates()
        raw_stats = self._BBallEntity__raw_stats.copy()
        return raw_stats.merge(filter_df,left_on=['Game_ID','球队'],right_on=['Game_ID','对手'])

    @property
    def op_tm_total_stats(self):
        team_total_stats = self.op_tm_raw_stats.sum(numeric_only=True)
        return team_total_stats

    @property
    def op_m_avg_stats(self):
        return self.op_tm_total_stats/(self.op_tm_total_stats['首发']/5)


def main():
    player = Player('夏钰博')
    if player.plr_avg_stats.empty:
        print(f'{player.plr_name}无出场数据')
        exit()
    else:
        print(f'{player.plr_name},{player.plr_tm_name}')
        # stats_output(player.tm_total_stats)
        # print(player.tm_avg_stats)
        # print(player.op_m_avg_stats)
        print(player.tm_total_stats)


if __name__ == '__main__':
    main()
