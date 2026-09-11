# Xeno Comm-Log Send Reconciliation

## Assignment objective

Reproduce Finance's reported `target_base` of **22** for merchant 501, October 2026, across Diwali campaigns, using the supplied SQLite dataset.

## Business rules used

1. A campaign is eligible for reporting only when its creation workflow has cleared: `creation_status` is one of `approved`, `aborted`, `resumed`, or `stopped`, and `processing_status = 'processed'`.
2. A retry campaign is linked to its parent through `campaign.parent_id`.
3. A retry chain represents one underlying communication. Therefore, within a retry family, the same customer counts once even if they were sent multiple times.
4. A standalone campaign has no parent and no child retry campaign. Every send event under a standalone campaign counts separately, including legitimate repeat sends to the same customer.

## Investigation and reconciliation bridge

| Step | Description | Result | Reason |
|---:|---|---:|---|
| 0 | Naive count of all `communication_log` rows | **30** | Starting point: every row is a send attempt. |
| 1 | Exclude campaign `9004` | **26** | Campaign `9004` is `approval_awaiting`, so its 4 send-log rows are not eligible for reporting. |
| 2 | Collapse retry family `9001 → 9002 → 9003` | **23** | 13 send attempts represent 10 distinct customers in the same retry chain, a reduction of 3. |
| 3 | Collapse retry family `9201 → 9202` | **22** | 6 send attempts represent 5 distinct customers in the same retry chain, a reduction of 1. |
| 4 | Verify standalone campaign `9101` | **22** | Its 7 send events remain 7. Customer `C20` appears twice, but these are separate legitimate standalone sends. |

### Arithmetic

```text
30 raw rows
- 4 ineligible sends from campaign 9004
- 3 retry over-counts in family 9001 → 9002 → 9003
- 1 retry over-count in family 9201 → 9202
= 22
```

## Final result

**`target_base = 22`**

## Key findings

### Family A: 9001 → 9002 → 9003

There are 13 raw attempts involving 10 customers (`C1`–`C10`). Customers `C2` and `C3` appear in multiple campaigns because of retries. The retry chain is treated as one underlying communication per customer, giving **10** qualifying sends.

### Pending retry branch: 9004

Campaign `9004` is a retry of `9001`, but its creation status is `approval_awaiting`. It contributes 4 rows to the raw log, but none are eligible for official reporting.

### Standalone campaign: 9101

Campaign `9101` is standalone. It contains 7 send events. Customer `C20` is sent twice on different dates; both events count.

### Family B: 9201 → 9202

There are 6 raw attempts involving 5 customers (`D1`–`D5`). `D1` failed on `9201` and succeeded on `9202`, so the retry chain contributes **1** for `D1`, not 2. The family contributes **5** qualifying sends.

## What surprised me

One thing that surprised me was that communication-log rows exist for campaign `9004` even though its creation status is `approval_awaiting`. This showed that the communication log alone cannot be used to determine reporting eligibility. I was also initially cautious about the repeated `C20` records in standalone campaign `9101`, but the data rules clarify that repeated sends within a standalone campaign are legitimate separate events, whereas repeated customers across retry campaigns represent the same underlying communication.

## Repository contents

- `sql/01_investigation.sql` — investigation queries used to understand row counts, campaign eligibility, hierarchy, retry behavior, and repeated customers.
- `sql/final_reconciliation.sql` — final SQLite query that computes the reconciled `target_base`.
- `outputs/reconciliation_bridge.csv` — reconciliation bridge as a simple submission-friendly table.

## Reproducibility

The SQL is written for SQLite and is intended to run directly against the supplied `data/comm_log.db`.
