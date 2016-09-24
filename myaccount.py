import config
import ldap.modlist as modlist
from myldap import MyLDAP
from mygroup import MyGroup as gr

ld = MyLDAP()


class MyAccount(object):
	@classmethod
	def add_to_ldap(cls):
		"""
		Add new user to LDAP
		:return: Successfully or Error
		"""
		mod_list = {'objectClass': ['top', 'organizationalPerson', 'inetOrgPerson']}
		while True:
			uname = raw_input('Username? ')
			if ld.ldap_check_exist(uname):
				print("Username  %s existed. Try another name." % uname)
			else:
				mod_list['cn'] = uname
				break

		mod_list['givenName'] = raw_input('First Name? ')
		mod_list['sn'] = raw_input('Last Name? ')
		mod_list['displayName'] = mod_list['givenName'] + " " + mod_list['sn']
		mod_list['uid'] = mod_list['cn']
		mod_list['mail'] = raw_input('Mail? ')

		is_posix = raw_input('PosixAccount? (y/n) ')
		if is_posix == 'y':
			mod_list['objectClass'].append('posixAccount')
			mod_list['objectClass'].append('ldapPublicKey')
			prigroup = raw_input('Primary Group? ')
			mod_list['gidNumber'] = gr.search_by_name(prigroup)[1]['gidNumber'][0]
			mod_list['uidNumber'] = raw_input('uidNumber? ')
			mod_list['homeDirectory'] = '/home/' + uname
			mod_list['loginShell'] = '/bin/bash'
			mod_list['sshPublicKey'] = str(raw_input('Publickey? '))
		
		"""
		
		TODO: determine user DN here
		
		"""
		
		userdn = ""
		try:
			ld.ld.add_s(userdn, modlist.addModlist(mod_list))
			if is_posix == 'y':
				cls.add_to_group(uname, [prigroup])
			print("Added account %s successfully." % uname)
		except Exception, e:
			print(e)

	@staticmethod
	def add_to_group(cn, grouplist):
		"""
		Add user to group
		:param cn: username (cn)
		:param grouplist: list of groups
		:return: Successfully or Error
		"""
		for group in grouplist:
			if ld.ldap_check_exist(group):
				oldlist = {}
				newlist = {}
				gdn = gr.search_by_name(group)[0]
				searchfilter = "(&(objectClass=posixGroup)(cn=%s))" % group
				result = ld.ldap_search(searchfilter)
				if 'memberUid' not in result[0][0][1].keys():
					result[0][0][1]['memberUid'] = []

				old = result[0][0][1]['memberUid']
				new = list(old)
				new.append(cn)
				oldlist['memberUid'] = old
				newlist['memberUid'] = new

				try:
					ld.ld.modify_s(gdn, modlist.modifyModlist(oldlist, newlist))
					print("Added account %s to group %s successfully." % (cn, group))
				except Exception, e:
					print(e)
			else:
				print("Group %s not found." % group)

	@classmethod
	def add_posix(cls, cn):
		"""
		Add posixAccount, ldapPublicKey objectClass to user
		:param cn: username (cn)
		:return: Successfully or Error
		"""
		searchfilter = "(cn=%s)" % cn
		result = ld.ldap_search(searchfilter)
		if not result:
			print("Account not found.")
		else:
			userdn = result[0][0][0]
			oldlist = result[0][0][1]
			newlist = dict(oldlist)
			if 'posixAccount' not in newlist['objectClass']:
				if 'pwmEventLog' in newlist.keys():
					del newlist['pwmEventLog']
				if 'uid' not in newlist.keys():
					newlist['uid'] = newlist['cn']
				new_obj = list(newlist['objectClass'])
				new_obj.append('posixAccount')
				new_obj.append('ldapPublicKey')
				newlist['objectClass'] = new_obj

				prigroup = raw_input('Primary Group? ')
				newlist['gidNumber'] = gr.search_by_name(prigroup)[1]['gidNumber'][0]
				newlist['uidNumber'] = raw_input('uidNumber? ')
				newlist['homeDirectory'] = '/home/' + cn
				newlist['loginShell'] = '/bin/bash'
				newlist['sshPublicKey'] = str(raw_input('Publickey? '))

				try:
					ld.ld.modify_s(userdn, modlist.modifyModlist(oldlist, newlist))
					print("Update account %s successfully" % cn)
					cls.add_to_group(cn, [prigroup])
				except Exception, e:
					print(e)
			else:
				print("Account has had posixAccount attribute already.")

	@staticmethod
	def modify_attr(cn, attr):
		"""
		Modify user's current attributes
		:param cn: username (cn) to modify
		:param attr: attribute name
		:return: Successfully or Error
		"""
		searchfilter = "(cn=%s)" % cn
		result = ld.ldap_search(searchfilter)
		userdn = result[0][0][0]
		oldattr = result[0][0][1][attr]
		newattr = []
		oldlist = {}
		newlist = {}
		print("Old value of %s : %s" % (attr, oldattr[0]))
		na = raw_input('New value? ')
		newattr.append(na)

		oldlist[attr] = oldattr
		newlist[attr] = newattr
		try:
			ld.ld.modify_s(userdn, modlist.modifyModlist(oldlist, newlist))
			print("Update attribute %s successfully" % attr)
		except Exception, e:
			print(e)

	@staticmethod
	def search_membership(cn):
		"""
		Check user's membership
		:param cn: username
		:return: list of groups which user is belong to
		"""
		searchfilter = "(&(objectClass=posixGroup)(memberUid=%s))" % cn
		result = ld.ldap_search(searchfilter)
		grouplist = []
		if not result:
			return None
		else:
			for g in result:
				grouplist.append(g[0][1]['cn'][0])
			return grouplist

	@staticmethod
	def search_by_name(cn):
		"""
		:param cn: username
		:return: dn (string) and user infos (dict)
		"""
		searchfilter = "(&(objectClass=inetOrgPerson)(cn=%s))" % cn
		result = ld.ldap_search(searchfilter, basedn=config.user_basedn)
		if not result:
			return None, None
		else:
			return result[0][0][0], result[0][0][1]

	@staticmethod
	def search_by_mail(mail):
		"""
		:param mail: user's mail
		:return: dn (string) and user infos (dict)
		"""
		searchfilter = "(&(objectClass=inetOrgPerson)(mail=%s))" % mail
		result = ld.ldap_search(searchfilter, basedn=config.user_basedn)
		if not result:
			return None, None
		else:
			return result[0][0][0], result[0][0][1]

	@staticmethod
	def search_by_id(uid):
		"""
		:param uid: user's uidNumber
		:return: dn (string) and user infos (dict)
		"""
		searchfilter = "(&(objectClass=inetOrgPerson)(uidNumber=%s))" % uid
		result = ld.ldap_search(searchfilter, basedn=config.user_basedn)
		if not result:
			return None, None
		else:
			return result[0][0][0], result[0][0][1]

	@classmethod
	def remove_from_ldap(cls, cn):
		"""
		:return: Successfully or Error
		"""
		ld.ldap_remove(cn)
		cls.remove_from_group(cn)

	@staticmethod
	def remove_from_group(cn):
		"""
		Remove user (MemberUid) from groups
		:param cn: username (cn) to remove
		:return: Successfully or Error
		"""
		# Get where user belong to
		searchfilter1 = "(&(objectClass=posixGroup)(memberUid=%s))" % cn
		result1 = ld.ldap_search(searchfilter1)
		if not result1:
			print("Account not belong to any group.")
			return None
		else:
			grouplist = []
			for group in result1:
				grouplist.append(group[0][1]['cn'][0])

		# Remove user from where it belongs to
		for g in grouplist:
			searchfilter2 = "(&(objectClass=posixGroup)(cn=%s))" % g
			result2 = ld.ldap_search(searchfilter2)
			gdn = result2[0][0][0]
			oldlist = result2[0][0][1]
			newlist = dict(oldlist)
			newmem = list(oldlist['memberUid'])
			newmem.remove(cn)
			newlist['memberUid'] = newmem
			try:
				ld.ld.modify_s(gdn, modlist.modifyModlist(oldlist, newlist))
				print("Remove %s from group %s successfully." % (cn, g))
			except Exception, e:
				print(e)

	@classmethod
	def print_info(cls, infos):
		"""
		Print all user information
		:param infos: user information
		:return: all user informations include membership, sudo rights, etc
		:return:
		"""
		i = infos[1]
		full_name = i['displayName'][0] if 'displayName' in i.keys() else None
		email = i['mail'][0] if 'mail' in i.keys() else None

		print(100 * '#')
		print("User information:\n")
		print("\t- User    : %s" % infos[0])
		print("\t- Fullname: %s" % full_name)
		print("\t- Email   : %s" % email)

		is_posixAccount = True if 'posixAccount' in i['objectClass'] else False
		if is_posixAccount:
			username = i['uid'][0] if 'uid' in i.keys() else None
			uid = i['uidNumber'][0] if 'uidNumber' in i.keys() else None
			gid = i['gidNumber'][0] if 'gidNumber' in i.keys() else None
			publickey = i['sshPublicKey'][0] if 'sshPublicKey' in i.keys() else None
			groupname = gr.search_by_id(gid)[1]['cn'][0]
			memberof = cls.search_membership(username)

			print("\t+ Have posix account: %s" % is_posixAccount)
			print("\t- Username : %s" % username)
			print("\t- Uid      : %s" % uid)
			print("\t- Gid      : %s" % gid)
			print("\t- Primary Group: %s" % groupname)
			print("\t- Publickey: %s" % publickey)
			print("\t- Member of: %s" % memberof)

			if memberof != None:
				for g in memberof:
					gr.print_info(g)
