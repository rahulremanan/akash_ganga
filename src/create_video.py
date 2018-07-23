"""
Dependencies:
    pip install opencv - python

pngs_to_avi.py
Makes all the PNGs from one dir into a video .avi file

usage: pngs_to_avi.py [-h] [-d] png_dir

Author: Avi Vajpeyi and Rahul Remanan
"""
import sys
import argparse
import glob
import cv2
import os

def make_movie_from_png(png_dir, delete_pngs=False):
    """
    Takes PNG image files from a dir and combines them to make a movie
    :param png_dir: The dir with the PNG
    :return:
    """
    vid_filename = png_dir.split("/")[-1] + ".avi"
    vid_filepath = os.path.join(png_dir, vid_filename)
    images = glob.glob(os.path.join(png_dir, "*.png"))

    if images:
        frame = cv2.imread(images[0])
        height, width, layers = frame.shape

        video = cv2.VideoWriter(vid_filepath, -1, 25, (width, height))

        for image in images:
            video.write(cv2.imread(image))

        video.release()

        if delete_pngs:
            for f in images:
                os.remove(f)

        return True
    return False

def main():
    """
    Takes command line arguments to combine all the PNGs in dir into a .avi

    Positional parameters
    [STRING] png_dir: the dir containing the png files

    Optional parameters
    [BOOL] delete: to delete the PNG files once converted into a video

    :return: None
    """
    parser = argparse.ArgumentParser(description='Process PNG files.')

    # Positional parameters
    parser.add_argument("png_dir", help="dir where png files located")

    # Optional parameters
    parser.add_argument("-d", "--delete",
                        help="delete PNG files after .avi creation",
                        action="store_true")

    args = parser.parse_args()

    if os.path.isdir(args.fits_dir):
        make_movie_from_png(png_dir=args.png_dir,
                            delete_pngs=args.delete)

    else:
        print("Error: Invalid png dir")
        sys.exit(1)
    pass

if __name__ == "__main__":
    main()