The average loan amount is **about 124,353 USD**, across 44 loans.

The result uses the definitions you gave:
- **High-risk:** the account's district has an unemployment rate above 6.0% in 1995 (A12) or 1996 (A13).
- **Urban:** urbanization ratio (A10) above 65.
- **Stable economic conditions:** (economic_resilience × 2 + financial_health_score × 3 + development_index) / 6 above 50.

Only five districts pass the high-risk and urban tests (33, 34, 39, 40, 70). Of those, districts 33, 34, 39 and 40 contribute 24 loans and 70 contributes 24 more, all on the same account-level join. The average is per loan, not per client, and loans are assigned to districts through `account.district_id`, as you specified.

```sql
SELECT AVG(l.amount) AS avg_amount
FROM loan l
JOIN account a ON a.account_id = l.account_id
JOIN district d ON d.district_id = a.district_id
WHERE (d.A12 > 6.0 OR d.A13 > 6.0)
  AND d.A10 > 65
  AND ((d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6) > 50;
```