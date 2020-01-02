# CBA-stats

This is a project to generate advanced stats using scraped CBA stats from Sina.com, Sohu.com.

## root directory
All the working files and place holders are in root directory

### All_Game_Stats_Processing.ipynb
Notebook to process scraped detailed stats for each game. Can get teams, opponents, players stats.
Todo:
* Get player ID, player position (consider minutes played)

### RatingTest_GeorgeHill.ipynb
Notebook to test calculation of George Hill's offensive rating

### CBA_data_scrape.ipynb
Draft file to scrape detailed game stats out of Sina.com

### Rating_test.py
Place holder to refactor notebook into .py file

### Sina_Scrape.py
Place holder to refactor notebook into .py file

---

## "StatsData" folder
folder to store data

### GamesSchedulePage_2019-12-28.csv
Data scraped from http://cba.sports.sina.com.cn/cba/schedule/all/?qleagueid=205&qmonth=&qteamid= on 20191228
Containing schedule info and links to games' detailed stats

### GeorgeHill_testdata_20191225.csv
GeorgeHill's stats until 20191224. Used to validate my calculation of offensive rating

### MIL_stats.csv
Bucks stats until 20191224. Used to validate my calculation of offensive rating

### Opponent_stats.csv	
Buck opponents stats until 20191224. Used to validate my calculation of offensive rating

### Player_Stats_2019-12-24.csv	
All CBA player stats scraped on 20191224

### Player_Stats_2019-12-25.csv
All CBA player stats scraped on 20191225

---

## "Archive" folder
Archive folder to store past files

### Do not use below files - Sohu stats are not as complete as Sina

* zzDoNotUSe_Sohu_Scrape.py
* zzDoNotUSe_Sohu_automatically_get_all_rounds.ipynb
* zzDoNotUse_Sohu_get_all_data_v1.ipynb
