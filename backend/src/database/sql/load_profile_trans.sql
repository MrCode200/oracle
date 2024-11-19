SELECT *
FROM orders
WHERE profile_id = (SELECT profile_id
                     FROM profiles
                     WHERE profile_name = %(profile_name)s);
