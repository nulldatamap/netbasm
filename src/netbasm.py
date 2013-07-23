#!/usr/bin/python2.7
import os
from getpass import getpass
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random
import time
from nbutils import *
import nbuser

def login():
  """
  Gives the user the ability to login to an existing user, or create a new one.
  """
  print "Welcome to %s v%s, please log in:" % ( APPLICATION_NAME ,
                                              APPLICATION_VERSION );
  while True:
    print "Username:",;
    username = raw_input();
    if not validateKey( username ):
      print "Usernames can only contain alphanumerals, '_'s and '.'s.";
      continue;
    if not nbuser.checkUser( username ):
      print "Unknown user, want to make a new one?",
      if yesOrNo():
        nbuser.createNewUser( username );
        break;
      print "Ok, try again then."
    else:
      # Pro tip, watch out for the keyloggers ;)
      hasher = SHA256.new( getpass( "Password: " ) );
      password = hasher.digest();
      del hasher; # Can't be to paranoid can we?
      if not nbuser.loginTo( username , password ):
        print "Invalid password! Try again."
      else:
        break;

def main():
  nbuser.setupFileSystem();
  login();
  #startNode();
  #joinNetwork();
  #syncData();
  # user action
  nbuser.logout();
  print "Bye!"

if __name__ == "__main__":
	main();
