import requests
# from bs4 import BeautifulSoup
import lxml.html as lh
import pandas as pd
import datetime

header = {'User-Agent': r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                        r'Chrome/41.0.2227.1 Safari/537.36'}
session = requests.Session()
base_url = r"http://cba.sports.sina.com.cn/cba/stats/playerstats/"
response = session.get(base_url, headers=header)

response.encoding = 'GBK'

doc = lh.fromstring(response.content)

rows = doc.xpath('//tr')

table_headers = [t.text_content() for t in rows[0]]
print(table_headers)

print(len(rows))

i = 0
table = []
#
for row in rows:
    one_row = []
    for cell in row:
        txt = cell.text_content().strip()
        one_row.append(txt)
    table.append(one_row)

len(table)

player_stats_sina = pd.DataFrame(table[1:], columns=table[0])

player_stats_sina.rename(columns={"号码": '排名'}, inplace=True)

print(datetime.date.today())

player_stats_sina.to_csv(f'Player_Stats_{datetime.date.today()}.csv', index=False)
