SELECT *
FROM profile
WHERE (:profile_name IS NULL OR profile_name = :profile_name);
