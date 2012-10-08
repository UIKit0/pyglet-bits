# ##### BEGIN MIT LICENSE BLOCK #####
#
# Copyright (c) 2012 Matt Ebb
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 
#
# ##### END MIT LICENSE BLOCK #####

import platform
import math
from math import pi, sin, cos

import euclid
from euclid import Vector3, Point3, Matrix4

import pyglet
from pyglet.window import key
from pyglet.window import mouse
from pyglet.gl import *

from keys import keys

class CameraHandler(object):
    def __init__(self, window, camera):
        self.camera = camera
        self.window = window
        
        window.push_handlers(keys)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        
        if platform.system() != 'Darwin':
            dy = -dy

        if modifiers & pyglet.window.key.MOD_SHIFT:
            if buttons & mouse.RIGHT:
                self.camera.fov -= dx
                if self.camera.fov < 5.:
                    self.camera.fov = 5.
                elif self.camera.fov > 150:
                    self.camera.fov = 150
            
                winsize = self.window.get_size()
                self.camera.view_update(winsize[0], winsize[1])
                return pyglet.event.EVENT_HANDLED

        elif keys[key.SPACE]:
            if buttons & mouse.LEFT:
                s = 0.0075

                m = self.camera.matrix
                loc = Point3(*m[12:14]) # - self.camera.center   # translation part
                xaxis = Vector3(m[0], m[4], m[8])
                
                m.translate(*(-loc))
                m.rotate_axis(s*dy, xaxis).rotate_axis(s*dx, Vector3(0,1,0))
                m.translate(*(loc))

                
            if buttons & mouse.RIGHT:
                s = 0.05
                m = self.camera.matrix
                zaxis = Vector3(m[2], m[6], m[10])
                m.translate(*(zaxis*s*dx))
                self.camera.center -= zaxis*s*dx

            
            if buttons & mouse.MIDDLE:
                s = 0.01
                m = self.camera.matrix
                dist = abs(self.camera.center - Vector3(m[3], m[7], m[11])) * 0.5
                xaxis = Vector3(m[0], m[4], m[8])
                yaxis = Vector3(m[1], m[5], m[9])
                trans = Matrix4.new_translate(*(xaxis*s*dx*dist)).translate(*(yaxis*s*-dy*dist))
                
                m *= trans
                self.camera.center -= xaxis*s*dx + yaxis*s*-dy

            
            winsize = self.window.get_size()
            self.camera.view_update(winsize[0], winsize[1])
            return pyglet.event.EVENT_HANDLED

    def on_resize(self, width, height):
        self.camera.view_update(width, height)
        #return pyglet.event.EVENT_HANDLED


class Camera(object):

    def update_projection(self):
        width, height = self.window.get_size()
        self.persp_matrix = Matrix4.new_perspective(math.radians(self.fov), width / float(height), self.clipnear, self.clipfar)


    def __init__(self, window):
        self.phi = pi / 2.0
        self.theta = pi * 0.4
        self.radius = 10.
        self.fov = 50.
        self.clipnear = 0.1
        self.clipfar = 100000
        
        self.center = Vector3(0,0,0)

        self.matrix = Matrix4()
        self.persp_matrix = Matrix4()
        
        self.needs_update = True
        
        self.params = {}
        
        self.window = window
        handlers = CameraHandler(window, self)
        window.push_handlers(handlers)
        
        self.matrix = Matrix4().new_translate(0,-0.5,-6)

    def focus(self, center):
        self.matrix = Matrix4.new_look_at(Point3(self.matrix.d, self.matrix.h, self.matrix.l), center, Vector3(0,1,0))

    def project_ray(self, px, py):
        cam_view = (self.center - self.loc).normalize()
        
        self.cam_h =  cam_view.cross(self.up).normalize()
        self.cam_v = -1 * cam_view.cross(self.cam_h).normalize()
        
        half_v = math.tan(math.radians(self.fov)*0.5) * self.clipnear
        win = self.window.get_size()
        aspect = win[0] / float(win[1])
        half_h = half_v * aspect
        
        # mouse to ndc
        nx = (px - win[0]*0.5) / (win[0]*0.5)
        ny = (py - win[1]*0.5) / (win[1]*0.5)
        
        self.cam_h *= half_h
        self.cam_v *= half_v

        click = self.loc + (cam_view*self.clipnear)  + (nx * self.cam_h) + (ny * self.cam_v)

        '''
        modelview = (GLdouble * 16)()
        projection = (GLdouble * 16)()
        view = (GLint * 4)()
        
        glGetDoublev (GL_MODELVIEW_MATRIX, modelview);
        glGetDoublev (GL_PROJECTION_MATRIX, projection);
        glGetIntegerv( GL_VIEWPORT, view );
        
        wx,wy,wz = GLdouble(),GLdouble(),GLdouble() 
        gluUnProject(px, py, self.clipnear, modelview, projection, view, wx, wy, wz)
        click = Vector3(wx.value, wy.value, wz.value)
        '''
        dir = (click - self.loc).normalize()
        return click, dir
    
    def view_update(self, width, height):
        glViewport(0, 0, width, height)
        
        # match openGL format
        self.persp_matrix = Matrix4.new_perspective(math.radians(self.fov), width / float(height), self.clipnear, self.clipfar)

        
        
