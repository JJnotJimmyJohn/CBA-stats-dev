from CBAStats.BBallEntity import *


class Team(BBallEntity):
    def __init__(self, name):
        BBallEntity.__init__(self)
        self.__name = name
        pass

    @property
    def tm_name(self):
        return self.tm_raw_stats['球队'].unique()[0]

    @property
    def tm_raw_stats(self):
        raw_stats = self._BBallEntity__raw_stats.loc[self._BBallEntity__raw_stats['球队'] == self.__name, :].copy()
        if raw_stats.empty:
            print('No such team. Please check name entered.')
            exit()
        return raw_stats

    @property
    def tm_total_stats(self):
        return self.tm_raw_stats.sum(numeric_only=True)

    @property
    def tm_avg_stats(self):
        return self.tm_total_stats / (self.tm_total_stats['首发'] / 5)

    @property
    def op_tm_raw_stats(self):
        # get game stats using game_ID and team names instead of only team names in case
        # player can be traded in the future
        # use df to filter games
        filter_df = self.tm_raw_stats[['Game_ID', '对手']].copy().drop_duplicates()
        raw_stats = self._BBallEntity__raw_stats.copy()
        return raw_stats.merge(filter_df, left_on=['Game_ID', '球队'], right_on=['Game_ID', '对手'])

    @property
    def op_tm_total_stats(self):
        op_tm_total_stats = self.op_tm_raw_stats.sum(numeric_only=True)
        return op_tm_total_stats

    @property
    def op_tm_avg_stats(self):
        return self.op_tm_total_stats / (self.op_tm_total_stats['首发'] / 5)


def main():
    jilin = Team('吉林')
    if jilin.tm_raw_stats.empty:
        print(f'{jilin.tm_name}无数据')
        exit()
    else:
        print(f'{jilin.tm_name}队')
        print(jilin.op_tm_total_stats)
        print(jilin.op_tm_avg_stats)


if __name__ == '__main__':
    main()
