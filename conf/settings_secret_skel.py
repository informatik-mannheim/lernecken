SECRET_KEY = "DEFAULT"

# LDAP connection data

"""
URI of your ldap, e.g. ldap://my.ldap.my-domain.org
"""
AUTH_LDAP_SERVER_URI = ""

"""
Template for DN, e.g. "uid=%(users)s,ou=Employees,dc=my-domain,dc=org". 
Be sure to have the '%(users)s' part set.
"""
AUTH_LDAP_USER_DN_TEMPLATE = ""

"""
Mappings for first name and last name. Change 'givenName' and 'sn' if necessary.
"""
AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName", "last_name": "sn"}

"""
Authentication data of a test user in your LDAP. Necessary only for test execution.
"""
TEST_USER_NAME = "user"
TEST_USER_PASS = "pass"
