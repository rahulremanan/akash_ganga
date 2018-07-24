"""
Dependencies:
    pip install opencv - python
    pip install astropy --no-deps

fits_to_png.py
Converts FITS files into PNGs. Can also make the PNGs into a video and delete
the FITS after processing into PNGs.

usage: fits_to_png.py [-h] [--video] [-d] [-v] fits_dir

Author: Avi Vajpeyi and Rahul Remanan
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from astropy.io import fits
import numpy as np
import glob
import os
import sys
import argparse
# custom import
import create_video

matplotlib.use('Agg')


def fits_to_png(fits_fn,
                delete_fits=False):
    """
    Converts the FITS file into a PNG image.
    Assumes that the image information is located in the Primary HDU of the
    FITS file.

    :param fits_fn: The FITS files
    :return: None
    """
    # Generally the image information is located in the Primary HDU (ext 0)
    # read the image data from this first extension using the keyword argument
    data = fits.getdata(fits_fn, ext=0)

    sizes = np.shape(data)
    height = float(sizes[0])
    width = float(sizes[1])

    fig = plt.figure()
    fig.set_size_inches(width / height, 1, forward=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)

    ax.imshow(data, cmap="binary")

    # creating png filename from fits filename
    png_fn = fits_fn.split(".fits")[0] + ".png"

    plt.savefig(png_fn, dpi=height)
    plt.close()

    if delete_fits:
        os.remove(fits_fn)
    pass


def fits_folder_to_png(fits_dir,
                       make_vid=False,
                       delete_fits=False,
                       verbose=False):
    """
    Converts all the FITS file in a dir to PNG images. Can also make a movie of
    the PNGs and can delete the FITS after processing complete.

    :param fits_dir: The folder containing the FITS files
    :param make_vid: bool to makes a video of the PNGs if True
    :param delete_fits: deletes FITS files after processing if True
    :param verbose: bool to print status of processed files
    :return: None
    """
    if verbose:
        print("FITS-->PNG for " + fits_dir.split('/')[-1])

    fits_files = glob.glob(os.path.join(fits_dir,  "*.fits"))
    num_files = len(fits_files)
    status_flag = num_files * 0.1

    for i in range(0, num_files):
        fits_to_png(fits_files[i], delete_fits)

        if verbose and i > status_flag:
            status_flag += num_files * 0.1
            p_done = i / num_files * 100
            print(str(round(p_done, 0)) + "% processed")

    if make_vid:
        vid_made = create_video.make_movie_from_png(fits_dir)
        if verbose and vid_made:
            print("Successfully saved video")
    pass


def delete_fits_from_folder(fits_dir):
    """
    Deletes the FITS files from fits_dir
    :param fits_dir: The dir containing the FITS files
    :return: True if successfully removed else False
    """
    fits_files = glob.glob(os.path.join(fits_dir, "*.fits"))
    if fits_files:
        for f in fits_files:
            os.remove(f)
        return True
    return False


def main():
    """
    Takes command line arguments to process a folder with FITS files into PNGs

    Positional parameters
    [STRING] fits_dir: the dir containing the FITS files

    Optional parameters
    [BOOL] video: to make the PNG files that are created into a video
    [BOOL] verbose: to print out FITS->PNG progress
    [BOOL] delete: to delete the FITS files once converted into PNGs

    :return: None
    """
    parser = argparse.ArgumentParser(description='Process FITS files.')

    # Positional parameters
    parser.add_argument("fits_dir", help="dir where fits files located")

    # Optional parameters
    parser.add_argument("--video", help="make a video of the PNGs generated",
                        action="store_true")
    parser.add_argument("-d", "--delete",
                        help="delete FITS files after PNG creation",
                        action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")

    args = parser.parse_args()

    if os.path.isdir(args.fits_dir):
        fits_folder_to_png(fits_dir=args.fits_dir,
                           make_vid=args.video,
                           delete_fits=args.delete,
                           verbose=args.verbose)
    else:
        print("Error: Invalid fits dir")
        sys.exit(1)
    pass


if __name__ == "__main__":
    main()
