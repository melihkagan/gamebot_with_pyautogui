import pyautogui
import time
import cv2
import numpy as np

print("get ready")
time.sleep(5)
#i = 0
while( True ): #to stop loop trigger the pyautogui failsafe by moving mouse to the left corner
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    imgray = cv2.cvtColor(screenshot,cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,127,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    num_of_dice = 0
    max_dice = (0,0)
    for c in contours:
        x,y,w,h = cv2.boundingRect(c)
        if ( w > 95 ) and ( h > 95) and ( w<220 ) and ( h<220):# try to obtain face of a dice
            num_of_dice = num_of_dice + 1
            screenshot  = cv2.rectangle(screenshot,(x,y),(x+w,y+h),(0,255,0),2)
            crop_img = imgray[y:y+h, x:x+w]
            #if( i < 5):
                #cv2.imwrite('crop_'+str(i)+'_'+str(num_of_dice)+'.png', crop_img)
            
            crop_img = cv2.medianBlur(crop_img, 5)
            circles = cv2.HoughCircles(crop_img,cv2.HOUGH_GRADIENT,1,6,param1=50,param2=30,minRadius=2,maxRadius=30)
            circles = np.uint16(np.around(circles))
            num_of_circles = 0
            for a in circles[0, :]:
                num_of_circles = num_of_circles + 1
            screenshot = cv2.putText(screenshot, str(num_of_circles), (x+w+20, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3, cv2.LINE_AA)
            if( num_of_circles > max_dice[1] ):
                max_dice= (num_of_dice,num_of_circles)
            
        
    #if( i < 5):
        #cv2.imwrite('rects'+str(i)+'.png', screenshot)
    #i= i + 1
    
    if ( max_dice[0] == 1 ):
        pyautogui.press('d')
    elif (  max_dice[0] == 2 ):
        pyautogui.press('s')
    else:
        pyautogui.press('a')
    time.sleep(1)
    #time.sleep(2)

print("done")