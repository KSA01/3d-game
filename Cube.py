# Cube.py

from OpenGL.GL import *
import numpy as np
import math
import random

from OpenGL.arrays import vbo
from OpenGL.GL import shaders

import pygame
from Texture import Texture

# 3 positions, 3 normals, 2 UVs
_verts = np.float32([(1, -1, -1, 0, 0, -1, 0, 0),   # first - 8 vertices x 3
                    (1, 1, -1, 0, 0, -1, 1, 0),
                    (-1, 1, -1, 0, 0, -1, 1, 1),
                    (-1, -1, -1, 0, 0, -1, 0, 1),

                    (-1, -1, -1, -1, 0, 0, 0, 0),
                    (-1, 1, -1, -1, 0, 0, 1, 0),
                    (-1, 1, 1, -1, 0, 0, 1, 1),
                    (-1, -1, 1, -1, 0, 0, 0, 1),

                    (-1, -1, 1, 0, 0, 1, 0, 0),    # second
                    (-1, 1, 1, 0, 0, 1, 1, 0),
                    (1, 1, 1, 0, 0, 1, 1, 1),
                    (1, -1, 1, 0, 0, 1, 0, 1),
                                  
                    (1, -1, 1, 1, 0, 0, 0, 0),
                    (1, 1, 1, 1, 0, 0, 1, 0),
                    (1, 1, -1, 1, 0, 0, 1, 1),
                    (1, -1, -1, 1, 0, 0, 0, 1),
                                  
                    (1, 1, -1, 0, 1, 0, 0, 0),   # third
                    (1, 1, 1, 0, 1, 0, 1, 0),
                    (-1, 1, 1, 0, 1, 0, 1, 1),
                    (-1, 1, -1, 0, 1, 0, 0, 1),
                                  
                    (1, -1, 1, 0, -1, 0, 0, 0),
                    (1, -1, -1, 0, -1, 0, 1, 0),
                    (-1, -1, -1, 0, -1, 0, 1, 1),
                    (-1, -1, 1, 0, -1, 0, 0, 1)
                    ])

def Init():
    global _shader
    global _vbo
    global _verts
    global _uniformInv
    global _position
    global _color
    global _vertex_normal

    global _uv_coords

    _VERTEX_SHADER = shaders.compileShader("""
        uniform mat4 inv;
        attribute vec3 position;
        uniform vec3 color;
        attribute vec3 vertex_normal;
        varying vec4 vertex_color;
                                           
        attribute vec2 inTexCoord;
        varying vec2 vertexTexCoord;
                                           
        void main()
        {
            gl_Position = gl_ModelViewProjectionMatrix * vec4(position, 1.0);
            vec4 light = inv * vec4(0, 0, 1, 0);
            float dt = dot(light.xyz, vertex_normal);
            float mult = max(min(dt, 1.0), 0.0);
            vertex_color = vec4(color * mult, 1.0);
                                           
            vertexTexCoord = inTexCoord;
        }
    """, GL_VERTEX_SHADER)

    _FRAGMENT_SHADER = shaders.compileShader("""
        varying vec4 vertex_color;
                                             
        varying vec2 vertexTexCoord;
        uniform sampler2D myTex;
                                             
        void main()
        {
            gl_FragColor = texture(myTex, vertexTexCoord) * vertex_color;
        }
    """, GL_FRAGMENT_SHADER)

    _shader = shaders.compileProgram(_VERTEX_SHADER, _FRAGMENT_SHADER)
    _vbo = vbo.VBO(_verts)

    _uniformInv = glGetUniformLocation(_shader, "inv")
    _position = glGetAttribLocation(_shader, "position")
    _color = glGetUniformLocation(_shader, "color")
    _vertex_normal = glGetAttribLocation(_shader, "vertex_normal")

    _uv_coords = glGetAttribLocation(_shader, "inTexCoord")

class Cube:
    def __init__(self, localPos, color=([0,0,1]), filepath="blueberryI.png"):
        #super().__init__()
        self.color = np.asfarray(color)
        self.ang = 0
        self.axis = (3,1,1)
        self.localPos = localPos   # Takes local positions of the current cube from pieces

        self.filepath = filepath

        #Generate the texture
        self.fruit_texture = Texture(self.filepath)

    def GetCubePos(self):
        return self.localPos

    def SetCubePos(self, newPos):
        self.localPos = newPos

    # Rotation function for cube
    '''def Rotate(self, angle, axis):
        self.ang += angle
        rotation_matrix = axis_rotation_matrix(angle, axis)
        self.localPos = np.dot(self.localPos, rotation_matrix)'''

    def Update(self, deltaTime, move):
        self.ang += 50.0 * deltaTime
        #self.localPos += move

    def _DrawBlock(self):
        global _shader
        global _vbo
        global _verts
        global _uniformInv
        global _position
        global _color
        global _vertex_normal
        global _uv_coords

        
        #Set the texture of the block
        self.fruit_texture.use()


        shaders.glUseProgram(_shader)

        inv = np.linalg.inv(glGetDouble(GL_MODELVIEW_MATRIX))
        glUniformMatrix4fv(_uniformInv, 1, False, inv)
        glUniform3fv(_color, 1, self.color)

        try:
            _vbo.bind()
            try:
                glEnableVertexAttribArray(_position)
                glEnableVertexAttribArray(_vertex_normal)
                glEnableVertexAttribArray(_uv_coords)
                stride = 32
                glVertexAttribPointer(_position, 3, GL_FLOAT, False, stride, _vbo)
                glVertexAttribPointer(_vertex_normal, 3, GL_FLOAT, True, stride, _vbo+12)
                glVertexAttribPointer(_uv_coords, 2, GL_FLOAT, True, stride, _vbo+24)
                glDrawArrays(GL_QUADS, 0, 24)
            finally:
                _vbo.unbind()
                glDisableVertexAttribArray(_position)
                glDisableVertexAttribArray(_vertex_normal)
                glDisableVertexAttribArray(_uv_coords)
        finally:
            shaders.glUseProgram(0)
    
    #DIFF HERE

    def Render(self, scale_factor=0.75, block_spacing=0.25):  # Change these 2 values to adjust size
        #m = glGetDouble(GL_MODELVIEW_MATRIX)

        glPushMatrix()
        #glTranslatef(*self.localPos)     # Translates the local position of each cube from pieces.py
        glScalef(scale_factor, scale_factor, scale_factor)
        adjusted_translation = [pos * (scale_factor + block_spacing) for pos in self.localPos]
        glTranslatef(*adjusted_translation)
        #glRotatef(self.ang, *self.axis)
        self._DrawBlock()
        glPopMatrix()

        #glLoadMatrixf(m)


# rotation matrix quaternians
def axis_rotation_matrix(angle, axis):
        axis = np.asarray(axis)
        axis = axis / np.sqrt(np.dot(axis, axis))
        a = np.cos(angle / 2.0)
        b, c, d = -axis * np.sin(angle / 2.0)
        aa, bb, cc, dd = a * a, b * b, c * c, d * d
        bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
        return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                        [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                        [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])