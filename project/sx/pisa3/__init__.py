# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2007 ##
## All rights reserved                     ##
#############################################

__revision__ = "$Revision: 146 $"
__author__   = "$Author: holtwick $"
__date__     = "$Date: 2008-01-22 10:51:59 +0100 (Di, 22 Jan 2008) $"
__svnid__    = "$Id: __init__.py 146 2008-01-22 09:51:59Z holtwick $"

try:
    from pisa import *
except:
    pass

from pisa_version import VERSION, VERSION_STR
__version__ = VERSION
