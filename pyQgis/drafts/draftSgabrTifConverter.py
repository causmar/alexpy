import os
import Raster as rst

def listdirs(rootdir, dirList=[], function=None):
    for it in os.scandir(rootdir):
        if it.is_dir():
            listdirs(it, dirList, function=function)
        elif it.is_file():
            dirList.append(it.path)
            if function is not None: function(it.path)
            
    return(dirList)

def sgabr2tif(filepath):
    lyr = rst.Raster(filepath)
    expname = os.path.splitext(os.path.basename(lyr.path))[0]
    dirpath = os.path.dirname(lyr.path)
    outpath = os.path.join(dirpath, f'{expname}.tif')
    lyr.exportRaster(outpath)

def tif2sgabr(filepath):
    lyr = rst.Raster(filepath)
    lyr.changeNoDataValue(-9999)
    expname = os.path.splitext(os.path.basename(lyr.path))[0]
    dirpath = os.path.dirname(lyr.path)
    outpath = os.path.join(dirpath, f'{expname}.sgabr')
    lyr.exportRaster(outpath)