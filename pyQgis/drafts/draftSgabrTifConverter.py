import os
import numpy as np
import Raster as rst

def listdirs(rootdir, extension=None, function=None, **kwargs):
    """
    Navigates a directory, generates a list with the paths of
    all the files inside the directory and its subdirectories
    and applies a specified function over each one of the
    files (using the filepath as the single argument).

    Parameters
    ----------
    rootdir: string
        Path to the directory where the function will be applied
        over
    extension: list of strings (optional)
        Specific file extension(s) you are interested in. Only
        files with this extension(s) will be appended to the
        dirList object and will be passed as an argument to the
        specified function. Default None, which means that all
        file extensions will be taken into account. The file
        extension strings must start with a point. Example:
        extension = ['.tif', '.csv']
    function: function (optional)
        Function that will be applied to the files. It can be
        any function that takes as its only argument a file
        path. Please check if the function supports working
        over all the specified file extensions
    **kwargs: (optional)
        Additional arguments required by the function
    
    Returns
    -------
    dirList: list
        List object storing the paths to all the considered
        files inside the directory and its subdirectories
    resultDict: dictionary (optional)
        Dict object storing the results of the function.
        Keys are file paths and values are the actual
        results
    """
    dirList = []
    resultDict = {}
    if type(extension) == str: extension = [extension]
    for it in os.scandir(rootdir):
        if it.is_dir():
            listdirs(it, dirList, extension=extension, function=function,
                        resultDict=resultDict, **kwargs)
        elif it.is_file():
            ext = os.path.splitext(os.path.basename(it.path))[1]
            if extension is None or ext in extension:
                dirList.append(it.path)
                if function is not None:
                    result = function(it.path, **kwargs)
                    resultDict[it.path] = result
            
    return(dirList, resultDict)

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

def stats(filepath, statNames):
    summary = {}
    lyr = rst.Raster(filepath)
    data = lyr.mtrx[lyr.mtrx!=lyr.nodt]
    if 'mean' in statNames:
        summary['mean'] = np.mean(data)
    if 'max' in statNames:
        summary['max'] = np.max(data)
    if 'min' in statNames:
        summary['min'] = np.min(data)
    
    return summary

def prueba(filepath):
    name = os.path.basename(filepath)
    print(f'Filename: {name} | Extension: {os.path.splitext(name)[1]}')