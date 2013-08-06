
#  Filename : svg.py
#  Author   : Tomasz Lenarcik
#  Date     : 04/06/2013
#  Purpose  : Saves each stroke to an SVG file

import bpy
import freestyle
import os
import io

# find attributes of the current scene

scene = bpy.context.scene

frame = scene.frame_current
width = scene.render.resolution_x * scene.render.resolution_percentage / 100.0
height = scene.render.resolution_y * scene.render.resolution_percentage / 100.0

# create output file

filepath = bpy.path.abspath(scene.render.filepath)
# TODO: use render.filepath to set prefix
filename = '{0:04}.svg'.format(frame)
output = open(os.path.join(filepath,filename),'w')

# SVG "preamble"
output.write('<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="{0} {1} {2} {3}">\n'.format(0,0,width,height));   

# basic SVG commands

def moveTo(point):
    return 'M{0:.2f},{1:.2f}'.format(point.x,height-point.y)

def lineTo(point):
    return 'L{0:.2f},{1:.2f}'.format(point.x,height-point.y)

class SVGShader(freestyle.StrokeShader):
    def __init__(self, output):
        super(SVGShader, self).__init__()
        self.output = output
        
    def shade(self, stroke):
        #TODO: use stroke color
        path = ""
        it = stroke.stroke_vertices_begin()
        path += moveTo(it.object.point)
        # initialize attributes and counting
        thickness = it.object.attribute.thickness.copy()
        nVertices = 1
        while True:
            it.increment()
            if it.is_end:
                break
            path += ' ' + lineTo(it.object.point)
            nVertices += 1
            # accumulate attributes
            thickness += it.object.attribute.thickness
        #end: while          
        self.output.write('<path d="{0}" fill="none" stroke="{1}" stroke-width="{2:.2f}" />\n'.format(
            path, "black", (thickness.x + thickness.y) / (2 * nVertices)
        ))
    #end: shade

from freestyle import ChainSilhouetteIterator, ConstantColorShader, ConstantThicknessShader, \
    Operators, PolygonalizationShader, QuantitativeInvisibilityUP1D, SamplingShader, TrueUP1D
from logical_operators import NotUP1D

Operators.select(QuantitativeInvisibilityUP1D(0))
Operators.bidirectional_chain(ChainSilhouetteIterator(), NotUP1D(QuantitativeInvisibilityUP1D(0)))
shaders_list = [
        SamplingShader(2.0),
        ConstantThicknessShader(3),
        ConstantColorShader(0.0, 0.0, 0.0),
        SVGShader(output),
    ]
Operators.create(TrueUP1D(), shaders_list)

shaders_list = [
        SamplingShader(2.0),
        ConstantThicknessShader(1),
        ConstantColorShader(0.0, 0.0, 0.0),
        PolygonalizationShader(8),
        SVGShader(output),
    ]
Operators.create(TrueUP1D(), shaders_list)

output.write('</svg>');
output.close()
