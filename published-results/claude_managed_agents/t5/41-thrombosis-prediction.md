Patients with an LDH value above 500 and a first hospital visit (Date3) from 1990-01-01 through 1997-12-31 returned 80-odd IDs, each listed once with sex. The query below returns that list; I did not reproduce the full list here.

I checked three things with you before writing it:
- **Hospital visit:** Date3 is the first hospital visit date.
- **Time window:** "the many first years of the 1990s" means 1990 through 1997 inclusive.
- **LDH threshold:** "beyond normal range" means LDH > 500.

Patients with several qualifying lab rows appear once.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE l.LDH > 500
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
ORDER BY p.ID;
```