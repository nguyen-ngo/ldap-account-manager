import config
from myldap import MyLDAP

ld = MyLDAP()


class MyGroup(object):
	def add_to_ldap(self):
		pass

	@staticmethod
	def search_by_name(cn):
		"""
		:param cn: name of group
		:return: dn (string) and group infos (dict)
		"""
		searchfilter = "(&(objectClass=posixGroup)(cn=%s))" % cn
		result = ld.ldap_search(searchfilter, basedn=config.group_basedn)
		if not result:
			return None, None
		else:
			return result[0][0][0], result[0][0][1]

	@staticmethod
	def search_by_id(gid):
		"""
		:param gid: group's gidNumber
		:return: dn (string) and group infos (dict)
		"""
		searchfilter = "(&(objectClass=posixGroup)(gidNumber=%s))" % gid
		result = ld.ldap_search(searchfilter, basedn=config.group_basedn)
		if not result:
			return None, None
		else:
			return result[0][0][0], result[0][0][1]

	@staticmethod
	def search_member(cn):
		"""
		Print user in group
		:param cn: name of group
		:return: member of group
		"""
		searchfilter1 = "(&(objectClass=posixGroup)(cn=%s))" % cn
		result1 = ld.ldap_search(searchfilter1)
		if not result1:
			print('Group have no member')
		else:
			members = result1[0][0][1]['memberUid']
			for mem in members:
				searchfilter2 = "(&(objectClass=inetOrgPerson)(cn=%s))" % mem
				result2 = ld.ldap_search(searchfilter2)
				for data in result2:
					attr = data[0][1]
					fullname = attr['displayName'][0] if 'displayName' in attr else None
					username = attr['cn'][0] if 'cn' in attr else None
					mail = attr['mail'][0] if 'mail' in attr else None
					print "%s\t%s\t%s" % (fullname, username, mail)

	@staticmethod
	def remove_from_ldap(cn):
		"""
		:param cn: name of group
		:return: Successfully or Error
		"""
		ld.ldap_remove(cn)

	@classmethod
	def print_info(cls, cn):
		"""
		Print group information
		:param cn: group name or group id
		:return: group id, sudo rights of group
		"""
		try:
			if isinstance(int(cn), int):
				gid = cn
				gname = cls.search_by_id(cn)[1]['cn'][0]
		except ValueError:
			gid = cls.search_by_name(cn)[1]['gidNumber'][0]
			gname = cn

		searchfilter = "(&(objectClass=sudoRole)(sudoUser=*%s))" % gname
		result = ld.ldap_search(searchfilter)
		if not result:
			return None
		else:
			print '\t+ Group name: %s' % gname
			print '\t+ Group ID: %s' % gid
			print '\t+ Group privileges:'
			for i in result:
				sudoHost = i[0][1]['sudoHost'] if 'sudoHost' in i[0][1] else None
				sudoCommand = i[0][1]['sudoCommand'] if 'sudoCommand' in i[0][1] else None
				sudoRunAsUser = i[0][1]['sudoRunAsUser'] if 'sudoRunAsUser' in i[0][1] else None
				sudoUser = i[0][1]['sudoUser'] if 'sudoUser' in i[0][1] else None

				print '\t  - cn: %s' % i[0][0]
				print '\t    sudoHost: %s' % sudoHost
				print '\t    sudoCommand: %s' % sudoCommand
				print '\t    sudoRunAsUser: %s' % sudoRunAsUser
				print '\t    sudoUser: %s' % sudoUser
				print '\n'