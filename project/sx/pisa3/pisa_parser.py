# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2007 ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 20 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2007-10-09 12:58:24 +0200 (Di, 09 Okt 2007) $"
__svnid__   = "$Id: pml.py 20 2007-10-09 10:58:24Z holtwick $"

import pprint
import copy
import types
import re
import os
import os.path
import cStringIO

import html5lib
from html5lib import treebuilders, serializer, treewalkers
from xml.dom import Node
import xml.dom.minidom

from pisa_default import *
from pisa_util import *
from pisa_tags import *
from pisa_tables import *

from sx.w3c import css, cssDOMElementInterface

rxhttpstrip = re.compile("http://[^/]+(.*)", re.M|re.I)

class AttrContainer(dict):
      
    def __getattr__(self, name):       
        try:
            return dict.__getattr__(self, name)            
        except:
            return self[name]

def pisaGetAttributes(c, tag, attributes):
    global TAGS

    attrs = {}
    if attributes:
        for k, v in attributes.items():
            try:
                attrs[str(k)] = str(v) # XXX no Unicode! Reportlab fails with template names
            except:
                attrs[k] = v
                
    nattrs = {}
    if TAGS.has_key(tag):        
        block, adef = TAGS[tag]
        adef["id"] = STRING
        # print block, adef
        for k, v in adef.items():                
            nattrs[k] = None
            # print k, v
            # defaults, wenn vorhanden
            if type(v) == types.TupleType:
                if v[1] == MUST:
                    if not attrs.has_key(k):
                        c.error("attribute '%s' must be set!" % (k))
                nv = attrs.get(k, v[1])                    
                dfl = v[1]
                v = v[0]
            else:
                nv = attrs.get(k, None)
                dfl = None               
            try:
                if nv is not None:
                    
                    if type(v)==types.ListType:
                        nv = nv.strip().lower()
                        if nv not in v:
                            #~ raise PML_EXCEPTION, "attribute '%s' of wrong value, allowed is one of: %s" % (k, repr(v))
                            c.warning("attribute '%s' of wrong value, allowed is one of: %s" % (k, repr(v)))
                            nv = dfl

                    elif v == BOOL:
                        nv = nv.strip().lower()
                        nv = nv in ("1", "y", "yes", "true", str(k))

                    elif v == SIZE:
                        try:
                            nv = getSize(nv)
                        except:
                            c.error("attribute '%s' expects a size value" % (k))

                    elif v == BOX:
                        nv = getBox(nv, c.pageSize)

                    elif v == POS:
                        nv = getPos(nv, c.pageSize)

                    elif v == INT:
                        nv = int(nv)

                    elif v == COLOR:
                        nv = getColor(nv)
                    
                    elif v == FILE:
                        nv = c.getFile(nv)
                                                
                    elif v == FONT:
                        nv = c.getFontName(nv)

                    nattrs[k] = nv

            #for k in attrs.keys():
            #    if not nattrs.has_key(k):
            #        c.warning("attribute '%s' for tag <%s> not supported" % (k, tag))

            except Exception, e:
                msg = ErrorMsg()
                #print msg
                c.error(msg)

    #else:
    #    c.warning("tag <%s> is not supported" % tag)
   
    return AttrContainer(nattrs)


def getCSSAttr(self, cssCascade, attrName, default=NotImplemented):
    if attrName in self.cssAttrs:
        return self.cssAttrs[attrName]

    result = None

    attrValue = self.attributes.get(attrName, None)
    if attrValue is not None:
        result = cssCascade.parser.parseSingleAttr(attrValue.value)

    if result is None:
        result = cssCascade.findStyleFor(self.cssElement, attrName, default)

    if result == 'inherit':
        if hasattr(self.parentNode, 'getCSSAttr'):
            result = self.parentNode.getCSSAttr(cssCascade, attrName, default)
        elif default is not NotImplemented:
            return default
        else:
            raise LookupError("Could not find inherited CSS attribute value for '%s'" % (attrName,))

    self.cssAttrs[attrName] = result
    return result

xml.dom.minidom.Element.getCSSAttr = getCSSAttr

def pisaPreLoop(node, c, collect=False):
    """
    Collect all CSS definitions 
    """
    if node.nodeType == Node.TEXT_NODE and collect:
        c.addCSS(node.data)
        # c.debug(repr(node.data)
        
    elif node.nodeType == Node.ELEMENT_NODE:
        name = node.tagName.lower()

        # print name, node.attributes.items()
        if name in ("style", "link"):
            attr = pisaGetAttributes(c, name, node.attributes)
            # print " ", attr
            media = [x.strip() for x in attr.media.lower().split(",")]
            
            if (attr.type.lower() in ("", "text/css") and (
                "all" in media or
                "print" in media or
                "pdf" in media)):  
    
                if name=="style":
                    # print "CSS STYLE", attr
                    for node in node.childNodes:
                        pisaPreLoop(node, c, collect=True)
                    return 
                    #collect = True
                                
                if name=="link" and attr.href and attr.rel.lower()=="stylesheet":
                    # print "CSS LINK", attr
                    c.addCSS('\n@import "%s" %s;' % (attr.href, ",".join(media)))
                    # c.addCSS(unicode(file(attr.href, "rb").read(), attr.charset))

    #else:
    #    print node.nodeType

    for node in node.childNodes:
        pisaPreLoop(node, c, collect=collect)

attrNames = '''
    color
    font-family 
    font-size 
    font-weight
    font-style
    text-decoration
    line-height
    background-color
    display
    margin-left
    margin-right
    margin-top
    margin-bottom
    padding-left
    padding-right
    padding-top
    padding-bottom
    border-top-color
    border-top-style
    border-top-width
    border-bottom-color
    border-bottom-style
    border-bottom-width
    border-left-color
    border-left-style
    border-left-width
    border-right-color
    border-right-style
    border-right-width
    text-align
    vertical-align
    width
    height
    zoom
    page-break-after
    page-break-before
    list-style-type
    white-space
    text-indent
    -pdf-page-break
    -pdf-frame-break
    -pdf-next-page
    -pdf-keep-with-next
    -pdf-outline
    -pdf-outline-level
    -pdf-outline-open
    '''.strip().split()

def pisaLoop(node, c, path=[], **kw):

    # Initialize KW
    if not kw:
        kw = {
            "margin-top": 0,
            "margin-bottom": 0,
            "margin-left": 0,
            "margin-right": 0,
            }
    else:
        kw = copy.copy(kw)
        
    indent = len(path) * "  "

    # TEXT
    if node.nodeType == Node.TEXT_NODE:
        # print indent, "#", repr(node.data) #, c.frag
        c.addFrag(node.data)
        # c.text.append(node.value)
       
    # ELEMENT
    elif node.nodeType == Node.ELEMENT_NODE:  
        
        node.tagName = node.tagName.replace(":", "").lower()
        
        if node.tagName in ("style", "script"):
            return
        
        path = copy.copy(path) + [node.tagName]
        
        # Prepare attributes        
        attr = pisaGetAttributes(c, node.tagName, node.attributes)        
        c.debug(1, indent, "<%s %s>" % (node.tagName, attr), node.attributes.items()) #, path
        
        # Calculate styles
        c.cssAttr = {}        
        if c.css:
            node.cssElement = cssDOMElementInterface.CSSDOMElementInterface(node)
            node.cssAttrs = {}
            node.cssElement.onCSSParserVisit(c.cssCascade.parser)
    
            cssAttrMap = {}
            for cssAttrName in attrNames:
                try:
                    cssAttrMap[cssAttrName] = node.getCSSAttr(c.cssCascade, cssAttrName)
                except Exception, e:
                    # print indent, "CSSERR", cssAttrName, e
                    # print ErrorMsg()
                    pass
            
            # print indent, "STYLE", node.tagName, node.cssAttrs
            c.cssAttr = node.cssAttrs

        c.node = node

        # Block?    
        pageBreakAfter = False
        frameBreakAfter = False
        display = c.cssAttr.get("display", "inline").lower()
        # print indent, node.tagName, display, c.cssAttr.get("background-color", None), attr
        isBlock = (display == "block")
        if isBlock:
            c.addPara()

            # Page break by CSS
            if c.cssAttr.has_key("-pdf-next-page"):                 
                c.addStory(NextPageTemplate(str(c.cssAttr["-pdf-next-page"])))
            if c.cssAttr.has_key("-pdf-page-break"):
                if str(c.cssAttr["-pdf-page-break"]).lower() == "before":
                    c.addStory(PageBreak()) 
            if c.cssAttr.has_key("-pdf-frame-break"): 
                if str(c.cssAttr["-pdf-frame-break"]).lower() == "before":
                    c.addStory(FrameBreak()) 
                if str(c.cssAttr["-pdf-frame-break"]).lower() == "after":
                    frameBreakAfter = True
            if c.cssAttr.has_key("page-break-before"):            
                if str(c.cssAttr["page-break-before"]).lower() == "always":
                    c.addStory(PageBreak()) 
            if c.cssAttr.has_key("page-break-after"):            
                if str(c.cssAttr["page-break-after"]).lower() == "always":
                    pageBreakAfter = True
            
        if display == "none":
            # print "none!"
            return
        
        # Translate CSS to frags 

        # Save previous frag styles
        c.pushFrag()
        
        # COLORS
        if c.cssAttr.has_key("color"):            
            c.frag.textColor = getColor(c.cssAttr["color"])
        if c.cssAttr.has_key("background-color"):            
            c.frag.backColor = getColor(c.cssAttr["background-color"])
                
        # FONT SIZE, STYLE, WEIGHT
        if c.cssAttr.has_key("font-family"):
            c.frag.fontName = c.getFontName(c.cssAttr["font-family"])            
        if c.cssAttr.has_key("font-size"):
            # XXX inherit
            c.frag.fontSize  = getSize("".join(c.cssAttr["font-size"]), c.frag.fontSize)
        if c.cssAttr.has_key("line-height"):
            leading = "".join(c.cssAttr["line-height"])
            c.frag.leading  = getSize(leading, c.frag.fontSize)
            c.frag.leadingSource = leading
        else:
            c.frag.leading = getSize(c.frag.leadingSource, c.frag.fontSize)
        if c.cssAttr.has_key("font-weight"):   
            value = c.cssAttr["font-weight"].lower()        
            if value in ("bold", "bolder", "500", "600", "700", "800", "900"):
                c.frag.bold = 1
            else:
                c.frag.bold = 0
        for value in toList(c.cssAttr.get("text-decoration","")):               
            if "underline" in value:
                c.frag.underline = 1
            if "line-through" in value:
                c.frag.strike = 1                
            if "none" in value:
                c.frag.underline = 0
                c.frag.strike = 0
        if c.cssAttr.has_key("font-style"):   
            value = c.cssAttr["font-style"].lower()                        
            if value in ("italic", "oblique"):
                c.frag.italic = 1
            else:
                c.frag.italic = 0
        if c.cssAttr.has_key("white-space"):   
            # normal | pre | nowrap
            c.frag.whiteSpace = str(c.cssAttr["white-space"]).lower()
         
        # ALIGN & VALIGN
        if c.cssAttr.has_key("text-align"):
            c.frag.alignment = getAlign(c.cssAttr["text-align"])
        if c.cssAttr.has_key("vertical-align"):            
            c.frag.vAlign = c.cssAttr["vertical-align"]

        # HEIGHT & WIDTH
        if c.cssAttr.has_key("height"):  
            c.frag.height = "".join(toList(c.cssAttr["height"])) # XXX Relative is not correct!
            if c.frag.height in ("auto",):
                c.frag.height = None
        if c.cssAttr.has_key("width"):
            # print c.cssAttr["width"]  
            c.frag.width = "".join(toList(c.cssAttr["width"])) # XXX Relative is not correct!
            if c.frag.width in ("auto",):
                c.frag.width = None
                
        # ZOOM
        if c.cssAttr.has_key("zoom"):
            # print c.cssAttr["width"]  
            zoom = "".join(toList(c.cssAttr["zoom"])) # XXX Relative is not correct!
            if zoom.endswith("%"):
                zoom = float(zoom[:-1]) / 100.0
            c.frag.zoom = float(zoom)  
            
        # MARGINS & LIST INDENT, STYLE    
        if isBlock:    
            if c.cssAttr.has_key("margin-top"):  
                c.frag.spaceBefore = getSize(c.cssAttr["margin-top"], c.frag.fontSize)
            if c.cssAttr.has_key("margin-bottom"):  
                c.frag.spaceAfter = getSize(c.cssAttr["margin-bottom"], c.frag.fontSize)            
            if c.cssAttr.has_key("margin-left"):               
                c.frag.bulletIndent = kw["margin-left"] # For lists
                kw["margin-left"] += getSize(c.cssAttr["margin-left"], c.frag.fontSize)
                c.frag.leftIndent = kw["margin-left"]
                # print "MARGIN LEFT", kw["margin-left"], c.frag.bulletIndent      
            if c.cssAttr.has_key("margin-right"):
                kw["margin-right"] += getSize(c.cssAttr["margin-right"], c.frag.fontSize)
                c.frag.rigthIndent = kw["margin-right"] 
                # print c.frag.rigthIndent         
            if c.cssAttr.has_key("list-style-type"):  
                c.frag.listStyleType = str(c.cssAttr["list-style-type"]).lower()
            if c.cssAttr.has_key("text-indent"):
                c.frag.firstLineIndent = getSize(c.cssAttr["text-indent"], c.frag.fontSize)

        # PADDINGS
        if isBlock:
            if c.cssAttr.has_key("padding-top"):  
                c.frag.paddingTop = getSize(c.cssAttr["padding-top"], c.frag.fontSize)
            if c.cssAttr.has_key("padding-bottom"):  
                c.frag.paddingBottom = getSize(c.cssAttr["padding-bottom"], c.frag.fontSize)
            if c.cssAttr.has_key("padding-left"):  
                c.frag.paddingLeft = getSize(c.cssAttr["padding-left"], c.frag.fontSize)
            if c.cssAttr.has_key("padding-right"):  
                c.frag.paddingRight = getSize(c.cssAttr["padding-right"], c.frag.fontSize)

        # BORDERS
        if isBlock:
            if c.cssAttr.has_key("border-top-width"):  
                c.frag.borderTopWidth = getSize(c.cssAttr["border-top-width"], c.frag.fontSize)
            if c.cssAttr.has_key("border-bottom-width"):  
                c.frag.borderBottomWidth = getSize(c.cssAttr["border-bottom-width"], c.frag.fontSize)
            if c.cssAttr.has_key("border-left-width"):  
                c.frag.borderLeftWidth = getSize(c.cssAttr["border-left-width"], c.frag.fontSize)
            if c.cssAttr.has_key("border-right-width"):  
                c.frag.borderRightWidth = getSize(c.cssAttr["border-right-width"], c.frag.fontSize)
            if c.cssAttr.has_key("border-top-style"):  
                # XXX c.frag.borderWidth = getSize(c.cssAttr["border-top-style"], c.frag.fontSize)
                pass
            if c.cssAttr.has_key("border-top-color"):  
                c.frag.borderTopColor = getColor(c.cssAttr["border-top-color"])
            if c.cssAttr.has_key("border-bottom-color"):  
                c.frag.borderBottomColor = getColor(c.cssAttr["border-bottom-color"])
            if c.cssAttr.has_key("border-left-color"):  
                c.frag.borderLeftColor = getColor(c.cssAttr["border-left-color"])
            if c.cssAttr.has_key("border-right-color"):  
                c.frag.borderRightColor = getColor(c.cssAttr["border-right-color"])
                          
        # EXTRAS
        if c.cssAttr.has_key("-pdf-keep-with-next"):
            c.frag.keepWithNext = getBool(c.cssAttr["-pdf-keep-with-next"])
        if c.cssAttr.has_key("-pdf-outline"):
            c.frag.outline = getBool(c.cssAttr["-pdf-outline"])
        if c.cssAttr.has_key("-pdf-outline-level"):
            c.frag.outlineLevel = int(c.cssAttr["-pdf-outline-level"])
        if c.cssAttr.has_key("-pdf-outline-open"):
            c.frag.outlineOpen = getBool(c.cssAttr["-pdf-outline-open"])            
                          
        # BEGIN tag
        klass = globals().get("pisaTag%s" % node.tagName.replace(":", "").upper(), None)
        obj = None      

        # Static block
        elementId = attr.get("id", None)             
        staticFrame = c.frameStatic.get(elementId, None)
        if staticFrame:
            oldStory = c.swapStory()
                  
        # Tag specific operations
        if klass is not None:        
            obj = klass(node, attr)
            obj.start(c)
            
        # Visit child nodes
        c.fragBlock = fragBlock = copy.copy(c.frag)        
        for nnode in node.childNodes:
            pisaLoop(nnode, c, path, **kw)        
        c.fragBlock = fragBlock
                            
        # END tag
        if obj:
            obj.end(c)

        # Block?
        if isBlock:
            c.addPara()

            # XXX Buggy!

            # Page break by CSS
            if pageBreakAfter:
                c.addStory(PageBreak()) 
            if frameBreakAfter:                
                c.addStory(FrameBreak()) 

        # Static block, END
        if staticFrame:
            c.addPara()
            for frame in staticFrame:
                frame.pisaStaticStory = c.story            
            c.swapStory(oldStory)
            
        c.debug(1, indent, "</%s>" % (node.tagName))
        
        # Reset frag style                   
        c.pullFrag()                                    

    # Unknown or not handled
    else:
        # c.debug(1, indent, "???", node, node.nodeType, repr(node))
        # Loop over children
        for node in node.childNodes:
            pisaLoop(node, c, path, **kw)

def pisaParser(src, c, default_css=""):
    """    
    - Parse HTML and get miniDOM
    - Extract CSS informations, add default CSS, parse CSS
    - Handle the document DOM itself and build reportlab story
    - Return Context object     
    """
    parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))

    # XXX Bugfix for HTML5lib
    src = src.read().replace("<![CDATA[", "\n").replace("]]>", "\n")
    src = cStringIO.StringIO(src)
    
    document = parser.parse(src)
    # print document.toprettyxml()    

    if default_css:
        c.addCSS(default_css)
        
    pisaPreLoop(document, c)    
    #try:
    c.parseCSS()        
    #except:
    #    c.cssText = DEFAULT_CSS
    #    c.parseCSS()        
    c.debug(9, pprint.pformat(c.css))        
    pisaLoop(document, c)
    return c
