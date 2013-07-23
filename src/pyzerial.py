# Pyzerial
# A module for serializing Python data structures safely.
import struct;

def save( obj ):
  """
  Save a Python object to a string.
  Classes, instances, modules and functions are not allowed.
  MUST BE SAVED IN BINARY MODE.

  obj -- The object to save.
  """
  out = "";
  if type( obj ) == dict:
    out += "d";
    for key in obj.keys():
      out += save( key ) + save( obj[key] );
    out += "\n";
  elif type( obj ) == list or type( obj ) == tuple:
    out += "a";
    for elem in obj:
      out += save( elem );
    out += "\n";
  elif type( obj ) == int:
    out += "i";
    out += struct.pack( "!i" , obj );
  elif type( obj ) == long:
    out += "l";
    out += struct.pack( "!q" , obj );
  elif type( obj ) == float:
    out += "f";
    out += struct.pack( "!d" , obj );
  elif type( obj ) == bool:
    out += "b";
    out += struct.pack( "?" , obj );
  elif type( obj ) == str:
    out += "s";
    out += struct.pack( "!H" , len( obj ) ) + obj
  elif obj == None:
    out += "n";
  else:
    raise ValueError( "Unserializable object '%s'!" % ( str( obj ) ) );
  return out;

def loads( data ): # This is for embedded use, since it only loads 1 object.
  """
  Loads a Python object from a string.
  Returns both the loaded object, and the size of the read string.
  MUST BE LOADED IN BINARY MODE.

  data -- The string to load from.
  """
  offset = 1;
  out = None;
  if data[0] == 'd':
    out = {};
    while data[offset] != '\n':
      key , size = loads( data[offset:] );
      offset += size;
      out[key] , size = loads( data[offset:] );
      offset += size;
    return out , offset+1;
  elif data[0] == 'a':
    out = [];
    while data[offset] != '\n':
      elem , size = loads( data[offset:] );
      offset += size;
      out.append( elem );
    return out , offset+1;
  elif data[0] == 'i':
    return struct.unpack( "!i" , data[1:5] )[0] , 5;
  elif data[0] == 'l':
    return struct.unpack( "!q" , data[1:9] )[0] , 9;
  elif data[0] == 'f':
    return struct.unpack( "!d" , data[1:9] )[0] , 9;
  elif data[0] == 'b':
    return struct.unpack( "?" , data[1:2] )[0] , 2;
  elif data[0] == 's':
    length = struct.unpack( "!H" , data[1:3] )[0];
    return data[ 3 : 3+length ] , 3 + length;
  elif data[0] == 'n':
    return out , 1;
  else:
    raise ValueError( "Invalid pyzerial format!" );

def load( data ):
  """
  Loads a Python object from a string.
  Returns the loaded object.
  MUST BE LOADED IN BINARY MODE.

  data -- The string to load from.
  """
  return loads( data )[0]; # Discard the length value
