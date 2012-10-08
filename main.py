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

import pyglet
from pyglet.gl import *

def init():

    # Disable error checking for increased performance
    pyglet.options['debug_gl'] = False

    from random import random

    import euclid
    from euclid import Vector3, Point3, Matrix4
    import math

    import ui2d
    import ui3d

    import ctypes

    from parameter import Parameter, Color3

    
    from pyglet.window import mouse, key

    from shader import Shader

    from camera import Camera
    from object3d import Scene, Object3d
    
    import numpy as np


    '''
    try:
        # Try and create a window with multisampling (antialiasing)
        config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True,)
        window = pyglet.window.Window(720, 360, resizable=True, config=config)
    except pyglet.window.NoSuchConfigException:
        # Fall back to no multisampling for old hardware
        window = pyglet.window.Window(resizable=True)
    '''
    window = pyglet.window.Window(600, 300, resizable=True)
    window.set_location(1200, 800)


    def setup():
        # One-time GL setup
        glClearColor(0.4, 0.4, 0.4, 1)


    scene = Scene()
    pyglet.clock.schedule(scene.update)
    

    scene.camera = Camera(window)

    setup()


    ui = ui2d.Ui(window, layoutw=0.35)
    ui.control_types['numeric'] += [euclid.Point3, euclid.Vector3]
    ui.control_types['color'] +=  [Color3]

    import ptc
    from ptc import Ptc

    import sys
    pointclouds = []
    for filename in sys.argv[1:]:
        pointcloud = ptc.Ptc(scene, filename)
        pointclouds.append( pointcloud )
    
    window.push_handlers(ptc.on_mouse_drag)
    ui.layout.addParameter(ui, pointcloud.frame)

    #p = Parameter(object=ptc2, attr="translate")
    #ui.layout.addParameter(ui, p)

    # class variables, global
    ui.layout.addParameter(ui, Ptc.ptsize)
    ui.layout.addParameter(ui, Ptc.gamma)
    ui.layout.addParameter(ui, Ptc.exposure)


    scene.camera.fieldofview = Parameter(object=scene.camera, attr="fov", update=scene.camera.update_projection, vmin=5, vmax=150)
    ui.layout.addParameter(ui, scene.camera.fieldofview)

    window.push_handlers(scene)

    pyglet.app.run()

    # import cProfile
    # cProfile.run('pyglet.app.run()', '/tmp/pyprof')
    # import pstats
    # stats = pstats.Stats('/tmp/pyprof')
    # stats.sort_stats('time')
    # stats.print_stats(25)

    # print 'INCOMING CALLERS:'
    # stats.print_callers(25)

    # print 'OUTGOING CALLEES:'
    # stats.print_callees(25)

if __name__ == "__main__":
    init()