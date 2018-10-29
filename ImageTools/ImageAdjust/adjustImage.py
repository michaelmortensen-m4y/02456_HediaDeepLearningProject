#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 15:14:31 2018

@author: meishaonv
"""

from PIL import Image
import os

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
        
 
def flip_image(image_path, saved_location):
    """
    Flip or mirror the image
    @param image_path: The path to the image to edit
    @param saved_location: Path to save the cropped image
    """
    #path_to_Flipped = (Path.home()  / 'DTU' / 'DeepLearning' /'Hedia'/'food images'/'google'/'291018_1418'/'raw'/'0'/'Flipped')
    image_obj = Image.open(image_path)
    rotated_image = image_obj.transpose(Image.FLIP_LEFT_RIGHT)
    rotated_image.save(saved_location)
    #rotated_image.show()
    #rotated_image = image_obj.rotate(90)
    #rotated_image.save(saved_location)


def rotate(image_path, saved_location):
    """
    Rotate the given photo the amount of given degreesk, show it and save it
    @param image_path: The path to the image to edit
    @param degrees_to_rotate: The number of degrees to rotate the image
    @param saved_location: Path to save the cropped image
    """
    image_obj = Image.open(image_path)
    rotated_image = image_obj.rotate(45)
    rotated_image.save(saved_location)
    
    
  
 
    
# =============================================================================
# if __name__ == '__main__':
#     image = '375. beef.jpg'
#     path_to_Adjusted = (Path.home()  / 'DTU' / 'DeepLearning' /'Hedia'/'food images'/'google'/'291018_1418'/'raw'/'0'/'Flipped')
#     createFolder(path_to_Adjusted)
#     flip_image(image, path_to_Adjusted/'375. beef.jpg')
# =============================================================================
    
    
