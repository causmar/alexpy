# -*- coding: utf-8 -*-
#
# ***************************************************************************
#     modify_raster_values_algorithm.py
#     ----------------
#     Date                 : November 2022
#     Copyright            : (C) 2022 by Alejandro Usma
#     Email                : causmar97@gmail.com
# ***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************

__author__ = 'Alejandro Usma'
__date__ = 'November 2022'
__copyright__ = '(C) 2022, Alejandro Usma'

from math import floor, ceil
from numbers import Number
from osgeo import gdal

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProject,
                       QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFileDestination,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsRasterLayer)


class ModifyRasterValuesAlgorithm(QgsProcessingAlgorithm):
    """Modifies the values of raster pixels using a point layer."""
    INPUT_RASTER = 'INPUT_RASTER'
    INPUT_POINTS = 'INPUT_POINTS'
    OUTPUT_RASTER = 'OUTPUT_RASTER'
    BAND = 'BAND'
    VALUE_FIELD = 'VALUE_FIELD'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_RASTER,
                self.tr('Input raster layer'),
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                 self.BAND,
                 self.tr('Raster band number'),
                 type=QgsProcessingParameterNumber.Integer,
                 defaultValue = 1
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_POINTS,
                self.tr('Input point layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterField(
                self.VALUE_FIELD,
                self.tr('Field that stores the desired values'),
                None,
                self.INPUT_POINTS
            )
        )

        # We add a file output of type CSV.
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_RASTER,
                self.tr('Output File'),
                'TIF files (*.tif)',
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        gridPath = self.parameterAsFile(parameters, self.INPUT_RASTER, context)
        band = self.parameterAsInt(parameters, self.BAND, context)
        pointLayer = self.parameterAsSource(parameters, self.INPUT_POINTS, context)
        valueField = self.parameterAsFields(parameters, self.VALUE_FIELD, context)
        outPath = self.parameterAsFileOutput(parameters, self.OUTPUT_RASTER, context)

        # Load data
        gridLayer = gdal.Open(gridPath)
        
        if gridLayer is None:
            raise RuntimeError("The path specified in the " \
                "'Input raster layer' parameter does not match any raster layer")
        elif band <= 0 or band > gridLayer.RasterCount:
            raise RuntimeError("The value specified in the "\
                "'Raster band number' parameter does not match any existing band")
        
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
        pointCrs = pointLayer.sourceCrs()
        gridCrs = QgsCoordinateReferenceSystem(proj)
        tr = QgsCoordinateTransform(pointCrs, gridCrs, QgsProject.instance())

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / pointLayer.featureCount() if pointLayer.featureCount() else 0
        
        # Iterate over the point layer features
        for current, p in enumerate(pointLayer.getFeatures()):
            
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled(): break
            
            # Replace raster values with point values
            geom = p.geometry()
            geom.transform(tr)
            x = geom.asPoint().x()
            y = geom.asPoint().y()
            col = int(floor((x - xll) / clszx))
            row = int(rows - ceil((y - yll) / clszy))
            value = p[valueField[0]]
            if isinstance(value, Number):
                mtrx[row][col] = value

            # Update the progress bar
            feedback.setProgress(int(current * total))

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
        
        # Load the modified layer to the QGIS GUI
        outLayer = QgsRasterLayer(outPath, 'modified_raster', 'gdal')
        QgsProject.instance().addMapLayer(outLayer)
        return {self.OUTPUT_RASTER: outLayer}

    def name(self):
        return 'modify_raster_values'

    def displayName(self):
        return self.tr('Modify Raster Values From Points')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ModifyRasterValuesAlgorithm()
