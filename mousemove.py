import time
import pyautogui
import numpy as np
import random


def bezier_curve(start, control, end, num_points=3):
    t_values = [i / (num_points - 1) for i in range(num_points)]
    curve_points = [
        (
            (1 - t) ** 2 * start[0] + 2 * (1 - t) *
            t * control[0] + t ** 2 * end[0],
            (1 - t) ** 2 * start[1] + 2 * (1 - t) *
            t * control[1] + t ** 2 * end[1]
        )
        for t in t_values
    ]
    return curve_points


def humanizedMouseMove(start, end, duration=0.1):
    control1 = (start[0] + (end[0] - start[0]) * random.uniform(0.2, 0.8) + random.uniform(-20, 20),
                start[1] + (end[1] - start[1]) * random.uniform(0.2, 0.8) + random.uniform(-20, 20))

    points = bezier_curve(start, control1, end, num_points=3)

    for point in points:
        pyautogui.moveTo(point[0], point[1], random.uniform(duration / len(points) * 0.9, duration / len(points) * 1.1) )  #
        
        
def humanizedClick(point, width, height):
    x, y = point
    x += random.randint(-4, width + 4)
    y += random.randint(-4, height + 4)
    pyautogui.click(x, y)
    
