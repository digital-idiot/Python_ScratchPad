import matplotlib.pyplot as plt
import numpy as np
import gdal
import threading
import itertools
import sys
import time

from skimage.color import rgb2gray
from skimage.filters import sobel
from skimage.segmentation import felzenszwalb, slic, quickshift, watershed
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float


image = (np.array(gdal.Open(r'data/image.tif').ReadAsArray())).astype(float)
image = image.transpose(1, 2, 0)
img = img_as_float(image[::2, ::2])


def main(): 
    segments_fz = felzenszwalb(img, scale=100, sigma=0.5, min_size=100)
    segments_slic = slic(img, n_segments=500, compactness=10, sigma=0.5)
    segments_quick = quickshift(img, kernel_size=5, max_dist=5, ratio=0.001)
    gradient = sobel(rgb2gray(img))
    segments_watershed = watershed(gradient, markers=500, compactness=0.001)
    return [segments_fz, segments_slic, segments_quick, segments_watershed]


def show(lst):
    segments_fz = lst[0]
    segments_slic = lst[1]
    segments_quick = lst[2]
    segments_watershed = lst[3]
    print("Felzenszwalb number of segments: {}".format(len(np.unique(segments_fz))))
    print('SLIC number of segments: {}'.format(len(np.unique(segments_slic))))
    print('Quickshift number of segments: {}'.format(len(np.unique(segments_quick))))
 
    fig, ax = plt.subplots(2, 2, figsize=(100, 100), sharex=True, sharey=True)
 
    ax[0, 0].imshow(mark_boundaries(img, segments_fz))
    ax[0, 0].set_title("Felzenszwalbs's method")
    ax[0, 1].imshow(mark_boundaries(img, segments_slic))
    ax[0, 1].set_title('SLIC')
    ax[1, 0].imshow(mark_boundaries(img, segments_quick))
    ax[1, 0].set_title('Quickshift')
    ax[1, 1].imshow(mark_boundaries(img, segments_watershed))
    ax[1, 1].set_title('Compact watershed')
 
    for a in ax.ravel():
        a.set_axis_off()
 
    plt.tight_layout()
    plt.show()


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
    th = threading.Thread(target=show_spinner)
    th.daemon = True
    th.start()
    segments = main()
    th.run_flag = False
    th.join()
    sys.stdout.write('\b')
    print("Completed Successfully...\n")
    show(segments)

