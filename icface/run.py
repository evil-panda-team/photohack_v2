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
#from imutils import face_utils
import numpy as np
from PIL import Image
#import pdb   
import argparse

import os
from options.test_options import TestOptions
from data.data_loader import CreateDataLoader
from models.models import create_model
#from util.visualizer import Visualizer
#from util import html
import pdb

opt = TestOptions().parse()
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

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
   
rects = detector(RGB, 1)
faces = dlib.full_object_detections()

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
    
#    f_im.save('./new_crop/'+ name[4:-4] +'.png')
    f_im.save('./temp.png')
        
    
#### PART 2
data_loader = CreateDataLoader(opt)
dataset = data_loader.load_data()
model = create_model(opt)
#visualizer = Visualizer(opt)
# create website
web_dir = os.path.join(opt.results_dir, opt.name, '%s_%s' % (opt.phase, opt.which_epoch))
#webpage = html.HTML(web_dir, 'Experiment = %s, Phase = %s, Epoch = %s' % (opt.name, opt.phase, opt.which_epoch))
# test
for i, data in enumerate(dataset):
#    pdb.set_trace()
    
  
    if i >= opt.how_many:
        break
    
    model.set_input(data)
    img_path = model.get_image_paths()
    model.test()

    img_path = model.get_image_paths()
#    print('%04d: process image... %s' % (i, img_path))
print("Done!")
