import requests
from bs4 import BeautifulSoup
import json
import sqlite3

CACHE_FNAME = 'basketball.json'
DBNAME = 'basketball.db'

try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

def get_unique_key(url):
    return url

def make_requests_using_cache(url):
    unique_ident = get_unique_key(url)

    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

class BasketballPlayers:
    def __init__(self, name, start_year, end_year, position, height, weight):
        self.name = name
        self.startyear = start_year
        self.endyear = end_year
        self.position = position
        self.height = height
        self.weight = weight

    def init_from_details_url(self, details_url):
        page_text = make_requests_using_cache(details_url)
        page_soup = BeautifulSoup(page_text, 'html.parser')

        stats = []
        stats_div = page_soup.find(class_ = 'p1')
        stats_num = stats_div.find_all('p')
        for item in stats_num:
            get_stats = item.text.strip()
            stats.append(get_stats)

        career_games = stats[1]
        career_points = stats[3]
        career_rebounds = stats[5]
        career_assists = stats[7]

        self.gamesplayed = career_games
        self.totalpoints = career_points
        self.totalrebounds = career_rebounds
        self.totalassists = career_assists



    def __str__(self):
        return self.name + ' Career Began: ' + self.startyear + ' Career Ended: ' + self.endyear + ' Position: ' \
                + self.position + ' Height: ' + self.height + ' Weight: ' \
                + self.weight + ' Career Points:  ' + self.totalpoints

    def __repr__(self):
        return self.__str__()



def init_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
        DROP TABLE IF EXISTS 'Players';
    '''
    cur.execute(statement)
    statement = '''
        DROP TABLE IF EXISTS 'Stats';
    '''
    cur.execute(statement)

    conn.commit()

    statement = '''
        CREATE TABLE 'Players' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL,
            'StartYear' INTEGER,
            'EndYear' INTEGER,
            'Position' TEXT NOT NULL,
            'Height' TEXT NOT NULL,
            'Weight' INTEGER
        );
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Stats' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'GamesPlayed' INTEGER,
            'AvgPoints' INTEGER,
            'AvgRebounds' INTEGER,
            'AvgAssists' INTEGER
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()


def get_basketball_name(initial):
    baseurl = 'https://www.basketball-reference.com/players/'
    initial = initial.lower()
    new_url = baseurl + initial + '/'

    page_text = make_requests_using_cache(new_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')

    content_div = page_soup.find(class_ = 'overthrow table_container')
    table_body = content_div.find('tbody')

    basketball_player_result = []

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    init_db()

    for item in table_body.find_all('tr'):
        find_player_name = item.find('th')
        final_find_player_name = find_player_name.find('a')
        player_name = final_find_player_name.text.strip()

        find_player_info = item.find_all('td')

        stats_list = []
        for item in find_player_info:
            get_stats = item.text.strip()
            stats_list.append(get_stats)

        player_start_year = stats_list[0]
        player_end_year = stats_list[1]
        player_position = stats_list[2]
        player_height = stats_list[3]
        player_weight = stats_list[4]

        player_extra_details = final_find_player_name['href']
        player_details_url = 'https://www.basketball-reference.com'+ player_extra_details


        basketball_player = BasketballPlayers(player_name, player_start_year, player_end_year, player_position, player_height, player_weight)
        basketball_player.init_from_details_url(player_details_url)
        basketball_player_result.append(basketball_player)


    for x in basketball_player_result:
        insertion = (None, x.name, x.startyear, x.endyear, x.position, x.height, x.weight)
        statement = 'INSERT INTO "Players" '
        statement += 'Values (?, ?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)

    for y in basketball_player_result:
        insertion = (None, y.gamesplayed, y.totalpoints, y.totalrebounds, y.totalassists)
        statement1 = 'INSERT INTO "Stats" '
        statement1 += 'Values (?, ?, ?, ?, ?)'
        cur.execute(statement1, insertion)


    conn.commit()
    conn.close()



    return basketball_player_result

get_basketball_name('a')
