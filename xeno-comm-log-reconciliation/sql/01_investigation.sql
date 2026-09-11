-- Xeno Comm-Log Reconciliation - Investigation Queries
-- Scope: merchant 501, October 2026, campaign communication_type = '2'.

-- 1. Naive starting count
SELECT COUNT(*) AS naive_count
FROM communication_log;

-- 2. Campaign/send-attempt distribution
SELECT
    communication_id,
    COUNT(*) AS send_attempts
FROM communication_log
GROUP BY communication_id
ORDER BY communication_id;

-- 3. Inspect campaign eligibility and hierarchy
SELECT
    id AS campaign_id,
    parent_id,
    name,
    creation_status,
    processing_status,
    CASE
        WHEN parent_id IS NULL THEN 'ROOT'
        ELSE 'RETRY'
    END AS campaign_role
FROM campaign
WHERE merchant_id = 501
ORDER BY id;

-- 4. Find send attempts attached to an ineligible campaign
SELECT
    cl.id,
    cl.communication_id,
    cl.customer_id,
    c.creation_status,
    c.processing_status,
    cl.sent_time
FROM communication_log cl
JOIN campaign c
    ON c.id = cl.communication_id
WHERE cl.merchant_id = 501
  AND cl.communication_type = '2'
  AND c.creation_status NOT IN ('approved', 'aborted', 'resumed', 'stopped')
ORDER BY cl.communication_id, cl.sent_time;

-- 5. Inspect Family A retry chain
SELECT
    cl.communication_id,
    cl.customer_id,
    cl.delivery_status,
    cl.sent_time
FROM communication_log cl
WHERE cl.communication_id IN (9001, 9002, 9003)
ORDER BY cl.customer_id, cl.sent_time;

-- 6. Inspect standalone campaign 9101 for legitimate repeat sends
SELECT
    cl.communication_id,
    cl.customer_id,
    cl.delivery_status,
    cl.sent_time
FROM communication_log cl
WHERE cl.communication_id = 9101
ORDER BY cl.customer_id, cl.sent_time;

-- 7. Inspect Family B retry chain
SELECT
    cl.communication_id,
    cl.customer_id,
    cl.delivery_status,
    cl.sent_time
FROM communication_log cl
WHERE cl.communication_id IN (9201, 9202)
ORDER BY cl.customer_id, cl.sent_time;

-- 8. Build root campaign mapping so multi-level retries can be treated as one family
WITH RECURSIVE campaign_tree AS (
    SELECT
        id AS campaign_id,
        id AS root_campaign_id
    FROM campaign
    WHERE merchant_id = 501
      AND parent_id IS NULL

    UNION ALL

    SELECT
        c.id AS campaign_id,
        ct.root_campaign_id
    FROM campaign c
    JOIN campaign_tree ct
        ON c.parent_id = ct.campaign_id
    WHERE c.merchant_id = 501
)
SELECT *
FROM campaign_tree
ORDER BY root_campaign_id, campaign_id;
