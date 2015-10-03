#!/usr/bin/env python

'''
    enw.py
    Copyright (C) 2012 Rhys Owen, rhysun@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

        A
        |\
        | \
        |  \
        |   \
        |    \
       b|     \h
        |      \
        |       \
        |_       \
        |_|_______\
       C     a     B
'''

import inkex, simplepath, simpletransform
from math import *
import gettext
_ = gettext.gettext

def poltocar(r, rad, negx=False, negy=False):
    # converts polar coords to cartesian
    x = r * cos(rad)
    y = r * sin(rad)
    if negx and not negy:
        return [-x, y]
    elif not negx and negy:
        return [x, -y]
    elif not negx and not negy:
        return [-x, -y]
    else:
        return [x, y]

def deuclid(x1, y1, x2, y2):
    # euclidean distance between two cartesian coords
    squarex = (x1 - x2)**2
    squarey = (y1 - y2)**2
    d = sqrt(squarex + squarey)
    return d

def getAngle(b, h):
    angle = asin(b / h)
    return angle

def aLength(b, h):
    # the Pythagorean theorem
    a = sqrt(h**2-b**2)
    return a


def getPathData(obj):
    if obj.get("d"):# If the selected circle is defined as a path object
        d = obj.get("d")
        p = simplepath.parsePath(d)
        if obj.get("transform"):
            trans = simpletransform.parseTransform(obj.get("transform"))
            scalex = trans[0][0]
            scaley = trans[1][1]
            data = {'rx' : p[1][1][0]*scalex,
                    'ry' : p[1][1][1]*scaley,
                    'x' : (trans[0][0]*p[0][1][0])+(trans[0][1]*p[0][1][1])+trans[0][2]-(p[1][1][0]*scalex),
                    'y' : (trans[1][0]*p[0][1][0])+(trans[1][1]*p[0][1][1])+trans[1][2]}
        else:
            data = {'rx': p[1][1][0],
                    'ry': p[1][1][1],
                    'x' : p[0][1][0]-p[1][1][0],
                    'y' : p[0][1][1]}
    elif obj.get("r"):# If the selected circle is defined as a circle object
        r = obj.get("r")
        cx = obj.get("cx")
        cy = obj.get("cy")
        data = {'rx' : float(r),
                'ry' : float(r),
                'x' : float(cx),
                'y' : float(cy)}
    elif obj.get("rx"):# If the selected circle is defined as an ellipse
        rx = obj.get("rx")
        ry = obj.get("ry")
        cx = obj.get("cx")
        cy = obj.get("cy")
        data = {'rx' : float(rx),
                'ry' : float(ry),
                'x' : float(cx),
                'y' : float(cy)}
    else:
        stockErrorMsg("4")# for quick bug id

    return data


def stockErrorMsg(errID):
    inkex.errormsg(_("Please select exactly two circles and try again! %s" % errID))
    exit()

class Tangent(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("-p", "--position",
                        action="store", type="string",
                        dest="position", default="inner",
                        help=_("Choose either inner or outer tangent lines"))
    def effect(self):
        if len(self.options.ids) != 2:
            stockErrorMsg("1")
            
        c1object = self.selected[self.options.ids[0]]
        c2object = self.selected[self.options.ids[1]]

        c1 = getPathData(c1object)
        c2 = getPathData(c2object)

        # Create a third 'virtual' circle
        if c1['rx'] <= c2['rx']:
            c3x = c2['x']
            c3y = c2['y']
            if self.options.position == "outer":
                c3r = c2['rx'] - c1['rx']
            else:
                c3r = c2['rx'] + c1['rx']
            cyfA = [c1['x'], c1['y']]
            cyfB = [c2['x'], c2['y']]
        elif c1['rx'] > c2['rx']:
            c3x = c1['x']
            c3y = c1['y']
            if self.options.position == "outer":
                c3r = c1['rx'] - c2['rx']
            else:
                c3r = c1['rx'] + c2['rx']
            cyfA = [c2['x'], c2['y']]
            cyfB = [c1['x'], c1['y']]

        # Test whether the circles are actually circles!
        if c1['rx'] != c1['ry'] or c2['rx'] != c2['ry']:
            stockErrorMsg("One or both objects may be elliptical.")

        # Hypotenws y triongl - pellter euclidaidd rhwng c1 x,y a c2 x,y.
        # The hypotenuse of the triangle - euclidean distance between point c1 x,y and point c2 x,y
        h = deuclid(c1['x'], c1['y'], c2['x'], c2['y'])
        b = c3r
        B = getAngle(b, h)
        a = aLength(b, h)
        # Ongl yr hypotenws i echelin x
        # The angle of the hypotenuse to the x axis
        E = getAngle(max(c1['y'], c2['y']) - min(c1['y'], c2['y']), h)

        # I destio os ydi'r cylch lleiaf yn is na'r llall
        # Test whether the smallest circle is below the other
        if cyfB[1] <= cyfA[1]:
            negx = False
        else:
            negx = True

        # I destio os ydi'r cylch lleiaf i'r dde o'r llall
        # Test whether the smallest circle is to the right of the other
        if cyfB[0] <= cyfA[0]:
            negy = False
        else:
            negy = True

        onglTop = -B+E
        onglGwaelod = B+E
        if self.options.position == "outer":# Allanol
            perptop = -(pi/2)
            perpgwaelod = pi/2
        else:# Mewnol
            perptop = pi/2
            perpgwaelod = -(pi/2)

        # Cyfesurynnau pen y llinell top
        cyfC = poltocar(a, onglTop, negx, negy)
        # Gwybodaeth er mwyn trosi'r cyfesurynnau top 90gradd
        trositop = poltocar(min(c1['rx'], c2['rx']), perptop+onglTop, negx, negy)#1.5707964 1.57079632679

        # Cyfesurynnau pen y llinell gwaelod
        cyfD = poltocar(a, onglGwaelod, negx, negy)
        # Gwybodaeth er mwyn trosi'r cyfesurynnau gwaelod 90gradd
        trosigwaelod = poltocar(min(c1['rx'], c2['rx']), perpgwaelod+onglGwaelod, negx, negy)

        # Tynnu llinell
        llx1 = cyfA[0]
        lly1 = cyfA[1]
        llsteil = (c1object.get("style"))

        # Llinell 1
        ll1x2 = cyfC[0]
        ll1y2 = cyfC[1]
        enw = "llinell"
        rhiant = self.getParentNode(c1object)

        attribsLlinell = {'style':llsteil,
                        inkex.addNS('label','inkscape'):enw,
                        'd':'m '+str(llx1+trositop[0])+','+str(lly1+trositop[1])+' l '+str(ll1x2)+','+str(ll1y2)}
        elfen1 = inkex.etree.SubElement(rhiant, inkex.addNS('path','svg'), attribsLlinell )

        #Llinell 2
        ll2x2 = cyfD[0]
        ll2y2 = cyfD[1]
        enw = "llinell"
        rhiant = self.getParentNode(c1object)

        attribsLlinell = {'style':llsteil,
                        inkex.addNS('label','inkscape'):enw,
                        'd':'m '+str(llx1+trosigwaelod[0])+','+str(lly1+trosigwaelod[1])+' l '+str(ll2x2)+','+str(ll2y2)}
        inkex.etree.SubElement(rhiant, inkex.addNS('path','svg'), attribsLlinell )

if __name__ == '__main__':
    e = Tangent()
    e.affect()

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
