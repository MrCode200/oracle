SELECT *
FROM profiles
WHERE (%(profile_id)s IS NULL OR profile_id = %(profile_id)s);