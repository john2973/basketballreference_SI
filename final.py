import requests
from bs4 import BeautifulSoup
import json
import sqlite3

CACHE_FNAME = 'basketball.json'

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
    def __init__(self, name, height, weight, games, points, rebounds, assists, team):
        self.name = name
        self.height = height
        self.weight = weight
        self.games = games
        self.points = points
        self.rebounds = rebounds
        self.assists = assists
        self.team = team

    def init_from_details_url(self, details_url):
        page_text = make_requests_using_cache(details_url)
        page_soup = BeautifulSoup(page_text, 'html.parser')

        team_info = page_soup.find(class_ = 'teams')
        find_all_team_info = team_info.find_all('p')

        team_info = []
        for item in find_all_team_info:
            get_team_stats = item.text.strip()
            team_info.append(get_team_stats)

        team_record = team_info[2]
        team_coach = team_info[5]
        team_arena = team_info[11]

        find_team_name = page_soup.find(id = 'meta')
        get_team_name = find_team_name.find('h1')
        last_find = get_team_name.find_all('span')

        team_name_list = []
        for item in last_find:
            specific_team_name = item.text.strip()
            team_name_list.append(specific_team_name)

        final_team_info = team_name_list[1]




        self.team_record = team_record
        self.team_coach = team_coach
        self.team_arena = team_arena
        self.team_name = final_team_info


    def __str__(self):
        return self.name + ' Height: ' + self.height + ' Weight: ' + self.weight + ' Career Games Played: ' \
                + self.games + ' Career Points per Game: ' + self.points + ' Career Rebounds per Game: ' \
                + self.rebounds + ' Career Assists per Game: ' + self.assists

    def __repr__(self):
        return self.__str__()




def get_basketball_name(player):
    baseurl = 'https://www.basketball-reference.com/players/'
    new_player = player.lower()
    player_split = new_player.split()
    if len(player_split[1]) < 5:
        player_url = baseurl + player_split[len(player_split) - 1][0] + '/' + player_split[1] + player_split[0][0:2] + '01.html'
    else:
        player_url = baseurl + player_split[len(player_split) - 1][0] + '/' + player_split[1][0:5] + player_split[0][0:2] + '01.html'

    page_text = make_requests_using_cache(player_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')

    content_div = page_soup.find(itemtype = 'https://schema.org/Person')

    find_player_name = content_div.find('h1')
    player_name = find_player_name.text.strip()

    find_player_height = content_div.find(itemprop = 'height')
    player_height = find_player_height.text.strip()

    find_player_weight = content_div.find(itemprop = 'weight')
    player_weight = find_player_weight.text.strip()

    #looking at player stats now
    # gets games, assists points, etc current year and career
    stats = []
    stats_div = page_soup.find(class_ = 'p1')
    stats_num = stats_div.find_all('p')
    for item in stats_num:
        get_stats = item.text.strip()
        stats.append(get_stats)

    #previous_year_games = stats[0]
    career_games = stats[1]
    #previous_year_points = stats[2]
    career_points = stats[3]
    #previous_year_rebounds = stats[4]
    career_rebounds = stats[5]
    #previous_year_assists = stats[6]
    career_assists = stats[7]

    #crawling to the team of the player
    crawling_nums = content_div.find_all('p')
    extra_layer = crawling_nums[4]
    team_website = extra_layer.find('a')
    team_name = team_website.text.strip()

    details_page = team_website['href']

    basketball_player_result = []

    details_page_url = 'https://www.basketball-reference.com' + details_page
    basketball_player = BasketballPlayers(player_name, player_height, player_weight, career_games, career_points, career_rebounds, career_assists, team_name)
    basketball_player.init_from_details_url(details_page_url)
    basketball_player_result.append(basketball_player)

    return basketball_player_result

#print (get_basketball_name('Lebron James'))



DBNAME = 'basketball.db'

def init_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
        DROP TABLE IF EXISTS 'Players';
    '''
    cur.execute(statement)
    statement = '''
        DROP TABLE IF EXISTS 'Teams';
    '''
    cur.execute(statement)

    conn.commit()

    statement = '''
        CREATE TABLE 'Players' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL,
            'Height' TEXT NOT NULL,
            'Weight' TEXT NOT NULL,
            'GamesPlayed' INTEGER,
            'Points' INTEGER,
            'Rebounds' INTEGER,
            'Assists' INTEGER,
            'Team' TEXT NOT NULL,
            'TeamsId' INTEGER
        );
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Teams' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Record' TEXT NOT NULL,
            'Coach' TEXT NOT NULL,
            'Arena' TEXT NOT NULL,
            'TeamName' TEXT NOT NULL
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()

# def insert_into_db():
#     conn = sqlite3.connect(DBNAME)
#     cur = conn.cursor()
