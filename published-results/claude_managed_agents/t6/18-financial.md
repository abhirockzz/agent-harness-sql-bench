The average loan amount for high-risk clients in urban districts with stable economic conditions is **about $124,353** (44 loans).

Your definitions:
- **High-risk:** the account's district has unemployment above 6.0% in 1995 (A12) or 1996 (A13).
- **Urban:** urbanization ratio (A10) above 65.
- **Stable economic conditions:** `(economic_resilience*2 + financial_health_score*3 + development_index)/6` above 50.

Joining through the client table gives the same result, because every qualifying loan has exactly one OWNER disposition. So the answer doesn't depend on how "client" is counted.

```sql
SELECT AVG(l.amount) AS avg_loan_amount
FROM loan l
JOIN account a ON a.account_id = l.account_id
JOIN district d ON d.district_id = a.district_id
WHERE (d.A12 > 6.0 OR d.A13 > 6.0)
  AND d.A10 > 65
  AND (d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6.0 > 50;
```