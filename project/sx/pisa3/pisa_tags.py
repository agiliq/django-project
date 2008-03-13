# -*- coding: utf-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2007 ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 20 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2007-10-09 12:58:24 +0200 (Di, 09 Okt 2007) $"
__svnid__   = "$Id: pml.py 20 2007-10-09 10:58:24Z holtwick $"

from pisa_util import *
from pisa_reportlab import *
from pisa_default import DEFAULT_CSS

from reportlab.platypus.paraparser import ParaParser, ParaFrag, ps2tt, ABag
from reportlab.platypus.paragraph import cleanBlockQuotedText
from reportlab.platypus.flowables import *
from reportlab.lib.styles import ParagraphStyle

import pprint
import os
import re

class pisaTag:

    """
    The default class for a tag definition
    """
    
    def __init__(self, node, attr):
        self.node = node
        self.tag = node.tagName
        self.attr = attr
        
    def start(self, c):
        pass
    
    def end(self, c):
        pass    

class pisaTagTITLE(pisaTag):
    def end(self, c):
        c.meta["title"] = c.text
        c.clearFrag()

class pisaTagSTYLE(pisaTag):
    def start(self, c):
        c.addPara()
    def end(self, c):        
        c.clearFrag()

class pisaTagMETA(pisaTag):
    def start(self, c):
        name = self.attr.name.lower()
        if name in ("author" , "subject", "keywords"):
            c.meta[name] = self.attr.content
        
class pisaTagSUP(pisaTag):
    def start(self, c):
        c.frag.super = 1
        
class pisaTagSUB(pisaTag):
    def start(self, c):
        c.frag.sub = 1

class pisaTagA(pisaTag):

    rxLink = re.compile("^(#|[a-z]+\:).*")
    
    def start(self, c):
        attr = self.attr
        if attr.name:
            afrag = c.newFrag(cbDefn = ABag(
                kind = "anchor",
                name = attr.name,
                label = "anchor"
                ))
            c.fragAnchor.append(afrag)
            c.anchorName.append(attr.name)
        if attr.href and self.rxLink.match(attr.href):            
            c.frag.link = attr.href

    def end(self, c):
        pass   
    
class pisaTagP(pisaTag):
    def start(self, c):
        # save the type of tag; it's used in PmlBaseDoc.afterFlowable()
        # to check if we need to add an outline-entry
        # c.frag.tag = self.tag
        if self.attr.align is not None:
            #print self.attr.align, getAlign(self.attr.align)
            c.frag.alignment = getAlign(self.attr.align)

class pisaTagDIV(pisaTagP): pass
class pisaTagH1(pisaTagP): pass
class pisaTagH2(pisaTagP): pass
class pisaTagH3(pisaTagP): pass
class pisaTagH4(pisaTagP): pass
class pisaTagH5(pisaTagP): pass
class pisaTagH6(pisaTagP): pass

def listDecimal(c):
    c.listCounter += 1
    return unicode("%d." % c.listCounter)

_bullet = u"\u2022"
_list_style_type = {
    "none": u"",
    "disc": _bullet,
    "circle": _bullet, # XXX PDF has no equivalent
    "square": _bullet, # XXX PDF has no equivalent
    "decimal": listDecimal, 
    "decimal-leading-zero": listDecimal, 
    "lower-roman": listDecimal,      
    "upper-roman": listDecimal, 
    "hebrew": listDecimal,     
    "georgian": listDecimal,  
    "armenian": listDecimal,  
    "cjk-ideographic": listDecimal,  
    "hiragana": listDecimal,  
    "katakana": listDecimal, 
    "hiragana-iroha": listDecimal, 
    "katakana-iroha": listDecimal, 
    "lower-latin": listDecimal, 
    "lower-alpha": listDecimal, 
    "upper-latin": listDecimal, 
    "upper-alpha": listDecimal, 
    "lower-greek": listDecimal,  
}

class pisaTagUL(pisaTagP):
    
    def start(self, c):  
        self.counter, c.listCounter = c.listCounter, 0       

    def end(self, c):        
        c.addPara()        
        # XXX Simulate margin for the moment                
        c.addStory(Spacer(width=1, height=c.fragBlock.spaceAfter))
        c.listCounter = self.counter        

class pisaTagOL(pisaTagUL): 
    pass

class pisaTagLI(pisaTag):

    def start(self, c):
        lst = _list_style_type.get(c.frag.listStyleType or "disc", _bullet)
        if type(lst) == type(u""):
            c.frag.bulletText = [c.newFrag(text=lst)]
        else:
            c.frag.bulletText = [c.newFrag(text=lst(c))]
    
    #def end(self, c):
    #    c.addPara()
    
class pisaTagBR(pisaTag): 
    
    def start(self, c):
        # print "BR", c.text[-40:]
        c.frag.lineBreak = 1 
        c.addFrag()
        c.fragStrip = True
        del c.frag.lineBreak 
        
class pisaTagIMG(pisaTag):

    def start(self, c):
        c.addPara() 
            
    def start(self, c):
        c.addPara()
        attr = self.attr        
        if attr.src:
            if attr.src.lower().endswith("svg"):
                # self.next_para()
                img = PmlSVG(attr.src, attr.width, attr.height)
                img.hAlign = string.upper(attr.align)
                img.spaceBefore = c.frag.spaceBefore
                img.spaceAfter = c.frag.spaceAfter                
                c.addStory(img)
            else:
                try:
                    # oldnextstyle = self.nextstyle
                    # self.next_para(style="img")
                    _width = attr.width 
                    _height = attr.height 
                    _img = PmlImage(attr.src, _width, _height) #, kind="proportional") #, lazy=2)
                    # _img.hAlign = attr.align.upper()
                    _img.hAlign = "LEFT" 
                    _img.pisaZoom = c.frag.zoom
                    if (_width is None) and (_height is not None):
                        factor = float(_height) / _img.imageHeight
                        _img.drawWidth = _img.imageWidth * factor
                    elif (_height is None) and (_width is not None):
                        factor = float(_width) / _img.imageWidth
                        _img.drawHeight = _img.imageHeight * factor
                    elif (_width is None) and (_height is None):                        
                        _img.drawWidth = _img.drawWidth * dpi96
                        _img.drawHeight = _img.drawHeight * dpi96
                        
                    # print 888,                    _img.drawWidth, c.frag.zoom,  _img.drawHeight  
                    _img.drawWidth *= _img.pisaZoom
                    _img.drawHeight *= _img.pisaZoom
                    _img.spaceBefore = c.frag.spaceBefore
                    _img.spaceAfter = c.frag.spaceAfter
                  
                    c.addStory(_img)
                    
                except Exception, e:
                    c.warning("Error in handling image '%s': %s" % (attr.src, str(e)))
        else:
            c.warning("File '%s' does not exist." % attr.src)
            
        c.addPara()
       
class pisaTagHR(pisaTag):

    def start(self, c):
        c.addPara()
        c.addStory(HRFlowable(
            color = self.attr.color,
            thickness = self.attr.size,
            width = "100%",
            spaceBefore = c.frag.spaceBefore,
            spaceAfter = c.frag.spaceAfter
            ))

# ============================================

class pisaTagPDFNEXTPAGE(pisaTag):    
    """
    <pdf:nextpage name="" />
    """
    def start(self, c):
        c.addPara()
        if self.attr.name:
            c.addStory(NextPageTemplate(self.attr.name))
        c.addStory(PageBreak())
        
class pisaTagPDFNEXTTEMPLATE(pisaTag):    
    """
    <pdf:nexttemplate name="" />
    """
    def start(self, c):
        c.addStory(NextPageTemplate(self.attr["name"]))

    
class pisaTagPDFNEXTFRAME(pisaTag):    
    """
    <pdf:nextframe name="" />
    """
    def start(self, c):
        c.addPara()
        c.addStory(FrameBreak())

class pisaTagPDFSPACER(pisaTag):    
    """
    <pdf:spacer height="" />
    """
    def start(self, c):
        c.addPara()
        c.addStory(Spacer(1, self.attr.height))

class pisaTagPDFPAGENUMBER(pisaTag):    
    """
    <pdf:pagenumber example="" />
    """   
    def start(self, c):
        c.frag.pageNumber = True 
        c.addFrag(self.attr.example)
        c.frag.pageNumber = False
        
class pisaTagPDFFRAME(pisaTag):    
    """
    <pdf:frame name="" static box="" />
    """
    def start(self, c):
        attrs = self.attr       

        name = attrs["name"]        
        if name is None:
            name = "frame%d" % c.UID()
        
        x, y, w, h = attrs.box
        self.frame = Frame(
                x, y, w, h, 
                id=name, 
                leftPadding=0, 
                rightPadding=0, 
                bottomPadding=0, 
                topPadding=0, 
                showBoundary=attrs.border)
        
        self.static = False
        if self.attr.static:
            self.static = True
            c.addPara()
            self.story = c.swapStory()
        else:
            c.frameList.append(self.frame)

    def end(self, c):
        if self.static:
            c.addPara()
            self.frame.pisaStaticStory = c.story
            c.frameStaticList.append(self.frame)
            c.swapStory(self.story)

class pisaTagPDFTEMPLATE(pisaTag):    
    """
    <pdf:template name="" static box="" >
        <pdf:frame...>
    </pdf:template>
    """
    def start(self, c):
        attrs = self.attr    
        #print attrs
        name = attrs["name"]
        c.frameList = []
        c.frameStaticList = []
        if c.templateList.has_key(name):
            self.warning("template '%s' has already been defined" % name)
       
        '''
        self.oldpagesize = A4 # self._pagesize

        self._pagesize = PML_PAGESIZES[attrs.format]
        if attrs.orientation is not None:
            if attrs.orientation == "landscape":
                self._pagesize = landscape(self._pagesize)
            elif attrs.orientation == "portrait":
                self._pagesize = portrait(self._pagesize)
        '''
        
        # self._drawing = PmlPageDrawing(self._pagesize)

    def end(self, c):
        
        attrs = self.attr 
        name = attrs["name"]
        if len(c.frameList) <= 0:
            c.error("missing frame definitions for template")
            
        pt = PmlPageTemplate(
            id = name, 
            frames = c.frameList, 
            pagesize = A4,
            ) 
        pt.pisaStaticList = c.frameStaticList
        pt.pisaBackgroundList = c.pisaBackgroundList
        pt.pisaBackground = self.attr.background
        
        # self._pagesize)
        # pt.pml_statics = self._statics
        # pt.pml_draw = self._draw
        # pt.pml_drawing = self._drawing
        # pt.pml_background = attrs.background
        # pt.pml_bgstory = self._bgstory

        c.templateList[name] = pt
        c.template = None
        c.frameList = []
        c.frameStaticList = []

class pisaTagPDFFONT(pisaTag):    
    """
    <pdf:fontembed name="" src="" />
    """
    def start(self, c):
        c.loadFont(self.attr.name, self.attr.src, self.attr.encoding)
