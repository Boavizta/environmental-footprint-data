# This file is part of ecodiag-data, a set of scripts to assemble
# environnemental footprint data of ICT devices.
# 
# Copyright (C) 2021-2022 Gael Guennebaud <gael.guennebaud@inria.fr>
# 
# This Source Code Form is subject to the terms of the Mozilla
# Public License v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import cv2
import numpy as np
import argparse
import json
import math
import copy
import re
import os
import sys

import pytesseract

def rgb2int(a):
  return (a[2] << 16) + (a[1] << 8) + a[0]

def bgr2int(a):
  return (a[0] << 16) + (a[1] << 8) + a[2]

def int2rgb(a):
  return np.array([(a>>0)&0xff, (a>>8)&0xff, (a>>16)&0xff])

def distint2(a,b):
  a = int2rgb(a)
  b = int2rgb(b)
  return np.max(np.abs(a-b))


def p2f(x):
  if '%' in x:
    return float(x.split('%')[0])
  return float(x)


def gammaCorrection(src, gamma):
  invGamma = 1 / gamma

  table = [((i / 255) ** invGamma) * 255 for i in range(256)]
  table = np.array(table, np.uint8)

  return cv2.LUT(src, table)

def missingPart(data):
  if (not 'use' in data) and ('prod' in data) and ('transp' in data):
    return 'use'
  if (not 'transp' in data) and ('use' in data) and ('prod' in data):
    return 'transp'
  if (not 'prod' in data) and ('use' in data) and ('transp' in data):
    return 'prod'
  return False


class PiechartAnalyzer:
  def __init__(self, profileFile=None, debug=0):
    self.debug = debug

    if not profileFile:
      if 'PYTHONPATH' in os.environ:
        profileFile = os.path.join(os.environ['PYTHONPATH'], "tools/parsers/lib/profiles.json")
      else:
        profileFile = os.path.join(sys.path[0], "lib/profiles.json")
    
    with open(profileFile) as f:
      self.profiles = json.load(f)

    # turn [r,g,b] to packed 32 bits integers
    for pk,p in self.profiles['profiles'].items():
      if 'map' in p:
        for ck,c in p['map'].items():
          p['map'][ck] = rgb2int(c)

  def print(self, debug: int, *args):
    if self.debug >= debug:
      print(*args)

  def imshow(self, debug: int, title: str, img):
    if self.debug >= debug:
      cv2.imshow(title, img)
      cv2.waitKey(0)

  def sum_of_details(self, piedata):
    extra = ['confidence1','confidence2','profile/main','profile/prod','extrapolated']
    mains = ['use','prod','transp','EOL']
    sum = 0
    for k,v in piedata.items():
      if k not in extra and k not in mains:
        sum += v
    return sum

  def prod_from_other_mains(self, piedata):
    mains = ['use','transp','EOL']
    sum = 0
    for k,v in piedata.items():
      if k in mains:
        sum += v
    return 100.-sum

  def auto_prod(self, piedata):
    if not 'prod' in piedata:
      details = self.sum_of_details(piedata)
      if 'use' in piedata and 'transp' in piedata:
        piedata['prod'] = self.prod_from_other_mains(piedata)
        if abs(details - piedata['prod'] > 1.):
          self.print(1, "WARNING: production != sum of sub-components (", piedata['prod'], details)
      elif details>0:
        # this path is hazardous
        piedata['prod'] = self.sum_of_details(piedata)
    return piedata
  
  def append_to_boavizta(self, boaitem, piedata):

    main = ['use', 'prod', 'transp', 'EOL']
    toBoa = {
      'use':          'gwp_use_ratio',
      'prod':         'gwp_manufacturing_ratio',
      'transp':       'gwp_transport_ratio',
      'EOL':          'gwp_eol_ratio',
      'board':        'gwp_mainboard_ratio',
      'SSD':          'gwp_ssd_ratio',
      'HDD':          'gwp_hdd_ratio',
      'disp':         'gwp_display_ratio',
      'power':        'gwp_psu_ratio',
      'box':          'gwp_chassis_ratio',
      'battery':      'gwp_battery_ratio',
      'packaging':    'gwp_packaging_ratio',
      'optical_drive':'gwp_opticaldrive_ratio',
      'electronics':  'gwp_electronics_ratio',
      'housing':      'gwp_chassis_ratio',
      'panel':        'gwp_display_ratio',
      'materials':    'gwp_othercomponents_ratio',
      'assembly':     'gwp_othercomponents_ratio',
      'IC':           'gwp_othercomponents_ratio',
      'PWBs':         'gwp_othercomponents_ratio',
      'lcd_assembly': 'gwp_display_ratio',
    }
    main_sum = 0
    other_sum = 0
    for k,v in toBoa.items():
      if k in piedata:
        if k in main:
          main_sum += piedata[k]
        else:
          other_sum += piedata[k]
        if v in boaitem:
          boaitem[v] = round(boaitem[v] + piedata[k]/100., 3)
        else:
          boaitem[v] = round(piedata[k]/100., 3)
        
    # sanity checks
    if abs(100. - main_sum) > 0.5:
      self.print(1, "WARNING sum of use+manufacturing+transport+eol != 100 (", main_sum, ")")
    if 'prod' in piedata and abs(piedata['prod'] - other_sum) > 1e-2*other_sum:
      self.print(1, "WARNING sum of sub manufacturing components != manufacturing (", other_sum, "vs", piedata['prod'], ")")

    return boaitem
  
  
  ###################################################################################################
  def create_legend_from_ocr(self, input_img, img_no_charts, profile, cimg):
    """This function strives to automatically reconstruct the legend as
       a dictionary mapping a color to a known item.
       In practice, this function is looking for known text labels (as defined by the profile)
       having a colored square slightly on its right. The color is picked at the center of the square.
       Any text label that is not matched by the profile is ignored."""

    self.print(2, "Run create_legend_from_ocr...")
    
    img = img_no_charts.copy()

    # remove border and piecharts
    # cv2.rectangle(img, (0,0), (img.shape[1],img.shape[0]), (255,255,255), 5)
    # cv2.circle(img, (circle[0], circle[1]), int(circle[2])+10, (255,255,255), -1)


    grayimg1 = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #self.imshow(3, 'legend ocr: grayimg1',grayimg1)
    # thret, th1 = cv2.threshold(grayimg1, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    thret, th1 = cv2.threshold(grayimg1, 200, 255, cv2.THRESH_BINARY_INV)
    
    #self.imshow(3, 'legend ocr: binarized image',th1)

    # identify non letter pixels
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(6,6))
    k2 = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))
    mask1 = th1.copy()
    mask1 = cv2.erode(mask1,kernel,1)
    mask1 = cv2.dilate(mask1,kernel,1)
    mask1 = cv2.dilate(mask1,k2,1)
    
    #self.imshow(3, 'legend ocr mask1',mask1)

    # remove non letter pixels
    th1[mask1==255] = 0

    # remove noise
    # k3 = cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))
    # th1 = cv2.erode(th1,k3,1)
    # th1 = cv2.dilate(th1,k3,1)

    #self.imshow(3, 'legend ocr: input of dilate',th1)

    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, profile['vertical dilation']))
    dilation = cv2.dilate(th1, rect_kernel, iterations = 1)

    #self.imshow(3, 'legend ocr: input of findContours',dilation)

    im2 = img.copy()

    contours, hierarchy = cv2.findContours( dilation, cv2.RETR_LIST,  
                                            cv2.CHAIN_APPROX_NONE)

    # get a copy without letters for color identification
    im4color = im2.copy()
    # im4color[mask1==0] = 255
    grayimg2 = cv2.cvtColor(im4color,cv2.COLOR_BGR2GRAY)

    #self.imshow(4, 'legend ocr: input of findContours 2',grayimg2)
    #self.imshow(5, 'ocr im4color',im4color)

    res = {}

    # print(len(contours))
    for cnt in contours: 
      x, y, w, h = cv2.boundingRect(cnt)
      if w<20:
        continue
      x += 3
      w -= 6
      
      cv2.rectangle(cimg, (x, y), (x + w, y + h), (255, 255, 0), 1) 
      
      # extract block for feeding OCR
      cropped = input_img[y:y + h, x:x + w].copy()
      custom_oem_psm_config = '--psm 6'
      fulltext = pytesseract.image_to_string(cropped, config=custom_oem_psm_config).strip()
      #self.imshow(4, fulltext, cropped)

      nLine = 0
      nbLines = len(fulltext.splitlines())
      for text in fulltext.splitlines():

        actualH = int(h / nbLines)
        actualY = int(y + h*nLine/nbLines)
        nLine += 1

        # find corresponding label
        label_out = False
        for k,v in profile['ocr patterns legend'].items():
          ret = re.search(v,text)
          if ret:
            label_out = k
            break
        if not label_out:
          if len(text)>2:
            self.print(1, "WARNING failed to find matching label for ", text)
          continue

        if label_out in res and res[label_out] > 0:
          self.print(2, "Skip already found label: {", text, "}")
          continue

        self.print(2, "   ocr found ",text, " -> ", label_out)

        # search respective color
        cv2.rectangle(cimg, (max(0,x-actualH), actualY), (x+2, actualY + actualH), (0, 0, 255), 1) 
        cropped = input_img[actualY:actualY + actualH, max(0,x-actualH):x+2]
        # binarize
        x0 = max(0,x-actualH)
        y0 = actualY
        thin = grayimg2[y0:actualY + actualH, x0:x+2].copy()
        thin = gammaCorrection(thin, 0.1) # enhance contrast
        thret, th2 = cv2.threshold(thin, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        # get contour
        if self.debug>=4 and (not thin is None) and len(thin.shape)>=2 and thin.shape[0]>0 and thin.shape[1]>0:
          #cv2.imshow('find contours in ', thin)
          #cv2.imshow('find contours in th ', th2)
          cv2.waitKey(0)
        contours2, hierarchy2 = cv2.findContours( th2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(contours2)>0:
          areas = [cv2.contourArea(c)/max(1,cv2.arcLength(c,True)) for c in contours2]
          largestId = areas.index(max(areas))
          x2, y2, w2, h2 = cv2.boundingRect(contours2[largestId])
          cv2.rectangle(cimg, (x0+x2, y0+y2), (x0 + x2 + w2, y0 + y2 + h2), (0, 255, 0), 1)

          c = cropped[y2+int(h2/2),x2+int(w2/2),:]
          ci = bgr2int(c)
          self.print(2, "    picked color : ", c, " -> ", ci)
          res[label_out] = ci
          
        else:
          self.print(1, "WARNING failed to find color picking contour for '",text,"'")

    self.print(2, "  res = ",res)
    
    return res
  
  ###################################################################################################
  def percent_from_ocr(self, input_img, circle, profile, cimg):
    """This function strives to find block of known labels (as defined by the profile)
       ending with a percentage number.
       Found pairs are returned as a dictionary."""
    
    self.print(2, "Run percent_from_ocr...")
    
    malus = 0

    y0 = max(0, int(circle[1]-circle[2]*1.5))
    y1 = min(input_img.shape[0], int(circle[1]+circle[2]*1.5))

    x0 = max(0, int(circle[0]-circle[2]*1.9))
    x1 = min(input_img.shape[1], int(circle[0]+circle[2]*1.9))
    img = input_img[y0:y1, x0:x1]
    #self.imshow(3, 'percent_from_ocr/in', img)

    # select characters
    char_method = profile.get('ocr percent letter select method')
    if char_method and char_method=='average':
      img_max = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    else:
      img_max = np.max(img, 2)
    #self.imshow(3, 'percent_from_ocr/img_max',img_max)
    mask = cv2.threshold(img_max, 70, 255, cv2.THRESH_BINARY_INV)[1]
    #self.imshow(3, 'percent_from_ocr/mask1',mask)
    K2_width = 20
    K2 = cv2.getStructuringElement(cv2.MORPH_RECT,(K2_width,30))
    if 'ocr percent dilate size' in profile:
      s = profile['ocr percent dilate size']
      K2_width = max(1,round(s[0]*circle[2]))
      K2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(K2_width,max(1,round(s[1]*circle[2]))))
    mask = cv2.dilate(mask,K2,1)
    #self.imshow(3, 'percent_from_ocr/mask',mask)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    res = {}
    for cnt in contours:
      x, y, w, h = cv2.boundingRect(cnt)
      if w<20:
        continue
      shrink = math.ceil(K2_width*0.15)
      x+=shrink
      w-=2*shrink
      cv2.rectangle(cimg, (x0 + x, y0 + y), (x0 + x + w, y0 + y + h), (255, 255, 0), 1) 
        
      cropped = img[y:y + h, x:x + w].copy()
      cropped = cv2.cvtColor(cropped,cv2.COLOR_BGR2GRAY)

      if 'ocr percent gamma' in profile:
        cropped = gammaCorrection(cropped, profile['ocr percent gamma'])
      else:
        cropped = gammaCorrection(cropped, 1.8)

      if h<50:
        # scale by a factor to keep high quality resampling
        factor = int(math.pow(2,math.ceil(math.log2(math.ceil(50/h)))))
        cropped = cv2.resize(cropped, (factor*w, factor*h), interpolation = cv2.INTER_AREA)
      
      custom_oem_psm_config = '--psm 6 --oem 1'
      text = pytesseract.image_to_string(cropped, config=custom_oem_psm_config).strip()
      
      lines = text.splitlines()
      singleLine = re.sub("\n", "|", text)
      self.print(2, "    ocr found:", singleLine)

      if len(lines)==0:
        continue
      
      if self.debug>=2:
        cv2.imwrite('tmp_ocr/'+lines[0]+'_ocr.png',cropped)

      #self.imshow(4, singleLine,cropped)

      # find corresponding label
      label_out = False
      for k,v in profile['ocr patterns direct'].items():
        ret = re.search(v,text)
        if ret:
          if label_out != False:
            self.print(1, "WARNING: found multiple labels in ", text)
            malus += 0.2
          label_out = k

          # try to find associated percentage value
          ret = re.search(v+"[^0-9sS\%]*([0-9sS]+\.?[0-9]*)\s*\%",text)
          if ret:
            try:
              rawVal = re.sub(r'(S|s)', '5', ret.group(1))
              if rawVal!=ret.group(1):
                malus += 0.1
              value = p2f(rawVal)
              self.print(2,value)
              self.print(2, "   ocr found ", label_out, " = ", value)
              if value>100:
                self.print(1, "WARNING: read percentage value", value, "for", label_out, "is greater than 100%! -> skip it.")
              else:
                if label_out in res:
                  self.print(1, "WARNING: found duplicate for \"", label_out, "\" with values ", res[label_out], " and ", value, " (keep smallest)")
                  malus += 0.2
                  if value < res[label_out]:
                    res[label_out] = value  
                else:
                  res[label_out] = value
            except Exception:
              self.print(1, "WARNING: cannot convert " + ret.group(1) + " to float for ", label_out)
          else:
            self.print(1, "WARNING: cannot find associated percentage for", label_out)
          
      if not label_out:
        self.print(1, "WARNING failed to find label out for ", singleLine)
        continue

      if len(lines) < 2:
        self.print(1, "WARNING: found a single line for ", singleLine)
    
    self.print(2, "  res = ",res)
    
    return res, malus
  
  def analyze_file(self,filename,ocrprofile=None):
    input_img = cv2.imread(filename,cv2.IMREAD_COLOR)
    self.analyze(input_img, ocrprofile)

  def analyze(self,input_img,ocrprofile=None):

    profiles = copy.deepcopy(self.profiles)

    img = input_img.copy()
    
    grayimg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    grayimg = gammaCorrection(grayimg, 0.5)
    grayimg = cv2.blur(grayimg,(5,5))
    
    gradx = cv2.Sobel(grayimg,cv2.CV_32F,1,0,ksize=5)
    grady = cv2.Sobel(grayimg,cv2.CV_32F,0,1,ksize=5)

    mindim = min(img.shape[0],img.shape[1])
    maxrad = max(1, int(mindim/2))

    #self.imshow(4, "input of HoughCircles", grayimg)

    circles = cv2.HoughCircles(grayimg,cv2.HOUGH_GRADIENT_ALT,dp=1,
                                minDist=max(1,int(mindim/10)),
                                param1=50,
                                param2=0.95,
                                minRadius=10,maxRadius=maxrad)

    self.print(2, "Found circles:", circles)
    
    cimg = img.copy()

    if circles is None or len(circles)==0:
      return None
    
    circles = circles[0]

    if not ocrprofile:
      if len(circles) >= 2:
        ocrprofile = 'DELL'
      else:
        ocrprofile = 'HP'
      self.print(1, "Fallback to default OCR profile:", ocrprofile)
    mainprofile = profiles['profiles'][ocrprofile]

    # remove text (needed when extracting percentage from the piechart itself)
    img_max = np.max(img, 2)
    mask = cv2.threshold(img_max, 70, 255, cv2.THRESH_BINARY_INV)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    mask = cv2.dilate(mask,kernel,1)
    img = cv2.inpaint(img, mask, 20, cv2.INPAINT_TELEA)
    #self.imshow(3, 'inpainted', img)

    img_id = np.left_shift(img[:,:,0].astype(np.int32),16) + np.left_shift(img[:,:,1].astype(np.int32),8) + img[:,:,2].astype(np.int32)
    #self.imshow(3, 'mask', mask)

    res = {}

    ##############################
    # Prepare image for OCR legend extraction.
    # The goal is to remove as much stuff as possible but the legend itself.
    img_no_charts = input_img.copy()
    # Remove border (TODO for HP only?)
    cv2.rectangle(img_no_charts, (0,0), (img_no_charts.shape[1],img_no_charts.shape[0]), (255,255,255), 5)
    # Remove piecharts (= erase the found circles + their common bounding box)
    rmin0=img_no_charts.shape[1]
    rmin1=img_no_charts.shape[0]
    dmin = min(img_no_charts.shape[0], img_no_charts.shape[1])
    rmax0=0
    rmax1=0
    offset = 0
    first = True
    for circle in circles:
      circle = np.uint16(np.around(circle))
      # filter very small circles (noise)
      if first or circle[2] > 50:
        rmax0 = max(rmax0, circle[0]+int(circle[2])+offset)
        rmax1 = max(rmax1, circle[1]+int(circle[2])+offset)
        rmin0 = min(rmin0, circle[0]-int(circle[2])-offset)
        rmin1 = min(rmin1, circle[1]-int(circle[2])-offset)
        first = False
    rmax1 -= 30
    self.print(3, "img_no_charts.shape:", img_no_charts.shape)
    self.print(3, "rmin-max:", rmin0,rmin1, rmax0,rmax1)
    cv2.rectangle(img_no_charts, (rmin0,rmin1), (rmax0,rmax1), (255,255,255), -1)
    for circle in circles:
      circle = np.uint16(np.around(circle))
      if circle[2] > dmin/4:
        cv2.circle(img_no_charts, (circle[0], circle[1]), int(circle[2])+10, (255,255,255), -1)
    ##############################

    autolegend = False
    
    if 'ocr patterns legend' in mainprofile:
      autolegend = self.create_legend_from_ocr(input_img, img_no_charts, mainprofile, cimg)

    # for each pie-chart
    circle_count = -1
    radius0 = 0
    for circle in circles[:min(2,len(circles))]:
      # print(circle)
      circle = np.uint16(np.around(circle))
      circle_count+=1
      if circle_count==0:
        radius0 = circle[2]

      if self.debug:
        # draw the outer circle
        cv2.circle(cimg,(circle[0],circle[1]),circle[2],(0,255,0),2)
        # draw the center of the circle
        cv2.circle(cimg,(circle[0],circle[1]),2,(0,0,255),3)

      # check that the circle is within the image
      if (circle[0]-circle[2]<0) or (circle[1]-circle[2]<0) or (circle[0]+circle[2]>=img.shape[1]) or (circle[1]+circle[2]>=img.shape[0]):
        cv2.circle(cimg,(circle[0],circle[1]),2,(0,255,255),3)
        self.print(2, "skip clamped circle", circle)
        continue

      if circle_count > 0 and circle[2] < radius0*0.3:
        self.print(2, "skip too small circle", circle)
        continue

      ##############################
      # compute the donut radii
      #
      # first, check gradient direction to see if we should shrink or enlarge
      nsamples = 100
      cumsign = 0
      for i in range(nsamples):
        angle = float(i)/float(nsamples)*math.pi
        egx = math.cos(angle)
        egy = math.sin(angle)
        px = circle[2]*egx + circle[0]
        py = circle[2]*egy + circle[1]
        gx = gradx.item(int(py),int(px))
        gy = grady.item(int(py),int(px))
        s = math.sqrt(gx*gx+gy*gy)
        if s>0:
          gx = gx/s
          gy = gy/s
          cumsign += egx*gx+egy*gy
      cumsign /= nsamples
        
      if cumsign>0:
        re = float(circle[2]-4)
        ri = 2*re/3
      else:
        ri = float(circle[2]+4)
        re = 3*ri/2

      cv2.circle(cimg,(circle[0],circle[1]),int(ri),(0,0,128),1)
      cv2.circle(cimg,(circle[0],circle[1]),int(re),(0,0,255),1)
      ##############################


      # create the mask (i.e., 255 inside the donut, 0 elsewhere)
      mask = np.zeros(grayimg.shape, np.uint8)
      cv2.circle(mask,(circle[0],circle[1]),int(re),255, -1)
      cv2.circle(mask,(circle[0],circle[1]),int(ri),0, -1)

      (u,c) = np.unique(img_id[mask==255],return_counts=True)
      ind = np.lexsort( (u,c) )
      ind = np.flip(ind)
      freq = np.asarray((u[ind], c[ind])).T

      if self.debug:
        for i in freq[0:20]:
          self.print(2, int2rgb(i[0]), " : ", i[0], " : ", i[1])
      
      try_ocr = True
      total_px = np.sum(freq[:,1])
      total_pixels = np.sum(freq[:,1])
      trueSum = 0

      # try using the extracted legend
      if autolegend:
        score = 0
        count_opt = 0
        sum_pixels = 0
        opt = mainprofile['opt']
        i=0
        self.print(2, "\n--- auto legend ---")
        self.print(2, autolegend)
        self.print(2, "--- frequencies ---")
        self.print(2, freq)
        self.print(2, "---\n")
        for ck,c in autolegend.items():
          # score -= 1
          if c in freq[:,0]:
            score += 1
            ind = np.where(freq[:,0]==c)[0]
            sum_pixels += np.sum(freq[ind,1])
            self.print(3, "add ", ck, c)
          elif ck in opt:
            count_opt +=1
          i += 1
        
        score += float(sum_pixels)/float(total_pixels)
        
        self.print(2, "autolegend scoring: {}+{} / {}".format(score, count_opt, len(autolegend)))
        
        if score > 0:
          self.print(2," -> clean up unique color ")

          count = 0
          sum = 0
          try:
            dist_th = mainprofile['color_th']
          except:
            dist_th = 20
          for r in freq:
            a = r[0]
            best_dist = 1e9
            best_c = 0
            if not a in autolegend:
              for ck,c in autolegend.items():
                d = distint2(a,c)
                if d<best_dist:
                  best_dist = d
                  best_c = c
                  if d < dist_th:
                    r[0] = c
              if best_dist > dist_th:
                if self.debug and r[1] > 2:
                  self.print(2, "skip ", best_dist, " : ", int2rgb(a), int2rgb(best_c), " (", r[1], ")")
                if r[1] > 0.05*total_px: # > 5%, arbitrary
                  count += 1
                  sum += r[1]
          if self.debug:
            tmp = {}
            for r in freq:
              if r[1]>dist_th:
                if not r[0] in tmp:
                  tmp[r[0]] = 0
                tmp[r[0]] += r[1]
            self.print(2, freq[0:10,:])
            self.print(2, tmp)
            # print("nb unique: ",np.unique(freq[:,0]).size)

          names = {}
          for ck in autolegend.keys():
            names[ck] = ck
          
          inserteditems = []
          trueSum = 0
          for ck,c in autolegend.items():
            ind = np.where(freq[:,0]==c)[0]
            item_name = ck
            if names and ck in names:
              item_name = names[ck]
            if ind.size>0 :
              q = np.sum(freq[ind,1])
              if trueSum==0 or ('opt' in mainprofile and item_name not in mainprofile['opt']) or float(q)/float(total_px)>0.0015: # filter noise
                res[item_name] = q
                trueSum += q
                count += 1
                inserteditems.append(item_name)
              elif self.debug:
                self.print(2, "NOTE skip noise: ", item_name, " with ", q, " pixels (", float(q)/float(total_px)*100, "%)")
            # else:
              # res[item_name] = 0
          
          if trueSum/total_px > 0.5:

            self.print(2, "GOOD ", trueSum, "/" , total_px)

            try_ocr = False
            sum += trueSum

            is_details_pie_charts = ('profile/main' in res and res['profile/main'] == 'ocr')
            if (not is_details_pie_charts) and (not 'EOL' in res):
              self.print(1, "WARNING: missed end-of-life, add it explicitely...")
              res['EOL'] = 0
              count+=1
              inserteditems.append('EOL')
              res['extrapolated'] = 'EOL'

            # correction & normalization:
            corr = 0
            if count > 0:
              corr = float(total_px-sum)/float(count)
              # bound correction to 1% ?
              corr = min(corr, total_px*0.01)
              total_px = sum + corr * count
            factor = 1

            if is_details_pie_charts and 'prod' in res:
              factor = res['prod']/100.
            for ck,c in res.items():
              if ck in inserteditems:
                res[ck] = round(10000*(c+corr)/total_px*factor)/100.

            if 'profile/main' in res:
              res['confidence2'] = round(100*trueSum/total_px)/100.
              res['profile/prod'] = 'auto legend'
            else:
              res['confidence1'] = round(100*trueSum/total_px)/100.
              res['confidence2'] = 1
              res['profile/main'] = 'auto legend'
          else:
            # cleanup
            for k in inserteditems:
              res.pop(k)
        
      if try_ocr:
        self.print(2, "No profile is good enough, we should have trueSum/total_px = ", trueSum/total_px, " > ", 0.5)
        if not res and 'ocr patterns direct' in mainprofile:
          res, malus = self.percent_from_ocr(input_img, [circle[0],circle[1],re], mainprofile, cimg)
          if res:
            is_details_pie_charts = ('profile/main' in res and res['profile/main'] == 'ocr')

            # remove possible wrong entries in auto profile
            if autolegend:
              self.print(2, autolegend)
              for k in res:
                if k in autolegend:
                  autolegend.pop(k)
              self.print(2, autolegend)

            res['confidence1'] = 0
            for k in ['use', 'prod', 'transp', 'EOL']:
              if k in res:
                res['confidence1'] += res[k]
            res['confidence1'] /= 100
            res['confidence1'] -= malus

            if not is_details_pie_charts:
              part = missingPart(res)
              if part:
                self.print(1, "WARNING: missed ", part, ", add it explicitely...")
                if not 'EOL' in res:
                  self.print(1, "WARNING: missed end-of-life, add it explicitely...")
                  res['EOL'] = 0.5 # arbitrary
                res[part] = 0
                res[part] = 100 - (res['use']+res['prod']+res['transp']+res['EOL'])
                res['extrapolated'] = part
              else:
                if not 'EOL' in res:
                  if 'use' in res and 'prod' in res and 'transp' in res:
                    res['EOL'] = max(0, 100 - (res['use']+res['prod']+res['transp']))
                  else:
                    res['EOL'] = 0.5 # arbitrary
                  self.print(1, "WARNING: missed end-of-life, add it explicitely... (", res['EOL'], ")")
                  res['extrapolated'] = 'EOL'
            
            res['profile/main'] = 'ocr'
            res['confidence2'] = 1

    #self.imshow(3, 'detected circles',cimg)
    cv2.destroyAllWindows()

    return res


if __name__ == "__main__":

  ap = argparse.ArgumentParser()

  ap.add_argument("-i", "--input", required=True, help="input image file")
  ap.add_argument("-o", "--ocrprofile", required=False, default='', type=str, help="profile for OCR")
  ap.add_argument("-d", "--debug", required=False, default=0, type=int, help="show circles and debug info")
  
  args = vars(ap.parse_args())

  pa = PiechartAnalyzer(os.path.join(sys.path[0], "profiles.json"), args['debug'])
  res = pa.analyze(args['input'] , args['ocrprofile'])
  
  if res:
     print(res)
  else:
    print("no good match")
    exit(1)