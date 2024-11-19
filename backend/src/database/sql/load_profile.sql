SELECT *
FROM profiles
WHERE (%(profile_name)s IS NULL OR profile_name = %(profile_name)s);
