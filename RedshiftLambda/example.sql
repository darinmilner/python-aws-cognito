-- Create new user (redshift)
CREATE USER sysadmin PASSWORD "verysecret";

-- Alter user, give sysadmin permissions (redshift)
ALTER USER sysadmin CREATEUSER;

-- Update permissions on a user for a schema  https://hevodata.com/learn/amazon-redshift-create-schema-syntax-usage/
GRANT { { CREATE | USAGE } [,...] | ALL [ PRIVILEGES ] }
ON SCHEMA schema_name [, ...]
TO { username [ WITH GRANT OPTION ] | GROUP group_name | PUBLIC } [, ...]