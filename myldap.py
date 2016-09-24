import config
import ldap


class MyLDAP(object):
    def __init__(self, uri=None, binddn=None, bindpw=None):
        self.uri = config.ldap_uri
        self.binddn = config.binddn
        self.bindpw = config.bindpw
        self.ld = self.__ldap_init()

    def __ldap_init(self):
        """
        Initializate connection to LDAP server
        :return: None
        """
        try:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            l = ldap.initialize(self.uri)
            l.set_option(ldap.OPT_REFERRALS, 0)
            l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            l.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
            l.set_option(ldap.OPT_X_TLS_DEMAND, True)
            l.set_option(ldap.OPT_DEBUG_LEVEL, 255)
            l.protocol_version = ldap.VERSION3
            l.simple_bind_s(self.binddn, self.bindpw)
            return l
        except ldap.LDAPError, e:
            return e

    def ldap_search(self, searchfilter, basedn=config.basedn):
        """
        Use for search
        :param searchfilter: LDAP filter format
        :param basedn: basedn to start search
        :return: search result
        """
        try:
            result = self.ld.search(basedn, ldap.SCOPE_SUBTREE, searchfilter, None)
            result_set = []
            while True:
                result_type, result_data = self.ld.result(result, 0)
                if not result_data:
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        result_set.append(result_data)
            return result_set
        except ldap.LDAPError, e:
            print(e)

    def ldap_remove(self, entry):
        """
        Remove user/group from ldap
        :param entry: user/group name
        :return: Successfully or Error
        """
        searchfilter = "(cn=%s)" % entry
        result = self.ldap_search(searchfilter)
        if result:
            entrydn = result[0][0][0]
            print 'Found : %s' % entrydn
            confirm = raw_input('Do you REALLY want to DELETE it? (y/n) ')
            if confirm == 'y':
                try:
                    self.ld.delete_s(entrydn)
                    print("Remove %s successfully." % entry)
                except ldap.LDAPError, e:
                    print(e)
        else:
            print("%s not exist." % entry)

    def ldap_check_exist(self, entry):
        """
        Check if user/group exist or not
        :param entry: username or groupname to check
        :return: True if exist, False otherwise
        """
        searchfilter = "(cn=%s)" % entry
        result = self.ldap_search(searchfilter)
        if not result:
            return False
        else:
            return True
