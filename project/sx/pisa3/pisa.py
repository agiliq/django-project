# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2007 ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 20 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2007-10-09 12:58:24 +0200 (Di, 09 Okt 2007) $"
__svnid__   = "$Id: pml.py 20 2007-10-09 10:58:24Z holtwick $"

import getopt
import sys
import os
import os.path
import urllib
import urlparse
import tempfile

from pisa_version import VERSION, VERSION_STR
from pisa_document import *
from pisa_default import DEFAULT_CSS

# Backward compatibility
CreatePDF = pisaDocument

USAGE = (VERSION_STR + """

USAGE: pisa [options] <src> <dest>

<src>
  Name of a HTML file or a file pattern using * placeholder.
  If you want to read from stdin use "-" as file name.
  You may also load an URL over HTTP. Take care of putting
  the <src> in quotes if it contains characters like "?". 

<dest>
  Name of the generated PDF file or "-" if you like
  to send the result to stdout. Take care that the
  destination file is not alread opened by an other
  application like the Adobe Reader. If the destination is
  not writeable a similar name will be calculated automatically.

[options]
  --css, -c:
    path to default css file
  --css-dump:
    dumps the default css definitions to STDOUT
  --debug, -d:
    show debugging informations of level 
  --help, -h:
    show this help text
  --quiet, -q:
    show no messages
  --start-viewer, -s:
    start PDF default viewer on Windows and MacOSX
    (e.g. AcrobatReader)
  --version:
    show version information 
  --warn, -w:
    show warnings
""").strip()

COPYRIGHT = VERSION_STR

BENCH = """
BENCHMARKING:
parsing   %.4f sec
document  %.4f sec
create    %.4f sec
""".strip()

def usage():
    print USAGE

class pisaLinkLoader:

    """
    Helper to load page from an URL and load corresponding
    files to temporary files. If getFileName is called it 
    returns the temporty filename and takes care to delete
    it when pisaLinkLoader is unloaded. 
    """
    
    def __init__(self, src, quiet=True):
        self.quiet = quiet
        self.src = src
        self.tfileList = []
    
    def __del__(self):
        for path in self.tfileList:
            # print "DELETE", path
            os.remove(path)
            
    def getFileName(self, name, relative=None):
        try:
            url = urlparse.urljoin(relative or self.src, name)            
            suffix = urlparse.urlsplit(url)[2].split(".")[-1]
            if suffix.lower() not in ("css", "gif", "jpg", "png"):
                return None
            ufile = urllib.urlopen(url)
            path = tempfile.mktemp(suffix = "." + suffix)
            tfile = file(path, "wb")
            while True:
                data = ufile.read(1024)
                if not data:
                    break
                # print data
                tfile.write(data)
            ufile.close()
            tfile.close()
            self.tfileList.append(path)
            if not self.quiet:
                print "  Loading", url, "to", path
            return path
        except Exception, e:
            if not self.quiet:
                print "  ERROR:", e
        return None
    
def command():
    import os
    import os.path
    import glob

    try:
        opts, args = getopt.getopt(sys.argv[1:], "bdhpqstwc", [
            "benchmark",
            "quiet",
            "help",
            "start-viewer",
            "debug=",
            "copyright",
            "version",
            "warn",
            "booklet=",
            "multivalent=",
            "multivalent-path=",
            "parse",
            "tempdir=",
            "format=",
            "css=",
            "css-dump",
            ])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    startviewer = 0
    quiet = 0
    bench = 0
    debug = 0
    warn = 0
    tidy = 0
    multivalent_path = ""
    booklet = ""
    # parse = 0
    tempdir = None
    format = "pdf"
    css = None

    for o, a in opts:
        if o in ("-h", "--help"):
            # Hilfe anzeigen
            usage()
            sys.exit()

        if o in ("-s", "--start-viewer"):
            # Anzeigeprogramm starten
            startviewer = 1

        if o in ("-q", "--quiet"):
            # Output unterdrücken
            quiet = 1

        if o in ("-b", "--benchmark"):
            # Zeiten ausgeben
            bench = 1

        if o in ("-d", "--debug"):
            # Debug
            debug = 10
            if a:                
                debug = int(a)

        if o in ("-w", "--warn"):
            # Warnings
            warn = 1

        if o in ("--multivalent", "--multivalent-path"):
            # Multivalent.jar für Booklet
            multivalent_path = a

        if o in ("--booklet",):
            # Booklet
            booklet = a

        if o in ("--copyright", "--version"):
            print COPYRIGHT
            sys.exit(0)

        #if o in ("-p", "--parse"):
        #    # Print parse
        #    parse = 1

        if o in ("--tempdir",):
            # Tempdir
            tempdir = a

        if o in ("-t", "--format"):
            # Format
            format = a

        if o in ("-c", "--css"):
            # CSS
            # css = "@import url('%s');" % a
            css = file(a, "r").read()

        if o in ("--css-dump",):
            # CSS dump
            print DEFAULT_CSS
            return 
        
    if len(args) not in (1, 2):
        usage()
        sys.exit(2)

    if len(args)==2:
        a_src, a_dest = args
    else:
        a_src = args[0]
        a_dest = None
        
    if "*" in a_src:
        a_src = glob.glob(a_src)
        # print a_src
    else:
        a_src = [a_src]
    
    for src in a_src:
    
        lc = None
        wpath = None
        
        if src=="-":
            fsrc = sys.stdin
            wpath = os.getcwd()
        else:
            # fsrc = open(src, "r")
            if src.startswith("http:"):
                # print "+++", src
                wpath = src
                fsrc = urllib.urlopen(src)
                lc = pisaLinkLoader(src, quiet=quiet).getFileName                
                src = "".join(urlparse.urlsplit(src)[1:3]).replace("/", "-")                                
            else:
                fsrc = wpath = os.path.abspath(src)
                fsrc = open(fsrc, "rb")

        if a_dest is None:
            dest_part = src            
            if dest_part.lower().endswith(".html") or dest_part.lower().endswith(".htm"):
                dest_part = ".".join(src.split(".")[:-1])
            dest = dest_part + "." + format.lower()
            for i in range(10):
                try:
                    open(dest, "wb").close()
                    break
                except:
                    pass
                dest = dest_part + "-%d.%s" % (i, format.lower())
        else:
            dest = a_dest
                
        fdestclose = 0
        
        if dest=="-":
            if sys.platform == "win32":
                import os, msvcrt
                msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
            fdest = sys.stdout
            startviewer = 0
        else:
            dest = os.path.abspath(dest)
            try:
                open(dest, "wb").close()
            except:
                print "File '%s' seems to be in use of another application." % dest
                sys.exit(2)
            fdest = open(dest, "wb")
            fdestclose = 1
    
        if not quiet:
            print "Converting %s to %s..." % (src, dest)          
    
        pdf = pisaDocument(
            fsrc,
            fdest,
            debug = debug,
            path = wpath,
            errout = sys.stdout,
            multivalent_path = multivalent_path,
            booklet = booklet,
            tempdir = tempdir,
            format = format,
            link_callback = lc,
            default_css = css,
            )
    
        if fdestclose:
            fdest.close()
    
        if not quiet:
    
            if pdf.log and (pdf.err or (pdf.warn and warn)):
                for mode, line, msg, code in pdf.log:
                    print "%s in line %d: %s" % (mode, line, msg)
        
            if pdf.err:
                print "*** %d ERRORS OCCURED" % pdf.err
            else:
                if bench:
                    print BENCH % tuple(pdf.bench)
                    
        if (not pdf.err) and startviewer:
            if not quiet:
                print "Open viewer for file %s" % dest
            try:
                # print repr(dest)
                os.startfile(dest)
            except:
                # try to opan a la apple
                # cmd = 'nohup /Applications/Preview.app/Contents/MacOS/Preview "%s" &' % dest
                cmd = 'open "%s"' % dest
                # print cmd
                os.system(cmd)

if __name__=="__main__":
    main()
