# from GameStats import *
from cbastats.GameStats import *
from sys import exit
import pandas as pd


class Team(GameStats):
    def __init__(self, name, df):
        GameStats.__init__(self,df)
        self.__name = name
        pass

    # -------- universal stats below (all are pd.DataFrame)--------
    @property
    def tm_name(self):
        if self.__name:
            return self.tm_raw_stats['球队'].unique()[0]
        else:
            return '所有队伍'

    @property
    def tm_raw_stats(self):
        # raw_stats = self._GameStats__raw_stats.copy()
        raw_stats = self.all_games_stats
        teams = raw_stats.groupby(['球队', 'GameID_Sina']).sum().rename(columns={'首发': '场次'})
        teams['场次'] = teams['场次'] / 5
        teams = teams.reset_index()

        oppteams = raw_stats.groupby(['对手', 'GameID_Sina']).sum().rename(columns={'首发': '场次'})
        oppteams['场次'] = oppteams['场次'] / 5
        oppteams = oppteams.add_prefix('对方')
        oppteams = oppteams.reset_index()

        merged_stats = pd.merge(teams, oppteams, left_on=['球队', 'GameID_Sina'], right_on=['对手', 'GameID_Sina'])
        merged_stats = merged_stats.set_index('球队')
        if self.__name:
            merged_stats = merged_stats.loc[self.__name].copy()
        else:
            pass
        assert not merged_stats.empty,'No data. Please check name entered.'
            # print('No data. Please check name entered.')
            # exit()
        return merged_stats

    @property
    def tm_total_stats(self):
        raw_stats = self.tm_raw_stats.groupby(['球队']).sum()
        return raw_stats

    @property
    def tm_avg_stats(self):
        return self.tm_total_stats.div(self.tm_total_stats['场次'],axis=0)
    # -------- universal stats above --------

    # -------- singel stats below (all are pd.series)--------
    @property
    def tm_ngames(self):
        return self.tm_total_stats['场次']

    @property
    def tm_pts(self):
        return self.tm_total_stats['得分']

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
        return self.tm_total_stats['对方防守篮板']

    @property
    def tm_fg(self):
        return self.tm_total_stats['2分中'] + self.tm_total_stats['3分中']

    @property
    def tm_tov(self):
        return self.tm_total_stats['失误']

    @property
    def op_tm_fga(self):
        return self.tm_total_stats['对方2分投'] + self.tm_total_stats['对方3分投']

    @property
    def op_tm_fta(self):
        return self.tm_total_stats['对方罚球投']

    @property
    def tm_drb(self):
        return self.tm_total_stats['防守篮板']

    @property
    def op_tm_fg(self):
        return self.tm_total_stats['对方2分中'] + self.tm_total_stats['对方3分中']

    @property
    def op_tm_tov(self):
        return self.tm_total_stats['对方失误']

    @property
    def op_tm_orb(self):
        return self.tm_total_stats['对方进攻篮板']

    @property
    def op_tm_pts(self):
        return self.tm_total_stats['对方得分']

    # -------- single stats above (all are pd.series)--------

    # -------- advanced stats below (all are pd.series)--------
    @property
    def mov(self):
        return (self.tm_pts-self.op_tm_pts)/self.tm_ngames

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
    def tm_def_poss(self):
        return 1 * (0 + (
                        self.op_tm_fga +
                        0.4 * self.op_tm_fta -
                        1.07 * (self.op_tm_orb / (self.op_tm_orb + self.tm_drb)) * (self.op_tm_fga - self.op_tm_fg)
                        + self.op_tm_tov)
        )

    @property
    def op_tm_poss(self):
        return 0.5 * (
                (self.op_tm_fga + 0.4 * self.op_tm_fta -
                 1.07 * (self.op_tm_orb / (self.op_tm_orb + self.tm_drb)) * (self.op_tm_fga - self.op_tm_fg) +
                 self.op_tm_tov
                 ) + (
                        self.tm_fga +
                        0.4 * self.tm_fta -
                        1.07 * (self.tm_orb / (self.tm_orb + self.op_tm_drb)) * (self.tm_fga - self.tm_fg)
                        + self.tm_tov)
        )

    @property
    def tm_poss_per_g(self):
        return self.tm_poss/self.tm_ngames

    @property
    def tm_pace(self):
        return 48 * ((self.tm_poss + self.op_tm_poss) / (2 * (self.tm_mp / 5)))

    @property
    def tm_ortg(self):
        return self.tm_pts/self.tm_poss*100

    @property
    def tm_drtg(self):
        return self.op_tm_pts/self.op_tm_poss*100

    @property
    def tm_nrtg(self):
        return (self.tm_ortg-self.tm_drtg)

    # -------- advanced stats above (all are pd.series)--------

def main():
    import pandas as pd
    from sqlalchemy import create_engine

    user_name = 'guest'
    passcode = 'Guest123456'
    endpoint = 'cbashuju.ctkaehd5rxxe.us-east-1.rds.amazonaws.com'
    database = 'CBA_Data'
    engine = create_engine(f'mysql+pymysql://{user_name}:{passcode}@{endpoint}/{database}')

    connection= engine.connect()
    df = pd.read_sql("select * from CBA_Data.PlayerStatsPerGame", connection)
    connection.close()
    teams = Team('',df)
    print(teams.tm_pts)
    print(teams.tm_poss)


if __name__ == '__main__':
    main()
