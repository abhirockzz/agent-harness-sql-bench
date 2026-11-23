The average loan amount is **about $124,353** across 44 loans.

These loans come from four districts that meet all the criteria: Chomutov, Most, Teplice and Karviná. Decín was excluded because its stability score is about 40.9, below the threshold of 50.

Per your definitions, the population is loans whose account district has:
- Urbanization (A10) above 65
- Unemployment (A12 or A13) above 6.0% in 1995 or 1996
- Stability score, (economic_resilience × 2 + financial_health_score × 3 + development_index) / 6, above 50

The figure is per loan, not per client. Loans are linked to districts through the account, as you specified. I did not check whether any client holds more than one of these loans.

```sql
SELECT AVG(l.amount) AS avg_loan_amount
FROM loan l
JOIN account a ON l.account_id = a.account_id
JOIN district d ON a.district_id = d.district_id
WHERE d.A10 > 65
  AND (d.A12 > 6.0 OR d.A13 > 6.0)
  AND ((d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6.0) > 50;
```