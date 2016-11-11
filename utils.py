import os
import random
import config
import hashlib
import smtplib

from base64 import encodestring as encode
from base64 import decodestring as decode


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

   \t [5]  - Add account to group
   \t [6]  - Remove account from groups
   \t [7]  - Add posixAccount to account
   \t [8]  - Modify account attribute
   \t [9]  - Reset password

   \t [10] - Create new account
   \t [11] - Create new group
   \t [12] - Remove account
   \t [13] - Remove group

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


def GetMaxUidNumber():
    '''
    Get PosixAccount max UidNumber (from file)
    :return: max_uid
    '''
    fobj = open(config.maxuid_file, 'r')
    max_uid = fobj.readline().rstrip()
    fobj.close()
    return max_uid


def IncreaseMaxUidNumber():
    '''
    Increase max UidNumber (to file)
    :return: None
    '''
    fobj = open(config.maxuid_file, 'r+')
    old_id = fobj.readline().rstrip()
    new_id = int(old_id) + 1
    fobj.seek(0)
    fobj.write(str(new_id))
    fobj.close()


def randomString(length=12):
    """
    Generate a string with length provided
    :param length: length of string to be generated
    :return: random string
    """
    rt = []
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890~!@#$%^&*-_+='
    for i in range(1, length + 1):
        rt.append(random.choice(chars))
    rt = "".join(rt)
    return rt


def makeSecret(string):
    """
    Make a secret SSHA hashed string for LDAP password
    :param string: raw string
    :return: SSHA hashed string
    """
    salt = os.urandom(4)
    h = hashlib.sha1(string)
    h.update(salt)
    return "{SSHA}" + encode(h.digest() + salt)


def checkPassword(challenge_password, password):
    """
    Check LDAP password
    :param challenge_password: SSHA hashed password
    :param password: raw password
    :return: True if match or False otherwise
    """
    challenge_bytes = decode(challenge_password[6:])
    digest = challenge_bytes[:20]
    salt = challenge_bytes[20:]
    hr = hashlib.sha1(password)
    hr.update(salt)
    return digest == hr.digest()


def sendMail(recipient='client@example.com', content=''):
    """
    Send mail through Gmail/Yahoo smtp
    :param recipient: who will receive this mail
    :param content:
    :return: Successfully or Not
    """
    mail_user = 'ldap_master@example.com'
    mail_pwd = ''
    FROM = mail_user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = 'Username and Password for central authentication'
    TEXT = content

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        """
        server = smtplib.SMTP("smtp.mail.yahoo.com", 587)
        server.ehlo()
        server.starttls()
        server.login(mail_user, mail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'Mail sent successfully.'
        """
        # SMTP_SSL Example
        server_ssl = smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465)
        server_ssl.ehlo()  # optional, called by login()
        server_ssl.login(mail_user, mail_pwd)
        # ssl server doesn't support or need tls, so don't call server_ssl.starttls()
        server_ssl.sendmail(FROM, TO, message)
        # server_ssl.quit()
        server_ssl.close()
        print 'Mail sent successfully.'
    except Exception, e:
        print e
