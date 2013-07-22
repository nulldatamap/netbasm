# Remote and local node code
import socket
import nbuser
from select import select
from nbutils import *

class LocalNode( object ):
  """
  An object representing a local node.
  """
  def __init__( self ):
    self.publickey = nbuser.userObject["certificate"]["public"];
    self.privatekey = nbuser.userObject["certificate"]["private"];
    self.nodeId = nbuser.userName;

class Node( object ):
  """
  An object representing a remote node.
  """
  def __init__( self ):
    pass

