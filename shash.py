"""
Jack Robbins and Randall Tarazona
10/27/2023
IT360 Homework 3 task 3
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
# max_move = 0.05
max_move = 2
# circle_rad = 0.05
circle_rad = 15
AgentSize = circle_rad*2
numCircles = 30
# MAX_FORCE = 0.01
# MAX_SPEED = 0.008
MAX_FORCE = 2
MAX_SPEED = 1.5
lastTime = time.time_ns()
frames = 0
totalTime = 0
updateTime = 0
updateFrames = 0
previousFPS = 0
previousAVG = 0

fps = 0.0
fps_avg = 0.0

# spatial hash
window_height = 800 # y : rows
window_width = 800  # x : cols
divisions = 10 # This controls how many cells the grid will be divided into. division division
numCells = divisions ** 2
cell_w = window_width // divisions
cell_h = window_height // divisions
grid_w = divisions
sHash = {k : []  for k in range(numCells)}

# hash function: use coordinated to get associated cell
def getGridCell(x,y) -> int:
    return (x // cell_w) + (y // cell_h) * grid_w

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

# initializes the circles
circles = []

for i in range(numCircles):
    circle = {
        # 'x': random.uniform(-boundary_x, boundary_x),
        # 'y': random.uniform(-boundary_y, boundary_y),
        'x': random.randint(0, window_width),
        'y': random.randint(0, window_height),
        'v_x': random.uniform(-max_move, max_move),
        'v_y': random.uniform(-max_move, max_move),
        'v_x_goal': random.uniform(-max_move, max_move),
        'v_y_goal': random.uniform(-max_move, max_move)
    }
    circles.append(circle)

# added to spatial hash (TODO combine this into initialize stage)
def update_sHash():
    for c in circles:
        x , y = c['x'] , c['y']
        gridCell = getGridCell(x, y)
        sHash[gridCell].append(c)

def distanceF(x1, y1, x2, y2):
    return math.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))
    

def update_circles():
    for i in range(numCircles):
        circle = circles[i]
        # Makes the circle move
        circle['x'] += circle['v_x']
        circle['y'] += circle['v_y']

        # Apply constraints to stay within the boundaries
        '''
        if circle['x'] < -0.5:
            circle['x'] = 0.5
        if circle['y'] < -0.5:
            circle['y'] = 0.5
        if circle['x'] > 0.5:
            circle['x'] = -0.5
        if circle ['y'] > 0.5:
            circle['y'] = -0.5
        '''
        # changed boundies to be one more and one less then the set window boundry. Just to make the math work
        if circle['x'] < 1:
            circle['x'] = 799
        if circle['y'] < 1:
            circle['y'] = 799
        if circle['x'] > 799:
            circle['x'] = 1
        if circle ['y'] > 799:
            circle['y'] = 1

        circle1x , circle1y = circle['x'], circle['y']
        gridCell = getGridCell(circle1x, circle1y)

        check(circle, gridCell)

        #looking at all circles in lefthand cell
        
        adjusted_x = circle1x - cell_w
        adjusted_y_upper = circle1y + cell_h
        adjusted_y_lower = circle1y - cell_h
        #we've wrapped around
        if(adjusted_x < 1):
            adjusted_x = window_width - 10
        if (adjusted_x > window_width - 1):
            adjusted_x = 10

        if (adjusted_y_upper > window_height - 1):
            adjusted_y_upper = 10
        
        if (adjusted_y_lower < 1):
            adjusted_y_lower = window_height - 1

        leftGridCell = getGridCell(adjusted_x, circle1y)
        leftUpperCell = getGridCell(adjusted_x,adjusted_y_upper)
        leftLowerCell = getGridCell(adjusted_x, adjusted_y_lower)

        check(circle, leftGridCell)
        check(circle, leftUpperCell)
        check(circle, leftLowerCell)

#FIXME
def check(circle, gridCell):
    # skip the cell if less than 2 agents in one cell
    if len(sHash[gridCell]) < 2:
        return

    # looking at all circles within the same cell
    for curr in sHash[gridCell]:
        # don't bother checking the same circle against itself
        if circle is curr:
            continue
        updateCircleVelocity(circle, curr)
  
           

def updateCircleVelocity(circle, circle2):
    circle1x = circle['x']
    circle1y = circle['y']
    circle2x = circle2['x']
    circle2y = circle2['y']

    zeta = 1.0023
    vx = circle['v_x']
    vy = circle['v_y']
      

    f_goal_x = (circle['v_x_goal'] - vx) / zeta
    f_goal_y = (circle['v_x_goal']- vy) / zeta

    #Get force sums
    force_sum_x, force_sum_y = getForce(circle1x, circle1y, circle2x, circle2y, f_goal_x, f_goal_y)
    #update velocities appropriately
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


def getForce(x, y, a, b, f_goal_x, f_goal_y):
    distance = distanceF(x, y, a, b)
    favoidx = 0
    favoidy = 0
    favoidctr = 0

    avoidanceD = AgentSize*2


    if distance > 0 and distance < avoidanceD:
        d_circle = max(distance - AgentSize, 0.001)
        k = 0.75 * max(AgentSize*3 - d_circle, 0)
        x_ab = (x - a)/distance
        y_ab = (y - b)/distance
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

    return force_sum_x, force_sum_y


"""
This is the drawCircle helper function
"""
def drawCircle(x, y, r, numberOfSegments):
    
    glColor(0.0, 0.0, 0.0)
    glLineWidth(2.0)  # Set the line width
    glBegin(GL_LINE_LOOP)  # Use GL_LINE_LOOP to draw the boundary
    for i in range(360):
        theta = i * (math.pi / 180)
        glVertex2d(x + r * math.cos(theta), y + r * math.sin(theta))
    glEnd()

    glColor(0.807, 0.0, 0.0)
    glBegin(GL_POLYGON)
    for i in range(360):
        theta = i * (math.pi / 180)
        glVertex2d(x + r * math.cos(theta),y + r * math.sin(theta))
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
 
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, window_width, 0, window_height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


    update_circles() 
    
    for i in sHash:
        sHash[i] = []
    
    update_sHash()

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