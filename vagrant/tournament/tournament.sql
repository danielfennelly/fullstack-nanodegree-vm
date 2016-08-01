-- Table definitions for the tournament project.
--

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament

CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name text
);

CREATE TABLE matches (
	id SERIAL PRIMARY KEY,
	winner integer REFERENCES players(id),
	loser integer REFERENCES players(id)
);

CREATE VIEW standings as SELECT 
	players.id,
	players.name,
	count(case when players.id = matches.winner then 1 else NULL end) as matches_won,
	count(matches.id) as matches_played
FROM players
LEFT JOIN matches
ON players.id = matches.winner or players.id = matches.loser
GROUP BY players.id, players.name
ORDER BY matches_won DESC;