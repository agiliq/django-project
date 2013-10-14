# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2008 ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 151 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2008-01-27 20:18:57 +0100 (So, 27 Jan 2008) $"

BUILD_DATE = "2008-02-13 13:09:19"
BUILD_NUMBER = "3145"

VERSION = "3.0.14"
VERSION_STR = "pisa %s (Build %s, %s)\n(c) 2004-2008 Dirk Holtwick, Germany" % (
    VERSION,
    BUILD_NUMBER,
    BUILD_DATE,
    )

def newBuild():
    import os
    import os.path
    import re
    import time

    global BUILD_DATE, BUILD_NUMBER

    rxBUILD_DATE = re.compile('BUILD\_DATE\s\=\s\"(.*?)\"', re.I|re.M|re.DOTALL)
    rxBUILD_NUMBER = re.compile('BUILD\_NUMBER\s\=\s\"(.*?)\"', re.I|re.M|re.DOTALL)

    # Get path of this file
    path = os.path.join(os.getcwd(), ".".join(__file__.split(".")[:-1]) + ".py")
    print "Update version file", path
    data = open(path, "r").read()

    # BUILD NUMBER
    BUILD_NUMBER = str(int(rxBUILD_NUMBER.search(data).group(1)) + 1)
    data = rxBUILD_NUMBER.sub('BUILD_NUMBER' + ' = "%s"' % BUILD_NUMBER, data)

    # BUILD DATE
    BUILD_DATE = time.strftime("%Y-%m-%d %H:%M:%S")
    data = rxBUILD_DATE.sub('BUILD_DATE' + ' = "%s"' % BUILD_DATE, data)

    # Write back
    open(path, "w").write(data)
    return data

if __name__=="__main__":
    newBuild()
    print BUILD_DATE, BUILD_NUMBER
    print VERSION_STR

