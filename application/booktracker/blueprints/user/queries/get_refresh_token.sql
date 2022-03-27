SELECT u.refresh_token
FROM users u
    JOIN eids e ON u.ref_id = e.ref_id
WHERE e.eid = :eid;
