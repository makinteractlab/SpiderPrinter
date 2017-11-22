import sys
import cv2
import numpy as np
#import random # for uniform random
import math # for pi
#import matplotlib.pyplot as plt # for plotting the error evolution
pi=np.pi

####### START - Parameters #######
ImgPath = "JC_middle.jpg" #"./starfish_01.jpg"# JC_middle.jpg ./couple_01.jpeg" #"./JC_middle.jpg"#""./yeoja_01.jpg" #./JC_middle.jpg" # "Marion_01.jpg"#
ImgRadius = 350     # Number of pixels that the image radius is resized to

InitPinIndex = 0         # Initial pin to start threading from 
NbPins = 200 #200         # Number of pins on the circular loom
NbLines = 1500 # 3000 #500        # Maximal number of lines

minLoop = 2#1# in java, none. 3   if-1 then not used      # Disallow loops of less than minLoop lines (if = NbLines then never twice the same pin. maybe a bad idea actually ;-) )
LineWidth = 1#3       # The number of pixels that represents the width of a thread
LineFade = 25#15       # The weight a single thread has in terms of "darkness"

MinDistConsecPins = 15#25 # // minimal distance between two consecutive pins (in number of pins)
myThreshCenterAngle=20./360.*2.*pi # if high, then no effect

LineScoreDef='sum_darkness_normalized' # 'sum_darkness' # 'sum_darkness_normalized'

FlagLineType = 'straight'#'bezier'#'straight'
variation=3 # for bezier? also for straight?
FlagMethod_PixelsOnLine='BLA'#'linsampling'#'BLA' # 'linsampling' # 
# Brensenham's Line Algorithm.
#https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm

RigShape="circle" # "circle" # "square"

LineOpacity=10.0/100.0#20.0/255.0 # if 1 then fully opaque
LineColor=0.0#100.0 # 0~255

LUP_LinePixels={}



NbMultiCircles=1 #2
####### END - Parameters #######

# Load image
def FnLoadImage(ImgPath):
    OrigImage = cv2.imread(ImgPath)
    if OrigImage is None:
       print "Error loading image: " + ImgPath 
       sys.exit()
    print "Image loaded: " + ImgPath 
       
    return OrigImage

# Invert grayscale image
def invertImage(image):
    return (255-image)

# Apply circular mask to image
def maskImage(image, radius):
    y, x = np.ogrid[-radius:radius + 1, -radius:radius + 1]
    mask = x**2 + y**2 > radius**2
    image[mask] = 0

    return image

# Compute coordinates of loom pins
def Fn_CreatePinCoords(radius, nPins=200, offset=0, x0=None, y0=None):

  if RigShape=="square":
    FlagSamplingMethod="Square_AngleSampling" # "Square_SideSampling"
        
  coords = []

  if RigShape=="circle" or (RigShape=="square" and FlagSamplingMethod=="Square_AngleSampling"):

    alpha = np.linspace(0 + offset, 2*np.pi + offset, nPins + 1)

    if (x0 == None) or (y0 == None): # the center
      x0 = radius# + 1
      y0 = radius# + 1

    
    for angle in alpha[0:-1]:

      if RigShape=="circle":

        x = int(x0 + radius*np.cos(angle))
        y = int(y0 + radius*np.sin(angle))

      elif RigShape=="square" and FlagSamplingMethod=="Square_AngleSampling":
        
        # right side
        if (0<= angle and angle <=pi/4) or (7*pi/4<= angle and angle <=2*pi):
          x = int(x0 + radius)
          y = int(y0 - radius*np.tan(angle)) # minus for going up when angle increases
        # left side
        elif (3*pi/4<= angle and angle <=5*pi/4):
          x = int(x0 - radius)
          y = int(y0 + radius*np.tan(angle))
        # top side
        elif (pi/4<= angle and angle <=3*pi/4):
          x = int(x0 + radius/np.tan(angle))
          y = int(y0 - radius)
        # bottom side
        elif (5*pi/4<= angle and angle <=7*pi/4):
          x = int(x0 + radius/np.tan(angle))
          y = int(y0 + radius)
        else:
          print "ERROR Wrong case: ", angle
          sys.exit()
        #print angle, x, y
      else:
            print "ERROR Wrong case: ", RigShape
            sys.exit()

      coords.append((x, y))


  elif RigShape=="square" and FlagSamplingMethod=="Square_SideSampling":

    D=4*(2*radius) #the length of the square
    d=D/nPins

    x=0
    y=0


  else:
    print "ERROR Wrong case: ", RigShape
    sys.exit() 
      
  #print coords
  #print y0, " ", x0
  #cv2.waitKey(0)
      
  return coords

def Fn_GetLinePixels_ForDrawing(coord0, coord1):

    # global FlagLineType #load
#     FlagLineType_backup=FlagLineType
#     FlagLineType='bezier'
#     xLine, yLine = Fn_GetLinePixels(pin0, pin1)
#     
#     FlagLineType=FlagLineType_backup
#     return (xLine,yLine)

     #if FlagLineType=='bezier': # cubic or quadratic?
        # Generate third point to introduce line variation (bezier control point)
        coordmiddle_x = np.random.uniform(-variation, variation) + (coord0[0] + coord1[0]) / 2
        coordmiddle_y = np.random.uniform(-variation, variation) + (coord0[1] + coord1[1]) / 2
        coordmiddle=(coordmiddle_x,coordmiddle_y)
        
        # Draw string as bezier curve
        return Fn_GetBezierCoords(coord0,coordmiddle,coordmiddle,coord1)
    

def Fn_CompareLinePixels():
    for ind1 in range(NbPins):
       for ind2 in range(ind1+1,NbPins):
    
        # string and hash table
        PairID=Fn_PinPairID(ind1,ind2) 
        coords = LUP_LinePixels[PairID]
        
        nb=-1
        for line in open("/Users/jcbazin/Downloads/WORK/KAIST offer/proposal/code/knitter-master/knitter/allcoords_" + str(ind1) + "_" + str(ind2) + ".txt", "r"):
            print line
            nb=nb+1
            if nb>=1:
                values = line.split(" ")
                x=int(values[0])
                y=int(values[1])
                
                x2=coords[nb-1][0]
                y2=coords[nb-1][1]
                
                
                print "x:", x, " y:", y, " x2:", x2, " y2:", y2
                
                if not (x==x2 and y==y2):
                   print "ERROR"
                   sys.exit()
        
        if not (nb==coords.shape[0]):
            print "ERROR SIZE"
            print nb, ' ', coords.shape[0]
            sys.exit()
        
        #sys.exit()

    #sys.exit()
    
# Compute a line mask
def Fn_GetLinePixels(ind1, ind2):
    if FlagLineType=='straight':
    
        # string and hash table
        PairID=Fn_PinPairID(ind1,ind2) 
        return LUP_LinePixels[PairID]
            
        
    # if FlagLineType=='straight':
#         
#         
#         if FlagMethod_PixelsOnLine=='linsampling':
#             length = int(np.hypot(pin1[0] - pin0[0], pin1[1] - pin0[1]))
# 
#             x = np.linspace(pin0[0], pin1[0], length)
#             y = np.linspace(pin0[1], pin1[1], length)
#             
#             x=x.astype(np.int)-1
#             y=y.astype(np.int)-1
#             
#             
#         elif FlagMethod_PixelsOnLine=='BLA': # Brensenham's Line Algorithm.
#         # https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
#             dx=abs(pin1[0] - pin0[0])
#             dy=-abs(pin1[1] - pin0[1])
#             if pin0[0] < pin1[0]:  # a.x < b.x ? 1 : -1;
#                 sx=1
#             else:
#                 sx=-1    
#             if pin0[1] < pin1[1]: # sy = a.y < b.y ? 1 : -1;
#                 sy=1
#             else:
#                 sy=-1
#             e=dx+dy
#             x = []
#             y = []
#             p=[pin0[0],pin0[1]] # starting point
#             while (1):
#                 #points.append(p)
#                 #x.append(p[0]-1)
#                 #y.append(p[1]-1)
#                 x.append(p[0])
#                 y.append(p[1])
#                 if p[0] == pin1[0] and p[1] == pin1[1]: # until we reach the end point
#                    break;
#                 e2 = 2 * e;
#                 if e2 > dy:
#                    e += dy;
#                    p[0] += sx;
#                
#                 if e2 < dx:
#                    e += dx;
#                    p[1] += sy;
#             x=np.asarray(x)
#             y=np.asarray(y)
#         else:
#             print "ERROR: Wrong case"
#             sys.exit()
#         
#         #return (x.astype(np.int)-1, y.astype(np.int)-1)
#         #return (x,y)
#         
#         return np.column_stack((x, y))

        
    
    # if FlagLineType=='straight':
#         if FlagMethod_PixelsOnLine=='linsampling':
#             length = int(np.hypot(pin1[0] - pin0[0], pin1[1] - pin0[1]))
# 
#             x = np.linspace(pin0[0], pin1[0], length)
#             y = np.linspace(pin0[1], pin1[1], length)
#             
#             x=x.astype(np.int)-1
#             y=y.astype(np.int)-1
#             
#             
#         elif FlagMethod_PixelsOnLine=='BLA': # Brensenham's Line Algorithm.
#         # https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
#             dx=abs(pin1[0] - pin0[0])
#             dy=-abs(pin1[1] - pin0[1])
#             if pin0[0] < pin1[0]:  # a.x < b.x ? 1 : -1;
#                 sx=1
#             else:
#                 sx=-1    
#             if pin0[1] < pin1[1]: # sy = a.y < b.y ? 1 : -1;
#                 sy=1
#             else:
#                 sy=-1
#             e=dx+dy
#             x = []
#             y = []
#             p=[pin0[0],pin0[1]] # starting point
#             while (1):
#                 #points.append(p)
#                 #x.append(p[0]-1)
#                 #y.append(p[1]-1)
#                 x.append(p[0])
#                 y.append(p[1])
#                 if p[0] == pin1[0] and p[1] == pin1[1]: # until we reach the end point
#                    break;
#                 e2 = 2 * e;
#                 if e2 > dy:
#                    e += dy;
#                    p[0] += sx;
#                
#                 if e2 < dx:
#                    e += dx;
#                    p[1] += sy;
#             x=np.asarray(x)
#             y=np.asarray(y)
#         else:
#             print "ERROR: Wrong case"
#             sys.exit()
#         
#         #return (x.astype(np.int)-1, y.astype(np.int)-1)
#         #return (x,y)
#         return np.column_stack((x, y))
    
    
    else:
       print "ERROR: Wrong case"
    sys.exit()
    
# http://incolumitas.com/2013/10/06/plotting-bezier-curves/
def Fn_GetBezierCoords(p1,p2,p3,p4):
    #t = 0
    #coords_x = []
    #coords_y = []
    #N=10000
    N = int(np.hypot(p1[0] - p4[0], p1[1] - p4[1]))*1.5
    #print N
    list_t=np.linspace(0,1,N)
    list_x=np.linspace(0,1,N)
    list_y=np.linspace(0,1,N)
    #while (t < 1):
    i=-1
    for t in list_t:
        x = cubic_bezier_sum(t, (p1[0], p2[0], p3[0], p4[0]))
        y = cubic_bezier_sum(t, (p1[1], p2[1], p3[1], p4[1]))
        x=round(x)
        y=round(y)
        #print x
        #print y
        #t += 0.001
        #coords.append((x, y))
        #coords_x.append(x)
        #coords_y.append(y)
        i=i+1
        list_x[i]=x
        list_y[i]=y
    #list_x=np.asarray(list_x)
    #list_y=np.asarray(list_y)
    #print "t:", type(list_x)         
    #return (coords_x.astype(np.int),coords_y.astype(np.int))
    #return (coords_x,coords_y)
    #return (list_x.astype(np.int)-1,list_y.astype(np.int)-1)
    return np.column_stack((list_x.astype(np.int)-1, list_y.astype(np.int)-1))
    
# http://incolumitas.com/2013/10/06/plotting-bezier-curves/
# Calculates the cubic Bezier polynomial for 
# the n+1=4 coordinates.
def cubic_bezier_sum(t, w):
        t2 = t * t
        t3 = t2 * t
        mt = 1-t
        mt2 = mt * mt
        mt3 = mt2 * mt
        return w[0]*mt3 + 3*w[1]*mt2*t + 3*w[2]*mt*t2 + w[3]*t3


# Image Pre-processing
def Fn_ImagePreProcessing(OrigImage,ImgRadius):

    # Crop image
    height, width = OrigImage.shape[0:2]
    minEdge= min(height, width)
    topEdge = int((height - minEdge)/2)
    leftEdge = int((width - minEdge)/2)
    imgCropped = OrigImage[topEdge:topEdge+minEdge, leftEdge:leftEdge+minEdge]
    cv2.imwrite('./cropped.png', imgCropped)

    # Convert to grayscale
    imgGray = cv2.cvtColor(imgCropped, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('./gray.png', imgGray)

    # Resize image
    imgSized = cv2.resize(imgGray, (2*ImgRadius + 1, 2*ImgRadius + 1)) 

    # Invert image
    #imgInverted = invertImage(imgSized)
    #cv2.imwrite('./inverted.png', imgInverted)
    imgInverted=imgSized

    # Mask image
    imgMasked = maskImage(imgInverted, ImgRadius)
    cv2.imwrite('./masked.png', imgMasked)
    
    ProcessedImage=imgMasked
    
    return ProcessedImage

#// Returns values a and b sorted in a string (e.g. a = 5 and b = 2 becomes 
#// "2-5"). This can be used as key in a map storing the lines between all
#// pins in a non-redundant manner.
def Fn_PinPairID(PinIndex1,PinIndex2):
    if PinIndex1<PinIndex2:
       ID= str(PinIndex1) + "-" + str(PinIndex2)
    else:
       ID= str(PinIndex2) + "-" + str(PinIndex1)
    #print "id1=", PinIndex1, " id2=", PinIndex2
    #print "ID=" + ID + "\n"
    return ID

def Fn_PlotFullConnectivity():

    print "Welcome to full connectivity"

    height= 2*ImgRadius + 1
    width = height
    
    # Define pin coordinates
    #PinCoords = Fn_CreatePinCoords(ImgRadius, NbPins)
    PinCoords = Fn_CreatePinCoords(ImgRadius, NbPins,0) # -pi/2 like Christian
    
    # image result is rendered to
    imgResult = 255 * np.ones((height, width))

    # Loop over all pins
    for PinIndex1 in range(1, NbPins):
        PinCoord1 = PinCoords[PinIndex1]
        print "PinCoord1: " , "x=" , PinCoord1[0] , "y=" , PinCoord1[1]

        # Loop over all pins
        #for PinIndex2 in range(1, NbPins):
        #    if PinIndex1==PinIndex2:
        #       continue
        for PinIndex2 in range(PinIndex1+1, NbPins):
                              
            PinCoord2 = PinCoords[PinIndex2]

            xyLine = Fn_GetLinePixels_ForDrawing(PinCoord1, PinCoord2)

            # Plot the line
            imgResult[xyLine[:,1], xyLine[:,0]] = 0
            #cv2.imshow('image', imgResult)
    
    cv2.imshow('image', imgResult)
    cv2.imwrite('./fullconnect.png', imgResult)
    cv2.waitKey(1)
    cv2.waitKey(0)
    
def Fn_CheckMinDistConsecPins(PrevPinIndex,NextPinIndex,myMinDistConsecPins):
    #// Prevent two consecutive pins with less than minimal distance
    diff = abs(PrevPinIndex - NextPinIndex)
    diff = min(diff,NbPins-diff)
    thresh = myMinDistConsecPins # np.random.uniform(myMinDistConsecPins * 2/3, myMinDistConsecPins * 4/3)
    #if (diff < dist or diff > NbPins - dist):
    if diff < thresh:
       return 0
    else:
       return 1

def Fn_CheckPassingOutCenter(PrevPinIndex,NextPinIndex,myThreshCenterAngle):
    #// Prevent two consecutive pins with more than maximal distance: it is used to avoid the thread to pass near the center
    # returns 1 if not passing (success), returns 0 if passing near the center (failure)
    DeltaTheta=2*pi/NbPins*abs(PrevPinIndex-NextPinIndex)#the angle between the two pins
    diff=abs(pi-DeltaTheta)#between the opposite pin and the next pin
    #print diff, myThreshCenterAngle
    #if (diff < dist or diff > NbPins - dist):
    if diff < myThreshCenterAngle:  
       return 0
    else:
       return 1
    
                 
def Fn_DrawPins(MyImage,PinCoords):
    for k in range(len(PinCoords)):
       #print "x:",PinCoords[k][0]," y:",PinCoords[k][1]
       cv2.circle(MyImage, (PinCoords[k][0],PinCoords[k][1]), 1, 0, -1) #x,y
    return MyImage
    
def Fn_ReadPinCoordsFile():
    coords = []      
    for line in open("pincoords.txt", "r"):
       values = line.split(" ")
       x=int(values[0])
       y=int(values[1])
       coords.append((x, y))
    return coords

def Fn_ReadResultFile():
    ListPinIndex=[]
    for line in open("instruction.txt", "r"):
       values = line.split(":")
       ListPinIndex.append(int(values[1]))
    return ListPinIndex

def Fn_PreComputeLinePixels(PinCoords):
    #LUP_LinePixels={}
    for ind1 in range(NbPins):
        coord1=PinCoords[ind1]
        for ind2 in range(ind1,NbPins):
            coord2=PinCoords[ind2]
    
            #xLine, yLine = Fn_GetLinePixels(ind1, ind2)
    
            
            if FlagLineType=='straight':
        
        
                  if FlagMethod_PixelsOnLine=='linsampling':
                      length = int(np.hypot(coord2[0] - coord1[0], coord2[1] - coord1[1]))
                      
                      x = np.linspace(coord1[0], coord2[0], length)
                      y = np.linspace(coord1[1], coord2[1], length)
                      
                      x=x.astype(np.int)-1
                      y=y.astype(np.int)-1
                      
                      
                  elif FlagMethod_PixelsOnLine=='BLA': # Brensenham's Line Algorithm.
                  # https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
                      dx=abs(coord2[0] - coord1[0])
                      dy=-abs(coord2[1] - coord1[1])
                      if coord1[0] < coord2[0]:  # a.x < b.x ? 1 : -1;
                          sx=1
                      else:
                          sx=-1    
                      if coord1[1] < coord2[1]: # sy = a.y < b.y ? 1 : -1;
                          sy=1
                      else:
                          sy=-1
                      e=dx+dy
                      x = []
                      y = []
                      p=[coord1[0],coord1[1]] # starting point
                      while (1):
                          #points.append(p)
                          #x.append(p[0]-1)
                          #y.append(p[1]-1)
                          x.append(p[0])
                          y.append(p[1])
                          if p[0] == coord2[0] and p[1] == coord2[1]: # until we reach the end point
                             break;
                          e2 = 2 * e;
                          if e2 > dy:
                             e += dy;
                             p[0] += sx;
                         
                          if e2 < dx:
                             e += dx;
                             p[1] += sy;
                      x=np.asarray(x)
                      y=np.asarray(y)
                  else:
                      print "ERROR: Wrong case"
                      sys.exit()
                      
                      
                  
            # string and hash table
            PairID=Fn_PinPairID(ind1,ind2) 
            LUP_LinePixels[PairID]=np.column_stack((x, y)) # (xLine,yLine)
            
        
        #return (x.astype(np.int)-1, y.astype(np.int)-1)
        #return (x,y)
        
    return 

def Fn_DrawSelectedStrings(SelectedLines,height,width,NbCircles):
  # Info: SelectedLines contains (prevind,nextind)

  N=len(SelectedLines)
  print "nlines:", N
  #NbCircles=1
  kth_circle=0


  FlagNewImage=1 # initialize

  for i in range(N):

    if FlagNewImage==1:
      kth_circle+=1
      imgResult = 255 * np.ones((height, width), np.uint8)
      FlagNewImage=0


    PrevPinIndex=SelectedLines[i][0]
    NextPinIndex=SelectedLines[i][1]
    #print PrevPinIndex, ' ', NextPinIndex

    PrevPinCoord = PinCoords[PrevPinIndex]
    NextPinCoord = PinCoords[NextPinIndex]
    
    # plot results
    xyLine = Fn_GetLinePixels_ForDrawing(PrevPinCoord, NextPinCoord)
    #print type(xyLine)
    #imgResult[yLine, xLine] = LineOpacity*LineColor/255.0
    #imgResult[yLine, xLine] = (1-LineOpacity)*imgResult[yLine, xLine] + LineOpacity*LineColor/255.0
    for k in range(xyLine.shape[0]):
        #print "val:", imgResult[yLine[k], xLine[k]], " val2:", LineOpacity*LineColor
        #imgResult[xyLine[k][1], xyLine[k][0]] = (1-LineOpacity)*imgResult[xyLine[k][1], xyLine[k][0]] + LineOpacity*LineColor #/255.0
        val = round((1-LineOpacity)*imgResult[xyLine[k][1], xyLine[k][0]] + LineOpacity*LineColor) #/255.0
        if val>255:
           val=255
        imgResult[xyLine[k][1], xyLine[k][0]]=val
    
    #print round(N/NbCircles) 
    if i==N-1 or (NbCircles>1 and i>0 and i%round(N/NbCircles)==0): # i==round(N/NbCircles)
      print "in:", i
      FlagNewImage=1
      cv2.imwrite('./threaded_part-' + str(kth_circle) + '_outof-' + str(NbCircles) + '.png', imgResult)

        
#def XXX(): #
if __name__=="__main__":
   
    print "Welcome to main"

    
    # Load input image
    InputImage = FnLoadImage(ImgPath)
    
    # Preprocess the image (crop, resize, grayscale, invert colors, etc)
    imgMasked = Fn_ImagePreProcessing(InputImage,ImgRadius)
    print "Image preprocessed"
    
    #imgMasked = cv2.imread('img_croped.png')
    #imgMasked = imgMasked[:,:,0] # just one channel
    OrigImage=imgMasked;
    cv2.imshow('image', imgMasked/255.0)
    #cv2.waitKey(0)

    
    # Define pin coordinates
    PinCoords = Fn_CreatePinCoords(ImgRadius, NbPins)
    #PinCoords=Fn_ReadPinCoordsFile()

    height, width = imgMasked.shape[0:2]
    print "height:", height, " width:", width
    
    Fn_PreComputeLinePixels(PinCoords)
    
    #Fn_CompareLinePixels()
    ListPinIndex_GT=Fn_ReadResultFile()

    
    # Initialize variables
    lines = [] 
    lines_MultiCircle = np.empty(NbMultiCircles, dtype=np.object) #create array
    lines_MultiCircle[:]=[[] for _ in xrange(NbMultiCircles)] # [],[],[] # initialize. mandatory
    ListPairs=[] # the list of selected pin pairs
    previousPins = []
    PrevPinIndex = InitPinIndex
    lineMask = np.zeros((height, width))
    ListErrEvolution=[]
    
    ListPrevIndex_MultiCircles=[InitPinIndex] * NbMultiCircles # i.e. repeat: InitPinIndex*np.ones((height, width))
    kth_MultiCircle=-1

    # image result is rendered to
    #imgResult = 255 * np.ones((height, width))
    imgResult = 255 * np.ones((height, width), np.uint8)
    imgResult_strings=imgResult
    # Note: imwrite always expects [0,255], whereas imshow expects [0,1] for floating point and [0,255] for unsigned chars.https://stackoverflow.com/questions/22488872/cv2-imshow-and-cv2-imwrite
    cv2.namedWindow('image', cv2.WINDOW_NORMAL) # resizable window
    #cv2.resizeWindow('image', 600,600)
    #cv2.imshow('image', imgResult/255.0)
    
    imgResult=Fn_DrawPins(imgResult,PinCoords)
    cv2.imshow('image', imgResult/255.0)
    #cv2.waitKey(0)
    #sys.exit()

    imgResult_MultiCircle=np.tile(imgResult[:, :, None],(1,1,NbMultiCircles)) # https://stackoverflow.com/questions/26166471/3d-tiling-of-a-numpy-array
    print imgResult_MultiCircle.shape

    # ListPinIndex=Fn_ReadResultFile()
#     print "nb lines:", len(ListPinIndex)
#     for i in range(len(ListPinIndex)-1):
#         PrevPinIndex=ListPinIndex[i]
#         NextPinIndex=ListPinIndex[i+1]
#         PrevPinCoord = PinCoords[PrevPinIndex]
#         NextPinCoord = PinCoords[NextPinIndex]
#         # plot results
#         xLine, yLine = Fn_GetLinePixels_ForDrawing(PrevPinCoord, NextPinCoord)
#         #imgResult[yLine, xLine] = LineOpacity*LineColor/255.0
#         #imgResult[yLine, xLine] = (1-LineOpacity)*imgResult[yLine, xLine] + LineOpacity*LineColor/255.0
#         for k in range(xLine.size):
#             #print "val:", imgResult[yLine[k], xLine[k]], " val2:", LineOpacity*LineColor
#             imgResult[yLine[k], xLine[k]] = min((1-LineOpacity)*imgResult[yLine[k], xLine[k]] + LineOpacity*LineColor,255.0) #/255.0
#             #imgResult[yLine[k], xLine[k]] = (1-LineOpacity)*255.0 + LineOpacity*LineColor
#             #print "val out:", imgResult[yLine[k], xLine[k]]
#         
#         #if 1:# 
#     
#     #kernel = np.ones((5,5),np.float32)/25
#     #imgResult = cv2.filter2D(imgResult,-1,kernel)
#     imgResult = cv2.blur(imgResult,(2,2))
#     
#     cv2.imshow('image', imgResult/255.0)
#     cv2.waitKey(0)
#     sys.exit()
    
    # Loop over lines until stopping criteria is reached
    for line in range(NbLines):

        kth_MultiCircle=kth_MultiCircle+1
        if kth_MultiCircle>=NbMultiCircles:
          kth_MultiCircle=0
        PrevPinIndex=ListPrevIndex_MultiCircles[kth_MultiCircle]

        BestLineScore = 0
        BestPinIndex = -1
        PrevPinCoord = PinCoords[PrevPinIndex]

        

        #DiffMat=imgMasked.astype(int)-imgResult_strings.astype(int) # i.e. signe diff of original image - the result/drawn image 
        DiffMat=(255.0-OrigImage.astype(int))-(255.0-imgResult_strings.astype(int)) # i.e. signe diff of original image - the result/drawn image 
        #print type(DiffMat)
        myerr=np.sum(np.absolute(DiffMat))
        #print myerr
        ListErrEvolution.append(myerr) #signed error

        # Loop over possible lines/pins
        for index in range(NbPins):
            #pin = (oldPin + index) % nPins
            NextPinIndex=index
            if NextPinIndex==PrevPinIndex:
               continue
            if Fn_CheckMinDistConsecPins(PrevPinIndex,NextPinIndex,MinDistConsecPins)==0:
               #print "PrevPinIndex:", PrevPinIndex, 'NextPinIndex:', NextPinIndex
               continue
            
            if line % 2 == 0: # i.e. # starting at 0 (like range()), even number is ok
               #good. nothing
               blatemp=0
            else: # i.e. odd number-th of connection
                if Fn_CheckPassingOutCenter(PrevPinIndex,NextPinIndex,myThreshCenterAngle)==0:
                  continue;


            NextPinCoord = PinCoords[NextPinIndex]

            xyLine = Fn_GetLinePixels(PrevPinIndex, NextPinIndex)
            
            # print "line:", line
            #print "size:", xyLine.shape, "rows:", xyLine.shape[0]
#             if index==139:
#                 print "PrevPinIndex:", PrevPinIndex, " NextPinIndex:", NextPinIndex
#                 print "PrevPinCoord:", PrevPinCoord, " NextPinCoord:", NextPinCoord
#                 #print xLine, yLine
#                 for t in range(xLine.size):
#                    print "x:", xLine[t], " y:", yLine[t]
#                 print "nbpoints:", xLine.size
#             #sys.exit()
#                 #raw_input("Press Enter to continue...")
             
            #print "PrevPinIndex:", PrevPinIndex, 'NextPinIndex:', NextPinIndex
               
            # Fitness function
            if LineScoreDef=='sum_darkness' or LineScoreDef=='sum_darkness_normalized':
                #LineScore = np.sum(imgMasked[yLine, xLine])
                #print "LineScore:", LineScore
                
                LineScore=0.0
                for t in range(xyLine.shape[0]):
                  #print "x:", xLine[t], " y:", yLine[t], " score:", imgMasked[yLine[t], xLine[t]], " score local:", 255-imgMasked[yLine[t], xLine[t]]
                  #if (PrevPinIndex==16 and NextPinIndex==155) or (PrevPinIndex==16 and NextPinIndex==136):
                  #    #1
                  #    print "x:", xyLine[t][0], " y:", xyLine[t][1], " score:", imgMasked[xyLine[t][1], xyLine[t]][0], " score local:", 255-imgMasked[xyLine[t][1], xyLine[t][0]]
                  #    raw_input("score Press Enter to continue...")
                  
                  # sum of darkness (in reduced image)
                  # LineScore+=255-imgMasked[xyLine[t][1], xyLine[t][0]]
                  #LineScore+=math.pow((255.0-imgMasked[xyLine[t][1], xyLine[t][0]])/255.0,2) # with mapping
                  #print imgMasked[xyLine[t][1], xyLine[t]][0], " score local:", (255.0-imgMasked[xyLine[t][1], xyLine[t][0]])/255.0, "val:", math.pow((255.0-imgMasked[xyLine[t][1], xyLine[t][0]])/255.0,2), " score:", LineScore
                  #raw_input("score Press Enter to continue...")

                  # signed sum of diff
                  LineScore+=DiffMat[xyLine[t][1], xyLine[t][0]]
                
                # if (PrevPinIndex==16 and NextPinIndex==155) or (PrevPinIndex==16 and NextPinIndex==136):  
                #    print "PrevPinIndex:", PrevPinIndex, 'NextPinIndex:', NextPinIndex
                #    print "nb:", xyLine.shape[0]
                #    print "LineScore:", LineScore
                
               
            else:
                print "ERROR: Wrong case"
                sys.exit()
                
            if LineScoreDef=='sum_darkness_normalized': 
                #print "length:", xLine.size
                #print "LineScore:", LineScore
                LineScore = float(LineScore) / xyLine.shape[0]
                #print "LineScore (normalized):", LineScore
                #sys.exit()
                # if (PrevPinIndex==16 and NextPinIndex==155) or (PrevPinIndex==16 and NextPinIndex==136):
                #     print "PrevPinIndex:", PrevPinIndex, 'NextPinIndex:', NextPinIndex
                #     print "LineScore (normalized2):", LineScore
                #     #raw_input("Press Enter to continue...")
            #sys.exit()
            
            PairID=Fn_PinPairID(PrevPinIndex,NextPinIndex)

            if (LineScore > BestLineScore) and not(NextPinIndex in previousPins) and not(PairID in ListPairs):
                BestLineScore = LineScore
                BestPinIndex = NextPinIndex

        if BestPinIndex == -1:
          print "break: no best pin"
          break


        # Update previous pins
        if minLoop !=-1:
          if len(previousPins) >= minLoop:
              previousPins.pop(0)
          previousPins.append(BestPinIndex)
        #print '\npreviousPins', previousPins

        BestPinCoord=PinCoords[BestPinIndex]
        
        #print "PrevPinIndex:", PrevPinIndex, 'BestPinIndex:', BestPinIndex
        #raw_input("Press Enter to continue...")
               

        # Subtract new line from image
        #lineMask = lineMask * 0
        #cv2.line(lineMask, PrevPinCoord, BestPinCoord, LineFade, LineWidth)
        #imgMasked = np.subtract(imgMasked, lineMask)
        #
        xyLine = Fn_GetLinePixels(PrevPinIndex, BestPinIndex)
        #print type(xyLine)
        #imgMasked[xyLine[:,1], xyLine[:,0]] += LineFade
        for k in range(xyLine.shape[0]):
             val=imgMasked[xyLine[k][1], xyLine[k][0]]
             oldval=val
             #print type(val)
             #print val
             val=val+LineFade
             #print val
             if val>255:
                val=255
                #print val
             #imgMasked[xyLine[k][1], xyLine[k][0]] += LineFade
             imgMasked[xyLine[k][1], xyLine[k][0]] = val
             #print "x:", xyLine[k][0],"y:", xyLine[k][1], "val:", imgMasked[xyLine[k][1], xyLine[k][0]], "before:", oldval
             #raw_input("Press Enter to continue...")
        #
        #imgMasked[imgMasked < 0] = 0 # truncate just in case
        imgMasked[imgMasked > 255] = 255 # truncate just in case


#         imfilename="/Users/jcbazin/Downloads/WORK/KAIST offer/proposal/code/knitter-master/knitter/img_reduced_" + str(line)+ ".png"
#         print imfilename
#         CheckReducedImage = cv2.imread(imfilename)
#         CheckReducedImage=CheckReducedImage[:,:,0]
#         err = np.sum((CheckReducedImage.astype("float") - imgMasked.astype("float")))
#         if not (err==0):
#            print "line:", line, " err:", err, 
#            print "ERROR: not same"
#            cv2.imshow('image', imgMasked/255.0)
#            cv2.imshow('CheckReducedImage from java', CheckReducedImage/255.0)
#            cv2.waitKey(0)
# 
#            sys.exit()
           
        # if not (BestPinIndex==ListPinIndex_GT[line]):
        #   print line, BestPinIndex, ListPinIndex_GT[line]
        #   print "ERROR: not same pin"
        #   sys.exit()

        # Save line to results
        lines.append((PrevPinIndex, BestPinIndex))
        #print kth_MultiCircle
        #print lines_MultiCircle[kth_MultiCircle]
        #print type(lines_MultiCircle[kth_MultiCircle])
        #print type(lines_MultiCircle)
        lines_MultiCircle[kth_MultiCircle].append((PrevPinIndex, BestPinIndex))
        
        PairID=Fn_PinPairID(PrevPinIndex,BestPinIndex)
        ListPairs.append(PairID)

        # plot results
        xyLine = Fn_GetLinePixels_ForDrawing(PrevPinCoord, BestPinCoord)
        #print type(xyLine)
        #imgResult[yLine, xLine] = LineOpacity*LineColor/255.0
        #imgResult[yLine, xLine] = (1-LineOpacity)*imgResult[yLine, xLine] + LineOpacity*LineColor/255.0
        for k in range(xyLine.shape[0]):
            #print "val:", imgResult[yLine[k], xLine[k]], " val2:", LineOpacity*LineColor
            #imgResult[xyLine[k][1], xyLine[k][0]] = (1-LineOpacity)*imgResult[xyLine[k][1], xyLine[k][0]] + LineOpacity*LineColor #/255.0
            val = round((1-LineOpacity)*imgResult[xyLine[k][1], xyLine[k][0]] + LineOpacity*LineColor) #/255.0
            if val>255:
               val=255
            imgResult[xyLine[k][1], xyLine[k][0]]=val
            imgResult_strings[xyLine[k][1], xyLine[k][0]]=val
            #print "val out:", imgResult[yLine[k], xLine[k]]


            val = round((1-LineOpacity)*imgResult_MultiCircle[xyLine[k][1], xyLine[k][0],kth_MultiCircle] + LineOpacity*LineColor) #/255.0
            if val>255:
               val=255
            imgResult_MultiCircle[xyLine[k][1], xyLine[k][0],kth_MultiCircle] =val
            
        
        #if 1:# 
        if line%20 ==0:
        
           imgResult_blured = cv2.blur(imgResult,(3,3))
    
           cv2.imshow('image', imgResult/255.0)
           cv2.imshow('image_blured', imgResult_blured/255.0)
           #cv2.imshow('target', imgMasked/255.0)

           for i in range(NbMultiCircles):
            cv2.imshow('image' + str(i), imgResult_MultiCircle[:,:,i]/255.0)

           cv2.waitKey(1)

        # Break if no lines possible
        #if BestPinIndex == PrevPinIndex:
        #    print "break: best pin is the prev pin (happens??)"
        #    break

        # Prepare for next loop
        PrevPinIndex = BestPinIndex
        ListPrevIndex_MultiCircles[kth_MultiCircle]=PrevPinIndex

        # Print progress
        if line%20==1:
          sys.stdout.write("\b\b")
          sys.stdout.write("\r")
          sys.stdout.write("[+] Computing line " + str(line + 1) + " of " + str(NbLines) + " total\n")
          sys.stdout.flush()

    print "\n[+] Image threaded"
    
    for l in lines:
        print l[0], " ", l[1]
   

    imgResult_blured = cv2.blur(imgResult,(2,2))
    cv2.imshow('image', imgResult/255.0)
    cv2.imshow('image_blured', imgResult_blured/255.0)
        
    # Wait for user and save before exit
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite('./threaded.png', imgResult)
    cv2.imwrite('./threaded_blured.png', imgResult_blured)
    for i in range(NbMultiCircles):
        cv2.imwrite('./threaded_circ-' + str(i) +'.png', imgResult_MultiCircle[:,:,i])
    imgResult_Combined=np.mean(imgResult_MultiCircle, 2)
    cv2.imwrite('./threaded_circ-combined.png', imgResult_Combined)


    svg_output = open('threaded.svg','wb')
    header="""<?xml version="1.0" standalone="no"?>
    <svg width="%i" height="%i" version="1.1" xmlns="http://www.w3.org/2000/svg">
    """ % (width, height)
    footer="</svg>"
    svg_output.write(header)
    pather = lambda d : '<path d="%s" stroke="black" stroke-width="0.5" fill="none" />\n' % d
    pathstrings=[]
    pathstrings.append("M" + "%i %i" % PinCoords[lines[0][0]] + " ")
    for l in lines:
        nn = PinCoords[l[1]]
        pathstrings.append("L" + "%i %i" % nn + " ")
    pathstrings.append("Z")
    d = "".join(pathstrings)
    svg_output.write(pather(d))
    svg_output.write(footer)
    svg_output.close()

    csv_output = open('threaded.csv','wb')
    csv_output.write("x1,y1,x2,y2,index1,index2\n")
    csver = lambda c1,c2,i1,i2 : "%i,%i" % c1 + "," + "%i,%i" % c2 + "," + "%i" % i1 + "," + "%i" % i2 + "\n"
    for l in lines:
        csv_output.write(csver(PinCoords[l[0]],PinCoords[l[1]],l[0],l[1]))
    csv_output.close()

    f = open( 'ErrEvolution.txt', 'w' )
    for e in ListErrEvolution:
      f.write("%f\n" % e)
    f.close()
    #
    #plt.plot(ListErrEvolution)
    #plt.ylabel('some numbers')
    #plt.show()

    

    Fn_DrawSelectedStrings(lines,height,width,NbCircles=1)
    Fn_DrawSelectedStrings(lines,height,width,NbCircles=3)

    MyImage0=imgResult_MultiCircle[:,:,0]
    MyImage1=imgResult_MultiCircle[:,:,1] # will be rotated
    Nrotate=100
    alpha = np.linspace(-90, 0, Nrotate)
    i=0
    for angle in alpha: 
      
      M = cv2.getRotationMatrix2D((width/2,height/2),angle,1)
#      flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255, 255))
      MyImage1_R = cv2.warpAffine(MyImage1,M,(width,height), borderMode=cv2.BORDER_CONSTANT, borderValue=255) # rotate and set he background color
      # average or sum
      MyImage_Combined=(MyImage0.astype(np.int)+MyImage1_R.astype(np.int))/2
      #MyImage_Combined[MyImage_Combined > 255]=255

      #I=np.concatenate((MyImage0, MyImage1_R, MyImage_Combined), axis=1)
      I=np.concatenate((MyImage0[1:,1:], MyImage1_R[1:,1:], MyImage_Combined[1:,1:]), axis=1)
      
      i=i+1
      cv2.imwrite('./threaded_anim_' + '{0:03d}'.format(i) +'.png', I)
      # https://wiki.libav.org/Snippets/avconv
      # https://askubuntu.com/questions/509826/how-do-i-fix-the-duration-of-frames-when-using-avconv
      # avconv -f image2 -i threaded_anim_%d.png -r 76 -s 800x600 foo.avi
      # avconv -f image2 -i threaded_anim_%03d.png -r 1 -c:v h264 -crf 1 foo.avi
      # avconv -f image2 -r 3 -i threaded_anim_%03d.png -r 24 -c:v h264 -crf 1 foo.avi
      #
      # avconv -loop 1 -i threaded_anim_100.png -vcodec libx264 -tune stillimage -t 10 temp.avi
      #
      # avconv -i concat:"foo.avi|temp.avi" -c copy out.avi  




