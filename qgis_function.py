from qgis.utils import iface, qgsfunction
from qgis.core import QgsExpression


@qgsfunction(
    args='auto', group='Your group', usesGeometry=False, referencedColumns=[], helpText='Define the help string here')
def your_expression(params, feature, parent):
    _ = feature, parent  # NOQA
    return 'your_result'
