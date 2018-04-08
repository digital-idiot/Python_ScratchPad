#!/usr/bin/env python

# Use native system consoles(cmd, linux shell etc) only
# Compatible with Python v3.6.4
# Dependencies: numpy, matplotlib, gdal, scikit-image

import matplotlib.pyplot as plt
import numpy as np
import gdal
import os
import threading
import itertools
import sys
import time
import warnings

from scipy import stats

import texttable

from skimage.color import rgb2gray
from skimage.filters import sobel
from skimage.segmentation import felzenszwalb, slic, quickshift, watershed
from skimage.segmentation import mark_boundaries
from skimage import transform
from skimage.util import img_as_float, img_as_ubyte, img_as_int
from skimage import exposure
from skimage import io
from scipy import ndimage


def straighten(band):

    top_row = np.amin(np.nonzero(band)[0])
    top_col = np.amin(np.nonzero(band[top_row, :]))

    bottom_row = np.amax(np.nonzero(band)[0])
    bottom_col = np.amax(np.nonzero(band[bottom_row, :]))

    left_col = np.amin(np.nonzero(band)[1])
    left_row = np.amin(np.nonzero(band[:, left_col]))

    right_col = np.amax(np.nonzero(band)[1])
    right_row = np.amax(np.nonzero(band[:, right_col]))

    src = np.array([[0, 0], [0, (band.shape[0]-1)], [(band.shape[1] - 1), (band.shape[0]-1)], [(band.shape[1] - 1), 0]])
    dst = np.array([[top_col, top_row], [left_col, left_row], [bottom_col, bottom_row], [right_col, right_row]])

    tform = transform.ProjectiveTransform()
    tform.estimate(src, dst)
    warped_img = transform.warp(band, tform)

    return img_as_float(warped_img)


def straighten_image(rgb_img, raw=False):
    rectified_bands = list()
    for b in range(rgb_img.shape[-1]):
        rectified_bands.append(straighten(rgb_img[:, :, b]))
    return np.dstack(rectified_bands)


def enhance(img):
    enhanced_bands = list()
    for b in range(img.shape[-1]):
        enhanced_bands.append(exposure.equalize_adapthist(img[:, :, b]))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return np.dstack(enhanced_bands)


def segment():

    segments_fz = felzenszwalb(correct_img, scale=100, sigma=0.5, min_size=100)
    segments_slic = slic(correct_img, n_segments=500, compactness=20, sigma=0.5)
    segments_quick = quickshift(correct_img, kernel_size=5, max_dist=5, ratio=0.1)
    gradient = sobel(rgb2gray(correct_img))
    segments_watershed = watershed(gradient, markers=500, compactness=0.0001)
    return [segments_fz, segments_slic, segments_quick, segments_watershed]


def show(lst):
    segments_fz = lst[0]
    segments_slic = lst[1]
    segments_quick = lst[2]
    segments_watershed = lst[3]
    print("Felzenszwalb number of segments: {}".format(len(np.unique(segments_fz))))
    print('SLIC number of segments: {}'.format(len(np.unique(segments_slic))))
    print('Quickshift number of segments: {}'.format(len(np.unique(segments_quick))))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        io.imsave(r"output/Felzenszwalbs.png", mark_boundaries(correct_img, segments_fz))
        io.imsave(r"output/SLIC.png", mark_boundaries(correct_img, segments_slic))
        io.imsave(r"output/Quick_Shift.png", mark_boundaries(correct_img, segments_quick))
        io.imsave(r"output/Compact_Watershed.png", mark_boundaries(correct_img, segments_watershed))
 
    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    ax[0, 0].imshow(mark_boundaries(correct_img, segments_fz))
    ax[0, 0].set_title("Felzenszwalbs's method")
    ax[0, 1].imshow(mark_boundaries(correct_img, segments_slic))
    ax[0, 1].set_title('SLIC')
    ax[1, 0].imshow(mark_boundaries(correct_img, segments_quick))
    ax[1, 0].set_title('Quickshift')
    ax[1, 1].imshow(mark_boundaries(correct_img, segments_watershed))
    ax[1, 1].set_title('Compact watershed')
 
    for a in ax.ravel():
        a.set_axis_off()

    plt.show()


def gen_statistics(img):
    data_range = list()
    means = list()
    variances = list()
    entrpoies = list()
    skewness = list()
    for b in range(img.shape[-1]):
        band = img[..., b]
        data_range.append((np.amin(band.ravel()), np.amax(band.ravel())))
        means.append(np.mean(band))
        variances.append(np.var(band))
        entrpoies.append(stats.entropy(band.ravel()))
        skewness.append(stats.skew(band.ravel(), bias=True))

    stat = texttable.Texttable()
    stat.set_cols_align(['c', 'c', 'c', 'c'])
    stat.set_cols_valign(['m', 'm', 'm', 'm'])
    stat.add_rows([['Measure', 'Band-I  ', 'Band-II ', 'Band-III'], ["Range"] + data_range, ["Mean"] + means,
                   ["Variance"] + variances, ["Entropy"] + entrpoies, ["Skewness"] + skewness])
    with open(r"output/statistics.txt", "w+") as file:
        file.write("\n" + stat.draw() + "\n")


def mean_image(img, window=(3, 3)):
    bands = list()
    for b in range(img.shape[-1]):
        bands.append(ndimage.uniform_filter(img[..., b], window))
    return np.dstack(bands)


def variance_image(img, window_size=3):
    bands = list()
    for b in range(img.shape[-1]):
        band = img[..., b]
        mean_img = ndimage.uniform_filter(band, (window_size, window_size))
        sqrmean_img = ndimage.uniform_filter(band ** 2, (window_size, window_size))
        bands.append(sqrmean_img - (mean_img**2))
    print(np.amin(bands[1]), np.amax(bands[1]))
    return np.dstack(bands)


def skewness_image(img, window_size=3):
    bands = list()
    for b in range(img.shape[-1]):
        bands.append(ndimage.generic_filter(img[..., b], stats.skew, window_size))
    return np.dstack(bands)


def entropy_image(img, window_size=3):
    bands = list()
    for b in range(img.shape[-1]):
        bands.append(ndimage.generic_filter(img[..., b], stats.entropy, window_size))
    return np.dstack(bands)


def show_spinner():
    t = threading.currentThread()
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    print('\nProcessing: ', end='', flush=True)
    while getattr(t, "run_flag", True):
        sys.stdout.write(next(spinner))  # write the next character
        time.sleep(0.2)
        sys.stdout.flush()  # flush stdout buffer (actual character display)
        sys.stdout.write('\b')


abspath = os.path.abspath(__file__)
dir_name = os.path.dirname(abspath)
os.chdir(dir_name)

input_image = (np.array(gdal.Open(r'data/study_area.tif').ReadAsArray())).astype(np.uint8)
img_array = img_as_ubyte((input_image.transpose(1, 2, 0)))
straight_image = straighten_image(img_array)
# correct_img = enhance(straight_image)
correct_img = straight_image
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # io.imsave(r"output/rectified_image.tiff", straight_image)
    # io.imsave(r"output/enhanced_image.tiff", correct_img)

if __name__ == '__main__':
    th = threading.Thread(target=show_spinner)
    th.daemon = True
    th.start()
    # segments = segment()
    th.run_flag = False
    th.join()
    sys.stdout.write('\b')
    # io.imsave(r"output/edge.png", variance_image(img_array))
    # io.imsave(r"output/edge.png", variance_image(img_array))
    # io.imsave(r'output/skewness.png', skewness_image(img_array))
    # io.imsave(r'output/entropy.png', entropy_image(img_array))
    io.imsave(r"output/variance.png", variance_image(img_array))

    print("Completed Successfully...\n")
    # show(segments)
