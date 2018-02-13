import gdal
import numpy
import os

abspath = os.path.abspath(__file__)
dir_name = os.path.dirname(abspath)
os.chdir(dir_name)

ikonos_rgb = gdal.Open(r'ikonos-rgb.tif')
ikonos_nir = gdal.Open(r'ikonos-nir.tif')

channel_red = (numpy.array(ikonos_rgb.GetRasterBand(1).ReadAsArray())).astype(float)
channel_nir = (numpy.array(ikonos_nir.GetRasterBand(1).ReadAsArray())).astype(float)

numerator = numpy.subtract(channel_nir, channel_red)
denominator = numpy.add(channel_nir, channel_red)

ndvi_array = numpy.true_divide(numerator, denominator, out=numpy.zeros_like(numerator, dtype=numpy.float),
                               where=denominator != 0)
ndvi_normalized = (numpy.around((ndvi_array + 1.0) * 127.5)).astype(int)

driver = gdal.GetDriverByName('GTiff')

# Change it accordingly
export_file = r"vegetation.tiff"

data_set = driver.Create(export_file, ndvi_normalized.shape[1], ndvi_normalized.shape[0], 1, gdal.GDT_Byte)
data_set.GetRasterBand(1).WriteArray(ndvi_normalized)
data_set.FlushCache()
