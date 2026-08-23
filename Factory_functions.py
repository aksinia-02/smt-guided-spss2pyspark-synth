from classes.Node import Node
from classes.nodes_types.AggregateNode import AggregateNode
from classes.nodes_types.AppendNode import AppendNode
from classes.nodes_types.DeriveNode import DeriveNode
from classes.nodes_types.FieldReorderNode import FieldReorderNode
from classes.nodes_types.FillerNode import FillerNode
from classes.nodes_types.FilterNode import FilterNode
from classes.nodes_types.MergeNode import MergeNode
from classes.nodes_types.ODBCExportNode import ODBCExportNode
from classes.nodes_types.ODBCImportNode import ODBCImportNode
from classes.nodes_types.RestructureNode import RestructureNode
from classes.nodes_types.SampleNode import SampleNode
from classes.nodes_types.SelectNode import SelectNode
from classes.nodes_types.SortNode import SortNode
from classes.nodes_types.TableNode import TableNode
from classes.nodes_types.TypeNode import TypeNode
from classes.nodes_types.ExcelInputNode import ExcelInputNode
from classes.nodes_types.ExcelNode import ExcelNode
from classes.nodes_types.TextFileExportNode import TextFileExportNode
from classes.nodes_types.DelimitedFileImportNode import DelimitedFileImportNode


NODE_TYPE_MAP = {
    "AggregateNode": AggregateNode,
    "AppendNode": AppendNode,
    "DeriveNode": DeriveNode,
    "FieldReorderNode": FieldReorderNode,
    "FillerNode": FillerNode,
    "FilterNode": FilterNode,
    "MergeNode": MergeNode,
    "ODBCExportNode": ODBCExportNode,
    "ODBCImportNode": ODBCImportNode,
    "RestructureNode": RestructureNode,
    "SampleNode": SampleNode,
    "SelectNode": SelectNode,
    "SortNode": SortNode,
    "TableNode": TableNode,
    "TypeNode": TypeNode,
    "ExcelInputNode": ExcelInputNode,
    "ExcelNode": ExcelNode,
    "TextFileExportNode": TextFileExportNode,
    "DelimitedFileImportNode": DelimitedFileImportNode
}

def create_node(id, uid, type, label, properties, importedFields, xml_diagram):
    node_class = NODE_TYPE_MAP.get(type, Node)
    return node_class(id, uid, type, label, properties, importedFields, xml_diagram)
