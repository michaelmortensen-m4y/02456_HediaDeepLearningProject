#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 14:07:34 2018

Main script for downloading and managagin images from google according to a 
food database with keywords.



@author: Mads Obdrup Jakobsen
"""

# Import libraries and modules
#from get_food_images_folders import downloadImages
#from remove_corrupted_images import clean_foodimages
#from partition_images import partition_data
#from resizeFoodImg import resizeImageFolder
#from mergeFolders import mergeFoldersFunc

from pathlib import Path
import numpy as np
import random
import pandas as pd
from google_images_download import google_images_download
import time

import os
import shutil

from os import listdir
import math
import random

from PIL import Image

from os import listdir, makedirs
from os.path import exists
from skimage.io import imread, imsave

from skimage.transform import resize
from PIL import Image, ImageOps

from PIL import ImageFilter
from skimage import exposure

import cv2

def downloadImages(path_to_food_database , path_to_datafolder , nTypes, nOfEachType):
    
    """ This function downloads images from google according to food keywords 
    in food database
    
    The function access food keywords accoring to a food database (Notice that 
    the database must have the same structure as the one delivered with the 
    code) and scrapes google for each foodtype. 
    The images are sorted in each type in path_to_datafolde
    and a csv file is written with information about each image.
    
    Args:
        path_to_food_database: The path to a food data base (csv).
        
        path_to_datafolder:    The path to the main directory of the 
                               downloaded image structure.
                               
        nTypes:                Number of distinct types of food to download.
        
        nOfEach:               Number of images to download within each food type.

    Return:
        Timestamp (ddmmyy_hhmm) telling when the script was run. This is used 
        to locate the folder in which the images are safed.
    
    @author: Mads Obdrup Jakobsen
    """
    response = google_images_download.googleimagesdownload()   #class instantiation
    
    # Load Food data base from Excel
    path = Path(path_to_food_database)
    #food_dict = pd.read_excel(path, parse_cols = [2],sheet_name = None)
    food_dict = pd.read_excel(path,sheet_name = None)
    
    
    
    # Collect names of food, trim names (remove details) 
    # and tuple them with their category
    i = 0
    food_names = []
    for key in food_dict.keys():
        dat = food_dict[key]
        #foodlist = dat.iloc[:,0]
        foodlist = dat.iloc[:]
        print(foodlist)
        for meal in foodlist:
            
            # Removes extra details from food name
            meal = meal.split(",")[0]
            meal = meal.split("(")[0]
            food_names.append( (meal , key) )
    
    
    # Remove duplicaes
    food_names = set(food_names)
    
    
    ########### Download images from google by searching for each food type ##
    timestamp = time.strftime("%d%m%y") + "_" + time.strftime("%H%M")
    
    # Set download directory
    path = path_to_datafolder + '\\food images' + '\\google\\' + timestamp + '\\raw'
    
    # Set number of food types to download
    nFood = nTypes-1
    # Set number of 
    id_list = []
    for i, searchkey in enumerate(food_names):
        
        # Get names of food
        food_name = searchkey[0] 
        print("Search string: {0}".format(food_name))
        foldername = str(i)
        
        # Defines arguments for search function
        arguments = {"format" : "jpg",
                     "keywords":food_name,
                     "limit":nOfEachType,
                     "image_directory":foldername,
                     "print_paths":True,
                     "output_directory":str(path),
                     "print_urls" : False,
                     "chromedriver" : "C:\\Chromedriver\\chromedriver.exe"
                     }
        print(i)   
        # Passing the arguments to the function
        paths = response.download(arguments)   
        
        # Match up Id Number, food name, main category and path to image
        for ImagePath in paths[food_name]:
            ImagePath = ImagePath.split('raw\\')[-1] ######
            print(ImagePath)
            id_list.append( (i , food_name , searchkey[1] , ImagePath) )
        if i > nFood:
            break
     
      
    # Construct dataframe with id and image info to log file 
    foodDataFrame = pd.DataFrame(id_list)
    foodDataFrame.columns = ["Food Class Label",
                             "Name of Food",
                             "Name of Category",
                             "Image Path"]
    
    logfilename = 'dataLog.csv'
    # Saves the logfile as CSV
    filename = path_to_datafolder + '\\food images' + '\\google\\' + timestamp + '\\raw\\' + logfilename
    foodDataFrame.to_csv(filename, sep=',', encoding='utf-8' , index = 0)
    
    return timestamp

def mergeFoldersFunc(timestamp, path):
    
    """ 
    Created on Wed Oct 10 13:50:17 2018
    
    --------------------------------------------------------------------------
    Optional function to merge the two train and testing folders renaming all 
    images to their index thus achieving the same data format as the one used
    in the Kaggle Challenge from Week 4 of 02456 Deep Learning E18 DTU
    This function downloads images from google according to food keywords 
    in food database.
    
    Args:
        timestamp: The timestamp of the download directory to be handled
        
        path:      Path to the parent directory of the folder to be merged
        

    Return:
        0
    
    @author: Mads Obdrup Jakobsen
    """
    
    # Create folder to ocntain the merged folders
    if not os.path.exists(path + '\\images_all'):
        os.makedirs(path + '\\images_all' )
        
    
    # Loop over the test and train folders
    for testOrTrain in ['train' , 'test']:
        Df = pd.read_csv(path + "\\" + (testOrTrain + '.csv'), sep = "," , header = 0)
        
        # Loop over all images in folder, move to images_all and rename to index
        #for imgPaths , idx  in zip(Df['Image Path'] , Df['id']):
            #imgPath = path + "\\" + (testOrTrain + 'ing_images') + "\\" + imgPaths
            #shutil.copy(imgPath, path + '\\images_all\\' + (str(idx)+'.jpg') )

def partition_data(trainRatio,path_to_datafolder,timestamp):
    
    """ 
    Created on Wed Sep 12 12:04:18 2018
    
    --------------------------------------------------------------------------
    This function partition images into training and test folder keeping the 
    class structure
    
    The function splits up a folder containing class separated images into two 
    folder with same separation. Each folder (training and testing) contains a 
    subset of the original collection of images accoring to a
    inputted ratio.
    
    Args:
        trainRatio:            The ratio determing the amount of images saved 
                               for validation versus training
                               
        path_to_datafolder:    The path to the main data directory
        
        timestamp:             The timestamp for which the images was 
                               downloaded (ddmmyy_hhmm)

    Return:
        0
    
    @author: Mads Obdrup Jakobsen
    """
    
    # Acces the relevant folders
    FolderToPartion = timestamp
    LogName = 'dataLogNoCorrupt.csv'
    path_train = path_to_datafolder + '\\food images' + '\\google\\' + FolderToPartion + '\\raw'
    dirs = listdir(path_train)
    dirs.remove(LogName)
    try:
        dirs.remove('.DS_Store')
    except:
        pass
    
    dirs = [int(i) for i in dirs]
    df2 = pd.read_csv(path_to_datafolder + '\\food images\\' + 'google\\' + FolderToPartion + '\\raw\\' + LogName, sep = "," , header = 0)
    
    nImage = df2.shape[0]
    print(nImage)
    # Allocates space in the dataframe for new index
    df2['Set index'] = np.zeros(nImage, dtype = np.int8)
    newFrame = df2[df2['Food Class Label'] == -1]
    
    classes = set(df2['Food Class Label'])
    for clas in classes:
        # Create folder tree
        path = (path_to_datafolder + '\\food images\\' + 'google\\' + FolderToPartion + '\\raw' )
        
        # Extract a subframe of logFrame to only consider one type of food
        subFrame = df2[df2['Food Class Label'] == clas]
        N = subFrame.shape[0]
        nTest = math.floor(trainRatio * N)
        nTrain = N - nTest
        ind = list(range(0,N))
        random.shuffle(ind)
        indTrain = ind[:(nTrain)]
        indTest = ind[nTrain:]
        
        # Put a one in the "Set Index" if file is in the training set
        subFrame.loc[subFrame.index[indTrain] , "Set index"] = 1
        
        # Append the extended frame to the total frame
        newFrame = newFrame.append(subFrame)
    
        path_test = (path_to_datafolder + '\\food images' + '\\google\\' + FolderToPartion + '\\DL' + '\\testing_images')
        path_train = (path_to_datafolder + '\\food images' + '\\google\\' + FolderToPartion + '\\DL\\' + 'training_images')
        
        # Copy files to new test/training folders
        if not os.path.exists(path_test + "\\" + str(clas)):
            os.makedirs(path_test + "\\" + str(clas))
        if not os.path.exists(path_train + "\\" + str(clas)):
            os.makedirs(path_train + "\\" + str(clas)) 
            
        IMGpaths = subFrame['Image Path']
        
        for index in indTrain:
            if (".jpg" in str(IMGpaths.iloc[index])):
                try:
                    shutil.copy(path + "\\" + IMGpaths.iloc[index], path_train + "\\" + IMGpaths.iloc[index])
                except:
                    print("shutil failed.")
            else:
                print("A non-jpg file was skipped: {0}".format(str(IMGpaths.iloc[index])))
            
            #shutil.copy(IMGpaths.iloc[index], IMGpaths.iloc[index])
        
        for index in indTest:
            if (".jpg" in str(IMGpaths.iloc[index])):
                try:
                    shutil.copy(path + "\\" + IMGpaths.iloc[index], path_test + "\\" + IMGpaths.iloc[index])
                except:
                    print("shutil failed.")
            else:
                print("A non-jpg file was skipped: {0}".format(str(IMGpaths.iloc[index])))
    
    
    newFrame = newFrame.sort_index()
    id_col = list(range(1,nImage+1))
    print(id_col)
    newFrame.insert(loc=0, column='id', value=id_col)
    logfilename =  'PartionLog.csv'
    
    # Saves the logfile as CSV
    filename = (path_to_datafolder + '\\food images\\' + 'google\\' + timestamp + "\\DL\\" + logfilename)
    newFrame.to_csv(filename, sep=',', encoding='utf-8' , index = 0)
    
    # Create a csv file for train and test set
    testFrame = newFrame[newFrame["Set index"] == 0]
    testFilename = (path_to_datafolder + '\\food images\\' + 'google\\' + timestamp + "\\DL" + '\\test.csv')
    trainFrame = newFrame[newFrame["Set index"] == 1]
    trainFilename = (path_to_datafolder + '\\food images\\' + 'google\\' + timestamp + "\\DL" + '\\train.csv')
    
    testFrame.to_csv(testFilename, sep=',', encoding='utf-8' , index = 0)
    trainFrame.to_csv(trainFilename, sep=',', encoding='utf-8' , index = 0)
    
    
    return 0

def clean_foodimages(path_to_datafolder , timestamp, srcfolder):
    
    """ Cleans a directory of downloaded images
    
    The function acces all images in the specified directory and removes any 
    images which is not jpg or cannot be accessed. It is reported when images 
    are removed due to corruption or wrong format.
    
    Args:
        path_to_datafolder:    The path to the main data directory
        
        timestamp:             The timestamp for which the images was 
                               downloaded (ddmmyy_hhmm)

    Return:
        0
    
    @author: Mads Obdrup Jakobsen
    """
    FolderToBeCleaned = timestamp
    
    if srcfolder == "raw":
        path_train = path_to_datafolder + '\\food images\\google\\' + FolderToBeCleaned + '\\raw'
        
        # Find the existing logfile and prepare the cleaned logFile
        logfilename = path_train + '\\dataLog.csv'
        logfilenameClean =  path_train + '\\dataLogNoCorrupt.csv'
    elif srcfolder == "train":
        path_train = path_to_datafolder + '\\food images\\google\\' + FolderToBeCleaned + '\\DL\\training_images'
        
        # Find the existing logfile and prepare the cleaned logFile
        logfilename = path_to_datafolder + '\\food images\\google\\' + FolderToBeCleaned + '\\DL\\train.csv'
        logfilenameClean =  path_to_datafolder + '\\food images\\google\\' + FolderToBeCleaned + '\\DL\\train_clean.csv'
    elif srcfolder == "test":
        path_train = path_to_datafolder + '\\food images\\google\\' + FolderToBeCleaned + '\\DL\\testing_images'
        
        # Find the existing logfile and prepare the cleaned logFile
        logfilename = path_to_datafolder + '\\food images\\google\\' + FolderToBeCleaned + '\\DL\\test.csv'
        logfilenameClean =  path_to_datafolder + '\\food images\\google\\' + FolderToBeCleaned + '\\DL\\test_clean.csv'
    else:
        raise ValueError("Error in cleaner.")

    df2 = pd.read_csv(logfilename, sep = "," , header = 0)
    for folder in next(os.walk(path_train))[1]:  
        for filename in listdir(path_train + "\\" + folder):
            if filename.endswith('.jpg'):
                try:
                    #img = Image.open(path_train / folder / filename) # open the image file
                    img = Image.open(path_train + "\\" + folder + "\\" + filename) # open the image file
                    img.verify() # verify that it is, in fact an image
                except (IOError, SyntaxError) as e:
                    #os.remove(path_train / folder / filename)
                    os.remove(path_train + "\\" + folder + "\\" + filename)
                    print('Corrupted file removed:', filename)
                    df2 = df2.loc[df2['Image Path'] != folder + '\\' + filename]
            else:
                #os.remove(path_train / folder / filename)
                os.remove(path_train + "\\" + folder + "\\" + filename)
                print('File not jpg. Removed:', filename)
                df2 = df2.loc[df2['Image Path'] != folder + '\\' + filename]
    
    # Saves the new logfile and removes the old.          
    df2.to_csv(logfilenameClean, sep=',', encoding='utf-8' , index = 0)
    os.remove(logfilename)

    return 0           
       
def resizeImageFolder(read_path,save_path = None, newShape = np.array((200,200)) , 
                      CropOrPad = 0 , cropShape = np.array([0,0,0,0])):
    
    """ 
    Created on Wed Oct  3 10:12:22 2018
    
    This function utilies reSizePad() to resize all images in a folder 
    structure in the same way.
    
    The function loops through all images in training and test folder 
    (and thus assume such structure) and resize all of them according to the 
    inputs. The scaling inputs are the same as for reSizePad(.)
    
    Args:
        read_path:   Path to the main data directory
        
        save_path:   Main folder where the resized images should be saved. This
                     argument is optional and should only be provided if the
                     existing images should not be overwritten
        
        newShape:    A numpy array of size 2 containing (heightNew,widthNew)
                     with the dimensions of the new image.
        
        CropOrPad:   Integer:
                                0: Simple rescaling of the image.
                                1: Cropping of the image.
                                2: Padding before rescaling of the image.
                                
        cropShape:  Optional numpy array [height1,height2,width1,width2] 
                    containing the exact 
                    pixels relative to the center to crop. Can be provided to 
                    save 
                    computation time if many images are to be cropped.

    Return:
        0
    
    @author: Mads Obdrup Jakobsen
    """    
    dir_names = ['testing_images' , 'training_images']
    if save_path == None:
        save_path = read_path
    
    # Loop through all downloaded images through nested loops
    for folder in dir_names:
        classFolders = listdir(read_path + "\\" + folder)
        
        # Avoid the hidden file '.DS_Store'
        try:
            classFolders.remove('.DS_Store')
        except:
            pass
        
        for foodType in classFolders:
            files = listdir(read_path + "\\" + folder + "\\" + foodType)
            for filename in files:
                
                # Read and scale the image
                img = imread(read_path + "\\" + folder + "\\" + foodType + "\\" + filename)
                
                (newImg , size) = reSizePad(img , newShape , CropOrPad , cropShape)
                
                # Create folders if they donøt exist
                if not exists(save_path + "\\" + folder + "\\" + foodType):
                    makedirs(save_path + "\\" + folder + "\\" + foodType)
                
                # Safe the scaled image
                if (".jpg" in filename):
                    try:
                        imsave(save_path + "\\" + folder + "\\" + foodType + "\\" + filename , newImg)
                    except:
                        print("This one failed to save for some reason: {0}".format(save_path + "\\" + folder + "\\" + foodType + "\\" + filename))
                else:
                    print("This was a non-jpg: {0}".format(filename))

    
    return 0

def reSizePad(image , newShape = np.array((100,100)) , CropOrPad = 0 , cropShape = np.array([0,0,0,0])):
    """ 
    Created on Wed Oct  3 10:12:22 2018
    
    This function resizes an image according to several parameters
    
    The function takes in an image and outputs a new image resized to a 
    specified scale. The function can either just rescale the image, crop it or
    pad it before rescaling to keep internal measures of the content of the 
    image.
    
    Args:
        image:       A numpy array of size 3 (or 2 if gray scale) containing 
                     (height,width,channels) with the original image data.
                     
        newShape:    A numpy array of size 2 containing (heightNew,widthNew) 
                     with the dimensions of the new image.
        
        CropOrPad:   Integer:
                                0: Simple rescaling of the image.
                                1: Cropping of the image.
                                2: Padding before rescaling of the image.
                                
        cropShape:  Optional numpy array [height1,height2,width1,width2] 
                    containing the exact pixels relative to the center to crop. 
                    Can be provided to safe computation time if many images 
                    are to be cropped.

    Return:
        img:        A numpy array of size 3 (or 2 if gray scale) containing 
                    (heightNew,widthNew,channels) with the new image.
        
        newDim:     The new dimensions of the image (heightNew,widthNew,channels).
        
    @author: Mads Obdrup Jakobsen
    """
    
    img_shape = image.shape
    r = img_shape[0]
    c = img_shape[1]
    center = np.array((int(np.ceil(c/2))-1 , int(np.ceil(r/2)-1)))
    
    # Cropping
    if CropOrPad == 1:
        
        
        if all(cropShape == 0): # If no cropping has been provided
            cropY = np.array((-1*int(np.ceil(newShape[0]/2)-1),
                              int(np.floor(newShape[0]/2)+1)))
            
            cropX = np.array((-1*int(np.ceil(newShape[1]/2)-1),
                              int(np.floor(newShape[1]/2)+1)))

        else: # If predefined cropping corners has been provided
            cropY = np.array([cropShape[0] , cropShape[1]])
            cropX = np.array([cropShape[2] , cropShape[3]])
        
        # Compute corners relative to center
        (x1,x2) = np.array((center[0] + cropX))
        (y1,y2) = np.array((center[1] + cropY))
        
        # Crop image
        image = image[y1:(y2) , x1:(x2)]
    
    # Padding
    elif CropOrPad == 2:
        
        # Compute new sides and padding
        new_side = np.max([r,c])
        padding = ((new_side - c)//2, 
                   (new_side - r)//2, 
                   int(np.ceil((new_side - c)/2)), 
                   int(np.ceil((new_side - r)/2)))
        
        img_as_img = Image.fromarray(image)
        
        # Apply padding
        img_as_img = Image.fromarray(image)
        new_img = ImageOps.expand(img_as_img, padding)
        img_pad = np.array(new_img)
        
        # Resize image
        image = resize(img_pad, output_shape=newShape, mode='reflect')
        
    else:
        image = resize(image, output_shape=newShape, mode='reflect')
        
    newDim = image.shape
        
    return(image , newDim)
 
def augmentImageFolders(settings, read_path, save_path):
    dir_names = ['testing_images' , 'training_images']
    if save_path == None:
        save_path = read_path
    
    # Loop through all downloaded images through nested loops
    for folder in dir_names:
        if folder == "testing_images":
            csvFilename = 'test_clean.csv'
            setIndex = "0"
        else:
            csvFilename = 'train_clean.csv'
            setIndex = "1"
            
        classFolders = listdir(read_path + "\\" + folder)
        
        # Avoid the hidden file '.DS_Store'
        try:
            classFolders.remove('.DS_Store')
        except:
            pass
        
        for foodType in classFolders:
            files = listdir(read_path + "\\" + folder + "\\" + foodType)
            for filename in files:
                imgPath = read_path + "\\" + folder + "\\" + foodType + "\\" + filename
                
                '''
                if "_FLIPPEDLEFTRIGHT" in imgPath or "_ROTATED90" in imgPath or "_OVEREXPOSED" in imgPath or "_UNDEREXPOSED" in imgPath or "_BLURED" in imgPath:
                    print("Removing: {0}".format(imgPath))
                    os.remove(imgPath)
                '''
                ### Here we do augmentation
                augmentedImages_PILimgs, augmentedImages_paths = augmentImage(settings, imgPath)
                
                # Create folders if they donøt exist
                if not exists(save_path + "\\" + folder + "\\" + foodType):
                    makedirs(save_path + "\\" + folder + "\\" + foodType)
                
                # Save the augmented images
                for idx, img in enumerate(augmentedImages_PILimgs):
                    newFilename = augmentedImages_paths[idx]
                    if (".jpg" in newFilename):
                        try:
                            img.save(newFilename)
                            # Add path to csv file as well
                            df = {"id":[""], "Food Class":[foodType], "Name of Food":[""], "Image Path":[("" + folder + "\\" + newFilename)], "Set Index":[setIndex]}
                            dataframe = pd.DataFrame(df)
                            with open('{0}.csv'.format(csvFilename),'a') as csvFile:
                                (dataframe).to_csv(csvFile, header=False)
                            print("Saved augmented image: {0}".format(newFilename))
                        except:
                            print("This augmented one failed to save for some reason: {0}".format(newFilename))
                    else:
                        print("This augmented was a non-jpg: {0}".format(newFilename))

    
    return 0
 
def boolvalue_prob(probability):
    return random.random() < probability
 
def augmentImage(settings, imgPath):
    augImages = []
    augImagesPaths = []
    
    if boolvalue_prob(settings["doAug_prob"]):
        if boolvalue_prob(settings["doFlip_prob"]):
            # Create a flipped version of the source image    
            newImgObj, newImgPath = flip_image(imgPath, settings["setFlip"])
            augImages.append(newImgObj)
            augImagesPaths.append(newImgPath)
        
        if boolvalue_prob(settings["doRotate_prob"]):
            # Create a rotated version of the source image    
            newImgObj, newImgPath = rotate_image(imgPath, settings["setRotate"])
            augImages.append(newImgObj)
            augImagesPaths.append(newImgPath)
        
        if boolvalue_prob(settings["doOverExpose_prob"]):
            # Create an over exposed version of the source image    
            newImgObj, newImgPath = overExposure(imgPath, settings["setOverExpose"])
            augImages.append(newImgObj)
            augImagesPaths.append(newImgPath)
        
        if boolvalue_prob(settings["doUnderExpose_prob"]):
            # Create an under exposed version of the source image    
            newImgObj, newImgPath = underExposure(imgPath, settings["setUnderExpose"])
            augImages.append(newImgObj)
            augImagesPaths.append(newImgPath)
        
        if boolvalue_prob(settings["doBlur_prob"]):
            # Create a blured version of the source image    
            newImgObj, newImgPath = blur(imgPath, settings["setBlur"])
            augImages.append(newImgObj)
            augImagesPaths.append(newImgPath)
    
    return augImages, augImagesPaths
 
def flip_image(srcImagePath, setting):
    image_obj = Image.open(srcImagePath)
    fliped_image = image_obj.transpose(setting)
    fliped_image_path = ".".join(srcImagePath.split(".")[0:-1]) + "_FLIPPEDLEFTRIGHT." + srcImagePath.split(".")[-1]
    
    return fliped_image, fliped_image_path


def rotate_image(srcImagePath, setting):
    image_obj = Image.open(srcImagePath)
    rotated_image = image_obj.rotate(setting)
    rotated_image_path = ".".join(srcImagePath.split(".")[0:-1]) + "_ROTATED90." + srcImagePath.split(".")[-1]
    
    return rotated_image, rotated_image_path
  
def overExposure(srcImagePath, setting):
    image_obj = Image.open(srcImagePath)
    im = cv2.imread(srcImagePath)
    imgRGB = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    gamma_corrected = exposure.adjust_gamma(imgRGB, setting)
    overExposed_image = Image.fromarray(gamma_corrected)
    overExposed_image_path = ".".join(srcImagePath.split(".")[0:-1]) + "_OVEREXPOSED." + srcImagePath.split(".")[-1]
    
    return overExposed_image, overExposed_image_path

def underExposure(srcImagePath, setting):
    image_obj = Image.open(srcImagePath)
    im = cv2.imread(srcImagePath)
    imgRGB = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    gamma_corrected = exposure.adjust_gamma(imgRGB, setting)
    underExposed_image = Image.fromarray(gamma_corrected)
    underExposed_image_path = ".".join(srcImagePath.split(".")[0:-1]) + "_UNDEREXPOSED." + srcImagePath.split(".")[-1]
    
    return underExposed_image, underExposed_image_path

def blur(srcImagePath, setting):
    image_obj = Image.open(srcImagePath)
    blured_image = image_obj.filter(ImageFilter.GaussianBlur(setting))
    blured_image_path = ".".join(srcImagePath.split(".")[0:-1]) + "_BLURED." + srcImagePath.split(".")[-1]
    
    return blured_image, blured_image_path

##### MAIN: #####

# Set path to food dataase csv file and main folder to save images
#path_to_FoodDataBase = (Path.home()  / 'Hedia Dropbox' / 'Mads Obdrup Jakobsen' / 
#                              'food-training-images-database' / 'Hedia_Food_Database.xlsx')
#path_to_FoodDataBase = 'C:\\food-training-images-database\\Hedia_Food_Database.xlsx'
path_to_FoodDataBase = 'C:\\food-training-images-database\\Michael_Food_Database.xlsx'

#path_to_dataFolder = Path.home()  / "data"
path_to_dataFolder = 'C:\\food-training-images-database\\data'  

nTypes = 5 # Number of distinct food types to download
nEacgFood = 5 # Number of images to download from each category
trainRatio = 1/5 # How large ratio of the images should be saved for validation
augmentImages = True
augmentSettings = {"doAug_prob" : 10/10,
                   "doFlip_prob" : 5/10,
                   "doRotate_prob" : 5/10,
                   "doOverExpose_prob" : 5/10,
                   "doUnderExpose_prob" : 5/10,
                   "doBlur_prob" : 5/10,
                   "setFlip" : Image.FLIP_LEFT_RIGHT,
                   "setRotate" : 90,
                   "setOverExpose" : 2,
                   "setUnderExpose" : 0.4,
                   "setBlur" : 2
                  }


# Run the three files to download and manage images
print("DOWNLOADING:")
#timestamp = "291018_1725"
timestamp = downloadImages(path_to_FoodDataBase , path_to_dataFolder, nTypes = nTypes, nOfEachType = nEacgFood)
print("CLEARNING:")
clean_foodimages(path_to_dataFolder , timestamp, "raw")
print("PARTITIONING:")
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

#read_path = Path.home() / 'data' / 'food images' / 'google' / timestamp / 'DL'
read_path = 'C:\\food-training-images-database\\' + 'data\\' + 'food images\\' + 'google\\' + timestamp + '\\DL'

#resizeImageFolder(read_path, save_path = read_path , newShape = newShape , CropOrPad = 0)

print("DONE SCRAPING")

if augmentImages:
    print("AUGMENTING IMAGES")
    augmentImageFolders(augmentSettings, read_path, save_path=read_path)

## OPTIONAL MERGE OF FOLDERS AGAIN TO ACHIEVE SAME STRUCTURE AS IN WEEK 4
#merge = True
#if merge:
#    mergeFoldersFunc(timestamp, read_path)
    
print("CLEARNING RESIZED TRAINING:")
#clean_foodimages(path_to_dataFolder , timestamp, "train")
print("CLEARNING RESIZED TESTING:")
#clean_foodimages(path_to_dataFolder , timestamp, "test")


print("DONE")