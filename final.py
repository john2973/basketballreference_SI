import requests
from bs4 import BeautifulSoup
import json
import sqlite3
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
import numpy as np


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
                + self.weight + ' Career Points: ' + self.totalpoints

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
            'Weight' INTEGER,
            'StatsId' INTEGER
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
        insertion = (None, x.name, x.startyear, x.endyear, x.position, x.height, x.weight, 0)
        statement = 'INSERT INTO "Players" '
        statement += 'Values (?, ?, ?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)

    for y in basketball_player_result:
        insertion = (None, y.gamesplayed, y.totalpoints, y.totalrebounds, y.totalassists)
        statement1 = 'INSERT INTO "Stats" '
        statement1 += 'Values (?, ?, ?, ?, ?)'
        cur.execute(statement1, insertion)


    statement2 = 'UPDATE Players '
    statement2 += 'SET StatsId = (SELECT Stats.ID FROM Stats WHERE Players.Id = Stats.Id);'
    cur.execute(statement2)
    conn.commit()
    conn.close()



    return basketball_player_result

#get_basketball_name('a')

# a command could be like players: list all those players.
def process_command(command):

    new_command = command.split()
    conn = sqlite3.connect(DBNAME)

    cur = conn.cursor()

    count = 0

    while (count < len(new_command) and 'players' in new_command):
        if 'players' in new_command[count]:
            statement = 'SELECT Name, Stats.AvgPoints, StartYear, EndYear, Position, Height, Weight '
            statement += 'FROM Players '
            statement += 'JOIN Stats '
            statement += 'ON Stats.Id = Players.StatsId '

            if len(new_command) == 1:
                statement += 'ORDER BY StartYear DESC '
                statement += 'LIMIT 50'
                break
        elif 'position' in new_command[count]:
            position_abrv = new_command[count][-1:]
            statement += 'WHERE Position LIKE ' + '"%' + position_abrv + '%"' + ' '
            if 'position' in new_command[len(new_command) - 1]:
                statement += 'ORDER BY StartYear DESC '
                statement += 'LIMIT 50'
        elif 'new' in new_command[count]:
            statement += 'ORDER BY StartYear DESC '
            statement += 'LIMIT 50'
        elif 'old' in new_command[count]:
            statement += 'ORDER BY StartYear ASC '
            statement += 'LIMIT 50'
        else:
            pass

        count += 1

    while (count < len(new_command) and 'stats' in new_command):
        if 'stats' in new_command[count]:
            statement = 'SELECT Players.Name, GamesPlayed, AvgPoints, AvgRebounds, AvgAssists, Players.StartYear, Players.EndYear '
            statement += 'FROM Stats '

        elif 'name' in new_command[count]:
            name_abrv = new_command[count].split('=')
            final_name_abrv = str(name_abrv[1]) + ' ' + str(new_command[count + 1])
            statement += 'JOIN Players '
            statement += 'ON Players.StatsId = Stats.Id '
            statement += 'WHERE Players.Name LIKE ' + '"%' + final_name_abrv + '"' + ' '
        else:
            pass
        count += 1

    cur.execute(statement)
    cur_list = []
    for item in cur:
        cur_list.append(item)

    return cur_list

def create_bar_graph(list_result):


    x0 = [item[0] for item in list_result]
    y0 = [item[1] for item in list_result]


    trace0 = go.Bar(
        x=x0,
        y=y0,
        #text=['27% market share', '24% market share', '19% market share'],
        marker=dict(
            color='rgb(158,202,225)',
            line=dict(
                color='rgb(8,48,107)',
                width=1.5,
            )
        ),
        opacity=0.6
    )

    data = [trace0]
    layout = go.Layout(
        title='Career Average Points -NBA Players',
    )

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='text-hover-bar')

def create_table(list_result):
    trace = go.Table(
        header=dict(values=['NAME', list_result[0][0]]),
        cells=dict(values=[['GAMES PLAYED', 'AVGPOINTS', 'AVGREBOUNDS', 'AVGASSISTS'],
                            [list_result[0][1], list_result[0][2], list_result[0][3], list_result[0][4]]]))


    data = [trace]
    py.plot(data, filename = 'basic_table')

def create_gannt(list_result):

    df = [dict(Task=str(list_result[0][0]), Start=str(list_result[0][5]), Finish=str(list_result[0][6])),
            dict(Task="Avg Career", Start=str(list_result[0][5]), Finish=str(list_result[0][5] + 5))]


    fig = ff.create_gantt(df)
    py.plot(fig, filename='gantt-simple-gantt-chart', world_readable=True)

# def create_scatter(list_result):
#     N = 1000
#     random_x = np.random.randn(N)
#     random_y = np.random.randn(N)
#
# # Create a trace
#     trace = go.Scatter(
#         x = random_x,
#         y = random_y,
#         mode = 'markers'
#     )
#
#     data = [trace]
#
# # Plot and embed in ipython notebook!
#     py.plot(data, filename='basic-scatter')





def interactive_prompt():
    response = ''
    players_count = 0
    stats_count = 0

    # player_input = input('Enter a players last initial to see data on NBA players with the last initial ')
    # get_basketball_name(player_input)

    while response != 'exit':
        response = input('Enter a command: ')

        first_word_response = response.split()

        if response == 'exit':
            print ('bye')
        # elif 'position' not in first_word_response[1] and 'name' not in first_word_response[1]:
        #     print ('Command not recognized: ' + response)
        #     print ('\n')
        elif response == 'bar graph' and players_count == 1:
            create_bar_graph(results)
            players_count = 0
        elif response == 'create table' and stats_count == 1:
            create_table(results)
            #stats_count = 0
        elif response == 'create gannt' and stats_count == 1:
            create_gannt(results)
            #stats_count = 0
            print ('\n')
        else:
            try:
                results = process_command(response)
                if first_word_response[0] == 'players':
                    player_column = "{:<25}{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}".format('NAME', 'AVGPOINTS', 'START', 'END', 'POSITION', 'HEIGHT', 'WEIGHT')
                    print (player_column)
                    for item in results:
                        return_str = "{:<25}{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}".format(item[0], item[1], item[2], item[3], item[4], item[5], item[6])
                        print (return_str)
                    players_count += 1
                elif first_word_response[0] == 'stats':
                    stats_column = "{:<25}{:<15}{:<15}{:<15}{:<15}".format('NAME', 'GAMES PLAYED', 'AVGPOINTS', 'AVGREBOUNDS', 'AVGASSISTS')
                    print (stats_column)
                    for item in results:
                        return_str = "{:<25}{:<15}{:<15}{:<15}{:<15}".format(item[0], item[1], item[2], item[3], item[4])
                        print (return_str)
                    stats_count += 1
                else:
                    pass
            except:
                print ('Command not recognized: ' + response)
            print ('\n')













if __name__ == '__main__':
    interactive_prompt()
