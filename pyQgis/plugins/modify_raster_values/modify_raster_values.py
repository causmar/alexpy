import os
import sys
import inspect
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon

from qgis.core import QgsProcessingAlgorithm, QgsApplication
import processing
from .modify_raster_values_provider import ModifyRasterValuesProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

class ModifyRasterValuesPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initProcessing(self):
        self.provider = ModifyRasterValuesProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)
    
    def initGui(self):
        self.initProcessing()
        icon = os.path.join(os.path.join(cmd_folder, 'icon.png'))
        self.action = QAction(QIcon(icon), 'Modify Raster Values From Points', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu('&Modify Raster Values', self.action)
        self.iface.addToolBarIcon(self.action)
    
    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu('&Modify Raster Values', self.action)
        del self.action
    
    def run(self):
        processing.execAlgorithmDialog('modify_raster_values:modify_raster_values')

