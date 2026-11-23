The average loan amount is about **$124,353** across 44 loans.

I counted loans, not unique clients. Each loan is attributed to its account's district, and I used the district from the account. Your definitions were:

- **High-risk:** the district's unemployment rate (A12 for 1995 or A13 for 1996) is above 6.0%.
- **Urban:** urbanization ratio (A10) is above 65.
- **Stable economic conditions:** (economic_resilience × 2 + financial_health_score × 3 + development_index) / 6 is above 50.

```sql
SELECT COUNT(*) AS loan_count, AVG(l.amount) AS avg_loan_amount
FROM loan l
JOIN account a ON a.account_id = l.account_id
JOIN district d ON d.district_id = a.district_id
WHERE d.A10 > 65
  AND (d.A12 > 6.0 OR d.A13 > 6.0)
  AND (d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6.0 > 50
```