# !/usr/bin/python
"""
Dependencies:

download_and_sort_EIFIGI_raw_data.py
Downloads EFIGI data and processes it into training and validataion folders
based on the Galaxy type.


brew install wget
pip install opencv-python


Author: Avi Vajpeyi and Rahul Remanan
"""
import shutil
import glob
import subprocess
import cv2
import os
from enum import Enum, unique, auto
# custom imports
import fits_to_png


def execute_in_shell(command=None, verbose=False):
    """
    This is a function that executes shell scripts from within python.

    Example usage:
    execute_in_shell(command = ['ls ./some/folder/',
                                'ls ./some/folder/  -1 | wc -l'],
                     verbose = True )

    This command returns dictionary with elements: Output and Error.

    Output records the console output,
    Error records the console error messages.

    :param command: takes a list of shell commands
    :param verbose: takes a boolean value to set verbose level
    :return: Dictionary with two elements Output and Error
    """

    error = []
    output = []

    if isinstance(command, list):
        for i in range(len(command)):
            try:
                process = subprocess.Popen(command[i], shell=True,
                                           stdout=subprocess.PIPE)
                process.wait()
                out, err = process.communicate()
                error.append(err)
                output.append(out)

                if error[0] is not None:
                    print("ERROR: running command {}".format(command[i]))
                    print(err)
                    exit(1)

                if verbose:
                    print('Success running shell command: {}'
                          ''.format(command[i]))
            except Exception as e:
                print('Failed running shell command: {}'.format(command[i]))
                if verbose:
                    print(type(e))
                    print(e.args)
                    print(e)

    else:
        print('The argument command takes a list input ...')
    return {'Output': output, 'Error': error}


def download_data(data_dir, verbose=False):
    """

    :param data_dir: the dir where the data will be saved  (eg ./data/raw/)
    :param verbose: takes a boolean value to set verbose level
    :return: Dictionary with two elements Output and Error
    """
    if verbose:
        print("Downloading files")

    commands = ["mkdir -p " + data_dir]

    # the download URL for the data
    data_urls = [
         "https://www.astromatic.net/download/efigi/efigi_tables-1.6.2.tgz",
         "https://www.astromatic.net/download/efigi/efigi_png_gri-1.6.tgz",
         "https://www.astromatic.net/download/efigi/efigi_ima_u-1.6.tgz",
         "https://www.astromatic.net/download/efigi/efigi_ima_g-1.6.tgz",
         "https://www.astromatic.net/download/efigi/efigi_ima_r-1.6.tgz",
         "https://www.astromatic.net/download/efigi/efigi_ima_i-1.6.tgz",
         "https://www.astromatic.net/download/efigi/efigi_ima_z-1.6.tgz"]
    # the file names and paths after downloading
    tgz_files = [data_dir + "efigi-1.6.tgz",
                 data_dir + "efigi_pics.tgz",   data_dir + "efigi_u_pics.tgz",
                 data_dir + "efigi_g_pics.tgz", data_dir + "efigi_r_pics.tgz",
                 data_dir + "efigi_i_pics.tgz", data_dir + "efigi_z_pics.tgz"]

    # adding download commands
    download_cmd = "wget -O {} {}"
    commands += [download_cmd.format(tgz_files[i], data_urls[i])
                 for i in range(len(tgz_files))]
    return execute_in_shell(command=commands, verbose=verbose)


def unzip_tgz_files(tgz_dir, dest_dir, verbose=False):
    """
    The tgz files to be unzipped

    :param tgz_dir: the dir with the tgz files
    :param dest_dir: ./data/raw/
    :param verbose: takes a boolean value to set verbose level
    :return: Dictionary with two elements Output and Error
    """
    if verbose:
        print("Unzipping files")

    tgz_files = glob.glob(tgz_dir+"*tgz")
    commands = []
    for f in tgz_files:
        commands += ["tar xzf " + f + " -C "+dest_dir, "rm " + f]
    return execute_in_shell(command=commands, verbose=verbose)


def convert_fits_to_png(fits_root_folder, fits_folders, verbose=False):
    """


    :param fits_root_folder: Folder containing other folders with FITS folders
    :param fits_folders: list of folder names containing fits files
    :param verbose: takes a boolean value to set verbose level
    :return:
    """
    if verbose:
        print("Unzipping files")

    for fits_folder in fits_folders:
        fits_dir = os.path.join(fits_root_folder, fits_folder)
        try:
            fits_to_png.fits_folder_to_png(fits_dir=fits_dir,
                                           make_vid=True,
                                           delete_fits=True,
                                           verbose=verbose)
        except NameError:
            fits_folder_to_png(fits_dir=fits_dir,
                               make_vid=True,
                               delete_fits=True,
                               verbose=verbose)


def zip_folder(folder_dir, zipped_filepath, verbose=False):
    """
    zips a folder into a .zip file

    :param folder_dir: the dir of the folder to be zipped
    :param zipped_filepath: the filepath of the resultant zipped folder
    :param verbose:
    :return:
    """
    commands = ["zip -r {} {}".format(zipped_filepath, folder_dir)]
    return execute_in_shell(command=commands, verbose=verbose)


def download_and_process_raw_files(root_dir, verbose=False):
    """

    :param root_dir:
    :param verbose:
    :return:
    """

    raw_data_dir = os.path.join(root_dir, "data/raw/")
    download_data(raw_data_dir, verbose)

    dest_dir = raw_data_dir
    unzip_tgz_files(raw_data_dir, dest_dir, verbose)

    fits_folders = ["ima_g", "ima_i", "ima_u", "ima_z", "ima_r"]
    unzipped_data_dir = os.path.join(raw_data_dir, "efigi-1.6")
    convert_fits_to_png(unzipped_data_dir, fits_folders, verbose)


def make_folders_from_labels(root_dir, verbose=False):

    if verbose:
        print("Make Organisational Folders")

    label_classes = [name for name, _ in T.__members__.items()]
    mk_train_fldr = "mkdir -p {}/data/train/".format(root_dir) + "{}"
    mk_val_fldr = "mkdir -p {}/data/validation/".format(root_dir) + "{}"
    commands = []
    for label_class in label_classes:
        commands += [mk_train_fldr.format(label_class),
                     mk_val_fldr.format(label_class)]

    if verbose:
        commands += ['echo "Folders in ./data/train/:"']
        commands += ["!ls ./data/train/"]
    execute_in_shell(commands)


def row_generator(filepath):
    """
    Grabs one row of the txt file if its not a comment
    :param filepath: path to the txt file
    :return: None
    """

    with open(filepath) as fp:

        row = ""
        # Skip initial comments that starts with #
        while True:
            row = fp.readline()
            if not row.startswith('#'):
                break

        # Second while loop to process the rest of the file
        while row:
            yield (row)
            row = fp.readline()

    pass



def move_files_according_to_txt(data_dir, dest_dir, extension, verbose):

    txt_filepath = os.path.join(data_dir, "EFIGI_attributes.txt")
    extensions = [None, "g", "i", "u", "z", "r"]
    image_folders = ["png", "ima_g", "ima_i", "ima_u", "ima_z", "ima_r"]
    image_dirs = [os.path.join(data_dir, f) for f in image_folders]

    for i in range(len(extensions)):

        image_dir = image_dirs[i]
        extension = extensions[i]
        if verbose:
            print("Moving images from " + image_folders[i])
        count = 0
        for line in row_generator(txt_filepath):
            attributes = line.split()

            # create file name based on PGC_name
            if extension is None:
                image_fname = attributes[0] + ".png"
            else:
                image_fname = attributes[0] + "_" + extension + ".png"

            # get type according to dataset
            image_class = check_class(attributes[1])
            image_class = image_class.name

            # move image from curr dir to new dir
            current_image_path = os.path.join(image_dir, image_fname)
            dest_image_path = os.path.join(dest_dir, image_class, image_fname)
            shutil.move(current_image_path, dest_image_path)

            count += 1
            if count % 100 == 0 and verbose:
                print("Image Num" + str(
                    count) + ": " + image_fname + " is a " + image_class)




@unique
class T(Enum):
    """
    Enum to store the different types of galaxies
    """
    ELLIPTICAL = auto()
    LENTICULAR = auto()
    SPIRAL = auto()
    IRREGULAR = auto()
    DWARF = auto()

    def __str__(self):
        """
        To print the name of the galaxy type when enum printed
        :return:  name of the galaxy type
        """
        return str(self.name)


def check_class(t_val):
    """
    Takes the t_val attribute and returns the associated enum
    :param t_val:  the attribute number (int)
    :return: the enum associated with the attribute number
    """
    try:
        t_val = int(t_val)
    except ValueError:
        pass  # it was a string, not an int.
    if t_val < -3:
        return T.ELLIPTICAL
    elif t_val < 0:
        return T.LENTICULAR
    elif t_val < 10:
        return T.SPIRAL
    elif t_val == 10:
        return T.IRREGULAR
    elif t_val == 11:
        return T.DWARF
    else:
        print("ERROR")
        # raise exception
        return None


def main():
    download_and_process_raw_files(root_dir="/Users/Vajpeyi/Documents/PostGraduation2018/MOADresearch/akash_ganga", verbose=True)

if __name__=="__main__":
    main()