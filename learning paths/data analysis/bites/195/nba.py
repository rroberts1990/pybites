from collections import namedtuple
import csv
from pathlib import Path
import sqlite3

import requests

DATA_URL = 'https://query.data.world/s/ezwk64ej624qyverrw6x7od7co7ftm'
TMP = Path('/tmp')
DB = TMP / 'nba.db'

Player = namedtuple('Player', ('name year first_year team college active '
                               'games avg_min avg_points'))

conn = sqlite3.connect(DB)
cur = conn.cursor()


def import_data():
    with requests.Session() as session:
        content = session.get(DATA_URL).content.decode('utf-8')

    reader = csv.DictReader(content.splitlines(), delimiter=',')

    players = []
    for row in reader:
        players.append(Player(name=row['Player'],
                              year=row['Draft_Yr'],
                              first_year=row['first_year'],
                              team=row['Team'],
                              college=row['College'],
                              active=row['Yrs'],
                              games=row['Games'],
                              avg_min=row['Minutes.per.Game'],
                              avg_points=row['Points.per.Game']))

    cur.execute('''CREATE TABLE IF NOT EXISTS players
                  (name, year, first_year, team, college, active,
                  games, avg_min, avg_points)''')
    cur.executemany('INSERT INTO players VALUES (?,?,?,?,?,?,?,?,?)', players)
    conn.commit()


if DB.stat().st_size == 0:
    print('loading data')
    import_data()


# you code:

def player_with_max_points_per_game():
    """The player with highest average points per game (don't forget to CAST to
       numeric in your SQL query)"""
    player = cur.execute('''select name from players 
                            order by cast(avg_points as float) desc limit 1''').fetchone()
    return player[0]


def number_of_players_from_duke():
    """Return the number of players with college == Duke University"""
    count = cur.execute('''select count(*) from players where college = 'Duke University' ''').fetchone()
    return count[0]


def avg_years_active_players_stanford():
    """Return the average years that players from "Stanford University
       are active ("active" column)"""
    active = cur.execute('''select avg(active) from players where college = 'Stanford University' ''').fetchone()
    return active[0]

def year_with_most_drafts():
    """Return the year with the most drafts, in SQL you can use GROUP BY"""
    year = cur.execute('''select year, count(*) from players 
    group by year order by count(*) desc limit 1 ''').fetchone()
    return year[0]
