#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

def connect(database_name="tournament"):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except psycopg2.Error as exception:
        print(exception)

def deleteMatches():
    """Remove all the match records from the database."""
    db, cur = connect()
    cur.execute("DELETE FROM matches")
    db.commit()
    db.close()

def deletePlayers():
    """Remove all the player records from the database."""
    db, cur = connect()
    cur.execute("DELETE FROM players")
    db.commit()
    db.close()

def countPlayers():
    """Returns the number of players currently registered."""
    db, cur = connect()
    cur.execute("SELECT count(*) FROM players")
    results = cur.fetchone()
    db.commit()
    db.close()
    return results[0]

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db, cur = connect()
    cur.execute("INSERT INTO players (name) VALUES (%s)", (name,))
    db.commit()
    db.close()

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
    db, cur = connect()
    query = "SELECT * FROM standings"
    cur.execute(query)
    results = cur.fetchall()
    return [(row[0], row[1], row[2], row[3])for row in results]
    db.close()

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db, cur = connect()
    cur.execute("INSERT INTO matches (winner, loser) VALUES (%s, %s)", (winner, loser,))
    db.commit()
    db.close()
 
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
    standings = playerStandings()
    pairs = []
    if len(standings) % 2 != 0:
        bye_player = standings.pop()
    while standings:
        first_id, first_name, _, _  = standings.pop()
        second_id, second_name, _, _ = standings.pop()
        pairs.append((first_id, first_name, second_id, second_name))
    return pairs
