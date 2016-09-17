import os


def Welcome():
	'''
	Print list of action for user to choose
	:return: None
	'''
	msg = """LDAP Account Manager:
   \t [1]  - Search account by username
   \t [2]  - Search account by email
   \t [3]  - Search group information
   \t [4]  - Search group member
   \t [5]  - Create new account
   \t [6]  - Add account to group
   \t [7]  - Remove account from groups
   \t [8]  - Add posixAccount to account
   \t [9]  - Modify account attribute
   \t [10] - Remove account

   \t [0] - Exit"""
	os.system('clear')
	print(msg)


def Todo():
	'''
	Ask user to choose action
	:return: number of actions
	'''
	todo = raw_input('What you want to do? (choose a number) ')
	return todo


def WaitUser():
	'''
	Wait for user
	:return: None
	'''
	raw_input('Press Enter to continue ...')