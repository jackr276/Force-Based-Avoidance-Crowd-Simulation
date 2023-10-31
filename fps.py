"""
Jack Robbins and Randall Tarazona
10/27/2023
IT360 Homework 3 task 2
"""

import glfw
import math
import random
import time
from OpenGL.GL import *
import io

TIMESTEP = 0.025

boundary_x = 0.5
boundary_y = 0.5
max_move = 0.05
circle_rad = 0.05
AgentSize = circle_rad*2
numCircles = 30 
MAX_FORCE = 0.01
MAX_SPEED = 0.008
lastTime = time.time_ns()
frames = 0
totalTime = 0
updateTime = 0
updateFrames = 0
previousFPS = 0
previousAVG = 0

fps = 0.0
fps_avg = 0.0

# Callback for mouse button events
def mouse_button_callback(window, button, action, mods):
    x, y = glfw.get_cursor_pos(window)
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        print(x,y)
        print("Left mouse button pressed!")
    elif button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE:
        print("Left mouse button released!")
    elif button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.PRESS:
        print("Right mouse button pressed!")
    elif button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.RELEASE:
        print("Right mouse button released!")

# Callback for keyboard events
def key_callback(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            print("Escape key pressed!")
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_A:
            print("A key pressed!")
        elif key == glfw.KEY_B:
            print("B key pressed!")
        # ... add more keys as needed


# Initialize the library
if not glfw.init():
    exit()


# Create a windowed mode window and its OpenGL context
window = glfw.create_window(800, 800, "Crowd", None, None)
if not window:
    glfw.terminate()
    exit()

# Make the window's context current
glfw.make_context_current(window)

# Set callbacks
glfw.set_mouse_button_callback(window, mouse_button_callback)
glfw.set_key_callback(window, key_callback)


circles = []

for i in range(numCircles):
    circle = {
        'x': random.uniform(-boundary_x, boundary_x),
        'y': random.uniform(-boundary_y, boundary_y),
        'v_x': random.uniform(-max_move, max_move),
        'v_y': random.uniform(-max_move, max_move),
        'v_x_goal': random.uniform(-max_move, max_move),
        'v_y_goal': random.uniform(-max_move, max_move)
    }
    circles.append(circle)

def distanceF(x1, y1, x2, y2):
    return math.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))
    

def update_circles():
    for i in range(numCircles):
        circle = circles[i]
        # Makes the circle move
        circle['x'] += circle['v_x']
        circle['y'] += circle['v_y']

        # Apply constraints to stay within the boundaries
        if circle['x'] < -0.5:
            circle['x'] = 0.5
        if circle['y'] < -0.5:
            circle['y'] = 0.5
        if circle['x'] > 0.5:
            circle['x'] = -0.5
        if circle ['y'] > 0.5:
            circle['y'] = -0.5

        vx = circle['v_x']
        vy = circle['v_y']
        zeta = 1.0023
        f_goal_x = (circle['v_x_goal'] - vx) / zeta
        f_goal_y = (circle['v_x_goal']- vy) / zeta
        favoidx = 0
        favoidy = 0
        favoidctr = 0

        # Collision checking
        for j in range(numCircles):
            circle1x = circle['x']
            circle1y = circle['y']

            circle2 = circles[j]
            circle2x = circle2['x']
            circle2y = circle2['y']

            # don't bother checking the same circle against itself
            if i == j:
                continue    
            
  
            distance = distanceF(circle1x, circle1y, circle2x, circle2y)

            if distance > 0 and distance < AgentSize*1.25:
                d_circle = max(distance - AgentSize, 0.001)
                k = 0.75 * max(AgentSize*3 - d_circle, 0)
                x_ab = (circle1x - circle2x)/distance
                y_ab = (circle1y - circle2y)/distance
                favoidx += k * x_ab/d_circle
                favoidy += k * y_ab/d_circle
                favoidctr += 1

            if favoidctr > 0:
                favoidx = favoidx / favoidctr
                favoidy = favoidy / favoidctr

            force_sum_x = f_goal_x + favoidx
            force_sum_y = f_goal_y + favoidy
            f_avoid_mag = math.sqrt(force_sum_x*force_sum_x + force_sum_y*force_sum_y)


            if f_avoid_mag > MAX_FORCE:
                force_sum_x = MAX_FORCE* force_sum_x/ f_avoid_mag
                force_sum_y = MAX_FORCE* force_sum_y / f_avoid_mag

            vx += TIMESTEP * force_sum_x
            vy += TIMESTEP * force_sum_y

            speed = math.sqrt(vx*vx + vy*vy)
            if speed > MAX_SPEED:
                vx = MAX_SPEED * vx / speed 
                vy = MAX_SPEED * vy / speed
                

            circle['v_x'] = vx
            circle['v_y'] = vy
            circle['x'] += TIMESTEP*vx
            circle['y'] += TIMESTEP*vy               


"""
This is the drawCircle helper function
"""
def drawCircle(x, y, r, numberOfSegments):
    glTranslatef(x, y, 0)
    
    # glColor3f(0, 0, 0, 1)
    glColor3f(0, 0, 1)
    glBegin(GL_LINE_LOOP)
    i = 0
    while (i < numberOfSegments):
        angle = 360 * i / numberOfSegments
        cx = r*math.cos(angle)
        cy = r*math.sin(angle)

        glVertex2f(x  + cx, y + cy)
        i += 1

    glEnd()
    
    glTranslatef(x, y, 0)

    # glColor3f(0.807, 0, 0, 1) 
    glColor3f(0.807, 0, 1) 
    glBegin(GL_TRIANGLE_FAN)
    i = 0
    while (i < numberOfSegments):
        angle = 2 * math.pi * i / numberOfSegments
        cx = r*math.cos(angle)
        cy = r*math.sin(angle)

        glVertex2f(cx, cy)
        i += 1

    glEnd()



def getFPS():
    global lastTime, totalTime, frames, updateTime, updateFrames, fps, fps_avg
    #Calculate fps
    now = time.time_ns()
    delta = now -lastTime
    lastTime = now
    totalTime += delta
    updateTime += delta
    frames += 1
    updateFrames += 1
    if (updateTime > 1000000000):
        fps = 1000000000 * frames/totalTime
        fps_avg = 1000000000 * updateFrames/updateTime
        updateTime = 0
        updateFrames = 0
    return fps_avg, fps


# Main loop
while not glfw.window_should_close(window):


    glClearColor(0.870, 0.905, 0.937, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)
    #Draw circles
    time.sleep(TIMESTEP)
 
    update_circles() 

    for circle in circles:
        glPushMatrix()
        drawCircle(circle['x'], circle['y'], circle_rad, 1000)
        glPopMatrix()


    currFPS, overallAvg = getFPS()
    currFPS = round(currFPS)
    overallAvg = round(overallAvg)

    if (previousFPS != currFPS):
        print(f"Current FPS: {currFPS} \nOverall FPS Average: {overallAvg}")
        previousFPS = currFPS


    # Swap front and back buffers
    glfw.swap_buffers(window)


    # Poll for and process events
    glfw.poll_events()

# Terminate GLFW
glfw.terminate()