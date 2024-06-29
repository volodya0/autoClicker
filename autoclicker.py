import sys
import mss
import time
import cv2
import numpy as np
import pygame.draw_py
import time
import pygame
from mousemove import humanizedClick


def filterUniquePoints(points, md = None):
    md = md if md else min_distance
    uniquePoints = []
    for pt in points:
        if all(np.linalg.norm((np.array(pt) - np.array(unique_pt)) > md) for unique_pt in uniquePoints):
            uniquePoints.append(pt)
    return uniquePoints
 

def matchTemplate(scr, template, th = 0.8, md = None, filter = True):    
    res = cv2.matchTemplate(scr, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= th)
    points = list(zip(*loc[::-1]))
    if filter: points = filterUniquePoints(points, md)
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
        else: 
            headPt = None
    
    return None
               

def detectI(scrScaled): 
    m1 = matchTemplate(scrScaled, i1TemScaled, 0.85, filter=False)
    m2 = matchTemplate(scrScaled, i2TemScaled, 0.85, filter=False)
    
    return  unScalePoints(filterUniquePoints(m1 + m2))


def detectD(scrScaled): 
    m1 = matchTemplate(scrScaled, d1TemScaled, 0.85, filter=False)
    m2 = matchTemplate(scrScaled, d2TemScaled, 0.85, filter=False)
    
    return  unScalePoints(filterUniquePoints(m1 + m2))


def detectB(scrScaled): 
    m1 = matchTemplate(scrScaled, b1TemScaled, 0.85, filter=False)
    m2 = matchTemplate(scrScaled, b2TemScaled, 0.85, filter=False)
    
    return  unScalePoints(filterUniquePoints(m1 + m2))


def nextStep():
    start_time = time.time()
    
    scrScaled = getGameScr()
    
    if scrScaled is None:
        pyGameScreen.fill(RED)
    else:
        heightScaled = scrScaled.shape[0]
        areaOffsetTop = gameH * 0.2
        areaOffsetBottom = 110
        areaScr = scrScaled[int(areaOffsetTop * scaleFactor):int(heightScaled-(areaOffsetBottom * scaleFactor)), :]
        
        print(f"area time: {( time.time() - start_time) * 1000} ms")
                
        pyGameScreen.fill(BLACK)
        
        gameX = headPt[0]
        gameY = headPt[1] + headH
        
        start_time = time.time()
        
        # cv2.imshow('areaScr', areaScr)
        # cv2.waitKey(0)
        
        pointsD = detectD(areaScr)
        pointsB = detectB(areaScr)
        pointsI = detectI(areaScr)
                 
        print(f"detect time: {( time.time() - start_time) * 1000} ms")
        
        start_time = time.time()
        
        if drawingEnabled:
            if len(pointsB):
                drawPoints(pointsB, areaOffsetTop, RED)
            if len(pointsD):
                drawPoints(pointsD, areaOffsetTop, BLUE)
            if len(pointsI):
                drawPoints(pointsI, areaOffsetTop, GREEN)
            
        if(clickingEnabled):
            if len(pointsD):
                x, y  = pointsD[0]
                humanizedClick((x + gameX, y + gameY + areaOffsetTop - 40), itemWidth, itemHeight)
            elif len(pointsI):
                pointsI.sort(key=lambda pt: pt[1], reverse=True)
                bottom_point = None
                for pointI in pointsI:
                    if all(np.linalg.norm((np.array(pointI) - np.array(b_point))) > 10 for b_point in pointsB):
                        bottom_point = pointI
                        break
                    
                if bottom_point:
                    x, y  = bottom_point
                    humanizedClick((x + gameX, y + gameY + areaOffsetTop - 40), itemWidth, itemHeight)

    
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
d2Tem = cv2.imread('templates_png/small_d.png', 0)
b1Tem = cv2.imread('templates_png/small_b.png', 0)
b2Tem = cv2.imread('templates_png/large_b.png', 0)

i1TemScaled = scaleImg(i1Tem, scaleFactor)
i2TemScaled = scaleImg(i2Tem, scaleFactor)
d1TemScaled = scaleImg(d1Tem, scaleFactor)
d2TemScaled = scaleImg(d2Tem, scaleFactor)
b1TemScaled = scaleImg(b1Tem, scaleFactor)
b2TemScaled = scaleImg(b2Tem, scaleFactor)


itemWidth, itemHeight = d1Tem.shape[::-1]

headPt = None
pyGameScreen = None

clickingEnabled = False
drawingEnabled = True

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

pygame.init()
pyGameScreen = pygame.display.set_mode((380, 600))
pygame.display.set_caption("Detected objects")
clock = pygame.time.Clock()  

if __name__ == "__main__":
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    clickingEnabled = not clickingEnabled
                elif event.key == pygame.K_d:
                    drawingEnabled = not drawingEnabled
        
        nextStep()
              
        font = pygame.font.Font(None, 20)
        text1 = font.render("Drawing enabled: " + str(drawingEnabled) + " ('D' key)", True, WHITE)
        text2 = font.render("Clicking enabled: " + str(clickingEnabled) + " ('C' key)", True, WHITE)
        pyGameScreen.blit(text1, (10, 10))
        pyGameScreen.blit(text2, (10, 30))
        
        pygame.display.update()
        clock.tick(16)
