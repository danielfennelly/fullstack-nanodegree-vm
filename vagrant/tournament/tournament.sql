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