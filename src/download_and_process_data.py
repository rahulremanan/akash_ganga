# !/usr/bin/python
"""
Dependencies: astropy

Downloads EFIGI data and processes it into training and validataion folders
based on the Galaxy type.

The image labeling is done using the t-values.

    t_val < -3 are classified elliptical galaxy.
    -3< t_val < 0 are classified lenticular galaxy.
    0< t_val < 10 is classified as spiral galaxy.
    t_val = 10 is classifier as irreugular galaxy.
    t_val = 11 is classfied as a dwarf galaxy.

@authors: Avi Vajpeyi and Rahul Remanan
@support: info@moad.computer

"""
import shutil
import glob
import argparse
import os
import random
from enum import Enum, unique, auto

# custom imports
import fits_to_png
import execute_in_shell

def string_to_bool(val):
    """
        A function that checks if an user argument is boolean or not.
        
        Example usage:
            
            
                import argsparse
            
                a = argparse.ArgumentParser()
                
                a.add_argument("--some_bool_arg", 
                   help = "Specify a boolean argument ...", 
                   dest = "some_bool_arg", 
                   required=False, 
                   default=[True], 
                   nargs=1, 
                   type = string_to_bool)
                
            args = a.parse_args()
            
            args = get_user_options()
            
    """
    if val.lower() in ('yes', 'true', 't', 'y', '1', 'yeah', 'yup'):
        return True
    elif val.lower() in ('no', 'false', 'f', 'n', '0', 'none', 'nope'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected ...')

def is_valid_dir(parser, arg):
    """
        This function checks if a directory exists or not.
        It can be used inside the argument parser.
        
        Example usage: 
            
            import argsparse
            
            a = argparse.ArgumentParser()
            a.add_argument("--dir_path", 
                              help = "Check if a file exists in the specified file path ...", 
                              dest = "file_path", 
                              required=False,
                              type=lambda x: is_valid_dir(a, x),
                              nargs=1)
            
            args = a.parse_args()
            
            args = get_user_options() 
    """
    if not os.path.isdir(arg):
        try:
            parser.error("The folder %s does not exist ..." % arg)
        except:
            if parser != None:
                print ("No valid argument parser found")
                print ("The folder %s does not exist ..." % arg)
            else:
                print ("The folder %s does not exist ..." % arg)
    else:
        return arg

def download_data(data_dir, 
                  verbose=False):
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
    return execute_in_shell.execute_in_shell(command=commands, verbose=verbose)


def unzip_tgz_files(tgz_dir, 
                    dest_dir, 
                    verbose=False):
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
    return execute_in_shell.execute_in_shell(command=commands, verbose=verbose)


def convert_fits_to_png(fits_root_folder, 
                        fits_folders, 
                        verbose=False):
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
                                           make_vid=False,
                                           delete_fits=True,
                                           verbose=verbose)
        except NameError:
            fits_folder_to_png(fits_dir=fits_dir,
                               make_vid=False,
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
    return execute_in_shell.execute_in_shell(command=commands, verbose=verbose)


def download_and_process_raw_files(root_dir, 
                                   verbose=False):
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


def make_folders_from_labels(root_dir, 
                             verbose=False, 
                             label_classes = None):

    if verbose:
        print("Make Organisational Folders")

    mk_train_fldr = "mkdir -p {}/train/".format(root_dir) + "{}"
    mk_val_fldr = "mkdir -p {}/validation/".format(root_dir) + "{}"
    commands = []
    for label_class in label_classes:
        commands = [mk_train_fldr.format(label_class),
                     mk_val_fldr.format(label_class)]

    if verbose:
        commands.append(['echo "Folders in {}/train/:"'.format(root_dir)])
        commands.append(["ls {}/train/".format(root_dir)])
    execute_in_shell.execute_in_shell(command = commands, verbose = verbose)


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



def move_files_according_to_txt(txt_filepath = None,
                                image_folders = None,
                                data_dir = None, 
                                dest_dir = None, 
                                extensions = None, 
                                verbose = None):
    image_dir = image_folders
    extension = extensions
    if verbose:
        print("Moving images from " + image_folders)
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
        try:
            image_class = image_class.name
        except:
            print ("Failed to process image: {}".format(image_fname))

        # move image from curr dir to new dir
        current_image_path = os.path.join(str(data_dir), str(image_dir) , str(image_fname))
        print (current_image_path)
        dest_image_path = os.path.join(str(dest_dir), str(image_class) , str(image_fname))
        print (dest_image_path)
        if os.path.exists(os.path.join(str(dest_dir), str(image_class))) !=True:
            make_folder(input_dir =  (os.path.join(str(dest_dir), str(image_class))), 
                verbose = verbose)
        if os.path.exists(current_image_path):
            try:
                shutil.move(current_image_path, dest_image_path)
            except:
                if verbose:
                    print ("Failed to move: {}".format(current_image_path))
        else:
            if verbose:
                print ("File not found: {}".format(current_image_path))

        count += 1
        if count % 100 == 0 and verbose:
            try:
                print("Found a total of: " + str(count) + ": images " + image_fname + "belonging to the image class: " + image_class)
            except:
                print ("Failed processing image class {}".format(image_class))

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
    elif -3 < t_val < 0:
        return T.LENTICULAR
    elif 0 < t_val < 10:
        return T.SPIRAL
    elif t_val == 10:
        return T.IRREGULAR
    elif t_val == 11:
        return T.DWARF
    else:
        print("ERROR")
        # raise exception
    return None

def make_folder(input_dir = None, 
                verbose = False):
    try:
        if not os.path.exists(input_dir):
            os.makedirs(input_dir)
            if verbose:
                return 'Sucessfully created the folder {}'.format(input_dir)
    except OSError as err:
        print ('Failed to create directory: {} ...'.format(input_dir))
        print ('Encountered an error {}'.format(err.args))
    
def shuffle_data(train_folder = None, 
                 validation_folder = None, 
                 data_split = None,
                 verbose = False):
  if 0<data_split<1:
    data_split = data_split
    if verbose:
        print ("Training data generated using default train-validation split of {}% ... ".format(data_split*100))
  else:
    if verbose:
        print ('Please input a data_split value between 0 and 1 ...')
    data_split = 0.2
    if verbose:
        print ('Training data generated using default train-validation split of 20% ...')
  subfolders = [f.path for f in os.scandir(train_folder) if f.is_dir()] 

  # For each training folder 
  for train_class_dir in subfolders:

    # Get total number of files in folder
    images = glob.glob(train_class_dir+"/*.png")
    total_num = len(images)
    print (train_class_dir +" has " + str(total_num)+" images.")

    # Shuffle 20% files
    number_of_validation = int(data_split*float(total_num)) # 20% validation
    files_to_move = random.sample(images, number_of_validation)


    class_name = train_class_dir.split("/")[-1]

    # Move 20% to the validation folder of the same class
    for file_dir in files_to_move:
      destination_dir = file_dir.split("/train/")[0]+"/validation/"+file_dir.split("/train/")[-1]
      make_folder(input_dir = destination_dir,
                  verbose = verbose)
      shutil.move(file_dir, destination_dir)

    num_images_remaining = len(glob.glob(train_class_dir+"/*.png"))
    if verbose:
        print ("After transfer " + str(num_images_remaining)+" images will remain in the training folder.\n")
  return None


def get_user_options():
    a = argparse.ArgumentParser()
    
    a.add_argument("--root_dir", 
                   help = "Specify the root directory ...", 
                   dest = "root_dir", 
                   required = True, 
                   type=lambda x: is_valid_dir(a, x), 
                   nargs=1)
    
    a.add_argument("--fetch_raw_data", 
                   help = "Specify whether raw data should be downloaded from EFIGI project website ...", 
                   dest = "fetch_raw_data", 
                   required = True, 
                   default = [True],
                   type=string_to_bool, 
                   nargs=1)
    
    a.add_argument("--verbose", 
                   help = "Specify versboe level ...", 
                   dest = "verbose", 
                   required = False, 
                   default = [True],
                   type=string_to_bool, 
                   nargs=1)
    
    a.add_argument("--create_train_data", 
                   help = "Specify whether to generate training data ...", 
                   dest = "create_train_data", 
                   required = True, 
                   default = [True],
                   type=string_to_bool, 
                   nargs=1)
    
    a.add_argument("--data_split", 
                   help = "Specify the validation:train split ...", 
                   dest = "data_split", 
                   required = True, 
                   default = [0.2],
                   type=float, 
                   nargs=1)
    args = a.parse_args()   
    return args  

if __name__=="__main__":
    args = get_user_options()
    verbose = args.verbose[0]
    if os.path.exists(args.root_dir[0]) != True:
        print ("Invalid root folder for processing the EFIGI data ...")
        sys.exit(1)
    if args.fetch_raw_data[0]:
        download_and_process_raw_files(root_dir=args.root_dir[0], \
                                       verbose=verbose)
    image_folders = ["png","ima_g", "ima_i", "ima_u", "ima_z", "ima_r"]
    extensions =[None, "g","i","u","z","r"]

    if args.create_train_data[0]:
      make_folders_from_labels(args.root_dir[0], 
                               verbose=verbose,
                               label_classes = [name for name, _ in T.__members__.items()])
      for i in range(0,len(extensions)):
          move_files_according_to_txt(txt_filepath = "{}/data/raw/efigi-1.6/EFIGI_attributes.txt".format(args.root_dir[0]),
                                      image_folders = image_folders[i],
                                      data_dir = "{}/data/raw/efigi-1.6/".format(args.root_dir[0]), 
                                      dest_dir = "{}/train".format(args.root_dir[0]), 
                                      extensions = extensions[i], 
                                      verbose = verbose)
          
      shuffle_data(train_folder = os.path.join(args.root_dir[0]+'/train/'),
                   validation_folder = os.path.join(args.root_dir[0]+'/validation/'),
                   data_split = args.data_split[0],
                   verbose = verbose)