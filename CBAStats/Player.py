from CBAStats.GameStats import *


# todo: develop op_plr (player same position, watch there will be starter and sub)


class Player(GameStats):
    def __init__(self, name):
        GameStats.__init__(self)
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
        raw_stats = GameStats().all_games_stats
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
        raw_stats = GameStats().all_games_stats
        raw_stats = raw_stats.groupby(['Game_ID', '球队','对手']).sum().reset_index()
        raw_stats['场次'] = raw_stats['首发']/5
        raw_stats.drop(columns=['首发'],inplace=True)
        temp = raw_stats.add_prefix('对方')
        raw_stats = raw_stats.add_prefix('本方')
        merged_tm_raw_stats = pd.merge(raw_stats,temp,left_on=['本方Game_ID','本方球队'],right_on=
                                ['对方Game_ID','对方对手'])

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
        raw_stats = pd.merge(self.plr_raw_stats,self.tm_raw_stats,left_on=['Game_ID','球队']
                             ,right_on=['本方Game_ID','本方球队'])
        return raw_stats

    @property
    def plr_total_stats(self):
        """球员总数据统计，每个球员对应一行数据"""
        return self.plr_raw_stats.groupby('球员').sum()

    @property
    def plr_avg_stats(self):
        """球员每场平均数据，每个球员对应一行数据"""
        return self.plr_total_stats.div(self.plr_total_stats['出场'],axis=0)

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
        return self.total_stats['本方进攻篮板']+self.total_stats['本方防守篮板']

    @property
    def op_tm_trb(self):
        return self.total_stats['对方进攻篮板']+self.total_stats['对方防守篮板']

    @property
    def plr_orb(self):
        return self.total_stats['进攻篮板']

    @property
    def plr_tov(self):
        return self.total_stats['失误']

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
    def plr_qast(self):
        """
        qAst: The percentage of a player's FG that are assisted, as estimated by his assist rate
        and eFG%, among other stats.
        """
        return (
                       (self.plr_mp / (self.tm_mp.values / 5)) *
                       (1.14 * ((self.tm_ast.values - self.plr_ast) / self.tm_fgm.values))
               ) + (
                       (
                               ((self.tm_ast.values / self.tm_mp.values) * self.plr_mp * 5 - self.plr_ast) /
                               ((self.tm_fgm.values / self.tm_mp.values) * self.plr_mp * 5 - self.plr_fgm)
                       ) *
                       (1 - (self.plr_mp / (self.tm_mp.values / 5)))
               )

    @property
    def tm_scposs(self):
        return self.tm_fgm + (1 - (1 - (self.tm_ftm / self.tm_fta))**2) * self.tm_fta * 0.4

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
        FG_Part = self.plr_fgm*(1-0.5*(self.plr_pts-self.plr_ftm)/(2*self.plr_fga))*self.plr_qast
        AST_Part = 0.5 * (((self.tm_pts - self.tm_ftm)-(self.plr_pts - self.plr_ftm))
                                     / (2 * (self.tm_fga - self.plr_fga))) * self.plr_ast
        FT_Part = (1-(1-(self.plr_ftm/self.plr_fta))**2)*0.4*self.plr_fta
        Team_ORB = self.tm_orb
        Team_Scoring_Poss = self.tm_scposs
        Team_ORB_perc = self.tm_orb / (self.tm_orb + (self.op_tm_trb - self.op_tm_orb))
        Team_Play_perc = Team_Scoring_Poss / (self.tm_fga + self.tm_fta * 0.4 + self.tm_tov)
        Team_ORB_Weight = ((1 - Team_ORB_perc) * Team_Play_perc) / \
                          ((1 - Team_ORB_perc) * Team_Play_perc + Team_ORB_perc * (1 - Team_Play_perc))
        ORB_Part = self.plr_orb*Team_ORB_Weight*Team_Play_perc
        ScPoss = (FG_Part + AST_Part + FT_Part) * (1 - (Team_ORB / Team_Scoring_Poss)
                                                   * Team_ORB_Weight * Team_Play_perc)\
                 + ORB_Part

        FGxPoss = (self.plr_fga - self.plr_fgm) * (1 - 1.07 * Team_ORB_perc)

        FTxPoss = ((1 - (self.plr_ftm / self.plr_fta)) ** 2) * 0.4 * self.plr_fta
        TOV = self.plr_tov
        return ScPoss + FGxPoss + FTxPoss + TOV

    @property
    def plr_ortg(self):
        """
        individual offensive rating is the number of points produced by a player
        per hundred total individual possessions
        """
        return ''
    # -------- advanced stats above (all are pd.series)--------


def main():
    player = Player('易建联')
    if player.plr_avg_stats.empty:
        print(f'{player.plr_name}无出场数据')
        exit()
    else:
        print(f'{player.plr_name},{player.plr_tm_name}')
        stats_output(player.plr_total_stats)
        stats_output(player.plr_avg_stats)


if __name__ == '__main__':
    main()
