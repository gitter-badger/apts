import igraph as ig
import pandas as pd
import seaborn as sns
# TODO: make this global and configurable in all apts
sns.set_style('whitegrid')

from .constants import NodeLabels
from .utils import Utils, Constants
from .models.optical import *
from .optics import *


class Equipment:
  """
  This class represents all possessed astronomical equipment. Allows to compute all possible 
  hardware configuration. It uses directed graph for internal processing.
  """

  def __init__(self):
    self.connection_garph = ig.Graph(directed=True)
    # Register standard input and outputs
    self.add_vertex(Constants.SPACE_ID)
    self.add_vertex(Constants.EYE_ID)
    self.add_vertex(Constants.IMAGE_ID)

  def _get_paths(self, output_id):
    # Connect all outputs with inputs
    self._connect()
    # Find input and output nodes
    space_node = self.connection_garph.vs.find(name=Constants.SPACE_ID)
    output_node = self.connection_garph.vs.find(name=output_id)
    results = []
    results_set = set()
    for optical_path in Utils.find_all_paths(self.connection_garph, space_node.index, output_node.index):
      result = [self.connection_garph.vs.find(
          name=id)[NodeLabels.EQUIPMENT] for id in optical_path]
      op = OpticalPath.from_path(
          [item for item in result if item is not None])
      if op.elements() not in results_set:
        results_set.add(op.elements())
        results.append(op)
    return results

  def get_zooms(self, node_id):
    result = [OpticsUtils.compute_zoom(path)
              for path in self._get_paths(node_id)]
    result.sort()
    return result

  def data(self):
    columns = ['label', 'type', 'zoom', 'useful_zoom',
               'fov', 'range', 'brightness', 'elements']

    def append(result_data, columns, paths):
      for path in paths:
        data = [[path.label(),
                 path.output.output_type(),
                 path.zoom().magnitude,
                 path.zoom() < path.telescope.max_useful_zoom(),
                 path.fov().magnitude,
                 path.telescope.max_range(),
                 path.brightness().magnitude,
                 path.length()]]
        result_data = result_data.append(pd.DataFrame(
            data, columns=columns), ignore_index=True)
      return result_data
    # TODO: This is still not best way to add data
    result_data = pd.DataFrame(columns=columns)
    result_data = append(result_data, columns,
                         self._get_paths(Constants.EYE_ID))
    result_data = append(result_data, columns,
                         self._get_paths(Constants.IMAGE_ID))
    return result_data

  def plot(self, to_plot):
    data = self.data()[[to_plot, 'type', 'label']].sort_values(by=to_plot)
    pd.DataFrame([{row[1]:row[0]} for row in data.values], index=data['label'].values).plot(
        kind="bar", stacked=True, title=to_plot)

  def plot_connection_garph(self):
    return ig.plot(self.connection_garph)

  def _connect(self):
    for out_node in self.connection_garph.vs.select(node_type=OpticalType.OUTPUT):
      # Get output type
      connection_type = out_node[NodeLabels.CONNECTION_TYPE]
      for in_node in self.connection_garph.vs.select(node_type=OpticalType.INPUT, connection_type=connection_type):
        # Connect all outputs with all inputs, excluding connecting part to itself
        out_id = OpticalEqipment.get_parent_id(
            out_node[NodeLabels.NAME])
        in_id = OpticalEqipment.get_parent_id(in_node[NodeLabels.NAME])
        if out_id != in_id:
          self.add_edge(out_node, in_node)

  def add_vertex(self, node_name, equipment=None, node_type=OpticalType.GENERIC, connection_type=None):
    """ 
    Add single node to graph. Return new vertex.
    """
    self.connection_garph.add_vertex(node_name)
    node = self.connection_garph.vs.find(name=node_name)

    if equipment is not None:
      node_type = equipment.type()
      node_label = "\n".join([equipment.get_name(), equipment.label()])
    elif node_type == OpticalType.GENERIC:
      node_label = node_name
    else:
      node_label = ""

    node[NodeLabels.TYPE] = node_type
    node[NodeLabels.LABEL] = node_label
    node[NodeLabels.COLOR] = Constants.COLORS[node_type]
    node[NodeLabels.EQUIPMENT] = equipment
    node[NodeLabels.CONNECTION_TYPE] = connection_type

    return node

  def add_edge(self, node_from, node_to):
    # Add edge if only it doesn't exist
    # TODO: are_connected is the right method?
    if not self.connection_garph.are_connected(node_from, node_to):
      self.connection_garph.add_edge(node_from, node_to)

  def register(self, optical_eqipment):
    """ 
    Register any optical equipment in a optical graph.
    """
    optical_eqipment.register(self)
