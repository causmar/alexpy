# -*- coding: utf-8 -*-
#
# ***************************************************************************
#     RasterValuesFromPoints.py
#     ----------------
#     Date                 : November 2022
#     Copyright            : (C) 2022 by Cristian Usma
#     Email                : causmar97@gmail.com
# ***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************
#     Instrucciones de uso como complemento para QGIS
#     -----------------------------------------------
#     1. Ubicar este archivo en la dirección adecuada según el OS:
#         1.1. Windows:
#             C:\Users\<usuario>\AppData\Roaming\QGIS\QGIS3\profiles\...
#             ...<perfil>\processing\scripts\RasterToBasin.py
#         1.2. Linux:
#             /usr/local/share/QGIS/QGIS3/profiles/...
#             ...<perfil>/processing/scripts/RasterToBasin.py
#         1.3 macOS:
#             Library/Application Support/QGIS/QGIS3/profiles/...
#             ...<perfil>/processing/scripts/RasterToBasin.py
#     2. Abrir QGIS normalmente.
#     3. Abrir el panel de procesamiento. En la parte inferior abrir el
#        ítem desplegable "Scripts" (identificado con el ícono de Python).
#     4. Hacer doble click en el algoritmo "Raster Values From Points" e ingresar los
#        parámetros normalmente a través de la interfaz gráfica de QGIS.
#         4.1. Input layer: Capa raster que corresponde al DEM.
#         4.2. Band number: Número de la banda que representa la elevación.
#         4.3. Fill value: Número para rellenar la matriz de cuenca.
#         4.4. Output file: Dirección del archivo TXT de salida.
# ***************************************************************************

__author__ = 'Cristian Usma'
__date__ = 'November 2022'
__copyright__ = '(C) 2022, Cristian Usma'

from math import floor, ceil
from numbers import Number
from osgeo import gdal
from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterBand,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFileDestination,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProject,
                       QgsPoint,
                       QgsGeometry)


class RasterValuesFromPoints(QgsProcessingAlgorithm):
    """Creates a SIGA basin file from a DEM raster."""
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    BAND = 'BAND'
    FILLVALUE = 'FILLVALUE'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Input layer')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterBand(
                self.BAND,
                self.tr('Band number'),
                1,
                self.INPUT
            )
        )
        
        fillValueParam = QgsProcessingParameterNumber(
                             self.FILLVALUE,
                             self.tr('Fill value'),
                             type=QgsProcessingParameterNumber.Double,
                             defaultValue = -9999
        )
        
        fillValueParam.setMetadata(
            {'widget_wrapper':{'decimals':2}
            }
        )
        
        self.addParameter(fillValueParam)

        # We add a file output of type TXT.
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Output file'),
                'TXT files (*.txt)',
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        band = self.parameterAsInt(parameters, self.BAND, context)
        fillValue = self.parameterAsDouble(parameters, self.FILLVALUE, context)
        txt = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        
        # User interface variables
        gridPath = r'C:\Personal\PyQGIS\pyqgis_in_a_day\srtm.tif'
        band = 1
        pointPath = r'C:\Personal\PyQGIS\otros\dique_UTM.shp'
        valueField = 'valor'
        outPath = r'C:\Personal\PyQGIS\otros\srtm_modif.tif'

        # Load data
        gridLayer = gdal.Open(gridPath)
        if gridLayer is None: sys.exit('Could not open raster path.')
        pointLayer = QgsVectorLayer(pointPath, 'point', 'ogr')
        if pointLayer is None: sys.exit('Could not open point path.')

        # Get raster information
        inpBand = gridLayer.GetRasterBand(band)
        mtrx = inpBand.ReadAsArray()
        georef = gridLayer.GetGeoTransform()
        proj = gridLayer.GetProjection()
        rows = gridLayer.RasterYSize
        cols = gridLayer.RasterXSize
        clszx = abs(georef[1])
        clszy = abs(georef[5])
        if georef[1]<0:
            xll = georef[0]+georef[1]*cols
        else:
            xll = georef[0]
        if georef[5]<0:
            yll = georef[3]+georef[5]*rows
        else:
            yll = georef[3]
        xur = xll + cols*clszx
        yur = yll + rows*clszy

        # Set transform to convert the points' CRS to the grid's CRS on the fly
        pointCrs = pointLayer.crs()
        gridCrs = QgsCoordinateReferenceSystem(proj)
        tr = QgsCoordinateTransform(pointCrs, gridCrs, QgsProject.instance())

        # Replace raster values with point values
        for p in pointLayer.getFeatures():
            geom = p.geometry()
            geom.transform(tr)
            x = geom.asPoint().x()
            y = geom.asPoint().y()
            col = int(floor((x - xll) / clszx))
            row = int(rows - ceil((y - yll) / clszy))
            value = p[valueField]
            if isinstance(value, Number):
                mtrx[row][col] = value

        # Export modified layer
        driver = gridLayer.GetDriver()
        outGrid = driver.Create(outPath, cols, rows, 1, gdal.GDT_Float32)
        outBand = outGrid.GetRasterBand(1)
        outGrid.SetGeoTransform((xll, clszx, 0.0, yur, 0.0, -clszy))
        outGrid.SetProjection(proj)
        band = outGrid.GetRasterBand(1)
        band.SetNoDataValue(inpBand.GetNoDataValue())
        band.WriteArray(mtrx, 0, 0)
        band.FlushCache()
        outGrid = None; band = None
        
        return {self.OUTPUT: txt}

    def name(self):
        return 'rastervaluesfrompoints'

    def displayName(self):
        return self.tr('Raster Values From Points')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RasterValuesFromPoints()