# Remote and local node code
import socket
from nbuser import *
from select import select
from nbutils import *
from threading import Thread , Lock

JOB_STATUS_READY = 0;
JOB_STATUS_PENDING = 1;
JOB_STATUS_DONE = 2;

class Job( object ):
  def __init__( self , workfunc , **kwargs ):
    self.status = JOB_STATUS_READY;
    self.data = kwargs;
    self.workfunc = workfunc;

  def work( self ):
    self.status = self.workfunc( self.data );

class Worker( Thread ):
  def __init__( self , name ):
    Thread.__init__( self , None , self , name );
    self.operations = []; # async operation queue
    self.lock = Lock();
    self.jobs = [];
    self.alive = True;

  def run( self ):
    while self.alive:
      for op in getOps():
        assignJob( op );
      for job in self.jobs:
        if job.status != JOB_STATUS_DONE:
          job.work();
        else:
          self.jobs.remove( job );

  def assignJob( self , op ):
    op , args = op;
    # Work on job types

  def queueOp( self , operation , *args ):
    # For outside the thread use.
    _OpOperation( False , operation , args );

  def getOps( self ):
    return _OpOperation( True );

  def stop( self ):
    alive = False;

  def _OpOperation( self , rw , op=None , args=[] ):
    # For thread safe access.
    with self.lock:
      if rw:
        value = self.operations;
        self.operations = [];
        return value;
      else:
        self.operations.append( ( op , args ) );


class LocalNode( Worker ):
  """
  An object representing a local node.
  """
  def __init__( self ):
    Worker.__init__( self , "localNodeWorker" );
    self.publickey = userObject["certificate"]["public"];
    self.privatekey = userObject["certificate"]["private"];
    self.nodeId = userName;
    # TCP because this port should be open.
    self.serverSocket = socket.socket( socket.AF_INET , socket.SOCK_STREAM );
    self.serverSocket.bind( ( '' , userObject["serverPort"] ) );

  def run( self ):
    self.serverSocket.listen( 4 );
    self.jobs.append( Job( acceptNode ) );
    Worker.run( self );

  def acceptNode( self , data ):
    rl , wl , el = select( [ serverSocket ] , [] , [] );
    if rl:
      sock , addr = self.serverSocket.accept();
      self.jobs.append( Job( handshakeNode , node= Node( sock , addr )
                            , state= 0 ) );
      return JOB_STATUS_READY; # Operation intent finished
    return JOB_STATUS_PENDING;

  def handshakeNode( self , data ):
    if data["state"] == 0:
      self.jobs.append( Job( writeTo ) );

  def assignJob( self , op ):
    op , args = op;
    # Work on job types

class Node( object ):
  """
  An object representing a remote node.
  """
  def __init__( self , sock , addr ):
    self.socket = sock;
    self.address = addr;
    self.alias = None;
    self.publicKey = None;
    self.userData = {};

