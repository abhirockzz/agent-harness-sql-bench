The average loan amount for this group is about **124,353.27 USD**, across 44 loans.

I used these definitions, which you gave me:
- **High-risk clients:** the account's district has an unemployment rate above 6.0 in 1995 (A12) or 1996 (A13).
- **Urban districts:** urbanization ratio (A10) above 65.
- **Stable economic conditions:** (economic_resilience × 2 + financial_health_score × 3 + development_index) / 6 above 50.

Each loan is counted once, using the account owner's disposition, since some accounts have a second client who would otherwise duplicate the loan. Counting every linked client gives the same 44 loans and the same average.

```sql
SELECT COUNT(*) AS loan_count, ROUND(AVG(l.amount), 2) AS avg_loan_amount
FROM loan l
JOIN account a ON a.account_id = l.account_id
JOIN district d ON d.district_id = a.district_id
JOIN disp dp ON dp.account_id = a.account_id AND dp.type = 'OWNER'
JOIN client c ON c.client_id = dp.client_id
WHERE (d.A12 > 6.0 OR d.A13 > 6.0)
  AND d.A10 > 65
  AND (d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6 > 50;
```