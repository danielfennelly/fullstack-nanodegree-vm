-- Fetches player standings
--

SELECT 
	players.id,
	players.name,
	count(case when players.id = matches.winner then 1 else NULL end) as matches_won,
	count(matches.id) as matches_played
FROM players
LEFT JOIN matches
ON players.id = matches.winner or players.id = matches.loser
GROUP BY players.id, players.name
ORDER BY matches_won DESC