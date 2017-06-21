#!/usr/bin/env python
#read file name list, get mask, get histogram, of images
# /home/sandeeps/IARP/python-envs/iarp-python-2.7.10/bin/python mygetimgprops_v30.py > TESTpropslarge

# ============================================================#
import os, re, string
import json
import sys
import time
import glob
import itertools
import numpy as np
import cv2 

import json
sys.stdout.flush()
#-----
sep2use ="#";   #sqlite3 new version doesnt like the ::  - ugh
#filelist_2read='../GetImageList/files_names_large_999999.txt' #sys.argv[1];
filelist_2read=sys.argv[1];

#use a variable to indicate what counts as a 'big' patch, ie to find stryker hole
#  and the min/max factors indicate the range of a hole vs outer border, for eg
min_big    = float(1000)/700000; # .001;
#eg 1 percent of total pixels,  originally 1000 was for 300x300 jpegs, roughly
#for large is .001*700000, or since holes are about 5-6K area,
#  1000/7000
st_min_fact= 2;  #the range of areas that could be hole punches
st_max_fact= 10.0;   #2000 and 7000 were hard coded originally, that was for smaller jpegs
backgrnfact= 0.5  #50 is for this x minbig is about the size of the foreground (ie main image)
                 #0.5 is image HxWx0.5 is main image foreground size
                 # IOW, it's the background of scene, foreground wrt borders)
mincirc=0.90
# ------------
#st     ='/oasis/projects/nsf/vlp100/slavenas/files_json/'
#st2    ='.jpg'
min_2read=sys.argv[2];
max_2read=sys.argv[3];

minfcnt= int(min_2read);       #pt1 ends at: 37516
maxfcnt= int(max_2read);       #200002
cntstr=str(minfcnt)+'_'+str(maxfcnt)
modck = round(maxfcnt/1000);
if (modck<1):
   modck=1
dcnt   =0
fcnt   =0
#d2get  = st+'*'
ds_fset    =open('imagefiles_procd_'+cntstr+'.txt','w')
ds_pset    =open('imageprop_info_'+cntstr+'.txt','w')
ds_hset    =open('imagehist_vecs_'+cntstr+'.txt','w')
ds_hogset    =open('imagehog_vecs_'+cntstr+'.txt','w')

#using defaults
myhogdesc = cv2.HOGDescriptor()
#myhogdesc = cv2.HOGDescriptor("hog_default.xml")  #hog_large.xml")

# -----------------
#with open("files_names_largest.txt", "r") as myfile:
#with open("files_names_large.txt", "r") as myfile:
with open(filelist_2read, "r") as myfile:

    for fileinfo in myfile:
       fileinfo.rstrip()

#fcnt :: resid :: previndex :: itemid :: itemidnum ::itemcall :: itemcallnum :: i
#mage_fname :: metadata_fname :: imagesurl

#       [fcntstr,resid,previndex,itemid,id2use,callstr,callnum,jf2use,metfname,furl]=fileinfo.split("::")
       [fcntstr,resid,previndex,itemid,id2use,callstr,callnum,jf2use,metfname,furl]=fileinfo.split("#")

       fcnt=int(fcntstr)
       if (fcnt>minfcnt):
           if (fcnt>maxfcnt):
                 print "fcnt > max.. quitting\n"
                 quit()
           if (fcnt % modck==0):
                    print time.ctime(time.time())+" "+str(fcnt)
           inputfile=jf2use
#           index = id2use;
           index = itemid[0:-3]; #id2use;  #check that /PP is in the input file, or

           print >> ds_fset, str(fcnt)+sep2use+str(index)+sep2use+jf2use+sep2use+furl.rstrip()

#parameters['inputfile']
#    fileid=parameters['fileid']
           ext='jpg'
           sectionfile=None

#pfr now do something w/image
           #masklist=myremove_circle.main(jf2use,index)
           #print >> ds_maskinfo,m
           # --------------process
           inputfile=jf2use     #parameters['inputfile']
           image    = cv2.imread(inputfile)
           gray     = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
           gray_orig = gray.copy()

           ret,gray = cv2.threshold(gray,20,255,0)
#pfr chagne 10 to 20, since a hole could have pixvalues of at least 14 in previous test on smaller jpgs


           gray2 = gray.copy()
           mask = np.zeros(gray.shape,np.uint8)   #mask defaults to 0s
           outline_mask = np.ones(gray.shape,np.uint8)*255  #outline defaults to 1s

           image, contours, hierarchy = cv2.findContours(gray2,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

           big_contours = []

           border_exists = False
           stryker_exists = False

           imgh = len(gray)
           imgw = len(gray[0])
           totarea =imgh*float(imgw);
           bigarea =float(min_big)*totarea
#           print "hxw: "+str(imgh)+"x"+str(imgw)+" tota: " + str(totarea)+" bigarea: "+str(bigarea)
           for contour in contours:
             if cv2.contourArea(contour) > bigarea:
               big_contours.append(contour)
           ci=0
           for contour in big_contours:
             ci           =ci+1
             (x,y),radius = cv2.minEnclosingCircle(contour)
             carea        = cv2.contourArea(contour)
             radius       = int(radius)
             circ_area  = np.pi*float(radius)*float(radius)
             perofcirc    = carea/circ_area
#             print str(fcnt)+" "+str(index)+" "+str(ci)+" "+str(perofcirc)+" "+str(carea)+" "+str(circ_area)
#so carea/mincir area > .90 should be a disk;

             if (perofcirc>mincirc) & ((bigarea*st_min_fact) < cv2.contourArea(contour) < (totarea*min_big*st_max_fact)):
               stryker_exists = True
#             if cv2.contourArea(contour) > (min_big*backgrnfact): #100000 was hardcoded
             #print "se?: "+str(stryker_exists)
             if cv2.contourArea(contour) > (totarea*backgrnfact): #try relatvie to full size
             #PFR why print this?   print cv2.contourArea(contour)
                cv2.drawContours(outline_mask,[contour],-1,0,-1)    #now make the 1s 0s (=not-hole)
                border_exists = True
             else: #so this is all nonreally big regions
               #PFR why do this?       print cv2.contourArea(contour)
                cv2.drawContours(mask,[contour],-1,255,-1)          #make the 0s 255=white and=hole)
                border_exists = True  #or false ..or this jsut the nonborder marking #but0 is nothole

           kernal = np.ones((12,12),np.uint8)
           opened_outline_mask = cv2.morphologyEx(outline_mask, cv2.MORPH_CLOSE,kernal)

           kernal = np.ones((5,5),np.uint8)
           opened_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE,kernal) #pfr why is the result called opened?

           final_mask = np.zeros(gray.shape,np.uint8)
           for i in range(mask.shape[0]):
             for j in range(mask.shape[1]):
               if opened_outline_mask[i][j] == 0 and opened_mask[i][j] == 0:  #so both 0 =nothole?
                   final_mask[i][j] = 255  #white
               else:
                   final_mask[i][j] = 0    #black

           #write these out, incase, or for testing
#           temp_file = './MASKS/Mask_'+str(index)+'.txt'
#           np.savetxt(temp_file,final_mask,fmt='%.2f')
#           temp_file = './MASKS/'+str(index)+'_mask_'+str(stryker_exists)+'.png'
#           cv2.imwrite(temp_file,final_mask)

#           temp_file = './MASKS/'+str(index)+'_gray_'+str(stryker_exists)+'.png'
#           cv2.imwrite(temp_file,gray_orig)
# ---- end for testing


#           maskbinzd= np.where(final_mask>1, 1, 0)
#           mngray2  = cv2.mean(np.multiply(gray,maskbinzd))[0]

           #print "get gray mean"
           mngray2, stdgray2  = cv2.meanStdDev(gray_orig, mask=final_mask) #mean,np.multiply(gray,maskbinzd))[0]

           #print "get gray hist"
           hist      = cv2.calcHist([gray_orig],[0],final_mask,[256],[0,256])
           #hist.tofile(ds_hset,sep="",
           print >> ds_hset, str(index)+sep2use,
           for x in np.nditer(hist):
                print >> ds_hset, '%.0f' % x,
#'{0}'.format(x),  # np.array_str(x, precision=2),
           print >> ds_hset, "\n",
           print >> ds_pset, str(index)+sep2use+ str(stryker_exists) + sep2use +str(border_exists)+sep2use+'%.2f' % mngray2+sep2use+'%.2f' % stdgray2
           ds_hset.flush()
           ds_pset.flush()
           ds_fset.flush()

# import cv2
           #im = cv2.imread(sample)
           #print "get hog"
           if 0:
               hog     = myhogdesc.compute(gray_orig)
               hoghist,hoghistedges  = np.histogram(hog, bins=32)
#each pix has 9 bins that indicate gradient strength in 9 directions;
# a binning of those looses direction but only represents 'strengthness' of those bin
#    ie if many pixels had 1 strong bin value=10, then we'd get that number of 10's for the
# binrange that has the 10
#make bins standard
#32 or 64 bins, a bit arbitryr maybe?
#          hog.tofile(ds_hogset,sep="",format='%0.3f')
               print >> ds_hogset, str(index)+sep2use,
               for x in np.nditer(hoghist):
                    print >> ds_hogset, '%0.3f' % x,  #np.array_str(x, precision=2),
               print >> ds_hogset, "\n",
               ds_hogset.flush()
#end of while
