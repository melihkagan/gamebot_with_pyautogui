import pyautogui
import time
import cv2
import math
import numpy as np

def order_points(pts):
  # first entry in the list is the top-left,
  # the second entry is the top-right, the third is the
  # bottom-right, and the fourth is the bottom-left
  rect = np.zeros((4, 2), dtype = "float32")
  # the top-left point will have the smallest sum
  # the bottom-right point will have the largest sum
  s = pts.sum(axis = 1)
  rect[0] = pts[np.argmin(s)]
  rect[2] = pts[np.argmax(s)]
  # top-right point will have the smallest difference,
  # bottom-left will have the largest difference
  diff = np.diff(pts, axis = 1)
  rect[1] = pts[np.argmin(diff)]
  rect[3] = pts[np.argmax(diff)]
  # return the ordered coordinates
  return rect

#to calculate the area of faces on the 3D dice
def calc_area(box):
    p1 = box[0]
    p2 = box[1]
    p3 = box[2]
    distance1 = math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )
    distance2 = math.sqrt( ((p2[0]-p3[0])**2)+((p2[1]-p3[1])**2) )
    return ( distance1*distance2 )
#to be able to only select one face from one dice
def is_close_to(center,saved_centers):
    p1 = center
    if ( len(saved_centers) == 0):
        return False
    for c in saved_centers:
        p2 = c
        distance = math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )
        if ( distance < 200 ):
            return True
    return False

print("get ready")
time.sleep(5)
#i = 0
while( True ): #to stop loop trigger the pyautogui failsafe by moving mouse to the left corner
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    ss2 = screenshot.copy()
    imgray = cv2.cvtColor(screenshot,cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,127,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    num_of_dice = 0
    #max_dice = [0,0,0,0]
    max_dice_list = []
    saved_centers = []
    fail = 0
    for c in contours:
        x,y,w,h = cv2.boundingRect(c)
        arr = [[0,0],[0,h],[w,h],[w,0]]
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        (x_c,y_c),radius = cv2.minEnclosingCircle(c)
        center = [int(x_c),int(y_c)]
        if ( calc_area(box) > 20000) and (w<280) and (h<280):#try to find proper face of dice
            if ( not(is_close_to(center,saved_centers))):
                saved_centers.append(center)
                num_of_dice = num_of_dice + 1
                screenshot  = cv2.rectangle(screenshot,(x,y),(x+w,y+h),(0,255,0),2)
                #print(box)
                box = order_points(box)
                pts1 = np.float32(box)
                pts2 = np.float32(arr)
                #transfrom minarearect shape to the bounding rectangle shape
                M = cv2.getPerspectiveTransform(pts1,pts2)
                crop_img = cv2.warpPerspective(ss2,M,(w,h))
                
                #if( i < 5):
                    #cv2.imwrite('crop_'+str(i)+'_'+str(num_of_dice)+'.png', crop_img)
                
                crop_img = cv2.cvtColor(crop_img,cv2.COLOR_BGR2GRAY)
                crop_img = cv2.medianBlur(crop_img, 5)
                circles = cv2.HoughCircles(crop_img,cv2.HOUGH_GRADIENT,1,10,param1=50,param2=30,minRadius=4,maxRadius=30)
                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    num_of_circles = 0
                    for a in circles[0, :]:
                        num_of_circles = num_of_circles + 1
                    screenshot = cv2.putText(screenshot, str(num_of_circles), (x+w+20, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3, cv2.LINE_AA)
                    max_dice_list.append([num_of_circles,int(x_c + y_c)])
                else:
                    fail = fail + 1
    
    if ( fail == 0 ):
        #if( i < 5):
            #cv2.imwrite('rects'+str(i)+'.png', screenshot)
        #i= i + 1
        if ( len( max_dice_list) < 3 ):
            continue
        max_dice_list = np.array(max_dice_list)
        max_dice_list = max_dice_list[max_dice_list[:, 1].argsort()]
        #find position of the maximum dice
        idx = 0
        max_dice = 0
        k = 0
        for dice in max_dice_list:
            if( dice[0] > max_dice ):
                max_dice = dice[0]
                idx = k
            k = k + 1 
        #print(max_dice_list)
        time.sleep(1)
        if ( idx == 2 ):
            pyautogui.press('d')
        elif (  idx == 1 ):
            pyautogui.press('s')
        else:
            pyautogui.press('a')
        
        time.sleep(0.25)

print("done")