from multiprocessing import Pool, cpu_count
import pyautogui
import keyboard
import time
import threading
import cv2
import numpy as np
import time
import random
import Quartz

from mousemove import human_like_mouse_move


def draw_lines_around_item(left, top, right, bottom):
    # Create a Quartz drawing context
    ctx = Quartz.CGContextCreateWithWindow(Quartz.CGMainDisplayID())

    # Set the drawing color to green
    Quartz.CGContextSetRGBStrokeColor(ctx, 0, 1, 0, 1)
    Quartz.CGContextSetLineWidth(ctx, 3)

    # Draw the rectangle
    Quartz.CGContextMoveToPoint(ctx, left, top)
    Quartz.CGContextAddLineToPoint(ctx, right, top)
    Quartz.CGContextAddLineToPoint(ctx, right, bottom)
    Quartz.CGContextAddLineToPoint(ctx, left, bottom)
    Quartz.CGContextAddLineToPoint(ctx, left, top)

    # Stroke the path
    Quartz.CGContextStrokePath(ctx)


def filter_unique_points(points, min_distance):
    unique_points = []
    for pt in points:
        if all(np.linalg.norm(np.array(pt) - np.array(unique_pt)) > min_distance for unique_pt in unique_points):
            unique_points.append(pt)
    return unique_points


def match_template(gray_screenshot, template, threshold, min_distance):
    res = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    match_points = list(zip(*loc[::-1]))
    unique_points = filter_unique_points(match_points, min_distance)
    return unique_points


def euclidean_distance(pt1, pt2):
    return ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** 0.5


def nextStep():
    if not ensureHead():
        return
    mouse_x, mouse_y = pyautogui.position()

    regX = headPt[0]
    regY = headPt[1]

    scr = pyautogui.screenshot(region=(int(regX), int(
        regY + headHeight), int(headWidth), int(750)))
    gray_scr = cv2.cvtColor(cv2.cvtColor(
        np.array(scr), cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)

    draw_lines_around_item(regX - 10, regY + headHeight,
                           regX + headWidth + 20, regY + 750)

    unique_points1 = match_template(gray_scr, i1_t, threshold, min_distance)
    unique_points2 = match_template(gray_scr, i2_t, threshold, min_distance)
    unique_points3 = match_template(gray_scr, d1_t, threshold, min_distance)

    unique_points = unique_points1 + unique_points2 + unique_points3

    if unique_points:
        nearest = min(unique_points, key=lambda pt: euclidean_distance(
            (pt[0] + w/2, pt[1] + h/2), (mouse_x - regX, mouse_y - regY)))
        item_x, item_y = nearest
        item_x += regX
        item_y += regY

        start_time = time.time()

        if drawing:
            draw_lines_around_item(item_x, item_y, item_x + w, item_y + h)

        print(f"drawing time: {(time.time() - start_time) * 1000} ms")

        start_time = time.time()

        if moving:
            pyautogui.click(item_x + random.uniform(0, w),
                            item_y + random.uniform(0, h))

        print(f"moving time: {(time.time() - start_time) * 1000} ms")

# Function to perform the clicking and draw lines around detected items


def run():
    while True:
        if running:
            print('running...')
            nextStep()
        else:
            print('waiting...')
        time.sleep(0.01)


def toggle_run():
    global running, click_thread
    running = not running
    if click_thread is None:
        click_thread = threading.Thread(target=run)
        click_thread.start()


def toggle_moving():
    global moving
    moving = not moving


def toggle_drawing():
    global drawing
    drawing = not drawing


def ensureHead():
    global headPt
    gray_scr = cv2.cvtColor(cv2.cvtColor(
        np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
    matches = match_template(gray_scr, head_t, threshold, min_distance)
    if matches:
        headPt = (matches[0][0], matches[0][1])
        return True
    return False


head_t = cv2.imread('templates_png/head.png', 0)
headWidth, headHeight = head_t.shape[::-1]

i1_t = cv2.imread('templates_png/small_i.png', 0)
i2_t = cv2.imread('templates_png/large_i.png', 0)
d1_t = cv2.imread('templates_png/large_d.png', 0)
min_distance = 20
threshold = 0.75
w, h = d1_t.shape[::-1]

running = False
moving = False
drawing = False
click_thread = None
headPt = None

# Main program
if __name__ == "__main__":
    print("Press 's' to toggle autoclicker")
    print("Press 'm' to toggle mouse moving")
    print("Press 'd' to toggle drawing")
    print("Press 'q' to exit")

    # Keyboard event listeners
    keyboard.add_hotkey('s', toggle_run)
    keyboard.add_hotkey('m', toggle_moving)
    keyboard.add_hotkey('d', toggle_drawing)

    toggle_run()

    # Keep the program running
    keyboard.wait('q')
