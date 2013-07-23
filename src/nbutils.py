# NetBasm Utils
import re

# Constants and global values
"""
The name of the application.
"""
APPLICATION_NAME = "Netbasm";
"""
The version of the application.
"""
APPLICATION_VERSION = "0.0.1a";
"""
The base folders used by the application.
"""
baseFolders = { 'root': "./data" , 'userroot':"./data/users" };

# Utility functions

def yesOrNo():
  """
  Prompts the user for a yes or no answer, and parse multiple answers.
  """
  while True:
    print "yes( Y ) or no( N ):",;
    answer = raw_input().lower();
    if answer in [ "yes" , "yup" , "y" , "dillermix" ]:
      return True;
    elif answer in [ "no" , "nope" , "n" , "sutmig" ]:
      return False;

def validateKey( key ):
  """
  Checks if a key only contains alphanumerals, '_'s and '.'s.
  """
  ptrn = re.compile( r"[a-zA-Z0-9_\.]+" );
  mtch = ptrn.match( key );
  return mtch and ( mtch.group(0) == key );

def validateIP( ip ):
  """
  Checks if the given IP address is valid.
  """
  ptrn = re.compile( r"[0-2]?[0-9]{1,2}\.[0-2]?[0-9]{1,2}\.[0-2]?[0-9]{1,2}\.[0-2]?[0-9]{1,2}" );
  mtch = ptrn.match( ip );
  if not mtch or ( mtch.group(0) != ip ):
    return False;
  values = mtch.group(0).split( "." );
  for i in values:
    if int(i)>255:
      return False;
  return True;
