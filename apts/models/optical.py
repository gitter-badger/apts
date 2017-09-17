import uuid
from enum import Enum

class Type(Enum):
  OPTICAL = 1
  INPUT = 2
  OUTPUT = 3
  GENERIC = 4  

class ConnectionType(Enum):
  F_1_25 = 1
  F_2 = 2
  T2 = 3

class OpticalEqipment:
  """
  Basic class for optical equipment
  """
  
  _SEPARATOR = "_"
  OUT = "out"
  IN = "in"
  
  def __init__(self, focal_length, vendor):
    self._id = str(uuid.uuid4())
    self._type = Type.OPTICAL 
    
    self.focal_length = focal_length
    self.vendor = vendor 
    
  def __str__(self):
    # Format: <vendor>
    return "{} f={}".format(self.vendor)

  def type(self):
    return self._type

  def label(self):
    return str(self)
    
  def id(self):
    return self._id  
    
  def in_id(self, connection_type):
    return self._SEPARATOR.join([self._id, connection_type.name, self.IN])
    
  def out_id(self, connection_type):
    return self._SEPARATOR.join([self._id, connection_type.name, self.OUT])
  
  def get_parent_id(name):
    return name.split(OpticalEqipment._SEPARATOR)[0]

  def _register(self, equipment):
    # Register equipment node
    equipment.add_vertex(self.id(), self)

  def _register_output(self, equipment, connection_type = ConnectionType.F_1_25):
    # Add output node
    equipment.add_vertex(self.out_id(connection_type), node_type = Type.OUTPUT, connection_type = connection_type)
    # Connect node to its output
    equipment.add_edge(self.id(), self.out_id(connection_type))

  def _register_input(self, equipment, connection_type = ConnectionType.F_1_25):
    # Add input node
    equipment.add_vertex(self.in_id(connection_type), node_type = Type.INPUT, connection_type = connection_type)
    # Connect node to its input
    equipment.add_edge(self.in_id(connection_type), self.id())

class Telescope(OpticalEqipment):
  """
  Class representing telescope
  """

  def __init__(self, aperture, focal_length, vendor = "unknown telescope", connection_type = ConnectionType.F_1_25, t2_output = False):
    self.aperture = aperture
    self.connection_type = connection_type
    self.t2_output = t2_output
    super(Telescope, self).__init__(focal_length, vendor)

  def register(self, equipment):
    """ 
    Register telescope in optical equipment graph. Telescope node is build out of two vertices:
    telescope node and its output. Telescop node is automatically connected with SPACE node.  
    """ 
    # Add telescope node
    super(Telescope, self)._register(equipment)
    # Add telescope output node and connect it to telescope
    self._register_output(equipment, self.connection_type)
    # Connect telescope node to space node
    equipment.add_edge(equipment.SPACE_ID, self.id())
    # Handling optional T2 ouptout
    if self.t2_output:
      self._register_output(equipment, ConnectionType.T2)

  def __str__(self):
    # Format: <vendor> <apertur>/<focal length>
    return "Telescope\n{} {}/{}".format(self.vendor, self.aperture, self.focal_length)

       
class Ocular(OpticalEqipment):   
  """
  Class representing ocular
  """
  
  def __init__(self, focal_length,vendor = "unknown ocular", connection_type = ConnectionType.F_1_25):
    self.connection_type = connection_type
    super(Ocular, self).__init__(focal_length, vendor)
    
  def register(self, equipment):
    """ 
    Register ocular in optical equipment graph. Ocular node is build out of two vertices:
    ocular node and its input. Ocular node is automatically connected with output IMAGE node.  
    """ 
    # Add ocular node
    super(Ocular, self)._register(equipment)
    # Add ocular input node and connect it to ocular
    self._register_input(equipment, self.connection_type)
    # Connect ocular with output eye node
    equipment.add_edge(self.id(), equipment.EYE_ID)

  def __str__(self):
    # Format: <vendor> f=<focal_length>
    return "Ocular\n{} f={}".format(self.vendor, self.focal_length)
    
class Barlow(OpticalEqipment):   
  """
  Class representing Barlow lense
  """
  
  def __init__(self, magnification, vendor = "unknown barlow", connection_type = ConnectionType.F_1_25, t2_output = False):
    self.connection_type = connection_type
    self.t2_output = t2_output
    self.magnification = magnification
    super(Barlow, self).__init__(0, vendor)
    
  def register(self, equipment):
    """ 
    Register barlow lense in optical equipment graph. Barlow node is build out of three vertices:
    barlow node its input and output. Ocular node is automatically connected with them.  
    """ 
    # Add barlow lense node
    super(Barlow, self)._register(equipment)
    # Add barlow lense output node and connect it to barlow lense
    self._register_output(equipment, self.connection_type)
    # Add barlow lense input node and connect it to barlow lense
    self._register_input(equipment, self.connection_type)
    # Handling optional T2 ouptout
    if self.t2_output:
      self._register_output(equipment, ConnectionType.T2)

  def __str__(self):
    # Format: <vendor> x<magnification>
    return "Berlow lense\n{} x{}".format(self.vendor, self.magnification)


class Camera(OpticalEqipment):
  """
  Class representing DSLR camera mounted via T2 adapter
  """

  def __init__(self, sensor_width, sensor_height, width, height, vendor = "unknown camera", connection_type = ConnectionType.T2):
    self.connection_type = connection_type
    self.sensor_width = sensor_width
    self.sensor_height = sensor_height
    self.width = width
    self.height = height
    super(Camera, self).__init__(0, vendor)

  def register(self, equipment):
    # Add camera node
    super(Camera, self)._register(equipment)
    # Add camera input node and connect it to camera
    self._register_input(equipment, self.connection_type)
    # Connect camera with output image node
    equipment.add_edge(self.id(), equipment.IMAGE_ID)

  def __str__(self):
    # Format: <vendor> <width>x<height>
    return "Camera\n{} {}x{}".format(self.vendor, self.sensor_width, self.sensor_height)

