# basketballreference_SI

This project scrapes https://www.basketball-reference.com/players/ for player information. 

On this website, the players are ordered by the first initial of the last name. 
Ex: 'Forest Able', 'John Abramovic', and 'Alex Acker' all are found under the "A" tab.

If you want to know more about NBA players with the specified last initial you would input that letter and this program
will scrape basketball reference for all the NBA players with that specified last initial. 

This program limits the player results to 50 players

If you would like to see this player list the command to do so would be: "players"

If you would like to constrain the list to players who play a specific position,
the command would be: "players name=position" (position being replaced with G, F, or C (Guard, Foward, Center))

If you would like to order this list by newer/active players the command would be: "players name=position new"
(position being replaced with G, F, or C (Guard, Foward, Center))
If you would like to order this list by older players the command would be: "players name=position old"

For example: If you wanted to see a list of newer players with the specified position of Center the command would be:
"players name=C new"
If you wanted to see a list of older players with no specified position the command would be:
"players old"

From the "players" command there is one visual representation available.
After executing the "players" command
type "create pie" if you want to see a pie chart that shows you the percentage of NBA players that play each postion: G, F, C

Next,
If you want to know about the statistics of specific player in the list returned from the "player" command
the command would be: "stats name=player"

For example: If you wanted to see the statistics of the player "Forest Able" the command would be:
"stats name=Forest Able"

From the "stats" command there are three visual representations available.
After executing the "stats" command,
type "bar graph" if you want to see a bar graph that shows you the career points per game of the specified player
compared to the average points per game of the other players in the database

type "create gannt" if you want to see a gannt graph that shows you the amount of years the specified player played
compared to the NBA average career duration.

type "create table" if you want to see a formated table that shows you the specified player's statistics.

HOW MY CODE IS STRUCTURED: 

I have a function called "get_basketball_name" that scrapes basketball reference. Within this function, I also
insert the information I have scraped and insert it into my database.
I have a class called "BasketballPlayers" that stores the information that I have scraped from the website.
I have a function called process_command that processes the user's command that they specifies and executes that command 
and returns the specified list of results from the database.






