import gnupg
import string
import sqlite3
import sys
from profile_env import *

class AWSCommunications:
    """ Class to gather AWS Credentials and environment paths """

    def __init__(self):
        """ Get variables from profile_env.py """

        self.file_database = file_database
        self.dir_gnupg = dir_gnupg
        self.dir_credentials = dir_credentials
        self.AWSAccount = ''
        self.zone = ''
        self.short_key = ''
        self.long_key = ''

        # Prepare DB Connection #
        try:
            self.connDB = sqlite3.connect(self.file_database)
        except sqlite3.Error as e:
            print "Error connection database: ", e.args[0]

    def set_env_from_db(self):
        """ Set environment from database """

        try:
            cur = self.connDB.cursor()
            cur.execute("SELECT * FROM GLOBAL_INFO")
            rows = cur.fetchone()
        except sqlite3.Error as e:
            print "Error reading database: ", e.args[0]

        # Fill data from database #
        try:
            self.AWSAccount = rows[0]
            self.zone = rows[1]
        except UnboundLocalError, ule:
            print "No valid rows found in database. Did you remember to run set_env.py?"
            sys.exit(1)

    def set_env_from_args(self, customer, zone):
        """ Set environment from script argparse """

        self.AWSAccount = customer
        self.zone = zone

    def decrypt_customer(self):
        """ Decrypt GPG customer """

        gpg = gnupg.GPG(homedir=self.dir_gnupg, verbose=True)
        gnupg._parsers.Verify.TRUST_LEVELS["DECRYPTION_KEY"] = ""
        gnupg._parsers.Verify.TRUST_LEVELS["DECRYPTION_COMPLIANCE_MODE"] = ""
        with open(self.dir_credentials+self.AWSAccount+'.gpg', 'rb') as f:
            status = gpg.decrypt_file(f)

        if status.ok:
            secrets = str(status)
            secrets = string.split(secrets, '\n')
            self.short_key = secrets[0]
            self.long_key = secrets[1]
            return 200
        else:
            print 'Decrypted Status: ', status.ok
            return 500

    def get_short_key(self):
        return self.short_key

    def get_long_key(self):
        return self.long_key

    def get_region(self):
        return self.zone

    def get_customer(self):
        return self.AWSAccount

