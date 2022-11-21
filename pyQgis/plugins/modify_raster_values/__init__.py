from .modify_raster_values import ModifyRasterValuesPlugin

def classFactory(iface):
    return ModifyRasterValuesPlugin(iface)
