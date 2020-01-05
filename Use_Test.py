from CBAStats.Player import *
from CBAStats.Team import *
from CBAStats.Player import stats_output
from pprint import pprint


yijianlian = Player('易建联')
stats_output(yijianlian.plr_avg_stats)

jilin = Team('吉林')
print(jilin.tm_name)
pprint(jilin.tm_total_stats)

