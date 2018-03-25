#!/usr/bin/env python

# Use native system consoles(cmd, linux shell etc) only
# Compatible with Python v3.6.4
# Dependencies: numpy, gdal, texttable

import gdal
import numpy
import os
import sys
import itertools
import texttable
import threading
import time


def __main():
    abspath = os.path.abspath(__file__)
    dir_name = os.path.dirname(abspath)
    os.chdir(dir_name)

    # Change The File names Accordingly
    original = gdal.Open(r'data/aoi.img')
    file_list = \
        {
            "Brovey": [gdal.Open(r'data/brovey.img'), "Sampling = Nearest Neighbour\n"
                                                      "Spectral Transform = PCA\n"
                                                      "Multi Spectral Layers = 1:3\n"
                                                      "Data = UINT16"],

            "Ehlers": [gdal.Open(r'data/ehlers.img'), "Sampling = Nearest Neighbour\n"
                                                      "Filter = Auto\n"
                                                      "Image Content = Urban / Mixed"
                                                      "Color Resolution Tradeoff = Normal"
                                                      "Multi Spectral Layers = {R:1, G:2, B:3}\n"
                                                      "Data = UINT16"],

            "HPF": [gdal.Open(r'data/hpf.img'), "Sampling = Nearest Neighbour\n"
                                                "R = 4.0\n"
                                                "WF = 0.5\n"
                                                "Center Value = 80\n"
                                                "Multi Spectral Layers = 1:3\n"
                                                "Data = UINT16"],

            "Multiplicative": [gdal.Open(r'data/multiplicative.img'), "Sampling = Nearest Neighbour\n"
                                                                      "Spectral Transform = PCA\n"
                                                                      "Multi Spectral Layers = 1:3\n"
                                                                      "Data = UINT32\n"
                                                                      "Radiometric Rescale = UINT16"],

            "PCA": [gdal.Open(r'data/pca.img'), "Sampling = Nearest Neighbour\n"
                                                "Spectral Transform = PCA\n"
                                                "Multi Spectral Layers = 1:3\n"
                                                "Data = UINT16"],

            "Modified IHS": [gdal.Open(r'data/modified_ihs.img'), "Sampling = Nearest Neighbour\n"
                                                                  "Hi Res Sensor = SPOT Pan\n"
                                                                  "Multi Spectral Sensor = Color Aerial Photo\n"
                                                                  "Ratio Ceiling = 2.0\n"
                                                                  "Data = UINT16"],

            "Wavelet PCA": [gdal.Open(r'data/wavelet_pca.img'), "Sampling = Nearest Neighbour\n"
                                                                "Spectral Transform = PCA\n"
                                                                "Multi Spectral Layers = 1:3\n"
                                                                "Data = UINT16"],

            "Wavelet IHS": [gdal.Open(r'data/wavelet_ihs.img'), "Sampling = Nearest Neighbour\n"
                                                                "Spectral Transform = IHS\n"
                                                                "Multi Spectral Layers = 1:3\n"
                                                                "Data = UINT16"]
        }

    out = 'Statistical Comparison of Common Image Fusion Techniques\n\n\n'
    for key in file_list.keys():
        mse = get_rmse(original, file_list[key][0])
        img_quality = get_quality(original, file_list[key][0])
        co_rel = get_correlation(original, file_list[key][0])
        rel_mean = get_relative_mean(original, file_list[key][0])
        p_snr = get_psnr(original, file_list[key][0])

        orig_sd = get_std_dev(original)
        ref_sd = get_std_dev(file_list[key][0])
        orig_entropy = get_entropy(original)
        ref_entropy = get_entropy(file_list[key][0])

        stat = texttable.Texttable()
        stat.set_cols_align(['c', 'c', 'c'])
        stat.set_cols_valign(['m', 'm', 'm'])
        stat.add_rows([["Image", "Std Dev", "Entropy"],
                       ["Original", __decorate(orig_sd), __decorate(orig_entropy)],
                       [key, __decorate(ref_sd), __decorate(ref_entropy)]])

        table = texttable.Texttable()
        table.set_cols_align(['c', 'c', 'c', 'c'])
        table.set_cols_valign(["m", "m", "m", "m"])
        table.add_rows([['Measure', 'Band-I  \n(R)', 'Band-II \n(G)', 'Band-III\n(B)'], ['RMSE'] + mse,
                        ['Image Quality'] + img_quality, ['Correlation'] + co_rel,
                        ['Relative Mean'] + rel_mean, ['P-SNR'] + p_snr])

        config = texttable.Texttable()
        config.set_cols_align(['l'])
        config.set_cols_valign(['m'])
        config.add_row([file_list[key][1]])
        out = out + key + "\n" + stat.draw() + "\n" + config.draw() + "\n" + table.draw() + "\n" + "."*80 + "\n"*3
    with open(r"data/statistics.txt", "w+") as file:
        file.write(out[:-3])


def get_rmse(orig, ref):
    try:
        if orig.RasterCount == ref.RasterCount:
            count = orig.RasterCount
            rmse_vector = list()
            for i in range(count):
                current_band = orig.GetRasterBand(i + 1)
                ref_band = ref.GetRasterBand(i + 1)
                rmse_vector.append(rmse(current_band, ref_band))
            return rmse_vector
        else:
            raise IOError("No of Bands does not match")
    except IOError as dim_error:
        print(dim_error)
        return None


def rmse(curr_img, ref_img):
    try:
        if curr_img.DataType in (1, 2, 4) and ref_img.DataType in (1, 2, 4):
            if curr_img.DataType == ref_img.DataType:
                current = (numpy.array(curr_img.ReadAsArray())).astype(float)
                ref = (numpy.array(ref_img.ReadAsArray())).astype(float)
                if current.shape == ref.shape:
                    return numpy.sqrt(((numpy.subtract(current, ref)) ** 2).mean())
                else:
                    raise IOError("Dimension Mismatch")
            else:
                raise IOError("Data Type Mismatch")
        else:
            raise TypeError("Only Unsigned Integer Data Types are Supported")
    except TypeError as type_error:
        print(type_error)
        return None
    except IOError as dim_error:
        print(dim_error)
        return None


def covariance(orig, ref):
    try:
        if orig.shape == ref.shape:
            return ((numpy.sum(numpy.multiply((orig - orig.mean()), (ref - ref.mean())))).prod()) / (ref.size - 1)
        else:
            raise IOError("Dimension Mismatch")
    except IOError as dim_error:
        print(dim_error)
        return None


def quality(orig, ref):
    try:
        if orig.shape == ref.shape:
            numerator = 4 * covariance(orig, ref) * (orig.mean() * ref.mean())
            denominator = ((orig.mean() ** 2) + (ref.mean() ** 2)) * (
                    (numpy.var(orig.ravel())) + (numpy.var(ref.ravel())))
            return numerator / denominator
        else:
            raise IOError("Dimension Mismatch")
    except IOError as dim_error:
        print(dim_error)
        return None


def get_covariance(orig, ref):
    try:
        if orig.RasterCount == ref.RasterCount:
            count = orig.RasterCount
            cov_vector = list()
            for i in range(count):
                current_band = (numpy.array(orig.GetRasterBand(i + 1).ReadAsArray())).astype(float)
                ref_band = (numpy.array(ref.GetRasterBand(i + 1).ReadAsArray())).astype(float)
                cov_vector.append(covariance(current_band, ref_band))
            return cov_vector
        else:
            raise IOError("No of Bands does not match")
    except IOError as dim_error:
        print(dim_error)
        return None


def get_quality(orig, ref):
    try:
        if orig.RasterCount == ref.RasterCount:
            count = orig.RasterCount
            quality_vector = list()
            for i in range(count):
                current_band = (numpy.array(orig.GetRasterBand(i + 1).ReadAsArray())).astype(float)
                ref_band = (numpy.array(ref.GetRasterBand(i + 1).ReadAsArray())).astype(float)
                quality_vector.append(quality(current_band, ref_band))
            return quality_vector

        else:
            raise IOError("No of Bands does not match")
    except IOError as dim_error:
        print(dim_error)
        return None


def correlation(orig, ref):
    try:
        if orig.shape == ref.shape:
            numerator = (2 * numpy.sum(numpy.multiply(orig, ref)))
            denominator = (numpy.sum((orig ** 2)) + numpy.sum((ref ** 2)))
            return numerator / denominator
        else:
            raise IOError("Dimension Mismatch")
    except IOError as dim_error:
        print(dim_error)
        return None


def get_correlation(orig, ref):
    try:
        if orig.RasterCount == ref.RasterCount:
            count = orig.RasterCount
            correlation_vector = list()
            for i in range(count):
                current_band = (numpy.array(orig.GetRasterBand(i + 1).ReadAsArray())).astype(float)
                ref_band = (numpy.array(ref.GetRasterBand(i + 1).ReadAsArray())).astype(float)
                correlation_vector.append(correlation(current_band, ref_band))
            return correlation_vector

        else:
            raise IOError("No of Bands does not match")
    except IOError as dim_error:
        print(dim_error)
        return None


def relative_mean(orig, ref):
    try:
        if orig.shape == ref.shape:
            return (abs((ref.mean() - orig.mean())) / orig.mean()) * 100
        else:
            raise IOError("Dimension Mismatch")
    except IOError as dim_error:
        print(dim_error)
        return None


def get_relative_mean(orig, ref):
    try:
        if orig.RasterCount == ref.RasterCount:
            count = orig.RasterCount
            relative_vector = list()
            for i in range(count):
                current_band = (numpy.array(orig.GetRasterBand(i + 1).ReadAsArray())).astype(float)
                ref_band = (numpy.array(ref.GetRasterBand(i + 1).ReadAsArray())).astype(float)
                relative_vector.append(relative_mean(current_band, ref_band))
            return relative_vector

        else:
            raise IOError("No of Bands does not match")
    except IOError as dim_error:
        print(dim_error)
        return None


def entropy(img):
    try:
        size_dict = {1: 8, 2: 16, 3: 32}
        if img.DataType in (1, 2, 4):
            img_matrix = (numpy.array(img.ReadAsArray())).astype(float)
            upper = (2 ** size_dict[img.DataType]) - 1
            p_dist = numpy.histogram(img_matrix, bins=upper, range=(0, upper), density=True)[0]
            return -1 * numpy.sum(numpy.multiply(p_dist,
                                                 numpy.log2(p_dist, out=numpy.zeros_like(p_dist, dtype=numpy.float),
                                                            where=p_dist > 0)))
        else:
            raise TypeError("Only Unsigned Integer Datatypes are Supported")
    except TypeError as type_error:
        print(type_error)
        return None


def get_entropy(orig):
    count = orig.RasterCount
    entropy_vector = list()
    for i in range(count):
        current_band = orig.GetRasterBand(i + 1)
        entropy_vector.append(entropy(current_band))
    return entropy_vector


def get_std_dev(img):
    count = img.RasterCount
    sd_vector = list()
    for i in range(count):
        current_band = (numpy.array(img.GetRasterBand(i + 1).ReadAsArray())).astype(float)
        sd_vector.append(numpy.std(current_band))
    return sd_vector


def psnr(curr_img, ref_img):
    try:
        size_dict = {1: 8, 2: 16, 4: 32}
        if curr_img.DataType in (1, 2, 4) and ref_img.DataType in (1, 2, 4):
            if curr_img.DataType == ref_img.DataType:
                current = (numpy.array(curr_img.ReadAsArray())).astype(float)
                ref = (numpy.array(ref_img.ReadAsArray())).astype(float)
                if current.shape == ref.shape:
                    upper = (2 ** size_dict[ref_img.DataType]) - 1
                    val = 0.0
                    rms = rmse(curr_img, ref_img)
                    if rms != 0:
                        val = (upper / rms)
                    if val != 0:
                        return 20 * numpy.log10(val)
                    else:
                        raise ValueError("Value Error: Logarithm is undefined for zero or negative value")
                else:
                    raise IOError("Dimension Mismatch")
            else:
                raise IOError("Data Type Mismatch")
        else:
            raise TypeError("Only Unsigned Integer Data Types are Supported")
    except TypeError as type_error:
        print(type_error)
        return None
    except ValueError as val_error:
        print(val_error)
        return None
    except IOError as io_error:
        print(io_error)
        return None


def get_psnr(img, ref):
    try:
        if img.RasterCount == ref.RasterCount:
            count = img.RasterCount
            psnr_vector = list()
            for i in range(count):
                current_band = img.GetRasterBand(i + 1)
                ref_band = ref.GetRasterBand(i + 1)
                psnr_vector.append(psnr(current_band, ref_band))
            return psnr_vector

        else:
            raise IOError("No of Bands does not match")
    except IOError as dim_error:
        print(dim_error)
        return None


def __decorate(data):
    return "Band-I   : " + "{:4.3f}".format(data[0]) + "\n" + "Band-II  : " + "{:4.3f}".format(data[1]) + "\n" +\
           "Band-III : " + "{:4.3f}".format(data[2])


def show_spinner():
    t = threading.currentThread()
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    print('\nProcessing: ', end='', flush=True)
    while getattr(t, "run_flag", True):
        sys.stdout.write(next(spinner))  # write the next character
        time.sleep(0.2)
        sys.stdout.flush()  # flush stdout buffer (actual character display)
        sys.stdout.write('\b')


if __name__ == '__main__':
    t = threading.Thread(target=show_spinner)
    t.daemon = True
    t.start()
    __main()
    t.run_flag = False
    t.join()
    sys.stdout.write('\b')
    print("Completed Successfully...\n")
