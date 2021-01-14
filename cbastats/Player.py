# from GameStats import *
# from Team import *
from cbastats.GameStats import *
from cbastats.Team import *
# todo: develop op_plr (player same position, watch there will be starter and sub)


class Player(GameStats):
    def __init__(self, name,df):
        GameStats.__init__(self,df)
        self.__name = name
        pass

    @property
    def plr_name(self):
        if self.__name:
            return self.plr_raw_stats['球员'].unique()[0]
        else:
            return '所有球员'

    @property
    def plr_tm_name(self):
        # used a list in case in the future player can be traded during season
        return self.plr_raw_stats['球队'].unique().tolist()

    # -------- universal stats below (all are pd.DataFrame)--------

    @property
    def plr_raw_stats(self):
        """
        球员的每场比赛数据统计；一场比赛对应一行数据。
        """
        raw_stats = self.all_games_stats
        if self.__name:
            raw_stats = raw_stats.loc[raw_stats['球员'] == self.__name, :].copy()
        else:
            pass
        if raw_stats.empty:
            print('No such Player. Please check name entered.')
            exit()
        raw_stats.loc[:, '出场'] = 0
        raw_stats.loc[raw_stats['出场时间'] > 0, '出场'] = 1
        return raw_stats

    @property
    def tm_raw_stats(self):
        """
        本方球队和对方球队每场数据统计；一场比赛对应一行数据。
        """
        raw_stats = self.all_games_stats
        raw_stats = raw_stats.groupby(['GameID_Sina', '球队', '对手']).sum().reset_index()
        raw_stats['场次'] = raw_stats['首发'] / 5
        raw_stats.drop(columns=['首发'], inplace=True)
        temp = raw_stats.add_prefix('对方')
        raw_stats = raw_stats.add_prefix('本方')
        merged_tm_raw_stats = pd.merge(raw_stats, temp, left_on=['本方GameID_Sina', '本方球队'], right_on=
        ['对方GameID_Sina', '对方对手'])

        if merged_tm_raw_stats.empty:
            print('No data. Please check name entered.')
            exit()
        return merged_tm_raw_stats

    @property
    def raw_stats(self):
        """
        球员，本方球队，对方球队的单场比赛统计；一场比赛对应一行数据。
        注意: 这里的"本方球队"是一个抽象概念，一如"对方球队"是所有比赛中对方球队数据的集合。
        截止2020年1月为止，赛季中球员并不会交易，所以可以狭义得理解为他的主队。
        """
        raw_stats = pd.merge(self.plr_raw_stats, self.tm_raw_stats, left_on=['GameID_Sina', '球队']
                             , right_on=['本方GameID_Sina', '本方球队'])
        return raw_stats
#######################################################################################################
    @property
    def plr_total_stats(self):
        """球员总数据统计，每个球员对应一行数据"""
        return self.plr_raw_stats.groupby(['球员','球队']).sum(numeric_only=True)

    @property
    def plr_avg_stats(self):
        """球员每场平均数据，每个球员对应一行数据"""
        return self.plr_total_stats.div(self.plr_total_stats['出场'], axis=0)

    @property
    def total_stats(self):
        """
        球员，本方球队，对方球队的总数据统计；一位球员对应一行数据。
        注意: 这里的"本方球队"是一个抽象概念，一如"对方球队"是所有比赛中对方球队数据的集合。
        截止2020年1月为止，赛季中球员并不会交易，所以可以狭义得理解为他的主队。
        """
        total_stats = self.raw_stats.groupby(['球员']).sum()
        return total_stats

    # -------- universal stats above (all are pandas dataframes)--------

    # -------- simple stats below (all are pd.series)--------

    @property
    def tm_pts(self):
        return self.total_stats['本方得分']

    @property
    def tm_fga(self):
        return self.total_stats['本方2分投'] + self.total_stats['本方3分投']

    @property
    def tm_fta(self):
        return self.total_stats['本方罚球投']

    @property
    def tm_mp(self):
        return self.total_stats['本方出场时间']

    @property
    def tm_orb(self):
        return self.total_stats['本方进攻篮板']

    @property
    def op_tm_drb(self):
        return self.total_stats['对方防守篮板']

    @property
    def tm_fg(self):
        return self.total_stats['本方2分中'] + self.total_stats['本方3分中']

    @property
    def tm_tov(self):
        return self.total_stats['本方失误']

    @property
    def op_tm_fga(self):
        return self.total_stats['对方2分投'] + self.total_stats['对方3分投']

    @property
    def op_tm_fta(self):
        return self.total_stats['对方罚球投']

    @property
    def tm_drb(self):
        return self.total_stats['本方防守篮板']

    @property
    def op_tm_fg(self):
        return self.total_stats['对方2分中'] + self.total_stats['对方3分中']

    @property
    def op_tm_tov(self):
        return self.total_stats['对方失误']

    @property
    def op_tm_orb(self):
        return self.total_stats['对方进攻篮板']

    @property
    def op_tm_pts(self):
        return self.total_stats['对方得分']

    @property
    def plr_fgm(self):
        return self.total_stats['2分中'] + self.total_stats['3分中']

    @property
    def plr_pts(self):
        return self.total_stats['得分']

    @property
    def plr_ftm(self):
        return self.total_stats['罚球中']

    @property
    def plr_fga(self):
        return self.total_stats['2分投'] + self.total_stats['3分投']

    @property
    def plr_mp(self):
        return self.total_stats['出场时间']

    @property
    def tm_ast(self):
        return self.total_stats['本方助攻']

    @property
    def plr_ast(self):
        return self.total_stats['助攻']

    @property
    def tm_fgm(self):
        return self.total_stats['本方2分中'] + self.total_stats['本方3分中']

    @property
    def tm_ftm(self):
        return self.total_stats['本方罚球中']

    @property
    def plr_fta(self):
        return self.total_stats['罚球投']

    @property
    def tm_trb(self):
        return self.total_stats['本方进攻篮板'] + self.total_stats['本方防守篮板']

    @property
    def op_tm_trb(self):
        return self.total_stats['对方进攻篮板'] + self.total_stats['对方防守篮板']

    @property
    def plr_trb(self):
        return self.total_stats['进攻篮板'] + self.total_stats['防守篮板']

    @property
    def plr_orb(self):
        return self.total_stats['进攻篮板']

    @property
    def plr_tov(self):
        return self.total_stats['失误']

    @property
    def plr_3pm(self):
        return self.total_stats['3分中']

    @property
    def tm_3pm(self):
        return self.total_stats['本方3分中']

    @property
    def plr_stl(self):
        return self.total_stats['抢断']

    @property
    def plr_blk(self):
        return self.total_stats['盖帽']

    @property
    def tm_stl(self):
        return self.total_stats['本方抢断']

    @property
    def tm_blk(self):
        return self.total_stats['本方盖帽']

    @property
    def op_tm_fgm(self):
        return self.total_stats['对方2分中'] + self.total_stats['对方3分中']

    @property
    def plr_pf(self):
        return self.total_stats['犯规']

    @property
    def tm_pf(self):
        return self.total_stats['本方犯规']

    @property
    def op_tm_pf(self):
        return self.total_stats['对方犯规']

    @property
    def op_tm_ftm(self):
        return self.total_stats['对方罚球中']

    @property
    def op_tm_mp(self):
        return self.total_stats['对方出场时间']

    @property
    def tm_ngames(self):
        return self.total_stats['本方场次']

    @property
    def plr_drb(self):
        return self.total_stats['防守篮板']

    # -------- simple stats above (all are pd.series)--------

    # -------- advanced stats below (all are pd.series)--------
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
        return self.tm_poss / self.tm_ngames

    @property
    def tm_pace(self):
        return 48 * ((self.tm_poss + self.op_tm_poss) / (2 * (self.tm_mp / 5)))

    @property
    def tm_ortg(self):
        return self.tm_pts / self.tm_poss * 100

    @property
    def tm_drtg(self):
        return self.op_tm_pts / self.op_tm_poss * 100

    @property
    def tm_nrtg(self):
        return self.tm_ortg - self.tm_drtg

    @property
    def plr_qast(self):
        """
        qAst: The percentage of a player's FG that are assisted, as estimated by his assist rate
        and eFG%, among other stats.
        """
        return (
                       (self.plr_mp / (self.tm_mp / 5)) *
                       (1.14 * ((self.tm_ast - self.plr_ast) / self.tm_fgm))
               ) + (
                       (
                               ((self.tm_ast / self.tm_mp) * self.plr_mp * 5 - self.plr_ast) /
                               ((self.tm_fgm / self.tm_mp) * self.plr_mp * 5 - self.plr_fgm)
                       ) *
                       (1 - (self.plr_mp / (self.tm_mp / 5)))
               )

    @property
    def tm_orb_perc(self):
        return self.tm_orb / (self.tm_orb + (self.op_tm_trb - self.op_tm_orb))

    @property
    def tm_scposs(self):
        """
        team scoring possession
        """
        return self.tm_fgm + (1 - (1 - (self.tm_ftm / self.tm_fta)) ** 2) * self.tm_fta * 0.4

    @property
    def tm_play_perc(self):
        return self.tm_scposs / (self.tm_fga + self.tm_fta * 0.4 + self.tm_tov)

    @property
    def tm_orb_weight(self):
        Team_ORB_perc = self.tm_orb_perc
        Team_Play_perc = self.tm_play_perc
        return ((1 - Team_ORB_perc) * Team_Play_perc) / \
               ((1 - Team_ORB_perc) * Team_Play_perc + Team_ORB_perc * (1 - Team_Play_perc))

    @property
    def plr_scposs(self):
        FG_Part = self.plr_fgm * (1 - 0.5 * ((self.plr_pts - self.plr_ftm) / (2 * self.plr_fga)) * self.plr_qast)
        AST_Part = 0.5 * (((self.tm_pts - self.tm_ftm) - (self.plr_pts - self.plr_ftm))
                          / (2 * (self.tm_fga - self.plr_fga))) * self.plr_ast
        FT_Part = (1 - (1 - (self.plr_ftm / self.plr_fta)) ** 2) * 0.4 * self.plr_fta

        Team_ORB = self.tm_orb
        Team_Scoring_Poss = self.tm_scposs
        Team_ORB_perc = self.tm_orb_perc
        Team_Play_perc = self.tm_play_perc
        Team_ORB_Weight = self.tm_orb_weight
        ORB_Part = self.plr_orb * Team_ORB_Weight * Team_Play_perc
        return (FG_Part + AST_Part + FT_Part) * (1 - (Team_ORB / Team_Scoring_Poss) *
                                                 Team_ORB_Weight * Team_Play_perc) + ORB_Part

    @property
    def plr_totposs(self):
        """
        TotPoss = ScPoss + FGxPoss + FTxPoss + TOV
        Where:
            ScPoss = (FG_Part + AST_Part + FT_Part) *
                (1 - (Team_ORB / Team_Scoring_Poss) * Team_ORB_Weight * Team_Play%) + ORB_Part
            FGxPoss = (FGA - FGM) * (1 - 1.07 * Team_ORB%)
            FTxPoss = ((1 - (FTM / FTA))^2) * 0.4 * FTA
            TOV = Turnovers
        """
        ScPoss = self.plr_scposs

        FGxPoss = (self.plr_fga - self.plr_fgm) * (1 - 1.07 * self.tm_orb_perc)

        FTxPoss = ((1 - (self.plr_ftm / self.plr_fta)) ** 2) * 0.4 * self.plr_fta

        TOV = self.plr_tov

        return ScPoss + FGxPoss + FTxPoss + TOV

    @property
    def plr_pprod(self):
        """
        points produced
        PProd = (PProd_FG_Part + PProd_AST_Part + FTM) *
            (1 - (Team_ORB / Team_Scoring_Poss) * Team_ORB_Weight * Team_Play%) +
            PProd_ORB_Part
        """
        PProd_FG_Part = 2 * (self.plr_fgm + 0.5 * self.plr_3pm) * \
                        (1 - 0.5 * ((self.plr_pts - self.plr_ftm) / (2 * self.plr_fga)) * self.plr_qast)
        PProd_AST_Part = 2 * (
                (self.tm_fgm - self.plr_fgm + 0.5 * (self.tm_3pm - self.plr_3pm)) / (self.tm_fga - self.plr_fgm)) * \
                         0.5 * (
                                 ((self.tm_pts - self.tm_ftm) - (self.plr_pts - self.plr_ftm)) /
                                 (2 * (self.tm_fga - self.plr_fga))
                         ) * self.plr_ast
        PProd_ORB_Part = self.plr_orb * self.tm_orb_weight * self.tm_play_perc * \
                         (self.tm_pts / (
                                     self.tm_fgm + (1 - (1 - (self.tm_ftm / self.tm_fta)) ** 2) * 0.4 * self.tm_fta))
        return (PProd_FG_Part + PProd_AST_Part + self.plr_ftm) * \
               (1 - (self.tm_orb / self.tm_scposs) * self.tm_orb_weight * self.tm_play_perc) + PProd_ORB_Part

    @property
    def plr_ortg(self):
        """
        individual offensive rating is the number of points produced by a player
        per hundred total individual possessions
        """
        return 100 * (self.plr_pprod / self.plr_totposs)

    @property
    def plr_floor_perc(self):
        return self.plr_scposs / self.plr_totposs

    @property
    def plr_drtg(self):
        """
        Defensive Rating estimates how many points the player allowed per 100 possessions
        he individually faced while on the court
        The core of the Defensive Rating calculation is the concept of the individual Defensive Stop
        """
        DFG_perc = self.op_tm_fga / self.op_tm_fga
        DOR_perc = self.op_tm_orb / (self.op_tm_orb + self.tm_orb)

        FMwt = (DFG_perc * (1 - DOR_perc)) / (DFG_perc * (1 - DOR_perc) + (1 - DFG_perc) * DOR_perc)
        Stops1 = self.plr_stl + self.plr_blk * FMwt * (1 - 1.07 * DOR_perc) + self.plr_drb * (1 - FMwt)
        Stops2 = (((self.op_tm_fga - self.op_tm_fgm - self.tm_blk) / self.tm_mp) * FMwt * (1 - 1.07 * DOR_perc) + (
                    (self.op_tm_tov - self.tm_stl) / self.tm_mp)) * self.plr_mp + (
                             self.plr_pf / self.tm_pf) * 0.4 * self.op_tm_fta * (
                             1 - (self.op_tm_ftm / self.op_tm_fta)) ** 2
        Stops = Stops1 + Stops2
        Stop_perc = (Stops * self.op_tm_mp) / (self.tm_poss * self.plr_mp)
        Team_Defensive_Rating = self.tm_drtg
        D_Pts_per_ScPoss = self.op_tm_pts / (
                    self.op_tm_fgm + (1 - (1 - (self.op_tm_ftm / self.op_tm_fta)) ** 2) * self.op_tm_fta * 0.4)
        return Team_Defensive_Rating + 0.2 * (100 * D_Pts_per_ScPoss * (1 - Stop_perc) - Team_Defensive_Rating)

    @property
    def plr_nrtg(self):
        return self.plr_ortg-self.plr_drtg
    
    @property
    def plr_usg(self):
        """
        Usage percentage is an estimate of the percentage of team plays used by a player while he was on the floor
        """
        return 100 * ((self.plr_fga + 0.44 * self.plr_fta + self.plr_tov) * (self.tm_mp / 5)) / (self.plr_mp * (self.tm_fga + 0.44 * self.tm_fta + self.tm_tov))

    

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
    player = Player('',df)
    teams = Team('',df)
    
    if player.plr_avg_stats.empty:
        print(f'{player.plr_name}无出场数据')
        exit()
    else:
        league_pts = sum(teams.tm_pts)
        league_poss = sum(teams.tm_poss)
        league_pts_poss = league_pts/league_poss
        plr_marg_offense = player.plr_pprod-0.92*league_pts_poss*player.plr_scposs
        league_pace = teams.tm_pace.mean()
        league_avg_pts = sum(teams.tm_pts)/sum(teams.tm_ngames)
        plr_marg_pts_win = 0.32*league_avg_pts*(player.tm_pace/league_pace)
        plr_oWinShare = plr_marg_offense/plr_marg_pts_win
        
        # offensive win share
        # print(f'{player.plr_name},{player.plr_tm_name}')
        # print(f"marginal offense is {plr_marg_offense}")
        # print(f"marginal points per win is {plr_marg_pts_win}")
        # print(f"offensive win share is {plr_oWinShare}")


        # defensive win share
        player.plr_drtg
        plr_marg_defense = (player.plr_mp/player.tm_mp)*player.tm_def_poss*(1.08*(league_pts_poss)-((player.plr_drtg)/100))
        # print(f"marginal defense is {plr_marg_defense}")
        plr_dWinShare = plr_marg_defense/plr_marg_pts_win
        # print(f"defensive win share is {plr_dWinShare}")

        plr_WinShare = plr_dWinShare + plr_oWinShare
        plr_WinShare_df = pd.DataFrame(plr_WinShare)
        
        plr_WinShare_df.to_csv('data/WinShare.csv')
        print(plr_WinShare)



if __name__ == '__main__':
    main()
