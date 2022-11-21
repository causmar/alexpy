import os
import inspect
from PyQt5.QtGui import QIcon

from qgis.core import QgsProcessingProvider
from .modify_raster_values_algorithm import ModifyRasterValuesAlgorithm


class ModifyRasterValuesProvider(QgsProcessingProvider):

    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def unload(self):
        pass

    def loadAlgorithms(self):
        self.addAlgorithm(ModifyRasterValuesAlgorithm())

    def id(self):
        return 'modify_raster_values'

    def name(self):
        return self.tr('Modify Raster Values')

    def icon(self):
        cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        icon = QIcon(os.path.join(os.path.join(cmd_folder, 'icon.png')))
        return icon

    def longName(self):
        return self.name()
