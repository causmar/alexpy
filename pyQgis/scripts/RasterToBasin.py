# -*- coding: utf-8 -*-
#
# ***************************************************************************
#     RasterToBasin.py
#     ----------------
#     Date                 : November 2022
#     Copyright            : (C) 2022 by Gotta Ingeniería
#     Email                : cristian.usma@gottaingenieria.com
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
#     4. Hacer doble click en el algoritmo "Raster To Basin" e ingresar los
#        parámetros normalmente a través de la interfaz gráfica de QGIS.
#         4.1. Input layer: Capa raster que corresponde al DEM.
#         4.2. Band number: Número de la banda que representa la elevación.
#         4.3. Fill value: Número para rellenar la matriz de cuenca.
#         4.4. Output file: Dirección del archivo TXT de salida.
# ***************************************************************************

__author__ = 'Gotta Ingeniería'
__date__ = 'November 2022'
__copyright__ = '(C) 2022, Gotta Ingeniería'

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


class RasterToBasinAlgorithm(QgsProcessingAlgorithm):
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
        
        if fillValue%1 == 0: fillValue = int(fillValue)

        provider = layer.dataProvider()
        extent = layer.extent()
        rows = layer.height()
        cols = layer.width()
        ncls = rows * cols
        cszx = layer.rasterUnitsPerPixelX()
        cszy = layer.rasterUnitsPerPixelY()
        csz = (cszx+cszy)/2
        acl = csz ** 2
        yul = extent.yMaximum()
        xul = extent.xMinimum()

        srcCrs = layer.crs()
        dstCrs = QgsCoordinateReferenceSystem("EPSG:4326")
        tr = QgsCoordinateTransform(srcCrs, dstCrs, QgsProject.instance())

        block = provider.block(band, extent, cols, rows)

        vars = {'tipo':0,
                'destino':1,
                'tramo':fillValue,
                'llanura':fillValue,
                'embalse':0,
                'X':fillValue,
                'Y':fillValue,
                'Z':fillValue,
                'lat':fillValue,
                'lon':fillValue,
                'L':fillValue,
                'S':fillValue,
                'D':fillValue,
                'alfa1':fillValue,
                'beta1':fillValue,
                'S0':fillValue,
                'S1':fillValue,
                'S2':fillValue,
                'S3':fillValue,
                'S4':fillValue,
                'S5':fillValue,
                'H5b':fillValue,
                'W5b':fillValue,
                'Q5b':fillValue,
                'HU':fillValue,
                'LAI':fillValue,
                'arcS2S':fillValue,
                'limS2S':fillValue,
                'areS2S':fillValue,
                'arcS2D':fillValue,
                'limS2D':fillValue,
                'areS2D':fillValue,
                'arcS5S':fillValue,
                'limS5S':fillValue,
                'areS5S':fillValue,
                'arcS5D':fillValue,
                'limS5D':fillValue,
                'areS5D':fillValue,
                'alfa2':fillValue,
                'beta2':fillValue,
                'alfa3':fillValue,
                'beta3':fillValue,
                'S0EC':fillValue,
                'S1ECp':fillValue,
                'S1ECs':fillValue,
                'S2EC':fillValue,
                'S3EC':fillValue,
                'S4EC':fillValue,
                'S0NO':fillValue,
                'S1NOp':fillValue,
                'S1NOs':fillValue,
                'S2NO':fillValue,
                'S3NO':fillValue,
                'S4NO':fillValue,
                'S0NH4':fillValue,
                'S1NH4p':fillValue,
                'S1NH4s':fillValue,
                'S2NH4':fillValue,
                'S3NH4':fillValue,
                'S4NH4':fillValue,
                'S0NO3':fillValue,
                'S1NO3p':fillValue,
                'S1NO3s':fillValue,
                'S2NO3':fillValue,
                'S3NO3':fillValue,
                'S4NO3':fillValue,
                'S0PO':fillValue,
                'S1POp':fillValue,
                'S1POs':fillValue,
                'S2PO':fillValue,
                'S3PO':fillValue,
                'S4PO':fillValue,
                'S0PI':fillValue,
                'S1PIp':fillValue,
                'S1PIs':fillValue,
                'S2PI':fillValue,
                'S3PI':fillValue,
                'S4PI':fillValue,
                'S0PO_fb':fillValue,
                'S1POp_fb':fillValue,
                'S1POs_fb':fillValue,
                'S2PO_fb':fillValue,
                'S3PO_fb':fillValue,
                'S0PI_fb':fillValue,
                'S1PIp_fb':fillValue,
                'S1PIs_fb':fillValue,
                'S2PI_fb':fillValue,
                'S3PI_fb':fillValue,
                'OD':fillValue,
                'CDBO':fillValue,
                'CE':fillValue,
                'EC':fillValue,
                'NO3':fillValue,
                'NH4':fillValue,
                'NO':fillValue,
                'PO':fillValue,
                'PI':fillValue,
                'PT':fillValue,
                'pH':fillValue,
                'alk':fillValue,
        }

        # Compute the number of steps to display within the progress bar
        total = 100.0 / ncls if ncls > 0 else 0

        with open(txt, 'w') as outputFile:
            
            # Write head block
            line = f"[NÚMERO DE CELDAS]\n" \
                   f"{ncls:0.0f}\n\n" \
                   f"[ÁREA DE LAS CELDAS]\n" \
                   f"{acl:0.2f}\n\n" \
                   f"[TIPO DE TOPOLOGÍA]\n" \
                   f"SIGA_CAL_V1.0\n\n" \
                   f"[MATRIZ DE VARIABLES]\n"""
            outputFile.write(line)
            
            # Write titles
            line = ' '.join(key for key in vars.keys()) + '\n'
            outputFile.write(line)
            
            # Start the counter of steps to display within the progress bar
            current = 0
            
            for row in range(rows):
                for col in range(cols):
                    vars['X'] = xul + col*csz + csz/2
                    vars['Y'] = yul - row*csz - csz/2
                    vars['Z'] = block.value(row, col)
                    point = QgsPoint(vars['X'], vars['Y'], vars['Z'])
                    geom = QgsGeometry(point)
                    geom.transform(tr)
                    vars['lat'] = f"{geom.asPoint().y():0.6f}"
                    vars['lon'] = f"{geom.asPoint().x():0.6f}"
                    vars['X'] = f"{vars['X']:0.3f}"
                    vars['Y'] = f"{vars['Y']:0.3f}"
                    vars['Z'] = f"{vars['Z']:0.3f}"
                    
                    # Add a feature
                    line = ' '.join(f'{vars[key]}' for key in vars.keys()) + '\n'
                    outputFile.write(line)
                    
                    # Update the progress bar
                    current += 1
                    feedback.setProgress(int(current * total))
                    
        return {self.OUTPUT: txt}

    def name(self):
        return 'rastertobasin'

    def displayName(self):
        return self.tr('Raster To Basin')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RasterToBasinAlgorithm()