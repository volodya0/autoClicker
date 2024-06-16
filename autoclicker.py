import sys
import mss
import time
import threading
import cv2
import numpy as np
import pygame.draw_py
import time
import pygame


def filterUniquePoints(points, md = None):
    md = md if md else min_distance
    uniquePoints = []
    for pt in points:
        if all(np.linalg.norm((np.array(pt) - np.array(unique_pt)) > md) for unique_pt in uniquePoints):
            uniquePoints.append(pt)
    return uniquePoints
 

def matchTemplate(scr, template, th = 0.8, md = None, filter = True):    
    # start_time = time.time()
    res = cv2.matchTemplate(scr, template, cv2.TM_CCOEFF_NORMED)
    # print(f"time1: {( time.time() - start_time) * 1000} ms")
    
    # start_time = time.time()
    loc = np.where(res >= th)
    # print(f"time2: {( time.time() - start_time) * 1000} ms")
    
    # start_time = time.time()
    points = list(zip(*loc[::-1]))
    # print(f"time3: {( time.time() - start_time) * 1000} ms")
    
    # start_time = time.time()
    if filter: points = filterUniquePoints(points, md)
    # print(f"time4: {( time.time() - start_time) * 1000} ms")
        
    return points

def scaleImg(image, sF = None):
    sF = sF if sF else scaleFactor
    height, width = image.shape[:2]
    newSize = (int(width * sF), int(height * sF))
    return cv2.resize(image, newSize)

def unScalePoints(points, sF = None):
    sF = sF if sF else scaleFactor
    return [(int(pt[0] / sF), int(pt[1] / sF)) for pt in points]

def captureScreen(rect=None):
    with mss.mss() as sct:
        rect = {'left': rect[0], 'top': rect[1], 'width': rect[2], 'height': rect[3]} if rect else sct.monitors[0]
        screenshot = sct.grab(rect)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
def drawPoints(points, yOffset = 0, color = None):
    for pt in points:
        x, y = pt
        pygame.draw.rect(pyGameScreen, color if color else WHITE, pygame.Rect(x, y + yOffset, itemWidth, itemHeight), 2)
        

def detectI(scrScaled): 
    m1 = matchTemplate(scrScaled, i1TemScaled, 0.7, filter=False)
    m2 = matchTemplate(scrScaled, i2TemScaled, 0.7, filter=False)
    
    return  unScalePoints( filterUniquePoints(m1 + m2))

def detectD(scrScaled): 
    return unScalePoints( matchTemplate(scrScaled, d1TemScaled, 0.7))

def nextStep():
    start_time = time.time()
    
    scrScaled = getGameScr()
    
    if scrScaled is None:
        pyGameScreen.fill(RED)
    else:
        heightScaled = scrScaled.shape[0]
        areaOffsetTop = gameH * 0.2
        areaOffsetBottom = 80
        areaScr = scrScaled[int(areaOffsetTop * scaleFactor):int(heightScaled-(areaOffsetBottom * scaleFactor)), :]
        
        print(f"area time: {( time.time() - start_time) * 1000} ms")
                
        pyGameScreen.fill(BLACK)
        
        gameX = headPt[0]
        gameY = headPt[1] + headH
        
        start_time = time.time()
        
        # cv2.imshow('areaScr', areaScr)
        # cv2.waitKey(0)
        
        pointsD = detectD(areaScr)
        pointsI = detectI(areaScr)
                 
        print(f"detect time: {( time.time() - start_time) * 1000} ms")
        
        start_time = time.time()
        
        
        if len(pointsD):
            drawPoints(pointsD, areaOffsetTop, BLUE)
            
        if len(pointsI):
            drawPoints(pointsI, areaOffsetTop, GREEN)
 
        print(f"drawD time: {( time.time() - start_time) * 1000} ms")


        # pygame.draw.circle(pyGameScreen, WHITE, ( random.uniform(0, 100), 100), 50)
        # pygame.draw.rect(pyGameScreen, RED, (200, 150, 100, 50))
    start_time = time.time()
    
    # pygame.display.flip()
  
    
    print(f"fu time: {( time.time() - start_time) * 1000} ms")
  


def ensureHead(ScrScaled):
    global headPt
    matches = matchTemplate(ScrScaled, headTemplateSmall, 0.7, 10)
    
    # cv2.imshow('ScrScaled', ScrScaled)
    # cv2.waitKey(0)
    # cv2.imshow('headTemplateSmall', headTemplateSmall)
    # cv2.waitKey(0)
    
    if matches:
        headPt = (int(matches[0][0] / scaleFactor), int( matches[0][1] / scaleFactor))
        return True
    return False

def getGameScr():
    global headPt
    
    if headPt or ensureHead(scaleImg(captureScreen(), scaleFactor)):
        x, y = headPt
        ScrScaled = scaleImg(captureScreen((x, y, gameW, gameH)), scaleFactor)
        headScaled = ScrScaled[0:int(headH * scaleFactor), :]
        # cv2.imshow('ScrScaled', ScrScaled)
        # cv2.imshow('headScaled', headScaled)
        # cv2.waitKey(0)
        matches = matchTemplate(headScaled, headTemplateSmall,  0.7)
        if matches:
            # cv2.imshow('Scr', scr)
            # cv2.waitKey(0)
            return ScrScaled; 
    
    return None
       
    
scaleFactor = 0.5
min_distance = 30
threshold = 0.75

headTemplate = cv2.imread('templates_png/head.png', 0)
headTemplateSmall = scaleImg(headTemplate, scaleFactor)

gameW, headH = headTemplate.shape[::-1]
gameH = 860

i1Tem = cv2.imread('templates_png/small_i.png', 0)
i2Tem = cv2.imread('templates_png/large_i.png', 0)
d1Tem = cv2.imread('templates_png/large_d.png', 0)

i1TemScaled = scaleImg(i1Tem, scaleFactor)
i2TemScaled = scaleImg(i2Tem, scaleFactor)
d1TemScaled = scaleImg(d1Tem, scaleFactor)


itemWidth, itemHeight = d1Tem.shape[::-1]

running = True
headPt = None
pyGameScreen = None

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

pygame.init()
pyGameScreen = pygame.display.set_mode((gameW, 800))
pygame.display.set_caption("Detected objects")
clock = pygame.time.Clock()  

if __name__ == "__main__":
   

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
        
        if running:
            print('running...')
            nextStep()
        else:
            print('waiting...')
            
        pygame.display.update()
        clock.tick(60)
