from CBAStats.Player import *
from CBAStats.Team import *
from CBAStats.Player import stats_output
from pprint import pprint

df = BBallEntity()
stats_output(df.all_games_stats)

# yijianlian = Player('易建联')
# stats_output(yijianlian.plr_raw_stats)
#
# jilin = Team('吉林')
# print(jilin.tm_name)
# stats_output(jilin.tm_total_stats)

