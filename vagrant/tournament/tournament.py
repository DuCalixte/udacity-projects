#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


"""Method to exit connection after commiting to  database"""
def exit(connection):
    connection.commit()
    connection.close()


def deleteMatches():
    """Remove all the match records from the database."""
    connection = connect()
    context = connection.cursor()

    """Call database to delete all matches."""
    context.execute("DELETE FROM Matches;")
    exit(connection)


def deletePlayers():
    """Remove all the player records from the database."""
    connection = connect()
    context = connection.cursor()

    """Call database to delete all registered players."""
    context.execute("DELETE FROM Players;")
    exit(connection)


def countPlayers():
    """Returns the number of players currently registered."""
    connection = connect()
    context = connection.cursor()

    """Call database to the Players' count."""
    context.execute("SELECT COUNT(*) FROM Players;")
    count = context.fetchone()
	
    connection.close()
    return count[0]


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    connection = connect()
    context = connection.cursor()

    """Call database to insert new player to tournament."""
    context.execute("INSERT INTO Players (name)  VALUES (%s);", (bleach.clean(name),))
    exit(connection)


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    connection = connect()
    context = connection.cursor()
    
    """Call database to delete all matches."""
    context.execute("SELECT * FROM Standings;")
    result = context.fetchall()
    connection.close()
    
    print(result)
    return result


def reportMatch(winner, loser=None, is_a_draw=False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost, Default value is 'None' which indicates a bye for the winner
	  is_a_draw: optional parameter that indicates whether the match is a draw. Default is false
    """
    connection = connect()
    context = connection.cursor()
    
    """If it is a bye insert the winner, otherwise insert all fields"""
    if loser==None:
        context.execute("""
        INSERT INTO Matches (winner_id) 
        SELECT %s 
        WHERE 
        NOT EXISTS (
        SELECT * FROM Matches 
        WHERE winner_id=%s);""",(winner, winner,))
    else:
        context.execute("""
        INSERT INTO Matches (winner_id, loser_id, draw) 
        SELECT %s, %s, %s 
        WHERE 
        NOT EXISTS ( 
        SELECT * FROM Matches 
        WHERE (winner_id=%s AND loser_id=%s)
        OR (loser_id=%s AND winner_id=%s));""",(winner, loser, is_a_draw, winner, loser, winner, loser,))
    
    exit(connection)

 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    """Access current standings"""
    standings = playerStandings()
    print('standings')
    print(standings)
    pairings = []

    last_index = len(standings) - 1
    iterations = []
    for iterate in range(0, len(standings)/2):
        print iterate
        iterations.append(iterate * 2)
 
    print iterations
    for player_index in iterations:
        pairing = ()
        print('player_index')
        print(player_index)
        for index in range(player_index, player_index + 2):
            print('index')
            print(index)
            pairing+=(standings[index][0],standings[index][1])
            print(pairing)
        pairings.append(pairing)
    
    if last_index%2==0:
        pairings.append(standings[last_index][0],standings[last_index][1])

    return pairings

"""The draw count for the player given id."""
def playerDrawCount(id):
    """Returns the number of draw outcomes by a player."""
    connection = connect()
    context = connection.cursor()

    """Call database to the Players' draw count."""
    context.execute("SELECT draws  FROM TotalDraws WHERE TotalDraws.id=%s;",[id])
    draws = context.fetchone()

    connection.close()
    return draws[0]

