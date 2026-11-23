No driver meets the criteria, so the query returns an empty result. Nobody scored more than 30 points in a single race in 2016.

- **Why it's empty:** The highest single-race score in the 2016 season in the `results` table is 25 points, across 445 result rows. The 30-point threshold is never reached, so the veteran filter doesn't matter.
- **Definitions I used:** You defined a veteran as a driver who has competed in 5 or more seasons. I counted seasons across the driver's whole career in `results` joined to `races.year`. For the main page, you chose `wikiUrl`.
- **Possible next steps:** If you meant a different threshold (for example, 25 points or more, or total points for a driver in a season), or a different measure such as `driverStandings`, tell me and I'll rerun it.

```sql
SELECT d.surname AS last_name, d.wikiUrl AS main_page
FROM drivers d
WHERE d.driverId IN (
  SELECT res.driverId FROM results res
  JOIN races r ON r.raceId = res.raceId
  WHERE r.year = 2016 AND res.points > 30
)
AND (SELECT COUNT(DISTINCT r2.year) FROM results res2 JOIN races r2 ON r2.raceId = res2.raceId WHERE res2.driverId = d.driverId) >= 5
ORDER BY d.surname ASC;
```