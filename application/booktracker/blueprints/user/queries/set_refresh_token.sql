WITH ref as (
    SELECT ref_id
    FROM eids
    WHERE eid = :eid
)
UPDATE users
SET refresh_token = :refresh_token
FROM users
WHERE ref_id = ref_id;
