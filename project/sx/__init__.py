# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2007 ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 128 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2008-01-10 21:26:42 +0100 (Do, 10 Jan 2008) $"
__svnid__   = "$Id: __init__.py 128 2008-01-10 20:26:42Z holtwick $"

# Also look in other packages with the same name

from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
