The average loan amount is about **124,353.27** across 44 loans, each for a different client.

I used your definitions:
- **High-risk:** the account's district has an unemployment rate above 6.0% in 1995 (A12) or 1996 (A13).
- **Urban:** urbanization ratio (A10) above 65.
- **Stable economic conditions:** the weighted score `(economic_resilience*2 + financial_health_score*3 + development_index)/6` is above 50.

Two choices I made without asking you:
- **Client link:** each loan is joined to its account's OWNER, so each loan is counted once. Including DISPONENT clients would count some loans more than once.
- **District source:** the account's district drives all three conditions, not the client's home district.

```sql
SELECT ROUND(AVG(l.amount), 2) AS avg_loan_amount
FROM loan l
JOIN account a ON a.account_id = l.account_id
JOIN district d ON d.district_id = a.district_id
JOIN disp dp ON dp.account_id = l.account_id AND dp.type = 'OWNER'
WHERE (d.A12 > 6.0 OR d.A13 > 6.0)
  AND d.A10 > 65
  AND (d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6 > 50;
```