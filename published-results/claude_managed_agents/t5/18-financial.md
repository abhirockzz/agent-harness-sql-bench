The average loan amount is about **124,353 USD**, across 44 loans.

I used the definitions you gave:
- **High-risk:** the account's district has an unemployment rate above 6.0% in 1995 (A12) or 1996 (A13).
- **Urban:** the district's urbanization ratio (A10) is above 65.
- **Stable economic conditions:** (economic_resilience × 2 + financial_health_score × 3 + development_index) / 6 is above 50.

Four districts qualify: Most, Teplice, Chomutov and Karviná. Decin passes the urban and unemployment tests but fails the stability score.

Loans are attributed to clients through the account's district (`account.district_id`), as you specified. I averaged over loans and did not join through the `disp` table, so accounts with several owners are counted once per loan rather than once per client.

```sql
SELECT AVG(l.amount) AS avg_loan_amount, COUNT(*) AS loan_count
FROM loan l
JOIN account a ON a.account_id = l.account_id
JOIN district d ON d.district_id = a.district_id
WHERE (d.A12 > 6.0 OR d.A13 > 6.0)
  AND d.A10 > 65
  AND (d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6.0 > 50
```