from CBAStats.BBallEntity import *


class Team(BBallEntity):
    def __init__(self, name):
        BBallEntity.__init__(self)
        self.__name = name
        pass

    # -------- universal stats below --------
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

    # -------- universal stats above --------

    # -------- singel stats below --------
    @property
    def tm_fga(self):
        return self.tm_total_stats['2分投'] + self.tm_total_stats['3分投']

    @property
    def tm_fta(self):
        return self.tm_total_stats['罚球投']

    @property
    def tm_mp(self):
        return self.tm_total_stats['出场时间']

    @property
    def tm_orb(self):
        return self.tm_total_stats['进攻篮板']

    @property
    def op_tm_drb(self):
        return self.op_tm_total_stats['防守篮板']

    @property
    def tm_fg(self):
        return self.tm_total_stats['2分中'] + self.tm_total_stats['3分中']

    @property
    def tm_tov(self):
        return self.tm_total_stats['失误']

    @property
    def op_tm_fga(self):
        return self.op_tm_total_stats['2分投'] + self.op_tm_total_stats['3分投']

    @property
    def op_tm_fta(self):
        return self.op_tm_total_stats['罚球投']

    @property
    def tm_drb(self):
        return self.tm_total_stats['防守篮板']

    @property
    def op_tm_fg(self):
        return self.op_tm_total_stats['2分中'] + self.tm_total_stats['3分中']

    @property
    def op_tm_tov(self):
        return self.op_tm_total_stats['失误']

    @property
    def op_tm_orb(self):
        return self.op_tm_total_stats['进攻篮板']

    @property
    def tm_poss(self):
        return 0.5 * (
                (self.tm_fga + 0.4 * self.tm_fta -
                 1.07 * (self.tm_orb / (self.tm_orb + self.op_tm_drb)) * (self.tm_fga - self.tm_fg) +
                 self.tm_tov
                 ) + (
                        self.op_tm_fga +
                        0.4 * self.op_tm_fta -
                        1.07 * (self.op_tm_orb / (self.op_tm_orb + self.tm_drb)) * (self.op_tm_fga - self.op_tm_fg)
                        + self.op_tm_tov)
        )

    @property
    def op_tm_poss(self):
        return 0.5 * (
                (self.op_tm_fga + 0.4 * self.op_tm_fta -
                 1.07 * (self.op_tm_orb / (self.op_tm_orb + self.tm_drb)) * (self.op_tm_fga - self.tm_fg) +
                 self.op_tm_tov
                 ) + (
                        self.tm_fga +
                        0.4 * self.tm_fta -
                        1.07 * (self.tm_orb / (self.tm_orb + self.op_tm_drb)) * (self.tm_fga - self.tm_fg)
                        + self.tm_tov)
        )

    @property
    def tm_pace(self):
        return 48 * ((self.tm_poss + self.op_tm_poss) / (2 * (self.tm_mp / 5)))







def main():
    jilin = Team('广东')
    if jilin.tm_raw_stats.empty:
        print(f'{jilin.tm_name}无数据')
        exit()
    else:
        print(f'{jilin.tm_name}队')
        # stats_output(jilin.op_tm_total_stats)
        print(jilin.tm_poss)
        print(jilin.op_tm_poss)
        print(jilin.tm_pace)


if __name__ == '__main__':
    main()
