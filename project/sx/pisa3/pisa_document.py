# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2007 ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 20 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2007-10-09 12:58:24 +0200 (Di, 09 Okt 2007) $"
__svnid__   = "$Id: pml.py 20 2007-10-09 10:58:24Z holtwick $"

from pisa_context import pisaContext
from pisa_parser import pisaParser
from pisa_util import *
from pisa_reportlab import *
from pisa_default import DEFAULT_CSS

import cStringIO
import os
import types
import cgi

def pisaErrorDocument(dest, c):  
    out = cStringIO.StringIO()
    out.write("<p style='background-color:red;'><strong>%d error(s) occured:</strong><p>" % c.err)        
    for mode, line, msg, code in c.log:
        if mode=="error":
            out.write("<pre>%s in line %d: %s</pre>" % (mode, line, cgi.escape(msg)))
    
    out.write("<p><strong>%d warning(s) occured:</strong><p>" % c.warn)        
    for mode, line, msg, code in c.log:
        if mode=="warning":
            out.write("<p>%s in line %d: %s</p>" % (mode, line, cgi.escape(msg)))
    
    return pisaDocument(out.getvalue(), dest)

def pisaDocument(
    src, 
    dest, 
    path = None, 
    link_callback = None,
    debug = 0,
    show_error_as_pdf = False, 
    default_css = None,
    **kw):

    try:       
        c = pisaContext(
            path, 
            debug = debug)
        c.pathCallback = link_callback
        
        # XXX Handle strings and files    
        if type(src) in types.StringTypes:
            src = cStringIO.StringIO(src)
        
        if default_css is None:
            default_css = DEFAULT_CSS
        
        pisaParser(src, c, default_css)
    
        if 0:
            import reportlab.pdfbase.pdfmetrics as pm
            pm.dumpFontData()
        
        # Avoid empty pages
        if not c.story:
            c.addPara(force=True)
    
        # Remove anchors if they do not exist (because of a bug in Reportlab)
        for frag, anchor in c.anchorFrag:       
            if anchor not in c.anchorName:                        
                frag.link = None
                
        out = cStringIO.StringIO()
        
        doc = PmlBaseDoc(
            out,
            pagesize = c.pageSize,
            author = c.meta["author"].strip(),
            subject = c.meta["subject"].strip(),
            keywords = [x.strip() for x in c.meta["keywords"].strip().split(",") if x],
            title = c.meta["title"].strip(),
            showBoundary = 0,
            allowSplitting = 1)
    
        # XXX It is not possible to access PDF info, because it is private in canvas
        # doc.info.producer = "pisa <http://www.holtwick.it>" 
               
        if c.templateList.has_key("body"):
            body = c.templateList["body"]
            del c.templateList["body"]
        else:
            x, y, w, h = getBox("1cm 1cm -1cm -1cm", c.pageSize)    
            body = PmlPageTemplate(
                id="body",
                frames=[
                    Frame(x, y, w, h, 
                        id = "body",
                        leftPadding = 0,
                        rightPadding = 0,
                        bottomPadding = 0,
                        topPadding = 0)],
                pagesize = c.pageSize)
    
        # print body.frames
    
        # print [body] + c.templateList.values()
        doc.addPageTemplates([body] + c.templateList.values())             
        doc.build(c.story)    
        
        # Add watermarks
        if pyPdf:             
            # print c.pisaBackgroundList   
            for bgouter in c.pisaBackgroundList:                    
                # If we have at least one background, then lets do it
                if bgouter:
                    istream = out 
                    # istream.seek(2,0) #cStringIO.StringIO(data)
                    try:                            
                        output = pyPdf.PdfFileWriter()
                        input1 = pyPdf.PdfFileReader(istream)
                        ctr = 0                        
                        for bg in c.pisaBackgroundList:                                
                            page = input1.getPage(ctr)
                            if bg:
                                if os.path.exists(bg):                    
                                    # print "BACK", bg                
                                    bginput = pyPdf.PdfFileReader(open(bg, "rb"))
                                    # page.mergePage(bginput.getPage(0))
                                    pagebg = bginput.getPage(0)
                                    pagebg.mergePage(page)
                                    page = pagebg 
                                else:
                                    c.warning("Background PDF %s doesn't exist." % bg)
                            output.addPage(page)
                            ctr += 1
                        out = cStringIO.StringIO()
                        output.write(out)
                        # data = sout.getvalue()
                    except Exception, e:
                        c.error("Exception: %s" % str(e))
                    # istream.close()
                # Found a background? So leave loop after first occurence
                break
        else:
            c.warning("pyPDF not installed!")
    
        # Get result
        data = out.getvalue()
        dest.write(data)
    except:
        c.error(ErrorMsg())
        
    if c.err and show_error_as_pdf:
        return pisaErrorDocument(dest, c)
        
    return c
