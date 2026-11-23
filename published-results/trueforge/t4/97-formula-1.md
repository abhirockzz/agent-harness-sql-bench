Five drivers meet the criteria. The request had two problems that I resolved with your input:

- **Points threshold:** No 2016 result exceeded 30 points. The highest single-race total that season was 25, so I used 25 points (a race win) as you asked.
- **Veteran:** You defined it as having competed in 5 or more seasons. I counted seasons through 2016. Counting all career seasons gives the same five drivers.

| Last name | Main page (principalUrl) |
|---|---|
| Behelmererer | http://FrancisBehelmererer.com/principal |
| Hamilton | http://en.wikipedia.org/wiki/Lewis_Hamilton/principal |
| Melher | http://JonathanMelher.com/principal |
| Ricciardo | http://en.wikipedia.org/wiki/Daniel_Ricciardo/principal |
| Rosberg | http://en.wikipedia.org/wiki/Nico_Rosberg/principal |

Behelmererer, and the two other non-Wikipedia names (Behelmer and Driver), look like placeholder or test records. Behelmererer is kept because it meets the criteria, but you may want to verify it. Behelmer and Driver were excluded because they have only one season.

```sql
WITH winners AS (
    SELECT DISTINCT res.driverId
    FROM results res
    JOIN races ra ON ra.raceId = res.raceId
    WHERE ra.year = 2016
      AND res.points >= 25
),
veterans AS (
    SELECT res.driverId
    FROM results res
    JOIN races ra ON ra.raceId = res.raceId
    WHERE ra.year <= 2016
    GROUP BY res.driverId
    HAVING COUNT(DISTINCT ra.year) >= 5
)
SELECT d.surname AS last_name,
       d.principalUrl AS main_page
FROM drivers d
JOIN winners w ON w.driverId = d.driverId
JOIN veterans v ON v.driverId = d.driverId
ORDER BY d.surname;
```