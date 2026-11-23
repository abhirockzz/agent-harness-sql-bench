The query returns 81 patients with at least one LDH value above 500 and a Date3 (first hospital visit) between 1990 and 1997.

Two of the answers I used differ from what you might expect:
- **Period:** you described "the many first years of the 1990s" and the definition I was given is 1990 through 1997 inclusive, so I used that range.
- **Threshold:** LDH is flagged when it is above 500, as the business definition specifies. Rows with no LDH value are excluded automatically.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE l.LDH > 500
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
ORDER BY p.ID;
```