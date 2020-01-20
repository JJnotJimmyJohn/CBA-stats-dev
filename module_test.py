from CBAStats.Player import *
from CBAStats.Team import *
from CBAStats.GameStats import stats_output
from CBAStats.GameStats import GameStats
import datetime

stats = GameStats.from_csv('StatsData/All_Games_Stats_2020-01-17.csv')
# print(stats.head())
#
# stats1 = GameStats(stats.all_games_stats)
# print(stats1.head())

# stats2 = Team.from_csv('StatsData/All_Games_Stats_2020-01-17.csv')
# print(stats2.head())

# stats3 = Team('',stats.all_games_stats)
# print(stats3)

stats4 = Player('易建联', stats.all_games_stats)
print(stats4.plr_total_stats)

# change .all_games_stats to .df


# yijianlian = Player('易建联')
# stats_output(yijianlian.plr_raw_stats.head())
# stats_output(yijianlian.plr_total_stats.head())
# stats_output(yijianlian.plr_avg_stats.head())
# print(yijianlian.plr_total_stats)
# print('')
# print(yijianlian.tm_total_stats)
# print((yijianlian.plr_fgm))
# print(yijianlian.tm_total_stats)
# print(yijianlian.tm_mp)
# print((yijianlian.plr_qast))

# players = Player('蒋浩然')
# print(players.plr_raw_stats)
# print(players.plr_ortg)
# print(players.plr_qast)
# print(players.tm_poss)
# print(players.total_stats)
# print(players.plr_totposs)
# print(players.plr_pprod)
# print(players.plr_ortg)
# players_ortg = players.plr_ortg
# ortg_df = pd.DataFrame(players_ortg,columns=['OffensiveRating'])
# ortg_df.sort_values(by='OffensiveRating').to_html('PlayersOrtg.html')
# print((players.plr_mp / (players.tm_mp / 5)))

# guangdong = Team('广东')
# print(guangdong.tm_poss)

# rawstats = GameStats().all_games_stats
# print(len(rawstats.loc[rawstats['球队']=='广东',]))
# teams = Team('')
# stats_output(teams.tm_pace)
# stats_output(teams.tm_poss_per_g)
# stats_output(guangdong.tm_ortg)
# stats_output(guangdong.tm_drtg)
# stats_output(teams.tm_nrtg)
# stats_output(teams.mov)


# df = pd.concat([teams.mov, teams.tm_pace, teams.tm_ortg, teams.tm_drtg, teams.tm_nrtg], axis=1)
# df.columns=['场均净胜分MOV', 'Pace', 'OffensiveRating', 'DefensiveRating', 'NetRating']
# df = df.sort_values(by='NetRating',ascending=False)
# stats_output(df.head())
# # df.to_csv(f'~/Documents/CBA_Stats/StatsData/team_rating_{datetime.date.today()}.csv',float_format='%.1f')
# df.to_html('test.html')
#
# from Scraping import Scraper
#
# Scraper.scrape_sina_schedule(output_path=r'StatsData/schedule_data.csv')
# Scraper.scrape_game_details(input_file=r'StatsData/schedule_data.csv',output_file=r'StatsData/All_games_data.csv')
