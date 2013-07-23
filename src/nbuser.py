# NetBasm user functions

import os
from getpass import getpass
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto import Random
import time
import nbutils
import re
import pyzerial
import base64

# <=== MAIN USER VARIABLES ===>

"""
A hashed version of the current user's password.
It is used to decrypt files without storing the password itself.
"""
sessionHash = None;
"""
A cache of the root path to the current user's files.
"""
userPath = "";
"""
The head object of the current user.
"""
userObject = None;
"""
The name of the current user.
"""
userName = "";
"""
The RSA key pair that is used to indentify the user.
"""
userCertificate = None;

# <=== END OF USER VARIABLES ===>

# Parser stuff
reKey = re.compile( r"[a-zA-Z_0-9\.]+" );
reNum = re.compile( r"[0-9]+" );
reData = re.compile( r"[^\n]*" );

# UserObject

class UserObject( object ):
  """
  A class representing encrpyted objects belonging to a specific user.
  The objects are loaded and saved to a file for persistency.
  An UserObject is just a fancy 'dict' wrapper.
  """

  @classmethod
  def loadObject( this ,  fname ):
    """
    Loads an encrypted user file.
    if the file format or the key is invalid 'None' will be returned.
    If the file is decryped corretly a new UserObject will be returned.

    fname -- The name of the file to load.
    """
    global userPath;
    fpath = os.path.join( userPath , fname );
    if not os.path.exists( fpath ):
      return None;
    with open( fpath , "rb" ) as f:
      fdata = f.read();
      cipher , _ = newCipher( fdata[:AES.block_size] );
      fdata = cipher.decrypt( fdata[AES.block_size:] );
    if fdata[:9] != "@NETBASM\n":
      return None;
    fdata = fdata[9:]; # fdata is now an array of key/values
    robj = this( **pyzerial.load( fdata ) ); # Make a new UserObject
    robj._unsaved = False;
    robj._path = fname;
    return robj;

  @classmethod
  def saveObject( this , fname , obj ):
    """
    Saves an UserObject to the specified file.
    ( By calling 'obj.save( fname )' )

    fname -- The name of the file to save to.
    obj -- The object to save to the specified file.
    """
    obj.save( fname );

  def __init__( self , **kwargs ):
    """
    Creates a new UserObject.

    kwargs -- An unzipped 'dict' containing the initial values.
    """
    self._internal = kwargs;
    self._unsaved = True;
    self._path = None;

  def __setitem__( self , key , item ):
    """
    Sets an item inside the internal 'dict'.
    And if any new changes are made, the 'unsaved' flag will be raised.

    key -- The key of the value.
    item -- The value to set the key to.
    """
    if not self._internal.has_key( key ) or self._internal[key] != item:
      self._unsaved = True;
    self._internal[key] = item;

  def __getitem__( self , key ):
    """
    Gets an item from the internal 'dict'.

    key -- The key of the item to get.
    """
    return self._internal[key];

  def __delitem__( self , key ):
    """
    Deltes an item.
    Raises the 'unsaved' flag.

    key -- The key of the item to delete.
    """
    del self._internal[key];
    self._unsaved = True;

  def __del__( self ):
    """
    Saves the object if the 'unsaved' flag is raised and there is a valid path.
    """
    if self._unsaved and self._path:
      self.save( self._path );

  def has_key( self , key ):
    """
    The same as '{}.has_key( key )'

    key -- The key to check for.
    """
    return self._internal.has_key( key );

  def load( self , fname=None ):
    """
    Loads an object from an encrypted file.
    This method will raise an IOError if the file format is invalid or
    the decryption failed. The loaded object will to saved to the interal 'dict'

    fname -- [Optional] Specifies what file to load. Defualts to the last
    registered file path ( if any, else an IOError will be raised ).
    """
    global userPath;
    if fname:
      self._path = fname;
    elif self._path:
      fpath = self._path;
    else:
      raise IOError( "No path to load from!" );
    fpath = os.path.join( userPath , self._path );
    if not os.path.exists( fpath ):
      raise IOError( "File: '%s', does not exists!" % ( fpath ) );
    with open( fpath , "rb" ) as f:
      fdata = f.read();
      cipher , _ = newCipher( fdata[:AES.block_size] );
      fdata = cipher.decrypt( fdata[AES.block_size:] );
    if fdata[:9] != "@NETBASM\n":
      raise IOError( "Invalid decryption key for file '%s'!" % ( fpath ) );
    fdata = fdata[9:]; # fdata is now an array of key/values
    self._internal = pyzerial.load( fdata );
    self._unsaved = False;

  def save( self , fname=None ):
    """
    Saves the internal 'dict' to an encrypted file.

    fname -- [Optional] Specifies what file to save to. Defualts to the last
    registered file path ( if any, else an IOError will be raised ).
    """
    global userPath;
    if not self._unsaved:
      return;
    if fname:
      self._path = fname;
    elif self._path:
      fpath = self._path;
    else:
      raise IOError( "No path to save to!" );
    fpath = os.path.join( userPath , self._path );
    with open( fpath , "wb" ) as f:
      cipher , iv = newCipher();
      f.write( iv );
      fdata = "@NETBASM\n" + pyzerial.save( self._internal );
      f.write( cipher.encrypt( fdata ) );
    self._unsaved = False;

  def __repr__( self ):
    return "<UserObject '%s' %s>" % ( self._path or "" ,
                                      str( self._internal ) );


# user functions

def setupFileSystem():
  """
  Sets up all 'baseFodlers' so that the basic file system will work.
  """
  for folder in nbutils.baseFolders.values():
    if not os.path.exists( folder ):
      os.mkdir( folder );

def newCipher( iv=None , session=None ):
  """
  Returns a new cipher object.

  iv -- [Optional] The initialization vector, used by the cipher. Defualts to a
  randomly generated one.
  session -- [Optionnal] The crypto key used by the cipher. Defualts to the
  current user 'sessionHash'.
  """
  if not session:
    session = sessionHash;
  if not iv:
    iv = Random.new().read( AES.block_size );
  return AES.new( session , AES.MODE_CFB , iv ) , iv;

def checkUser( username ):
  """
  Checks if the specified user exists. Returns true of so.

  username -- The username of the specified user.
  """
  username = username.lower();
  tpath = os.path.join( nbutils.baseFolders['userroot'] , username , ".user" );
  return os.path.exists( tpath );

def createNewUser( username ):
  """
  Starts a prompting process that will create a new user, and logs into it.

  username -- The username of the specified user.
  """
  global sessionHash , userPath;
  userPath = os.path.join( nbutils.baseFolders['userroot'] , username );
  if not os.path.exists( userPath ):
    os.mkdir( userPath );
  while True:
    print "Please enter a password you can remember."
    password = getpass( "Password: " );
    print "And again to be sure."
    if password == getpass( "Password: " ):
      hasher = SHA256.new( password );
      password = hasher.digest();
      break;
    else:
      print "They are not the same! Try again."
  sessionHash = password;
  obj = UserObject( creationTime= int( time.time() ) );
  obj.save( ".user" );
  loginTo( username , password );

def loginTo( user , session ):
  """
  Logs into the specified user and returns their 'userObject'.
  Returns None if the login failed.

  user -- The username of the specified user.
  session -- The hashed password( access key ) of the specified user.
  """
  global userPath , sessionHash , userObject;
  userPath = os.path.join( nbutils.baseFolders['userroot'] , user );
  sessionHash = session;
  userObject = UserObject.loadObject( ".user" );
  if userObject: # We have the right password
    userObject._path = ".user";
    userName = user;
    print "Logged into "+user;
    userObject["lastLogin"] = int( time.time() );
    loadCertificate();
  else:
    print "Failed login!";
    sessionHash = None;
    userPath = "";
    return None; # Login failed
  return userObject;

def loadCertificate():
  if userObject.has_key( "certificate" ):
    fcert = userObject["certificate"];
    userCertificate = { "private" : RSA.importKey( fcert["private"] ) ,
                        "public" : RSA.importKey( fcert["public"] ) };
  else:
    print """Generating a new certificate to you ( RSA 4096 bit ). This\
 certificate will be
the only way to identify you ( Anonymously ). Without it, you can't prove that
you are the same person, to others. NEVER give out your private key to ANYONE,
this can lead to massive security and identity problems. And should be avoided
doesn't matter what."""
    userCertificate = RSA.generate( 4096 );
    pubkey = userCertificate.publickey();
    userObject["certificate"] = { "private" : userCertificate.exportKey() ,
                                  "public" : pubkey.exportKey() };
    userObject.save( ".user" );
    print "The key was generated and stored."

def logout():
  """
  Logs out of the current user.
  """
  global userPath , sessionHash , userObject , userName;
  userObject.save( ".user" );
  userPath = "";
  sessionHash = None;
  userObject = None;
  userCertificate = None;
  print "Logged %s out." % ( userName );
  userName = "";
