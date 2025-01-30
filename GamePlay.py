# GamePlay.py

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import Pieces
import UI

import copy # for copying cubes to CubeList

#Camera
import Border
import Camera
import secrets

#Camera

score = 0 

icons = (
    "Icons/IIcon.png",
    "Icons/JIcon.png",
    "Icons/LIcon.png",
    "Icons/OIcon.png",
    "Icons/SIcon.png",
    "Icons/TIcon.png",
    "Icons/ZIcon.png"
)

def Init():
    global _piece
    #NEW
    global _nextPiece
    global nextIndex
    #NEW
    global OnStart
    global moveUp, moveDown, moveLeft, moveRight, rotateLeft, rotateRight, rotateDown

    #Camera
    global camUp, camDown, camLeft, camRight
    camUp, camDown, camLeft, camRight = False, False, False, False
    #Camera

    OnStart = True

    Pieces.Init() # Calls to run Cube Init() through Pieces file
    #Camera
    Camera.Init()
    #Camera

    moveUp, moveDown, moveLeft, moveRight, rotateLeft, rotateRight, rotateDown = False, False, False, False, False, False, False

def ProcessEvent(event):
    global moveUp, moveDown, moveLeft, moveRight, rotateLeft, rotateRight, rotateDown
    
    #Camera
    global camUp, camDown, camLeft, camRight
    #Camera

    #add player key shift movements using arrow keys
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            moveLeft = True
        elif event.key == pygame.K_RIGHT:
            moveRight = True
        elif event.key == pygame.K_DOWN:
            moveDown = True
        elif event.key == pygame.K_UP:
            moveUp = True
        elif event.key == pygame.K_a:
            rotateLeft = True
        elif event.key == pygame.K_d:
            rotateRight = True
        elif event.key == pygame.K_s:
            rotateDown = True

    #Camera
        if event.key == pygame.K_i:
            camUp = True
        elif event.key == pygame.K_k:
            camDown = True
        elif event.key == pygame.K_j:
            camLeft = True
        elif event.key == pygame.K_l:
            camRight = True
    #Camera

    return False

index = secrets.SystemRandom().randint(0, 6)
#NEW
#Get a random index for the next piece
nextIndex = secrets.SystemRandom().randint(0, 6)
#NEW

#Set the next piece display
icon_idx = nextIndex

_isGamePaused = False  # A new global variable to track the pause state

# Function to update and display the score
def update_score(points):
    global score
    score += points
    print(f"Score: {score}")  # Display the score 

#Change the value of appearing and disappearing for all cubes
def ToggleVisible(list, appear, disappear):
    for cube in list:
        cube.appearing = appear
        cube.disappearing = disappear

def Pause():
    global _isGamePaused
    global _piece

    _isGamePaused = True

    #Toggle current piece to disappear
    _piece.ToggleCubes(False, True)
    # trigger all cubes on screen to disappear (on final assignment)
    ToggleVisible(Pieces.CubeList, False, True)

def Resume():
    global _isGamePaused
    global _piece

    _isGamePaused = False
 
    #Toggle current piece to appear
    _piece.ToggleCubes(True, False)
    # trigger all cubes on screen to appear (on final assignment)
    ToggleVisible(Pieces.CubeList, True, False)

def Update(deltaTime, pieces):
    global _piece
    global index
    #NEW
    global nextIndex
    global icon_idx
    #NEW
    global OnStart
    global moveUp, moveDown, moveLeft, moveRight, rotateLeft, rotateRight, rotateDown

    #Camera
    global camUp, camDown, camLeft, camRight
    #Camera

    if pieces:
        _piece = pieces[index]

    if OnStart:
        _piece.ResetCubePos()
        updatePos = (1, 12, -1)
        _piece.SetPos(updatePos)
        OnStart = False

        #NEW
        #Toggle cubes of piece to fade in
        _piece.ToggleCubes(True, False)

    # checks if bottom row is filled
    if not Pieces.CheckForPoint():
        for cube in Pieces.CubeList:
            if cube.GetCubePos()[1] <= -4.9:
                Pieces.CubeList.remove(cube)   # removes any cubes at bottom from cube list
        for cube in Pieces.CubeList:
            cube.MoveCubeDown() # sets all remaining cubes y position 2 down
        update_score(1)

    # proof check if any cube are below bottom
    for cube in Pieces.CubeList:
        if cube.GetCubePos()[1] < -5.5:
            Pieces.CubeList.remove(cube)

    # keeps piece from moving into other cubes
    if not Pieces.checkCubeCol(_piece):
        if Pieces.CheckForCeil():
            _piece.position[0] = _piece.prevPosition[0]
            _piece.position[2] = _piece.prevPosition[2]
            # retains y value for next collision check purposes

    # Check if piece hits the bottom or stacks
    move = np.asfarray([0, -2*deltaTime, 0])

    if move[1] + _piece.GetPos()[1] < 12:
        if move[1] + _piece.GetPos()[1] + _piece.cubes[0].GetCubePos()[1] <= -5.01 or \
            move[1] + _piece.GetPos()[1] + _piece.cubes[1].GetCubePos()[1] <= -5.01 or \
            move[1] + _piece.GetPos()[1] + _piece.cubes[2].GetCubePos()[1] <= -5.01 or \
            move[1] + _piece.GetPos()[1] + _piece.cubes[3].GetCubePos()[1] <= -5.01 or \
            not Pieces.checkCubeCol(_piece):

            # if y value is now colliding after reverting x and z positions
            if not Pieces.checkCubeCol(_piece):
                if Pieces.CheckForCeil():
                    _piece.position = _piece.prevPosition
                    _piece.position[1] = np.ceil(_piece.prevPosition[1])
                    if (_piece.position[1] % 2) == 0:
                        _piece.position[1] -= 1

            #Update index to next index and grab a new next index
            index = nextIndex
            nextIndex = secrets.SystemRandom().randint(0, 6)

            #Set the next piece display
            icon_idx = nextIndex

            # Adds cubes to a seperate list to keep in place at bottom
            for cube in _piece.cubes:
                staticCube = copy.deepcopy(cube)
                staticCube.SetCubePos(cube.GetCubePos() + np.rint(_piece.GetPos()))
                Pieces.freezeCubes(staticCube)

            OnStart = True
            move[1] += 24

    # Had to comment out to get cubes to freeze
    #Check if piece is close to bottom. If so, toggle cubes to fade
    #if move[1] + _piece.GetPos()[1] <= -8: # temporary to get cubes to stack at bottom
        #Toggle cubes of piece to fade out
        #_piece.ToggleCubes(False, True)
        
    #Get the axis currently facing camera
    if moveUp or moveDown or moveLeft or moveRight:
        curSide = Camera.getCurSide()
        #print(curSide)

    # Key bindings
    # Move piece on z axis
    if moveUp:
        if curSide == 'z':
            move[2] += -2
        elif curSide == 'x':
            move[0] += 2
        elif curSide == '-z':
            move[2] += 2
        elif curSide == '-x':
            move[0] += -2
        moveUp = False
    if moveDown:
        if curSide == 'z':
            move[2] += 2
        elif curSide == 'x':
            move[0] += -2
        elif curSide == '-z':
            move[2] += -2
        elif curSide == '-x':
            move[0] += 2
        moveDown = False
    # Move piece on x axis
    if moveLeft:
        if curSide == 'z':
            move[0] += -2
        elif curSide == 'x':
            move[2] += -2
        elif curSide == '-z':
            move[0] += 2
        elif curSide == '-x':
            move[2] += 2
        moveLeft = False
    if moveRight:
        if curSide == 'z':
            move[0] += 2
        elif curSide == 'x':
            move[2] += 2
        elif curSide == '-z':
            move[0] += -2
        elif curSide == '-x':
            move[2] += -2
        moveRight = False

    # Rotate piece
    if rotateLeft:
        #_piece.ToggleRotate("left")
        _piece.Rotate(90, (0, -2, 0))
        rotateLeft = False
    elif rotateRight:
        #_piece.ToggleRotate("right")
        _piece.Rotate(-90, (0, -2, 0))
        rotateRight = False
    elif rotateDown:
        #_piece.ToggleRotate("down")
        _piece.Rotate(-90, (-2, 0, 0))
        rotateDown = False

    _piece.prevPosition = np.copy(_piece.position)

    _piece.Update(deltaTime, move, _isGamePaused)

    if Pieces.CubeList:
        for cube in Pieces.CubeList:
            cube.Update(deltaTime)

    #Camera
    if camUp:
        #print("Cam up")
        Camera.toggleCamMove(0, 1)
        #Border.rotateCamera(0)
        camUp = False
    elif camDown:
        #print("Cam down")
        Camera.toggleCamMove(0, -1)
        #Border.rotateCamera(1)
        camDown = False
    elif camLeft:
        #print("Cam left")
        Camera.toggleCamMove(1, 0)
        #Border.rotateCamera(2)
        camLeft = False
    elif camRight:
        #print("Cam right")
        Camera.toggleCamMove(-1, 0)
        #Border.rotateCamera(3)
        camRight = False
    #Camera

def Render():
    global _piece
    global icon_idx
    global score

    # screen size
    width, height = 640, 750

    # Setting up orthographic projection for text rendering
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, height, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    #Render the image
    UI.render_image(50, 50, 100, 100, image_path=icons[icon_idx])

    # Render the text
    UI.render_text("next", 40, 10, 28)

    # Render the score
    UI.render_text(f"Score: {str(score)}", 475, 10, 16)

    # Restore the previous projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    _piece.Render()
    
    if Pieces.CubeList:
        for cube in Pieces.CubeList:
            cube.Render()
