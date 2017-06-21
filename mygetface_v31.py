#!/usr/bin/env python
# /home/sandeeps/IARP/python-envs/iarp-python-2.7.10/bin/python mygetface_v30.py > test25_large

#run this, get face*txt file, run sql imports and selects, feed into matlab

# ============================================================#
import os, re, string
import json
import sys
import time
import glob
import itertools
import numpy as np
import cv2

import tempfile
#-----
extractorName = "ncsa.cv.faces"

filelist_2read=sys.argv[1];
minfcnt       =int(sys.argv[2]);
maxfcnt       =int(sys.argv[3]);
print "INFO, starting, using " + filelist_2read + " " + time.ctime(time.time())
print "INFO,   going from " + str(minfcnt) + " to "+ str(maxfcnt)
# path to opencv pretrained classifiers
path4opencv                ='/opt/opencv/share/OpenCV/haarcascades'
#face_cascade_path          = path4opencv+'/haarcascade_frontalface_alt.xml'
# alt was used for comet runs upto v31
face_cascade_path          = path4opencv+'/haarcascade_frontalface_alt.xml'
big_eyepair_cascade_path   = path4opencv+'/haarcascade_eye.xml'
small_eyepair_cascade_path = path4opencv+'/haarcascade_eye.xml'

#big_eyepair_cascade_path   = path4opencv+'/haarcascade_mcs_eyepair_big.xml'
#small_eyepair_cascade_path = path4opencv+'/haarcascade_mcs_eyepair_small.xml'
left_eye_cascade_path      = path4opencv+'/haarcascade_lefteye_2splits.xml'
right_eye_cascade_path     = path4opencv+'/haarcascade_righteye_2splits.xml'

profileface_cascade_path = path4opencv+'/haarcascade_profileface.xml'


ext='jpg'

# --------------------------
def findbiggesteye(eyes):
    maxsize=0
    biggesteye=[]
    for (x,y,w,h) in eyes:
        size=w*h
        if size>maxsize:
            maxsize=size
            biggesteye=[x, y, w, h]
    return biggesteye

# --------------------------
sep2use ="#";   #sqlite3 new version doesnt like the ::  - ugh

#st     ='/oasis/projects/nsf/vlp100/slavenas/files_json/'
#st2    ='.jpg'
cntstr  =str(minfcnt)+'_'+str(maxfcnt)  #for output file name
modck   = round(maxfcnt/100);           #for displaying messages during a run
if (modck<1):
   modck=1
dcnt   =0
fcnt   =0
#d2get  = st+'*'
ds_fset     =open('facefiles_procd_'+cntstr+'.txt','w')  #result files for database
ds_faces    =open('faceprop_info_'+cntstr+'.txt','w')

#with open("files_names_largest_comp.txt", "r") as myfile:
#with open("files_names_large.txt", "r") as myfile:
with open(filelist_2read, "r") as myfile:
    for fileinfo in myfile:
       fileinfo.rstrip()

#fcnt :: resid :: previndex :: itemid :: itemidnum ::itemcall :: itemcallnum :: i
#mage_fname :: metadata_fname :: imagesurl

       [fcntstr,resid,previndex,itemid,id2use,callstr,callnum,jf2use,metfname,furl]=fileinfo.split("#")

       fcnt=int(fcntstr)
       if (fcnt>minfcnt):
           if (fcnt>maxfcnt):
                 print str(fcnt)+" fcnt > max.. quitting\n"
                 quit()
           if (fcnt % modck==0):
                    print time.ctime(time.time())+" "+str(fcnt)
           inputfile=jf2use   # image2 input (eg 'jf2use' is like jpg file 2use,but it might not be jpg)
#           metfname =inputfile[0:(len(inputfile)-4)]+".json"
#           mdata   =json.loads(open(metfname).read())   #json returns a python dictionary
#           index   =mdata["index"]
#           imurls  =mdata["image"]
#           fullurl =imurls["full"]

           index = itemid[0:-3]; #id2use;  #check that /PP is in the input file, or
 #have getimage list take it out once and for all

           print >> ds_fset, str(fcnt)+sep2use+str(index)+sep2use+jf2use+sep2use+furl.rstrip()

#-------------
           if 1:
               #extract face from images using opencv face detector
               face_cascade = cv2.CascadeClassifier(face_cascade_path)
#    try:
               face_cascade          = cv2.CascadeClassifier(face_cascade_path)
               big_eyepair_cascade   = cv2.CascadeClassifier(big_eyepair_cascade_path)
               small_eyepair_cascade = cv2.CascadeClassifier(small_eyepair_cascade_path)
               left_eye_cascade  =cv2.CascadeClassifier(left_eye_cascade_path)
               right_eye_cascade =cv2.CascadeClassifier(right_eye_cascade_path)
               profile_face_cascade = cv2.CascadeClassifier(profileface_cascade_path)

#PFR updated for CV3   img = cv2.imread(inputfile, cv2.CV_LOAD_IMAGE_GRAYSCALE)  IMREAD_GRAYSCALE
               img       = cv2.imread(inputfile, cv2.IMREAD_GRAYSCALE)
               img_color = cv2.imread(inputfile)
               if img is not None:
                  gray   = img
               else:
                  print "color: "+str(fcnt)+sep2use+str(index)+sep2use+jf2use
                  #PFR not sure this was tested when the image is none or if its color???
                  gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
               gray = cv2.equalizeHist(gray)
#PFR, old cv     faces=face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=2, minSize=(20, 20), flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
#               faces=face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3, minSize=(50,50), flags=cv2.CASCADE_SCALE_IMAGE)
#for largest uses 1.2, minN=3, min size 75
#               faces=face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3, minSize=(75,75), flags=cv2.CASCADE_SCALE_IMAGE)
#for large
#               faces=face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=2, minSize=(50,50), flags=cv2.CASCADE_SCALE_IMAGE)
               faces=face_cascade.detectMultiScale(gray, scaleFactor=1.01, minNeighbors=2, minSize=(50,50), flags=cv2.CASCADE_SCALE_IMAGE)

              # (fd, sectionfile)=tempfile.mkstemp(suffix='.' + ext)  PFR not usign, now saving images
              # os.close(fd)

               secdataset      =[]
               profsecdataset  =[]
               eyesecdataset   =[]

               #To save the section of an image,i.e., faces from the image
               #for each face detected, create a section corresponding to it and upload section information to server
               #create a preview for the section and upload the preview and its metadata
               facecnt   =0
               eyepaircnt=0
               eyelfrtcnt=0
               profilecnt=0

               imgh = len(gray)
               imgw = len(gray[0])
               fmidCloseUp=0
               ffullCloseUp=0
               pmidCloseUp=0
               pfullCloseUp=0

               for (x,y,w,h) in faces:
                  if ((w*h>=(imgw*imgh/3)) or (w>=0.8*imgw and h>=0.5*imgh) or (w>=0.5*imgw and h>=0.8*imgh)): #this is a closeup
                     ffullCloseUp+=1
                  if (w*h>=(imgw*imgh/8)): #this is a medium closeup
                     fmidCloseUp+=1

#Profile and close ups ------------------------------------------
               profilefaces=profile_face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=10, minSize=(imgw/8, imgh/8))
               for (x,y,w,h) in profilefaces:
                  profilecnt+=1
                  profsecdataset.append(str(profilecnt)+","+str(int(x))+","+str(int(y))+","+str(int(w))+","+str(int(h))+";")
                  #roi_color = img[y:y+h, x:x+w]
                  #roi_color = img_color[y:y+h, x:x+w]
                  #temp_file = './FACES/Prof_'+str(index)+'_'+str(profilecnt)+'.jpg'
                  #cv2.imwrite(temp_file, roi_color)


                  if ((w*h>=(imgw*imgh/3)) or (w>=0.8*imgw and h>=0.5*imgh) or (w>=0.5*imgw and h>=0.8*imgh)): #this is a closeup
                     pfullCloseUp+=1
               for (x,y,w,h) in profilefaces:
                  if(w*h>=(imgw*imgh/8)): #this is a medium closeup
                     pmidCloseUp+=1


               for (x,y,w,h) in faces:
                  facecnt+=1   #use facecnt for output imagees
                  #roi_color = img[y:y+h, x:x+w]
                  #roi_color = img_color[y:y+h, x:x+w]
                  #temp_file = './FACES/Face_'+str(index)+'_'+str(facecnt)+'.jpg'
                  #cv2.imwrite(temp_file, roi_color)

                  secdataset.append(str(facecnt)+","+str(int(x))+","+str(int(y))+","+str(int(w))+","+str(int(h))+";")

#eye stuff --------------------------------------------
                  detected=False
                  #faces_all.append([x, y, w, h])
                  #roi_color = img_color[y:y+h, x:x+w]
                  #cv2.imwrite(sectionfile, roi_color)
                  roi_gray   = gray[y:y+h, x:x+w]
                  eyes       =big_eyepair_cascade.detectMultiScale(roi_gray, minSize=(0, 0), flags=cv2.CASCADE_SCALE_IMAGE)
#PFR replaced this: cv2.cv.CV_HAAR_SCALE_IMAGE)
            #   big_eyes=big_eye_cascade.detectMultiScale(roi_gray, minSize=(w/7, h/7), flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
                  if not len(eyes):
                      eyes=small_eyepair_cascade.detectMultiScale(roi_gray, minSize=(0, 0), flags=cv2.CASCADE_SCALE_IMAGE)
# and this: flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
                  for (ex,ey,ew,eh) in eyes:
                      #eyes_all.append([x+ex, y+ey, ew, eh])
                      #roi_eyepair = img_color[y+ey:y+ey+eh, x+ex:x+ex+ew]
                      #temp_file   = './FACES/EYESpair_'+str(index)+'_'+str(facecnt)+'.jpg'  #PFR, file names w/index
                      #cv2.imwrite(temp_file, roi_eyepair)
                      detected    =True
                      eyepaircnt+=1   #PFR added
                      eyesecdataset.append(str(facecnt)+","+str(int(ex))+","+str(int(ey))+","+str(int(ew))+","+str(int(eh))+";")


                    # create section of the image
#                    secdata={}
#                    secdata["file_id"]=fileid
#                    secdata["area"]={"x":int(ex), "y":int(ey),"w":int(ew),"h":int(eh)}

                    #upload section to medici
#                    sectionid=extractors.upload_section(sectiondata=secdata, parameters=parameters)

#------- write summary info for queries
               if facecnt==0:
                     secdataset='-1'
               if profilecnt==0:
                     profsecdataset='-1'
               if eyepaircnt==0:
                     eyesecdataset='-1'
               print >> ds_faces, str(index)+sep2use+str(imgh)+sep2use+str(imgw)+\
                      sep2use+"F"+sep2use+str(facecnt)+sep2use+"".join(secdataset)+\
                      sep2use+"P"+sep2use+str(profilecnt)+sep2use+"".join(profsecdataset)+\
                      sep2use+"Y"+sep2use+str(eyepaircnt)+sep2use+"".join(eyesecdataset)+\
                      sep2use+"C"+sep2use+str(ffullCloseUp)+sep2use+str(fmidCloseUp)+\
                      sep2use+str(pfullCloseUp)+sep2use+str(pmidCloseUp)
