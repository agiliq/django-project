# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2007 ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 2 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2007-09-04 13:26:38 +0200 (Di, 04 Sep 2007) $"

from reportlab.lib.units import inch, cm
from reportlab.lib.styles import *
from reportlab.lib.enums import *
from reportlab.lib.colors import *
from reportlab.lib.pagesizes import *
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import *
from reportlab.platypus.flowables import Flowable
# from reportlab.platypus.para import Para, PageNumberObject, UNDERLINE, HotLink

import reportlab
import copy
import types
import os
import os.path
import pprint
import sys

try:
    import pyPdf
except:
    pyPdf = None
    
try:
    from reportlab.graphics import renderPM
except:
    renderPM = None

try:
    from reportlab.graphics import renderSVG
except:
    renderSVG = None

def ErrorMsg():
    """
    Helper to get a nice traceback as string
    """
    import traceback, sys, cgi
    type = value = tb = limit = None
    type, value, tb = sys.exc_info()
    list = traceback.format_tb(tb, limit) + traceback.format_exception_only(type, value)
    return "Traceback (innermost last):\n" + "%-20s %s" % (
        string.join(list[:-1], ""), 
        list[-1])

def toList(value):
    if type(value) not in (types.ListType, types.TupleType):
        return [value]
    return list(value)

def getColor(c):
    " Convert to color value "
    try:
        c = str(c).lower()       
        if c=="transparent" or c=="none":
            return None
        if c.startswith("#") and len(c)==4:
            c = "#" + c[1] + c[1] + c[2] + c[2] + c[3] + c[3]
        return toColor(c) # XXX Throws illegal Exception e.g. toColor('none')
    except Exception, e:
        print e
        # warning(e)
        pass
    return None

mm = cm / 10.0
dpi96 = (1.0 / 96.0 * inch)

def getSize(value, relative=0):
    """
    Converts strings to standard sizes   
    """
    try:
        s = value
        if type(s)==types.TupleType:
            s = "".join(s)
        s = str(s).strip().lower().replace(",", ".")    
        if s[-2:]=='cm': 
            return float(s[:-2].strip()) * cm
        elif s[-2:]=='mm': 
            return (float(s[:-2].strip()) * mm) # 1mm = 0.1cm
        elif s[-2:]=='in': 
            return float(s[:-2].strip()) * inch # 1pt == 1/72inch
        elif s[-2:]=='inch': 
            return float(s[:-4].strip()) * inch # 1pt == 1/72inch
        elif s[-2:]=='pt': 
            return float(s[:-2].strip())
        elif s[-2:]=='pc': 
            return float(s[:-2].strip()) * 12.0 # 1pt == 12pt
        elif s[-2:]=='px': 
            return float(s[:-2].strip()) * dpi96 # XXX W3C says, use 96pdi http://www.w3.org/TR/CSS21/syndata.html#length-units
        elif s[-1:]=='i':  # 1pt == 1/72inch
            return float(s[:-1].strip()) * inch
        elif s[-2:]=='em': # XXX
            return (float(s[:-2].strip()) * relative) # 1em = 1 * fontSize
        elif s[-2:]=='ex': # XXX
            return (float(s[:-2].strip()) * 2.0) # 1ex = 1/2 fontSize
        elif s[-1:]=='%': 
            # print "%", s, relative, (relative * float(s[:-1].strip())) / 100.0
            return (relative * float(s[:-1].strip())) / 100.0 # 1% = (fontSize * 1) / 100
        elif s in ("normal", "inherit"):
            return relative
        elif s in ("none", "0", "auto"):
            return 0.0
        return float(s)
    except Exception, e:
        # print "ERROR getSize", repr(value), repr(s), e        
        return 0.0
    
def getCoords(x, y, w, h, pagesize):
    """
    As a stupid programmer I like to use the upper left
    corner of the document as the 0,0 coords therefore
    we need to do some fancy calculations
    """
    #~ print pagesize
    ax, ay = pagesize
    if x < 0:
        x = ax + x
    if y < 0:
        y = ay + y
    if w != None and h != None:
        if w <= 0:
            w = (ax - x + w)
        if h <= 0:
            h = (ay - y + h)
        return x, (ay - y - h), w, h
    return x, (ay - y)

def getBox(s, pagesize):
    """
    Parse sizes by corners in the form: 
    <X-Left> <Y-Upper> <Width> <Height>
    The last to values with negative values are interpreted as offsets form
    the right and lower border.
    """
    l = s.split()
    if len(l)<>4:
        raise Exception, "box not defined right way"
    x, y, w, h = map(getSize, l)
    return getCoords(x, y, w, h, pagesize)

def getPos(s, pagesize):
    """
    Pair of coordinates
    """
    l = string.split(s)
    if len(l)<>2:
        raise Exception, "position not defined right way"
    x, y = map(getSize, l)
    return getCoords(x, y, None, None, pagesize)

def getBool(s):
    " Is it a boolean? "
    return str(s).lower() in ("y","yes","1","true")

_uid = 0
def getUID():
    " Unique ID "
    global _uid
    _uid += 1
    return str(_uid)

_alignments = {
    "left": TA_LEFT,
    "center": TA_CENTER,
    "middle": TA_CENTER, 
    "right": TA_RIGHT,
    "justify": TA_JUSTIFY, 
    }

def getAlign(value):
    return _alignments.get(value.lower(), TA_LEFT)

def getVAlign(value):
    # Unused
    return value.upper()

