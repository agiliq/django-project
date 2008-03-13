# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2007 ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 2 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2007-09-04 13:26:38 +0200 (Di, 04 Sep 2007) $"

import copy

from reportlab.platypus.tables import *
from reportlab.platypus.flowables import *
from reportlab.platypus.flowables import KeepInFrame

from pisa_util import *
from pisa_tags import *

class PmlTable(Table):

    def _normWidth(self, w, maxw):
        " Helper for calculating percentages "
        if type(w)==type(""):
            w = ((maxw/100.0) * float(w[:-1]))
        elif (w is None) or (w=="*"):
            w = maxw
        return min(w, maxw)

    def wrap(self, availWidth, availHeight):

        # Strange bug, sometime the totalWidth is not set !?
        try:
            self.totalWidth
        except:
            self.totalWidth = availWidth

        # Prepare values
        totalWidth = self._normWidth(self.totalWidth, availWidth)
        remainingWidth = totalWidth
        remainingCols = 0
        newColWidths = self._colWidths

        # Calculate widths that are fix
        # IMPORTANT!!! We can not substitute the private value
        # self._colWidths therefore we have to modify list in place
        for i in range(len(newColWidths)):
            colWidth = newColWidths[i]
            if (colWidth is not None) or (colWidth=='*'):
                colWidth = self._normWidth(colWidth, totalWidth)
                remainingWidth -= colWidth
            else:
                remainingCols += 1
                colWidth = None
            newColWidths[i] = (colWidth)

        # Distribute remaining space
        if remainingCols:
            for i in range(len(newColWidths)):
                if newColWidths[i] is None:
                    newColWidths[i] = (remainingWidth / remainingCols) - 0.1

        # print "New values:", totalWidth, newColWidths, sum(newColWidths)

        # Call original method "wrap()"
        # self._colWidths = newColWidths
        return Table.wrap(self, availWidth, availHeight)

def _width(value=None):
    if value is None:
        return None
    value = str(value)
    if value.endswith("%"):
        return value
    return getSize(value)

class TableData:

    def __init__(self):
        self.data = []
        self.styles = []
        self.span = []
        self.mode = ""
        self.padding = 0

    def add_cell(self, data=None):
        self.col += 1
        self.data[len(self.data)-1].append(data)

    def add_style(self, data):
        # print self.mode, data
        self.styles.append(copy.copy(data))

    def add_empty(self, x, y):
        self.span.append((x, y))

    def get_data(self):
        data = self.data
        for x, y in self.span:
            try:
                data[y].insert(x, '')
            except:
                pass
        return data

    def add_cell_styles(self, c, begin, end, mode="td"):
        self.mode = mode.upper()
        if c.frag.backColor and mode!="tr": # XXX Stimmt das so?
            self.add_style(('BACKGROUND', begin, end, c.frag.backColor))
            # print 'BACKGROUND', begin, end, c.frag.backColor
        if c.frag.borderTopWidth:
            self.add_style(('LINEABOVE', begin, (end[0], begin[1]), c.frag.borderTopWidth, c.frag.borderTopColor, "squared"))
        if c.frag.borderLeftWidth:
            self.add_style(('LINEBEFORE', begin, (begin[0], end[1]), c.frag.borderLeftWidth, c.frag.borderLeftColor, "squared"))
        if c.frag.borderRightWidth:
            self.add_style(('LINEAFTER', (end[0], begin[1]), end, c.frag.borderRightWidth, c.frag.borderRightColor, "squared"))
        if c.frag.borderBottomWidth:
            self.add_style(('LINEBELOW', (begin[0], end[1]), end, c.frag.borderBottomWidth, c.frag.borderBottomColor, "squared"))
        self.add_style(('LEFTPADDING', begin, end, c.frag.paddingLeft or self.padding))
        self.add_style(('RIGHTPADDING', begin, end, c.frag.paddingRight or self.padding))
        self.add_style(('TOPPADDING', begin, end, c.frag.paddingTop or self.padding))
        self.add_style(('BOTTOMPADDING', begin, end, c.frag.paddingBottom or self.padding))

class pisaTagTABLE(pisaTag):
    
    def start(self, c):
        c.addPara()
    
        attrs = self.attr
        
        # Swap table data
        c.tableData, self.tableData = TableData(),  c.tableData
        tdata = c.tableData

        # border
        #tdata.border = attrs.border
        #tdata.bordercolor = attrs.bordercolor

        begin = (0, 0)
        end = (-1, -1)
            
        if attrs.border:
            tdata.add_style(("GRID", begin, end, attrs.border, attrs.bordercolor))
        
        tdata.padding = attrs.cellpadding
        
        if 0: #attrs.cellpadding:
            tdata.add_style(('LEFTPADDING', begin, end, attrs.cellpadding))
            tdata.add_style(('RIGHTPADDING', begin, end, attrs.cellpadding))
            tdata.add_style(('TOPPADDING', begin, end, attrs.cellpadding))
            tdata.add_style(('BOTTOMPADDING', begin, end, attrs.cellpadding))
            
        # alignment
        #~ tdata.add_style(('VALIGN', (0,0), (-1,-1), attrs.valign.upper()))

        # Set Border and padding styles
        
        tdata.add_cell_styles(c, (0,0), (-1,-1), "table")

        # bgcolor
        #if attrs.bgcolor is not None:
        #    tdata.add_style(('BACKGROUND', (0, 0), (-1, -1), attrs.bgcolor))

        tdata.align = attrs.align.upper()
        tdata.col = 0
        tdata.row = 0
        tdata.keepinframe = {
            "maxWidth": attrs["keepmaxwidth"],
            "maxHeight": attrs["keepmaxheight"],
            "mode": attrs["keepmode"],            
            "mergeSpace": attrs["keepmergespace"]
            }
        tdata.keep_maxwidth = attrs.keepmaxwidth
        tdata.keep_maxheight = attrs.keepmaxheight
        tdata.colw = []
        tdata.rowh = []
        tdata.repeat = attrs.repeat
        tdata.width = _width(attrs.width)

        # self.tabdata.append(tdata)

    def end(self, c):
        tdata = c.tableData
        data = tdata.get_data()        
        try:
            if tdata.data:
                t = PmlTable(
                    data,
                    colWidths = tdata.colw,
                    rowHeights = tdata.rowh,
                    # totalWidth = tdata.width,
                    splitByRow = 1,
                    # repeatCols = 1,
                    repeatRows = tdata.repeat,
                    hAlign = tdata.align,
                    vAlign = 'TOP',                    
                    style = TableStyle(tdata.styles))
                t.totalWidth = _width(tdata.width)
                t.spaceBefore = c.frag.spaceBefore
                t.spaceAfter = c.frag.spaceAfter
                # t.hAlign = tdata.align
                c.addStory(t)
            else:
                c.warning("<table> is empty")
        except:
            c.warning("Error in <table>")

        # Cleanup and re-swap table data
        c.clearFrag()
        c.tableData, self.tableData = self.tableData, None
    
class pisaTagTR(pisaTag):
    
    def start(self, c):            
        tdata = c.tableData
        row = tdata.row
        begin = (0, row)
        end = (-1, row)
        
        tdata.add_cell_styles(c, begin, end, "tr")       
        c.frag.vAlign = self.attr.valign or c.frag.vAlign
          
        tdata.col = 0
        tdata.data.append([])

    def end(self, c):
        tdata = c.tableData
        tdata.row += 1

class pisaTagTD(pisaTag):
    
    def start(self, c):

        if self.attr.align is not None:
            #print self.attr.align, getAlign(self.attr.align)
            c.frag.alignment = getAlign(self.attr.align)
            
        c.clearFrag()
        self.story = c.swapStory()
        # print "#", len(c.story)
        
        attrs = self.attr
        
        tdata = c.tableData

        cspan = attrs.colspan
        rspan = attrs.rowspan

        row = tdata.row
        col = tdata.col
        while 1:
            for x, y in tdata.span:
                if x==col and y==row:
                    col += 1
                    tdata.col += 1
            break
        cs = 0
        rs = 0

        begin = (col, row)
        end = (col, row)
        if cspan:
            end = (end[0] + cspan - 1, end[1])
        if rspan:
            end = (end[0], end[1] + rspan - 1)
        if begin!=end:
            #~ print begin, end
            tdata.add_style(('SPAN', begin, end))
            for x in range(begin[0], end[0]+1):
                for y in range(begin[1], end[1]+1):
                    if x!=begin[0] or y!=begin[1]:
                        tdata.add_empty(x, y)

        # Set Border and padding styles
        tdata.add_cell_styles(c, begin, end, "td")

        # Calculate widths
        # Add empty placeholders for new columns
        if (col + 1) > len(tdata.colw):
            tdata.colw = tdata.colw + ((col + 1 - len(tdata.colw)) * [_width()])
        # Get value of with, if no spanning
        if not cspan:
            # print c.frag.width
            width = c.frag.width or self.attr.width #self._getStyle(None, attrs, "width", "width", mode)
            # If is value, the set it in the right place in the arry
            # print width, _width(width)
            if width is not None:
                tdata.colw[col] = _width(width)

        # Calculate heights
        if row+1 > len(tdata.rowh):
            tdata.rowh = tdata.rowh + ((row + 1 - len(tdata.rowh)) * [_width()])
        if not rspan:
            height = None #self._getStyle(None, attrs, "height", "height", mode)
            if height is not None:
                tdata.rowh[row] = _width(height)
                tdata.add_style(('FONTSIZE', begin, end, 1.0))
                tdata.add_style(('LEADING', begin, end, 1.0))

        # Vertical align      
        valign = self.attr.valign or c.frag.vAlign
        if valign is not None:
            tdata.add_style(('VALIGN', begin, end, valign.upper()))

        # Reset border, otherwise the paragraph block will have borders too
        frag = c.frag
        frag.borderLeftWidth = 0
        frag.borderLeftColor = None
        frag.borderLeftStyle = None
        frag.borderRightWidth = 0
        frag.borderRightColor = None
        frag.borderRightStyle = None
        frag.borderTopWidth = 0
        frag.borderTopColor = None
        frag.borderTopStyle = None
        frag.borderBottomWidth = 0
        frag.borderBottomColor = None
        frag.borderBottomStyle = None

    def end(self, c):
        tdata = c.tableData
        
        c.addPara()
        cell = c.story
        
        # Handle empty cells, they otherwise collapse
        if not cell:
            cell = ' '
            
        c.swapStory(self.story)
      
        # zellen hinzufügen
        if 0: # tdata.keepinframe["maxWidth"] and tdata.keepinframe["maxHeight"]:
            # print tdata.keepinframe
            tdata.keepinframe["content"] = cell
            cell = KeepInFrame(**tdata.keepinframe)
        
        tdata.add_cell(cell)
        
class pisaTagTH(pisaTagTD):
    pass

'''
    end_th = end_td

    def start_keeptogether(self, attrs):
        self.story.append([])
        self.next_para()

    def end_keeptogether(self):
        if not self.story[-1]:
            self.add_noop()
        self.next_para()
        s = self.story.pop()
        self.add_story(KeepTogether(s))

    def start_keepinframe(self, attrs):
        self.story.append([])
        self.keepinframe = {
            "maxWidth": attrs["maxwidth"],
            "maxHeight": attrs["maxheight"],
            "mode": attrs["mode"],
            "name": attrs["name"],
            "mergeSpace": attrs["mergespace"]
            }
        # print self.keepinframe
        self.next_para()

    def end_keepinframe(self):
        if not self.story[-1]:
            self.add_noop()
        self.next_para()
        self.keepinframe["content"] = self.story.pop()
        self.add_story(KeepInFrame(**self.keepinframe))
'''