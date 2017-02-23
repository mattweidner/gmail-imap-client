# File: gmail.py
# Author: Matt Weidner <matt.weidner@gmail.com>
# Date: February 2017
# Description: GMAIL IMAP command line client. Navigate, read, and download
#              raw mail messages from a GMAIL account.
# TODO: Add support for XOAUTH
#   https://github.com/joestump/python-oauth2/wiki/XOAUTH-for-IMAP-and-SMTP
#
import imaplib
import sys
import pdb
import os

# If 2-factor auth for a Google account is enabled,
# create an App Password for use with this application.
# https://support.google.com/accounts/answer/185833?hl=en
#
# If 2FA is NOT enabled for a Google account, enable the
# "Allow less secure apps" option.
# https://support.google.com/accounts/answer/6010255
#
# Environment variables hold gmail account credentials
# with account name and app password separated by a space.
#
# GMAIL1=<gmail_address> <app_password>
# GAMIL2=<gmail_address> <gmail_password>
# etc.

def login_gmail(gmail_acct, gmail_pass):
	# Login to gmail with specified account username and app password.
	mail = imaplib.IMAP4_SSL('imap.gmail.com')
	mail.login(gmail_acct, gmail_pass)
	return mail

def get_message_ids(mail):
	# Returns list of unique message identifiers, in chronological order,
	# for all messages in the account's INBOX.
	mail.select("inbox")
	result, data = mail.search(None, "ALL")
	ids = data[0] # data is a list.
	id_list = ids.split() # ids is a space separated string
	return id_list

def get_metadata(gmail_conn, msg_id):
	# Returns a tuple (sender, subject)
	data = gmail_conn.fetch(msg_id, "(BODY[HEADER.FIELDS (SUBJECT FROM)])")
	head = data[1][0][1].decode("utf-8").split("\r\n")
	return head[1], head[0]

def get_message_body(gmail_conn, msg_id):
	# Returns the message body
	result, data = gmail_conn.fetch(msg_id, "(RFC822)")
	return data[0][1].decode("utf-8")

def save_message(msg_id, message):
	# Saves a message to disk as UTF-8 text.
	# Filename is <message_identifier>.txt
	f = open(msg_id.decode("utf-8") + ".txt", "w")
	f.write(message)
	f.close()
	print("   ")
	print('Message saved as: {0}.txt'.format(msg_id.decode("utf-8")))
	print("   ")

def print_help():
	print("   ")
	print("r : read current message")
	print("d : download current message")
	print("n : next message")
	print("p : previous message")
	print("q : quit")

def print_prompt(msg_id):
	print('[msg: {0}]>> '.format(msg_id.decode("utf-8")), end="")

if __name__ == "__main__":

	# Read GMAIL account credentials from environment variables.
	i = 1
	accounts = []
	env_account = ""
	env_account = os.environ.get('GMAIL{0}'.format(i))
	while env_account != None:
		accounts.append(env_account.split())
		i = i + 1
		env_account = os.environ.get('GMAIL{0}'.format(i))
	
	# Print banner
	cmd = ""
	print("   ")
	print("GMAIL IMAP client")
	print("Raw message downloader")
	print("   02/16/2017 Matt Weidner <matt.weidner@gmail.com>")
	print("   ")

	# Display the list of accounts and allow the user to choose one.
	if len(accounts) == 1:
		gmail_acct = accounts[0][0]
		gmail_pass = accounts[0][1]
	else:
		choice = len(accounts) + 1
		while choice > len(accounts) or choice < 0:
			print(" Choose a GMAIL account:")
			gmail_acct = ""
			gmail_pass = ""
			raw_in = ""
			for i, account in enumerate(accounts):
				print('    {0}: {1}'.format(i, account[0]))
			print("q to quit.")
			print("   ")
			print_prompt(b'disconnected')
			try:
				raw_in = input()
				choice = int(raw_in)
			except:
				if raw_in == 'q':
					print("   ")
					print("Thank you, come again!")
					sys.exit()
				print("Enter the index number of the account you would like to use.")
		gmail_acct = accounts[choice][0]
		gmail_pass = accounts[choice][1]

	# Login to gmail.
	print("   ")
	print('Connecting to gmail account: {0}'.format(gmail_acct))
	print("  'h' for help.")
	gmail_conn = login_gmail(gmail_acct, gmail_pass)

	# Generate a list of uniques message identifiers for the INBOX.
	id_list = get_message_ids(gmail_conn)
	# Start with the most recent message (the last ID in the list).
	x = -1
	# Get the metadata to show the user.
	sender, subject = get_metadata(gmail_conn, id_list[x])

	# Input loop
	while x < len(id_list):
		while cmd != "q":
			print(sender, subject)
			print_prompt(id_list[x])
			cmd = input()
			if cmd == "h":
				print_help()
			if cmd == "r":
				# Read the currently indexed message.
				print(get_message_body(gmail_conn, id_list[x]))
				print("   ")
			if cmd == "d":
				# Download the currently indexed message to disk.
				message = get_message_body(gmail_conn, id_list[x])
				save_message(id_list[x], message)
			if cmd == "n":
				# Move the index selector to the next message in the inbox.
				# Moving backward in time.
				# Grab the new metadata.
				x = x - 1
				sender, subject = get_metadata(gmail_conn, id_list[x])
				print("   ")
			if cmd == "p":
				# Move the index selector to the previous message in the inbox.
				# Moving forward in time.
				# Grab the new metadata.
				x = x + 1
				sender, subject = get_metadata(gmail_conn, id_list[x])
				print("   ")
		print("   ")
		gmail_conn.logout()
		print("Thank you, come again!")
		sys.exit()
