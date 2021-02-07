import pyautogui
import time
import cv2
import math
import numpy as np
import dlib

def draw_rectangle(rectangles, img): #draw rectangle to the image with tl and br corner
    if len(rectangles) > 1 :
        print("more than one rectangles")
        return img
    else:
        tl_x = rectangles[0].tl_corner().x
        tl_y = rectangles[0].tl_corner().y
        br_x = rectangles[0].br_corner().x
        br_y = rectangles[0].br_corner().y
        img = cv2.rectangle(img,(tl_x,tl_y),(br_x,br_y),(0,0,255),3)
        return img
def draw_landmarks(points, img): #draw landmarks for human faces
    for i in range(0,67):
        img = cv2.circle(img, (points.part(i).x, points.part(i).y) , 2 , (0,255,0), -1)
    return img

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
normal = cv2.imread("normal.png")
shocked = cv2.imread("shocked.png")
normal_g = cv2.cvtColor( normal , cv2.COLOR_BGR2GRAY)
shocked_g = cv2.cvtColor( shocked , cv2.COLOR_BGR2GRAY)
####
rectangles = detector(normal_g)
normal = draw_rectangle(rectangles,normal)
points_normal = predictor( normal_g, rectangles[0])
normal = draw_landmarks(points_normal,normal)
#####
rectangles = detector(shocked_g)
shocked = draw_rectangle(rectangles,shocked)
points_shocked = predictor( shocked_g, rectangles[0] )
shocked = draw_landmarks(points_shocked,shocked)
######
cv2.imwrite('normal_d.png',normal)
cv2.imwrite('shocked_d.png',shocked)


#calculate the length of facial shapes like eyebrows, nose, jawline
def calc_length(points,start,end):
    length = 0
    for i in range(start, end):
        p1 = [ points.part(i).x , points.part(i).y ]
        p2 = [ points.part(i+1).x , points.part(i+1).y ]
        distance = math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )
        length = length + distance
    return int(length)
#face class for comparing facial features
class Face:
  def __init__(self, points):
    self.left_eyebrow = calc_length(points,17,21)
    self.right_eyebrow = calc_length(points,22,26)
    self.nose_bridge = calc_length(points, 27,30)
    self.jawline = calc_length(points,0,16)
    self.lower_nose = calc_length(points,31,35)
    
f_normal = Face(points_normal)
f_shocked = Face(points_shocked)
dic_normal = {}
for attr,value in vars(f_normal).items():
    dic_normal[attr] = value
dic_shocked = {}
for attr,value in vars(f_shocked).items():
    dic_shocked[attr] = value
#determine the face if it is shocked or normal      
def is_shocked(image):
    image = cv2.cvtColor( image , cv2.COLOR_BGR2GRAY)
    rectangles = detector( image )
    points = predictor( image , rectangles[0] )
    f_curr = Face(points)
    count_normal = 0
    count_shocked = 0
    for attr,value in vars(f_curr).items():
        n = dic_normal[attr]
        s = dic_shocked[attr]
        if ( abs(n-value) > abs(s-value) ):
            count_shocked = count_shocked + 1
        else:
            count_normal = count_normal +1
    if ( count_normal > count_shocked ):
        return False
    
    return True
    
#func get location
def get_dino(image):
    image = cv2.cvtColor( image , cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(image,127,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        (x_c,y_c),radius = cv2.minEnclosingCircle(c)
        x_c = int(x_c)
        y_c = int(y_c)
        if ( 22 < radius < 45 ) and ( 15 < image[y_c][ x_c] < 150 ):
            if ( image.shape[1]/4 < x_c < image.shape[1]*3/4 ):
                center = [x_c, y_c]
            return center
    #if dino in black grid apply threshold 35
    return None
#get ss
print("get ready")
time.sleep(5)
screenshot = pyautogui.screenshot()
screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
center = get_dino(screenshot) # the location of our char does not change
if center is not None:
    print(center)
    dino = cv2.circle(screenshot, (center[0],center[1]), 25, ( 255,0,0), 6)
    cv2.imwrite('dino.png',dino)
    control = True
else:
    print("cannot found dino")
    control = False

moves = ["right","up","down","left"]

def get_opposite(move):
    if ( move == "up"):
        return "down"
    elif ( move == "down"):
        return "up"
    elif ( move == "left"):
        return "right"
    else:
        return "left"

def try_move(move):
    ss = pyautogui.screenshot()
    ss = cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2BGR)
    ss2 = cv2.cvtColor( ss , cv2.COLOR_BGR2GRAY)
    
    #check border 
    if ( move == "up"):
        c_x = center[0] 
        c_y = center[1] - 140
        y = center[1] + 30
        x = center[0] + 30
        curr_color = int(ss2[y][x])
    elif ( move == "down"):
        c_x = center[0]
        c_y = center[1] + 140
        y = center[1]+30
        x = center[0]+30
        curr_color = int(ss2[y][x])
    elif ( move == "left"):
        c_x = center[0] - 140
        c_y = center[1]
        y = center[1]-30
        x = center[0]-30
        curr_color = int(ss2[y][x])
    else:
        c_x = center[0] + 140
        c_y = center[1]
        y = center[1]+30
        x = center[0]+30
        curr_color = int(ss2[y][x])
    
    if ( ss[c_y][c_x][0] == 114 ) and ( ss[c_y][c_x][1] == 111 ) and ( ss[c_y][c_x][2] == 255 ): #dont go out of map
        return False
    
    flag = True
    failed = False
    count = 0
    while( flag ):
        if ( move == "up"):
            pyautogui.keyDown('w')
            time.sleep(0.1)
            pyautogui.keyUp('w')
        elif ( move == "down"):
            pyautogui.keyDown('s')
            time.sleep(0.1)
            pyautogui.keyUp('s')
        elif ( move == "left"):
            pyautogui.keyDown('a')
            time.sleep(0.1)
            pyautogui.keyUp('a')
        else:
            pyautogui.keyDown('d')
            time.sleep(0.1)
            pyautogui.keyUp('d')
        count = count + 1
        ss = pyautogui.screenshot()
        ss = cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2BGR)
        ss2 = cv2.cvtColor( ss , cv2.COLOR_BGR2GRAY)
        color = int(ss2[y][x])
        if ( is_shocked(ss) ):
            time.sleep(0.2)
            flag = False
            failed = True
        elif ( color != curr_color):
            flag = False
            failed = False
    
    if ( failed ):
        move = get_opposite(move)
        while ( count  > 0 ):
            if ( move == "up"):
                pyautogui.keyDown('w')
                time.sleep(0.1)
                pyautogui.keyUp('w')
            elif ( move == "down"):
                pyautogui.keyDown('s')
                time.sleep(0.1)
                pyautogui.keyUp('s')
            elif ( move == "left"):
                pyautogui.keyDown('a')
                time.sleep(0.1)
                pyautogui.keyUp('a')
            else:
                pyautogui.keyDown('d')
                time.sleep(0.1)
                pyautogui.keyUp('d')
            count = count - 1
        time.sleep(0.4)
        return False
    else:
        time.sleep(0.4)
        if ( move == "up"):
            count = count - 2
        while ( count  > 0 ):
            if ( move == "up"):
                pyautogui.keyDown('w')
                time.sleep(0.07)
                pyautogui.keyUp('w')
            elif ( move == "down"):
                pyautogui.keyDown('s')
                time.sleep(0.16)
                pyautogui.keyUp('s')
            elif ( move == "left"):
                pyautogui.keyDown('a')
                time.sleep(0.17)
                pyautogui.keyUp('a')
            else:
                pyautogui.keyDown('d')
                time.sleep(0.14)
                pyautogui.keyUp('d')
            count = count - 1
        time.sleep(0.4)
        return True
        

control = True
path = []
lastmove = None

while (control):
    round_move = False
    for move in moves:
        if lastmove is not None:
            if (  move == get_opposite(lastmove) ):
                continue
            
        if ( try_move(move) ):
            lastmove = move
            path.append(move)
            round_move = True
            time.sleep(0.5)
            break
        time.sleep(1.50)
    #check there is no move except where we came from
    if ( not(round_move) ):
        go_back = get_opposite(lastmove) #go back 
        if ( try_move(go_back) ):
            back_list = []
            path.append( go_back )
            for m in moves:
                if ( m != lastmove ): #but dont go back again
                    back_list.append(m)
            time.sleep(0.5)
            for move in back_list:
                if ( try_move( move) ):
                    path.append(move)
                    lastmove = move
                    time.sleep(0.5)
                    break
                time.sleep(0.5)
    
    if ( len(path) > 13 ):
        ss = pyautogui.screenshot()
        ss = cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2BGR)
        c_x = center[0] + 125
        c_y = center[1]
        if ( ss[c_y][c_x][0] == 114 ) and ( ss[c_y][c_x][1] == 111 ) and ( ss[c_y][c_x][2] == 255 ): #end of map
            control = False
            break
    time.sleep(0.75)
#get face
#create map
#try move check face
#if edge crossed 
    #save where we came from
    #get new ss

#finish
print ( path )
pyautogui.alert(text='END OF THE MAP', title='PYTHON WON', button='OK')
print("done")