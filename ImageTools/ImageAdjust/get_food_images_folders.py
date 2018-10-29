


# Import libraries
import pandas as pd
from google_images_download import google_images_download
from pathlib import Path
from adjustImage import *
import time
import matplotlib.pyplot as plt
import numpy as np

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
    food_dict = pd.read_excel(path, sheet_name = None)
    
    #Create a Folder to store the adjusted images
    path_to_Adjusted = (Path.home()  / 'DTU' / 'DeepLearning' /'Hedia'/'Food images'/'Adjusted')
    createFolder(path_to_Adjusted)
    
    
    # Collect names of food, trim names (remove details) 
    # and tuple them with their category
    i = 0
    food_names = []
    for key in food_dict.keys():
        dat = food_dict[key]
        foodlist = dat.iloc[:,0]
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
    path = Path(path_to_datafolder) / 'food images' / 'google' / timestamp / 'raw'
    
    # Set number of food types to download
    nFood = nTypes-1
    # Set number of 
    id_list = []
    for i, searchkey in enumerate(food_names):
        
        # Get names of food
        food_name = searchkey[0] 
        foldername = str(i)
        photo = 'photo'
        # Defines arguments for search function
        arguments = {"keywords":food_name,
                     "limit":nOfEachType,
                     "image_directory":foldername,
                     "type":photo,
                     "print_paths":True,
                     "output_directory":str(path),
                     "print_urls" : False,
                     "chromedriver" : "/DTU/DeepLearning/Hedia/food-training-images-database-master/chromedriver"
                     }
        print(i)   
        # Passing the arguments to the function
        paths = response.download(arguments)  
        # Match up Id Number, food name, main category and path to image
        for ImagePath in paths[food_name]:
            
            #===================
            #adjust image and store it in outputPath
            #The remaining problem now is the directory cannot create itself
            outputPath = ''.join([str(path_to_Adjusted),'/',food_name,'/',timestamp,'.jpg'])
            flip_image(ImagePath, outputPath)
            #=====================
            #ImageName = ImagePath.split(foldername)[-1]
            ImagePath = ImagePath.split('raw/')[-1]
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
    filename = Path(path_to_datafolder) / 'food images' / 'google' / timestamp / 'raw' / logfilename
    foodDataFrame.to_csv(filename, sep=',', encoding='utf-8' , index = 0)
    
    return timestamp



    
    
    
    
    
    
    
    
    
    
    