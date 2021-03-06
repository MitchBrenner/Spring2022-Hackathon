import cv2
import mediapipe as mp
import numpy as np
import time
import random
import math

HAND_RADIUS = 30
GOAL_RADIUS = 50
GOAL_INSET = 10
DIFF_INC = 5

objects = []

speed = 5

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()

pTimeSpawn = time.time()
pTimeDiff = time.time()
pTimeCount = time.time()

goals = 0
spawnInterval = 2 # seconds
timeRemaining = 60 # seconds

while True:
    # get image
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # image shape
    h, w, c = img.shape

    bkgrd = np.zeros(img.shape)

    # goals
    g1 = (GOAL_INSET,int(h/2))
    cv2.circle(bkgrd, g1, GOAL_RADIUS, (255, 0, 0), cv2.FILLED, 2)
    g2 = (w - GOAL_INSET,int(h/2))
    cv2.circle(bkgrd, g2, GOAL_RADIUS, (255, 0, 0), cv2.FILLED, 2)

    # get hand locations
    handLocs = []
    results = hands.process(imgRGB)
    if results.multi_hand_landmarks:
        if(len(results.multi_hand_landmarks) == 2): # ensures there are two hands
            for handLms in results.multi_hand_landmarks:
                p1 = (int(handLms.landmark[0].x * w), int(handLms.landmark[0].y * h))
                p2 = (int(handLms.landmark[5].x * w), int(handLms.landmark[5].y * h))
                p3 = (int(handLms.landmark[17].x * w), int(handLms.landmark[17].y * h))
                
                cent = (int((p1[0] + p2[0] + p3[0])/3), int((p1[1] + p2[1] + p3[1])/3))
                handLocs.append(cent)
                cv2.circle(bkgrd, cent, HAND_RADIUS, (0, 255, 0), cv2.FILLED, 2)

    # handle individual object actions
    for obj in objects:
        obj[0] = (int(obj[0][0] + obj[1][0]*speed), int(obj[0][1] + obj[1][1]*speed))

        if(obj[0][0] > w or obj[0][0] < 0 or obj[0][1] > h or obj[0][1] < 0):
            objects.remove(obj)
            continue
    
        if(math.hypot(g1[0] - obj[0][0], g1[1] - obj[0][1]) < GOAL_RADIUS
           or math.hypot(g2[0] - obj[0][0], g2[1] - obj[0][1]) < GOAL_RADIUS):
            objects.remove(obj)
            goals += 1
            continue

        cv2.circle(bkgrd, obj[0], 5, (0,0,255), cv2.FILLED, 2)

        if len(handLocs) == 2:
            if(math.hypot(handLocs[0][0] - obj[0][0], handLocs[0][1] - obj[0][1]) < HAND_RADIUS and obj[2]):
                obj[0] = (obj[0][0] - handLocs[0][0] + handLocs[1][0], obj[0][1] - handLocs[0][1] + handLocs[1][1])
                obj[2] = 0
            elif(math.hypot(handLocs[1][0] - obj[0][0], handLocs[1][1] - obj[0][1]) < HAND_RADIUS and obj[2]):
                obj[0] = (obj[0][0] - handLocs[1][0] + handLocs[0][0], obj[0][1] - handLocs[1][1] + handLocs[0][1])
                obj[2] = 0
            elif(not obj[2]
                and math.hypot(handLocs[0][0] - obj[0][0], handLocs[0][1] - obj[0][1]) > 2*HAND_RADIUS 
                and math.hypot(handLocs[1][0] - obj[0][0], handLocs[1][1] - obj[0][1]) > 2*HAND_RADIUS):
                obj[2] = 1
        else:
            obj[2] = 0

    # create new objects
    cTime = time.time()

    if(cTime - pTimeSpawn > spawnInterval):
        pTimeSpawn = cTime

        yVel = random.uniform(-1,1) * h / math.hypot(w,h)
        
        xVel = math.sqrt(1 - yVel*yVel)
        sign = random.random() - 0.5
        if(sign > 0):
            xVel = xVel
        else:
            xVel = -xVel

        if(xVel < 0):
            xPos = w
        else:
            xPos = 0

        if(yVel < 0):
            yPos = h
        else:
            yPos = 0
        
        # sturcture of object is [position pair, velocity pair]
        objects.append([(xPos, yPos), (xVel, yVel), 1])

    if(cTime - pTimeDiff > DIFF_INC):
        speed += 1
        spawnInterval -= 0.1
        pTimeDiff = cTime
    
    if(cTime - pTimeCount > 1):
        timeRemaining -= 1
        pTimeCount = cTime
    

    cv2.putText(bkgrd, str(goals), (30,50), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
    cv2.putText(bkgrd, str(timeRemaining), (w - 50,50), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)

    cv2.imshow("Image", bkgrd)
    k = cv2.waitKey(1) & 0xFF
    if k == 27 or (timeRemaining <= 0):    # Use Esc key to exit the program
        break

success, img = cap.read()
h, w, c = img.shape
bkgrd = np.zeros(img.shape)

cv2.putText(bkgrd, "GAME OVER", (int(w/2) - 100,int(h/2) - 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
cv2.putText(bkgrd, str(goals), (int(w/2) - 40,int(h/2) + 10), cv2.FONT_HERSHEY_COMPLEX, 2, (255,0,0), 2)
cv2.putText(bkgrd, "Press ESC to Exit", (int(w/2) - 150,int(h/2) + 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
cv2.imshow("Image", bkgrd)

while(cv2.waitKey(1) & 0xFF != 27):
    pass

cv2.destroyAllWindows()
