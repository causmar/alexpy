from math import floor, ceil
from numbers import Number
from osgeo import gdal

# User interface variables
gridPath = r'/home/alejo97/General/learning/pyqgis_in_a_day/srtm.tif'
band = 1
pointPath = r'/home/alejo97/General/learning/pyqgis_in_a_day/dique.shp'
valueField = 'Valor'
outPath = r'/home/alejo97/General/learning/pyqgis_in_a_day/srtm_modif.tif'

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

        
        
        
        
        
        
        
        
        
        
        
        