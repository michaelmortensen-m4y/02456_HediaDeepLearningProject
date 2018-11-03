#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 15:14:31 2018

@author: meishaonv
"""

from PIL import Image
from PIL import ImageFilter
from skimage import exposure
import os
import cv2

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
        
 
def flip(image_path):
    saved_location = ''.join([str(image_path), 'flip.jpg'])
    image_obj = Image.open(image_path)
    fliped_image = image_obj.transpose(Image.FLIP_LEFT_RIGHT)
    #flip_image.save(saved_location)
    return fliped_image,saved_location
  

def rotate(image_path):
    saved_location = ''.join([str(image_path), 'rotate.jpg'])
    image_obj = Image.open(image_path)
    rotated_image = image_obj.rotate(45)
    #rotated_image.save(saved_location)
    return rotated_image, saved_location
    
def overExposure (image_path):
    saved_location = ''.join([str(image_path), 'overExp.jpg'])
    image_obj = Image.open(image_path)
    im = cv2.imread(image_path)
    imgRGB = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    #corrected_image = exposure.rescale_intensity(image_path, in_range='image', out_range='dtype')
    gamma_corrected = exposure.adjust_gamma(imgRGB, 4)
    img = Image.fromarray(gamma_corrected)
    img.save(saved_location)
    return img, saved_location

def underExposure (image_path):
    saved_location = ''.join([str(image_path), 'underExp.jpg'])
    image_obj = Image.open(image_path)
    im = cv2.imread(image_path)
    imgRGB = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    gamma_corrected = exposure.adjust_gamma(imgRGB, 0.25)
    img = Image.fromarray(gamma_corrected)
    img.save(saved_location)
    return img, saved_location

def blur(image_path):
    saved_location = ''.join([str(image_path), 'blur.jpg'])
    image_obj = Image.open(image_path)
    im1 = image_obj.filter(ImageFilter.GaussianBlur(5))
    #im1.save(saved_location)
    return im1, saved_location
    
def augmentImage(image_path,proDict):
    augImage = []
    augImagePath = []
    if proDict["flip"] > 0.5:
        Image, Path = flip(image_path)
        augImage.append(Image)
        augImagePath.append(Path)
    if proDict["rotate"] > 0.5:
        Image, Path = rotate(image_path)
        augImage.append(Image)
        augImagePath.append(Path)
    if proDict["overExposure"] > 0.5:
        Image, Path = overExposure(image_path)
        augImage.append(Image)
        augImagePath.append(Path)
    if proDict["underExposure"] > 0.5:
        Image, Path = underExposure(image_path)
        augImage.append(Image)
        augImagePath.append(Path)
    if proDict["blur"] > 0.5:
        Image, Path = blur(image_path)
        augImage.append(Image)
        augImagePath.append(Path)
    
    return augImage, augImagePath
    
    
    
if __name__ == '__main__':
    image = '375. beef.jpg'
    pro = {"flip":0.6,
           "rotate": 0.4,
           "overExposure": 0.7,
           "underExposure": 0.8,
           "blur":0.3
            }
    augmentImage(image,pro)
    
