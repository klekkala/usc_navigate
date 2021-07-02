#!/usr/bin/env python 
# - *- coding: utf- 8 - *-
# streetview.py This program will download google street image
# ####################################################################### 
# The iLab Neuromorphic Vision C++ Toolkit - Copyright (C) 2000-2002   ##
# by the University of Southern California (USC) and the iLab at USC.  ##
# See http://iLab.usc.edu for information about this project.          ##
# //////////////////////////////////////////////////////////////////// ##
# Major portions of the iLab Neuromorphic Vision Toolkit are protected ##
# under the U.S. patent ``Computation of Intrinsic Perceptual Saliency ##
# in Visual Environments, and Applications'' by Christof Koch and      ##
# Laurent Itti, California Institute of Technology, 2001 (patent       ##
# pending; application number 09/912,225 filed July 23, 2001; see      ##
# http://pair.uspto.gov/cgi-bin/final/home.pl for current status).     ##
# ####################################################################### 
# This file is part of the iLab Neuromorphic Vision C++ Toolkit.       ##
#                                                                      ##
# The iLab Neuromorphic Vision C++ Toolkit is free software; you can   ##
# redistribute it and/or modify it under the terms of the GNU General  ##
# Public License as published by the Free Software Foundation; either  ##
# version 2 of the License, or (at your option) any later version.     ##
#                                                                      ##
# The iLab Neuromorphic Vision C++ Toolkit is distributed in the hope  ##
# that it will be useful, but WITHOUT ANY WARRANTY; without even the   ##
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR      ##
# PURPOSE.  See the GNU General Public License for more details.       ##
#                                                                      ##
# You should have received a copy of the GNU General Public License    ##
# along with the iLab Neuromorphic Vision C++ Toolkit; if not, write   ##
# to the Free Software Foundation, Inc., 59 Temple Place, Suite 330,   ##
# Boston, MA 02111-1307 USA.                                           ##
# ####################################################################### 
#
# Primary maintainer: Kai Chang <kai@aiorobotics.com>
# Created Date: 10/21/2015

import math
import glob
import errno
import urllib
import requests
import json
import re #regex
import threading
from optparse import OptionParser
from IPython import embed
import sys
import os
from cStringIO import StringIO #Get image from web
#import wxpil #convert pil image to wx image
from PIL import Image
import cv2
import numpy
import signal
import gistfile1
import shutil #for shutil.rmtree
from tempfile import TemporaryFile

red = (0,0,255)
green= (0,255,0)
blue = (255,0,0)

null_image_hist = numpy.load("NullImageHist.numpy.npy")
apikey = "AIzaSyDyhqZZQB4hUBX_AUg0NV3EjDtVXhvH1c0"
keep_running = True

#1
#https://www.google.com/maps/dir/34.3505138,-117.8916598/33.999327,-118.3687344/@34.1710142,-118.4671497,10z/data=!3m1!4b1
lasrc = "34.0252761,-118.293743"
ladst = "33.999327,-118.3687344"

#2
#https://www.google.com/maps/dir/34.0252761,-118.293743/33.999327,-118.3687344/@34.0111054,-118.3661323,13z/data=!3m1!4b1
la2src = "34.3505138,-117.8916598"
la2dst = "34.266041,-118.1884885"
#3
#https://www.google.com/maps/dir/51.4934508,-0.1934343/51.5326371,-0.3176583/@51.5097286,-0.3256288,12z/data=!3m1!4b1
london_src = "51.4934508,-0.1934343"
london_dst = "51.5326371,-0.3176583"

#4
#https://www.google.com/maps/dir/42.3784474,-71.0254106/42.3503306,-70.9622277/@42.3595618,-71.0214838,13.75z/data=!4m2!4m1!3e0
boston_src = "42.3784474,-71.0254106"
boston_dst = "42.3503306,-70.9622277"

#5
#https://www.google.com/maps/dir/36.0904014,-115.1731982/36.1345833,-115.1695728/@36.112812,-115.2047821,13z/data=!3m1!4b1!4m2!4m1!3e2
lasvegas_src = "36.0904014,-115.1731982"
lasvegas_dst = "36.1345833,-115.1695728"

#6
#https://www.google.com/maps/dir/48.960612,2.5925045/48.8521438,2.3004866/@48.954964,2.2369678,11.25z/data=!4m2!4m1!3e2
paris_src = "48.960612,2.5925045"
paris_dst = "48.8521438,2.3004866"

#7
#https://www.google.com/maps/dir/59.2675304,17.9731804/59.8586532,17.6105213/@59.5648243,17.5432525,10z/data=!3m1!4b1!4m2!4m1!3e2
stockholm_src = "59.2675304,17.9731804"
stockholm_dst = "59.8586532,17.6105213"

#8
#https://www.google.com/maps/dir/-41.3093217,173.9832353/-46.5988458,168.3404823/@-44.0058465,170.177245,7.75z
newzealand_src = "-41.3093217,173.9832353"
newzealand_dst = "-46.5988458,168.340482"

#9
#From WA to FL state
#https://www.google.com/maps/dir/46.1944951,-122.8370151/28.794734,-81.5268487/@39.2111807,-112.0028927,5z/data=!4m2!4m1!3e0
wa_fl_src = "46.1944951,-122.8370151"
wa_fl_dst = "28.794734,-81.5268487"

#10
#https://www.google.com/maps/dir/40.8529796,-72.9015837/34.1383763,-118.2680491/@37.6101857,-104.5961318,5z/data=!3m1!4b1!4m2!4m1!3e0
la_ny_src = "40.8529796,-72.9015837"
la_ny_dst = "34.1383763,-118.2680491"

#11
#From AL to Miami 52675
#https://www.google.com/maps/dir/61.5807646,-149.4433953/25.786742,-80.1921284/@26.544922,-105.6678961,3.5z
al_mi_src = "61.5807646,-149.4433953"
al_mi_dst = "25.786742,-80.1921284"

#12
#From Portugal to Rome Italy 55872
#https://www.google.com/maps/dir/37.0746235,-8.1216127/41.9141694,12.5252303/@40.8069856,-2.8529314,5.25z
pt_it_src = "37.0746235,-8.1216127"
pt_it_dst = "41.9141694,12.5252303"

#13
#Brazil to Chile 37429
#https://www.google.com/maps/dir/-5.5239174,-47.4714597/-45.5743411,-72.0672734/@-29.0552064,-84.3123691,3.5z
bz_cl_src = "-5.5239174,-47.4714597"
bz_cl_dst = "-45.5743411,-72.0672734" 

#14
#Japan 1949km
#https://www.google.com/maps/dir/31.3823565,130.8642009/40.8217794,140.7469299/@36.0266701,131.3014041,6z/data=!3m1!4b1!4m2!4m1!3e0
japan_src = "31.3823565,130.8642009"
japan_dst = "40.8217794,140.7469299"

#15
#South Africa 1851km
url = "https://www.google.com/maps/dir/-34.0778403,18.445731/-23.0410419,29.9107534/@-22.9398047,30.0419121,9.75z"
southafrica_src = "-34.0778403,18.445731"
southafrica_dst = "-23.0410419,29.9107534"

#16
#Russia
url = "https://www.google.com/maps/dir/59.9598779,30.3041615/61.2539916,73.4071257/@58.3151736,42.8934876,5z/data=!3m1!4b1!4m2!4m1!3e0"

#17
#Tailand
url = "https://www.google.com/maps/dir/13.3742338,99.7030518/20.1362084,99.9567671/@17.0158759,99.5000077,7z/data=!4m2!4m1!3e0"

#18
#Indonesia
#url = "https://www.google.com/maps/dir/-6.0600487,106.0006494/-8.4883236,114.2666757/@-7.7372215,112.8035497,9.25z"

#19
#Australia 4707km  size 66K 100 waypoints
url = "https://www.google.com/maps/dir/-34.9805923,116.7280861/-23.8393244,151.2558572/@-24.3443849,126.3392424,4.76z"

#20
#mexico 4453km size 46K 100 waypoints
url = "https://www.google.com/maps/dir/21.1604512,-86.848712/30.8931735,-115.9734129/@24.3296588,-107.5788775,5.5z/data=!4m2!4m1!3e0"

#21
#TX2ND 1688mile size 35K 100 w
url = "https://www.google.com/maps/dir/27.707813,-98.43042/48.6259817,-101.9079972/@36.8852451,-103.8172212,5z/data=!4m2!4m1!3e0"

#22
#MT2NC 2275mile size 59K 100 w
url = "https://www.google.com/maps/dir/46.0580947,-111.4261715/34.7698925,-78.7871341/@37.235927,-104.0808931,5z/data=!4m2!4m1!3e0"

#23
#Norway 1721km 84K 100w
url = "https://www.google.com/maps/dir/58.5407688,7.2042099/68.4610472,15.8737163/@62.064596,-3.9457182,5z/data=!4m2!4m1!3e0"
#b4 800K
#11/12 318K

dirname = "norway"
itemode = "driving"
SAMPLING_WAYPOINTS = 100
FETCH_ANGLE_NUM = 12





#pattern = "maps\/dir\/([\d\.]+),([\d\.]+)\/([\d\.]+),([\d\.]+)\/" #to match 4 variable
pattern = "maps\/dir\/([-\d\.,]+)\/([-\d\.,]+)\/" #to match two set coord
match = re.compile(pattern)
result = match.search(url)

src = result.group(1)
dst = result.group(2)
print src
print dst 
test_route = "https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&mode=%s" % (src,dst,itemode)


#position: {lat: 33.9974565, lng: -118.358027}
#position: {lat: 33.9983606, lng: -118.3684911}
#snapToRoad = "https://roads.googleapis.com/v1/snapToRoads?path=33.9974565,-118.358027|33.9983606, -118.3684911 &interpolate=true&key=AIzaSyD-LzvTFGDLI9XQlrmfRGBpufnPSEcmofE"
def signal_handler(signal, frame):
        
        print('You pressed Ctrl+C!')
        global keep_running 
        keep_running = False
        sys.exit()
##############################################################
class AioClientLog(object):
    def __init__(self, name="", level='DEBUG'):
        self.name = name
        self.level = level

        
    def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        print msg

    def info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        print msg

    def warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        print msg

    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        print msg

    def exception(self, msg, *args, **kwargs):
        """
        Convenience method for logging an ERROR with exception information.
        """
        print msg

    def critical(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """
        print msg
    
########################################################################
class FetchImageThread(threading.Thread):
    def __init__(self,options):
        """
        @param parent: The object that should recieve the value
        @param value: value to 'calculate' to
        """
        threading.Thread.__init__(self)
        self.w = w = 300
        self.h = h =300
        #self.lon = lon = 34.0214267
        #self.lat = lat = -118.2894274
        self.lat = lat = 34.0201559
        self.lon = lon = -118.2872051
        self.options = options


        self.heading = heading = 39.85
        self.pitch = pitch = 0
        self.previewURL =  self.updateURL()
        #################
        self.max_index = FETCH_ANGLE_NUM #<<<<<<<<<<< setup fetch angle
    def updateURL(self):
        self.previewURL =  "https://maps.googleapis.com/maps/api/streetview?size=%dx%d&location=%10.6f,%10.6f&heading=%6.2f8&pitch=%6.2f&key=%s" % (self.w,self.h,self.lat,self.lon,self.heading,self.pitch,apikey)
        return self.previewURL
    def trackCallback(self,value):
        self.pitch = cv2.getTrackbarPos('pitch','image') -90
        #self.heading = cv2.getTrackbarPos('heading','image')
        self.updateURL()
        img = self.getImage()
        cv2.imshow("image" , img)
        print "Current Pitch %d, heading %d " % (int(self.pitch),int(self.heading))
    #cover pitch to horizon line
    #we know image pitch is from -44~44 cover top to bottom image
    #for now we just use linear interpolation
    def pitch2hz(self,pitch):
        #polyfit 0.0003148498860  -0.0016488159544   2.7050819016882   148.2091043844485
        #horizon_offset/(screen_height/2)=tan(pitch)/tan(vertical_FOV/2).
        #vertical_FOV = 88.0
        #hz = (math.tan(math.radians(pitch+45)) / math.tan(math.radians(vertical_FOV/2)) ) * (self.h/2)
        coff = [ 0.0003148498860, -0.0016488159544, 2.7050819016882, 148.2091043844485]
        hz = numpy.polyval(coff,pitch)
        #print hz
        if hz < 0 or hz > self.h:
            hz = 0
        return int(hz)
    def heading2vt(self,heading_offset):
        #using matlab polyfit(X,Y,3)
        coff = [  -0.0003556245191 ,  0.0005850890405 , -2.6116922329983 ,  152.9177984106553]
        vt = numpy.polyval(coff,heading_offset)
        #print vt
        if vt < 0 or vt > self.w:
            vt = 0
        return int(vt)

    def getAngleBetweenCoord2(self,p1,p2):
        #lat1,lon1 = p1['lat'],p1['lng']
        #lat2,lon2 = p2['lat'],p2['lng']
        lon1,lat1 = p1
        lon2,lat2 = p2
        startLat = math.radians(lat1)
        startLong = math.radians(lon1)
        endLat = math.radians(lat2)
        endLong = math.radians(lon2)
        
        dLong = endLong - startLong
        
        dPhi = math.log(math.tan(endLat/2.0+math.pi/4.0)/math.tan(startLat/2.0+math.pi/4.0))
        if abs(dLong) > math.pi:
             if dLong > 0.0:
                 dLong = -(2.0 * math.pi - dLong)
             else:
                 dLong = (2.0 * math.pi + dLong)
        
        bearing = (math.degrees(math.atan2(dLong, dPhi)) + 360.0) % 360.0 - 180.0;
        #print bearing
        return bearing


    def getRoute(self):
        r = sendRequest(test_route)
        #from IPython import embed
        #embed()
        try:
            if r.status_code == 200:
                #embed()
                jsonobj = json.loads(r.content)
                steps = jsonobj['routes'][0]['legs'][0]['steps']
                return steps
        except Exception as e:
            print e
            pass
        return None
    def getImage(self):
        cvImage = None
        r = sendRequest(self.previewURL) 
        try:
            if r.status_code == 200:
                img = Image.open(StringIO(r.content))
                cvImage = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
		return cvImage
        except IOError as e:
            print "IO Error"
            print e
        except AttributeError as e:
	    print "Error"
	    print e
        except Exception as e:
	    print e
	    
        return cvImage

    def isImageValid(self,image):
	#check image hist is same as null image
	hist = cv2.calcHist(image,[0],None,[30],[0,256])
	#numpy.save("NullImageHist.numpy",hist)
	cmpRes = cv2.compareHist(hist,null_image_hist,cv2.cv.CV_COMP_CORREL)
	print cmpRes
	if cmpRes > 0.95:
		print "Image not available"
		return False
	return True

    def click_and_crop(self,event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print "Mouse click (%d,%d)" % (x,y)

    def run(self):
        """
        Overrides Thread.run. Don't call this directly 
        its called internally when you call Thread.start().
        """
        output_path = dirname
        img_path = "img"
        aioClientLog = AioClientLog()
        if os.path.isdir(output_path):
          ans = raw_input("%s Dir exist, do you want to delete it? (Y/n)" %\
              output_path)
          if ans == 'Y' or ans == 'y':
              shutil.rmtree(output_path)
              os.mkdir(output_path)
              os.mkdir(output_path+"/"+img_path)
        else:
          #create an empty crop image folder
          os.mkdir(output_path)
          os.mkdir(output_path+"/"+img_path)
	
        if self.options.preview:
          cv2.namedWindow('image')
          #cv2.createTrackbar('pitch','image',0,180,self.trackCallback)
          #cv2.createTrackbar('heading','image',0,360,self.trackCallback)
          cv2.setMouseCallback("image", self.click_and_crop)
        #steps = self.getRoute()
        img = self.getImage()
        embed()

        total_pts = 0
        for s in steps:
            polyline = s['polyline']['points']
            pts = gistfile1.decode(polyline)
            total_pts += len(pts)
            print "This seg has %d pts" % len(pts)

        print "Total way points %d image %d" % (total_pts,int(total_pts/SAMPLING_WAYPOINTS)* (self.max_index-1)*(self.max_index-1))
        if self.options.dryrun:
            img = numpy.zeros((self.w,self.h,3), numpy.uint8)
            cv2.imshow("image" , img)
            cv2.waitKey(0)

        num_seg = len(steps)
        seg = 0
        self.id = 0
        for s in steps:
            #print "======"
            p1 = s['start_location']
            p2 = s['end_location']
            lat,lon = p1['lat'],p1['lng']
            polyline = s['polyline']['points']
            #print p1
            #print p2
            #print polyline
            pts = gistfile1.decode(polyline)
            num_pts = len(pts)
            if num_pts <= 16: #skip first 12 waypoints and last 5 waypoints to avoid turning image
                seg += 1
                continue
            #print pts
            #print s['html_instructions']
            it = iter(pts)
            for index in range(12,num_pts-5):
                try:
                    p = pts[index]
                    lon,lat = p
                    p1 = p
                    p2 = pts[index+1]
                    self.lat = lat
                    self.lon = lon
                    #self.heading = self.getAngleBetweenCoord(p2,p1)
                    roadheading = self.getAngleBetweenCoord2(p2,p1)
		    def downloadImage():
                    	if self.options.preview:
                        	self.max_index = 2
                    	for i in range(1,self.max_index):
                            for j in range(1,self.max_index):
                            	if not keep_running:
                                    return
                           
                            	if self.options.preview:
                                    h_offset = 0
                                    p_offset = 0
                            	else:
                                    h_offset = (i-(self.max_index/2))*5
                                    p_offset = (j-(self.max_index/2))*5
                            	self.heading = roadheading + h_offset
                            	self.pitch = p_offset
                            	self.updateURL()
                            
                            	y = hzline = self.pitch2hz(self.pitch)
                            	x = vtline = self.heading2vt(h_offset)
                            	print "id %d seg %d/%d index %d/%d lon %f lat %f pitch %d head %d vp %d %d" % (self.id,seg,num_seg,index,num_pts,lon,lat,p_offset,h_offset,x,y)
                            	filename = "img_%d_vp_%d_%d_lon_%f_lat_%f_pitch_%d_headoffset_%d_roadhead_%f.jpg" % (self.id,x,y,lon,lat,p_offset,h_offset,roadheading)
                            	path = output_path+"/"+img_path+"/"+filename
                            	#print path

                            	if self.options.preview:
                                    if index % (SAMPLING_WAYPOINTS*10) == 0:
                                        img = self.getImage()
                                        #if image is not available, skip entire pan and tilt grab
				    	if not self.isImageValid(img):
					    return
					
                                    	cv2.line(img, (0,hzline), (self.w,hzline), green,1) #left green
                                    	cv2.line(img, (vtline,0), (vtline,self.h), blue,1) 
                                    	cv2.imshow("image" , img)
                                    	cv2.waitKey(0)
                            	else:
                                	if not self.options.dryrun:
                                    	    img = self.getImage()
                                            #if image is not available, skip entire pan and tilt grab
				    	    if not self.isImageValid(img):
					        return
                			    cv2.imwrite(path, img) 
                            	self.id+=1
                    #only download every 10 waypoints to keep variety
                    if index % SAMPLING_WAYPOINTS == 0:
                        downloadImage()
                except StopIteration as sie:
                    print sie
                except IndexError as ie:
                    print ie
                except Exception as e:
                    print e

            seg+=1
        print "======================================="
        print "%s All pts Finished, total %d images" % (dirname,self.id)
# Network Request Function 
##############################################################
def sendRequest(url,to=15):
    r = False
    try:
        r = requests.get(url,timeout=to)
    except requests.exceptions.Timeout:
        aioClientLog.info("Connection Timout")
    except requests.exceptions.TooManyRedirects:
        aioClientLog.info("Connection TooManyRedirects")
    except requests.exceptions.RequestException as e:
        #aioClientLog.debug("Connection Fail")
        #print e
        return r
    except Exception as e:
        aioClientLog.exception(e)
        return r

    return r

######################################################################### 
######################################################################### 
######################################################################### 
def main():
    signal.signal(signal.SIGINT, signal_handler)

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-q", "--quiet",
            action="store_true", dest="quiet",
            help="quiet mode without showing preview")
    parser.add_option("-p", "--preview",
            action="store_true", dest="preview",
            help="preview raw image with vp drawing")
    parser.add_option("-d", "--dryrun",
            action="store_true", dest="dryrun",
            help="dry run the script to get total id without download image")
    (options,args) = parser.parse_args(sys.argv)
    
    if len(args) != 1:
        parser.error("incorrect number %d" % len(args))

    fit = FetchImageThread(options)
    fit.start()

    signal.pause()
    print "Exit"
if __name__ == "__main__":
    main()
