#!/usr/local/bin/python
import utils
from myldap import MyLDAP
from myaccount import MyAccount
from mygroup import MyGroup


def main(lo, ao, go):
    while True:
        utils.Welcome()
        choice = utils.Todo()
        if choice == '1':
            account = raw_input('What account? ')
            if lo.ldap_check_exist(account):
                userdata = ao.search_by_name(account)
                ao.print_info(userdata)
                utils.WaitUser()
            else:
                print("Account not found.")
                utils.WaitUser()
        elif choice == '2':
            email = raw_input('What email? ')
            userdata = ao.search_by_mail(email)
            if userdata != (None, None):
                ao.print_info(userdata)
                utils.WaitUser()
            else:
                print("Account not found.")
                utils.WaitUser()
        elif choice == '3':
            group = raw_input('What group? ')
            if lo.ldap_check_exist(group):
                go.print_info(group)
                utils.WaitUser()
            else:
                print("Group not found.")
                utils.WaitUser()
        elif choice == '4':
            group = raw_input('What group? ')
            if lo.ldap_check_exist(group):
                go.search_member(group)
                utils.WaitUser()
            else:
                print("Group not found.")
                utils.WaitUser()
        elif choice == '5':
            account = raw_input('What account? ')
            if lo.ldap_check_exist(account):
                groups = raw_input('List of group? ')
                grouplist = groups.split(',')
                ao.add_to_group(account, grouplist)
                utils.WaitUser()
            else:
                print("Account not found.")
                utils.WaitUser()
        elif choice == '6':
            account = raw_input('What account? ')
            ao.remove_from_group(account)
            utils.WaitUser()
        elif choice == '7':
            account = raw_input('What account? ')
            if lo.ldap_check_exist(account):
                ao.add_posix(account)
                utils.WaitUser()
            else:
                print("Account not found.")
                utils.WaitUser()
        elif choice == '8':
            account = raw_input('What account? ')
            if lo.ldap_check_exist(account):
                attribute = raw_input('What attribute? ')
                ao.modify_attr(account, attribute)
                utils.WaitUser()
            else:
                print("Account not found.")
                utils.WaitUser()
        elif choice == '9':
            ao.add_to_ldap()
            utils.WaitUser()
        elif choice == '10':
            go.add_to_ldap()
            utils.WaitUser()
        elif choice == '11':
            account = raw_input('Delete account? ')
            if lo.ldap_check_exist(account):
                ao.remove_from_ldap(account)
                utils.WaitUser()
            else:
                print("Account not found.")
                utils.WaitUser()
        elif choice == '12':
            group = raw_input('Delete group? ')
            if lo.ldap_check_exist(group):
                ao.remove_from_ldap(group)
                utils.WaitUser()
            else:
                print("Group not found.")
                utils.WaitUser()
        elif choice == '0':
            print("Bye bye.")
            exit()
        else:
            print("Invalid choice. Please try again.")
            utils.WaitUser()


if __name__ == '__main__':
    # Init ldap object
    l = MyLDAP()
    # Init account object
    a = MyAccount()
    # Init group object
    g = MyGroup()
    main(l, a, g)
