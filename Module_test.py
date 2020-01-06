from CBAStats.Player import *
from CBAStats.Team import *
from CBAStats.Player import stats_output
import datetime

# yijianlian = Player('易建联')
# stats_output(yijianlian.plr_total_stats)

teams = Team('')
# stats_output(teams.tm_pace)
# stats_output(teams.tm_poss_per_g)
# stats_output(teams.tm_ortg)
# stats_output(teams.tm_drtg)
# stats_output(teams.tm_nrtg)
# stats_output(teams.mov)


df = pd.concat([teams.mov, teams.tm_pace, teams.tm_ortg, teams.tm_drtg, teams.tm_nrtg], axis=1)
df.columns=['场均净胜分MOV', 'Pace', 'OffensiveRating', 'DefensiveRating', 'NetRating']
df = df.sort_values(by='NetRating',ascending=False)
stats_output(df.head())
df.to_csv(f'~/Documents/CBA_Stats/StatsData/team_rating_{datetime.date.today()}.csv',float_format='%.1f')