#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 16:54:36 2019

@author: kenny
"""

#from imutils.face_utils import FaceAligner
from imutils.face_utils import rect_to_bb
import imutils
import dlib
import cv2
import numpy as np
from PIL import Image
import os
from options.test_options import TestOptions
from data.data_loader import CreateDataLoader
from models.models import create_model

def create_mp4(input_img_path, csv_path):
    
    opt = TestOptions().parse()
    opt.input_img = input_img_path
    opt.csv_path = csv_path
    opt.nThreads = 1   # test code only supports nThreads = 1
    opt.batchSize = 1  # test code only supports batchSize = 1
    opt.serial_batches = True  # no shuffle
    opt.no_flip = True  # no flip
    
    ###### PART 1    
    detector = dlib.get_frontal_face_detector()
    
    name = opt.input_img
    cap = cv2.imread(name) # add your image here
    image= cv2.resize(cap, (400, 400))
    
    RGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) 
           
    rects = detector(RGB, 1)
    
    for rect in rects:
        c1=rect.dcenter()
        (x, y, w, h) = rect_to_bb(rect)
        w=np.int(w*1.6) 
        h=np.int(h*1.6) 
        x=c1.x-np.int(w/2.0)
        y=c1.y-np.int(h/2.0)
        if y<0:
           y=0
        if x<0:
           x=0
           
        faceOrig = imutils.resize(RGB[y:y+h, x:x+w], height=256) #y=10,h+60,W+40
        d_num = np.asarray(faceOrig)
        f_im = Image.fromarray(d_num)
        f_im.save('./temp.png')
            
        
    #### PART 2
    data_loader = CreateDataLoader(opt)
    dataset = data_loader.load_data()
    model = create_model(opt)
    for i, data in enumerate(dataset):              
        if i >= opt.how_many:
            break        
        model.set_input(data)
        model.test()
    
    os.system('rm temp.png')
    print("Done!")
