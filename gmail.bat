REM Sample startup batch file for GMAIL IMAP client
REM replace the sample account names and passwords with your
REM account credentials.
REM inccrement the number of the GMAILX environment variable to
REM add more accounts.
REM 
REM See gmail.py for more details on account configuration.

@echo off
set GMAIL1=user1@gmail.com password1234
set GMAIL2=user2@gmail.com password4321
python gmail.py
pause
