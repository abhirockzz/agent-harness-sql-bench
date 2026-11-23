The average loan amount is **about 124,353 USD** across 44 loans.

This uses the definitions you gave:
- **High-risk:** the account's district has unemployment above 6.0% in 1995 (A12) or 1996 (A13).
- **Urban:** the district's urbanization ratio (A10) is above 65.
- **Stable economic conditions:** (economic_resilience × 2 + financial_health_score × 3 + development_index) / 6 is above 50.

The average is over loans, not distinct clients, since the query joins loans to accounts and districts. A client with several qualifying loans counts once per loan.

```sql
SELECT AVG(l.amount) AS avg_amount
FROM loan l
JOIN account a ON a.account_id = l.account_id
JOIN district d ON d.district_id = a.district_id
WHERE (d.A12 > 6.0 OR d.A13 > 6.0)
  AND d.A10 > 65
  AND (d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6 > 50;
```