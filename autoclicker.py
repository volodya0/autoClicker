from multiprocessing import Pool, cpu_count
import pyautogui
import keyboard
import time
import threading
import cv2
import numpy as np
import win32gui
import win32api
import win32con
import time

from mousemove import human_like_mouse_move

# Function to draw transparent rectangles (only borders) on the screen
def draw_lines_around_item(left, top, right, bottom):
    hwnd = win32gui.GetDesktopWindow()
    dc = win32gui.GetWindowDC(hwnd)
    pen = win32gui.CreatePen(win32con.PS_SOLID, 3, win32api.RGB(0, 255, 0))
    old_pen = win32gui.SelectObject(dc, pen)

    # Draw top line
    win32gui.MoveToEx(dc, left, top)
    win32gui.LineTo(dc, right, top)
    
    # Draw bottom line
    win32gui.MoveToEx(dc, left, bottom)
    win32gui.LineTo(dc, right, bottom)

    # Draw left line
    win32gui.MoveToEx(dc, left, top)
    win32gui.LineTo(dc, left, bottom)

    # Draw right line
    win32gui.MoveToEx(dc, right, top)
    win32gui.LineTo(dc, right, bottom)

    win32gui.SelectObject(dc, old_pen)
    win32gui.DeleteObject(pen)
    win32gui.ReleaseDC(hwnd, dc)

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

# Function to perform the clicking and draw lines around detected items
def click_and_draw_items():
    i1_t = cv2.imread('templates_png/small_i.png', 0)
    i2_t = cv2.imread('templates_png/large_i.png', 0)
    d1_t = cv2.imread('templates_png/large_d.png', 0)

    min_distance = 20
    threshold = 0.75

    w, h = d1_t.shape[::-1]

    while True:
        if running:
            print('running...')
            start_time = time.time()

            gray_screenshot = cv2.cvtColor(cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)

            unique_points1 = match_template(gray_screenshot, i1_t, threshold, min_distance)
            unique_points2 = match_template(gray_screenshot, i2_t, threshold, min_distance)
            unique_points3 = match_template(gray_screenshot, d1_t, threshold, min_distance)

            unique_points = unique_points1 + unique_points2 + unique_points3

            print(f'uq collecting time: {(time.time() - start_time) * 1000:.2f}ms')
            start_time = time.time()


            # Draw lines around the detected items
            for pt in unique_points:
                left, top = pt
                right, bottom = left + w, top + h
                if drawing:
                    draw_lines_around_item(left, top, right, bottom)
                start = np.array(pyautogui.position()).reshape(1, 2)
                end = np.array([pt[0] + w / 2, pt[1] + h / 2]).reshape(1, 2)
                if moving:
                    start_time_m = time.time()
                    human_like_mouse_move(start, end)
                    print(f'sm time: {(time.time() - start_time_m) * 1000:.2f}ms')

                # pyautogui.click(pt[0] + w / 2, pt[1] + h / 2)

            print(f'md time: {(time.time() - start_time) * 1000:.2f}ms')
            
        else:
            print('waiting...')

        
        time.sleep(1)

def toggle_autoclicker():
    global running, click_thread
    running = not running
    if click_thread == None:
        click_thread = threading.Thread(target=click_and_draw_items)
        click_thread.start()

def toggle_moving():
    global moving
    moving = not moving

def toggle_drawing():
    global drawing
    drawing = not drawing

running = False
moving = False
drawing = False
click_thread = None

# Main program
if __name__ == "__main__":
    print("Press 's' to toggle autoclicker")
    print("Press 'm' to toggle mouse moving")
    print("Press 'd' to toggle drawing")
    print("Press 'q' to exit")

    # Keyboard event listeners
    keyboard.add_hotkey('s', toggle_autoclicker)
    keyboard.add_hotkey('m', toggle_moving)
    keyboard.add_hotkey('d', toggle_drawing)


    toggle_autoclicker()

    # Keep the program running
    keyboard.wait('q')
