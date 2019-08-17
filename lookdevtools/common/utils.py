import random
import os
import logging
from lookdevtools.external import fuzzywuzzy
from lookdevtools.external.fuzzywuzzy import *

def get_random_color(seed):
    random.seed(seed + "_r")
    color_red = random.uniform(0, 1)
    random.seed(seed + "_g")
    color_green = random.uniform(0, 1)
    random.seed(seed + "_b")
    color_blue = random.uniform(0, 1)
    return [color_red, color_green, color_blue]

def create_directoy(path):
    try:
        # Create target Directory
        os.mkdir(path)
        logging.info("Directory create: %s" % path)
    except:
        logging.info("Directory alreay exists: %s" % path)

def is_directory(path):
    if os.path.exists(path) and os.path.isdir(path):
        return True
    else:
        return False

def get_files_in_folder (path, recursive = False, pattern = None):
    """Searchs files in a folder, with options for recursive search,
    and matching a pattern, usually used for extensions like '.exr'
    """
    logging.info("Searching for files in: %s" % path)
    logging.info("Search options: Recursive %s, pattern: %s" % (recursive,pattern))
    if os.path.isdir(path):
        for path, subdirs, files in os.walk(path):
            file_list = []
            for file in files:
                if pattern:
                    if pattern in file:
                        file_list.append(os.path.join(path,file))
                        logging.info("File with pattern found, added to the list: %s" % file)
                else:
                    file_list.append(os.path.join(path,file))
                    logging.info("File added to the list: %s" % file)
            if not recursive:
                break
    else:
        raise ValueError("Path not valid")
    return file_list

# fuzz.ratio
# fuzz.partial_ratio
# fuzz.token_sort_ratio
# fuzz.token_set_ratio

def string_matching_ratio(stringA, stringB):
    """Compares two strings and returns a ratio"""
    # We can -in the future- change the fuzzy string
    # comparisson algorigth here, maybe bitap with
    # partial substring matching will be better
    # Test Results:
    '''
    Different channels fuzzy ratio
        ('baseColor','diffusecolor')        =   67
        ('base','diffusecolor')             =   25
        ('specular','specularColor')        =   76
        ('specular','specularcolor')        =   76
        ('specular_color', 'specular_bump') =   67
        ('coat_color', 'coat_ior')          =   78
        ('secondary_specular_color', 'secondary_specular_ior')  =   91
        ('subsurface_weight', 'subsurface_Color')   =  67
        ('emission', 'emission_weight')     =   70
    Same channel diferent naming ratio
        ('diffuse_weight','diffuseGain')    =   64
    '''
    print fuzzywuzzy.fuzz.token_set_ratio(stringA, stringB)

# from lookdevtools.common import utils
# print utils.string_matching_ratio('a','b')