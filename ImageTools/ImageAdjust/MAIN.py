#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 14:07:34 2018

Main script for downloading and managagin images from google according to a 
food database with keywords.



@author: Mads Obdrup Jakobsen
"""

# Import libraries and modules
from get_food_images_folders import downloadImages
from remove_corrupted_images import clean_foodimages
from partition_images import partition_data
from resizeFoodImg import resizeImageFolder
from mergeFolders import mergeFoldersFunc
from adjustImage import *
from pathlib import Path
import numpy as np

# Set path to food dataase csv file and main folder to save images
path_to_FoodDataBase = (Path.home()  / 'DTU' / 'DeepLearning' /'Hedia'/'class1.xlsx')

path_to_dataFolder = (Path.home()  /'DTU' / 'DeepLearning' /'Hedia')

nTypes = 2 # Number of distinct food types to download
nEacgFood = 4 # Number of images to download from each category
trainRatio = 1/5 # How large ratio of the images should be saved for validation

# Run the three files to download and manage images
timestamp = downloadImages(path_to_FoodDataBase , path_to_dataFolder, nTypes = nTypes, nOfEachType = nEacgFood)
clean_foodimages(path_to_dataFolder , timestamp)
partition_data(trainRatio , path_to_dataFolder , timestamp)


#%% 

'''
Rescale images
    If you choose to overwrite the original images when rescaling, remember to
    remember to run the partion_data() function again, to copy the normal scaled
    images from the raw image folder
'''

# Set parameters for image scaling
newShape = np.array((100,100))
CropOrPad = 0 # See documentation of resizeImageFolder()
cropShape = np.array([-100,100,-100,100]) # Only active if crop is chosen

read_path = Path.home() / 'DTU' / 'DeepLearning' /'Hedia' / 'food images' / 'google' / timestamp / 'DL'

resizeImageFolder(read_path, save_path = read_path , newShape = newShape , CropOrPad = 0)


## OPTIONAL MERGE OF FOLDERS AGAIN TO ACHIEVE SAME STRUCTURE AS IN WEEK 4
merge = True
if merge:
    mergeFoldersFunc(timestamp, read_path)