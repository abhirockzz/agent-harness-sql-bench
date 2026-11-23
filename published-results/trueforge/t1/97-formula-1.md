No drivers meet the criteria, so the answer is an empty list.

In the 2016 season, the highest score by any driver in a single race was 25 points. The `results` table records points per driver per race, and no 2016 result exceeds 30. Because nothing matches, there are no veteran drivers to list.

I defined a veteran as a driver who has competed in 5 or more seasons, counted across all seasons in the database, as you described. I used `principalUrl` as the "main page" column because it appears to be the closest match, but the choice doesn't change the result since no rows are returned.

If you meant a different measure, such as a driver's total points across the 2016 season, I can rerun the query on that basis.

```sql
SELECT d.surname, d.principalUrl AS main_page
FROM drivers d
WHERE d.driverId IN (
  SELECT r.driverId FROM results r JOIN races ra ON ra.raceId = r.raceId
  WHERE ra.year = 2016 AND r.points > 30
)
AND (
  SELECT COUNT(DISTINCT ra2.year) FROM results r2 JOIN races ra2 ON ra2.raceId = r2.raceId
  WHERE r2.driverId = d.driverId
) >= 5
ORDER BY d.surname ASC;
```