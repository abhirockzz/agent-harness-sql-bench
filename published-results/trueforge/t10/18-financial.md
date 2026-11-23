The average loan amount for this group is about **$124,353**, across 44 loans.

I used these definitions, which you provided:
- **High-risk:** the account's district has an unemployment rate above 6.0% in 1995 (A12) or 1996 (A13).
- **Urban:** urbanization ratio (A10) above 65.
- **Stable economic conditions:** (economic_resilience × 2 + financial_health_score × 3 + development_index) / 6 is above 50.

The average is across loans, not distinct clients, and each loan's district comes from its account's `district_id`.

```sql
SELECT AVG(l.amount) AS avg_loan_amount,
       COUNT(*) AS loan_count
FROM loan l
JOIN account a ON l.account_id = a.account_id
JOIN district d ON a.district_id = d.district_id
WHERE (d.A12 > 6.0 OR d.A13 > 6.0)
  AND d.A10 > 65
  AND (d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6.0 > 50;
```