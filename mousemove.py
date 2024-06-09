import time
import pyautogui
import numpy as np
import random

def bezier_curve(start, control, end, num_points=3):  # Reduced number of points to 3
    t_values = np.linspace(0, 1, num_points)[:, None]
    curve_points = (1 - t_values) ** 2 * start + 2 * (1 - t_values) * t_values * control + t_values ** 2 * end
    return curve_points

def human_like_mouse_move(start, end):
    start = np.array(start).reshape(1, 2)
    end = np.array(end).reshape(1, 2)
    
    control1 = start + (end - start) * np.random.uniform(0.2, 0.8) + np.random.uniform(-50, 50, start.shape)
    # control2 = start + (end - start) * np.random.uniform(0.2, 0.8) + np.random.uniform(-50, 50, start.shape)
    
    points = bezier_curve(start, control1, end, num_points=3)  # Generate 3 points for the curve
    
    duration = random.uniform(0.02, 0.1)
    start_time_m = time.time() 

    for point in points:
        pyautogui.moveTo(point[0], point[1])  
        
    print(f'moving time: {(time.time() - start_time_m) * 1000:.2f}ms')
        
