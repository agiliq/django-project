##  Copyright by Dirk Holtwick <holtwick@web.de>, 2007

"""
Helper for complex CSS definitons like font, margin, padding and border
Optimized for use with PISA
"""

import types

def toList(value):
    if type(value)!=types.ListType:
        return [value]
    return value

_styleTable = {
    "normal": "",
    "italic": "",
    "oblique": "",
    }

_variantTable = {
    "normal": None,
    "small-caps": None,
    }

_weightTable = {
    "light": 300,
    "lighter": 300, # fake relativness for now
    "normal": 400,
    "bold": 700,
    "bolder": 700, # fake relativness for now

    "100": 100,
    "200": 200,
    "300": 300,
    "400": 400,
    "500": 500,
    "600": 600,
    "700": 700,
    "800": 800,
    "900": 900,

    #wx.LIGHT: 300,
    #wx.NORMAL: 400,
    #wx.BOLD: 700,
    }

_absSizeTable = {
    "xx-small" : 3./5.,
    "x-small": 3./4.,
    "small": 8./9.,
    "medium": 1./1.,
    "large": 6./5.,
    "x-large": 3./2.,
    "xx-large": 2./1.,
    "xxx-large": 3./1.,
    }

'''
_relSizeTable = {
    'pt':
        # pt: absolute point size
        # Note: this is 1/72th of an inch
        (lambda value, pt: value),
    'px':
        # px: pixels, relative to the viewing device
        # Note: approximate at the size of a pt
        (lambda value, pt: value),
    'ex':
        # ex: proportional to the 'x-height' of the parent font
        # Note: can't seem to dervie this value from wx.Font methods,
        # so we'll approximate by calling it 1/2 a pt
        (lambda value, pt: 2 * value),
    'pc':
        # pc: 12:1 pica:point size
        # Note: this is 1/6th of an inch
        (lambda value, pt: 12*value),
    'in':
        # in: 72 inches per point
        (lambda value, pt: 72*value),
    'cm':
        # in: 72 inches per point, 2.54 cm per inch
        (lambda value, pt,_r=72./2.54: _r*value),
    'mm':
        # in: 72 inches per point, 25.4 mm per inch
        (lambda value, pt,_r=72./25.4: _r*value),
    '%':
        # %: percentage of the parent's pointSize
        (lambda value, pt: 0.01 * pt * value),
    'em':
        # em: proportional to the 'font-size' of the parent font
        (lambda value, pt: pt * value),
    }
'''


def parseSpecialRules(declarations):
        # print selectors, declarations
        # CSS MODIFY!
        dd = []

        for d in declarations:

            name, parts, last = d
            parts = toList(parts)

            # FONT
            if name == "font":

                # print "FONT", repr(d)
                """
                [ [ <'font-style'> || <'font-variant'> || <'font-weight'> ]? <'font-size'> [ / <'line-height'> ]? <'font-family'> ] | inherit
                """

                part = parts.pop(0)
                while parts:
                    # print "??", repr(part)
                    if part in _styleTable:
                        print "style", part
                        # result.update(klass.cssStyle(part, parentFont))
                        part = parts.pop(0)
                    elif part in _variantTable:
                        print "variant", part
                        #result.update(klass.cssVariant(part, parentFont))
                        part = parts.pop(0)
                    elif part in _weightTable:
                        print "weight", part
                        #result.update(klass.cssWeight(part, parentFont))
                        part = parts.pop(0)
                    else:
                        break

                if isinstance(part, tuple) and len(part) == 3:
                    fontSize, slash, lineHeight = part
                    assert slash == '/'
                    dd.append(("font-size", fontSize, last))
                    dd.append(("line-height", lineHeight, last))
                else:
                    dd.append(("font-size", part, last))

                dd.append(("font-face", parts, last))

            # BACKGROUND
            elif name == "background":

                """
                [<'background-color'> || <'background-image'> || <'background-repeat'> || <'background-attachment'> || <'background-position'>] | inherit
                """

                part = parts.pop(0)

                # XXX Handling of images etc. is missing!
                dd.append(("background-color", part, last))

            # MARGIN
            elif name == "margin":

                # print parts, len(parts)

                if len(parts)==1:
                    top = bottom = left = right = parts[0]
                elif len(parts)==2:
                    top = bottom = parts[0]
                    left = right = parts[1]
                elif len(parts)==3:
                    top = parts[0]
                    left = right = parts[1]
                    bottom = parts[2]
                elif len(parts)==4:
                    top = parts[0]
                    right = parts[1]
                    bottom = parts[2]
                    left = parts[3]
                else:
                    continue

                dd.append(("margin-left", left, last))
                dd.append(("margin-right", right, last))
                dd.append(("margin-top", top, last))
                dd.append(("margin-bottom", bottom, last))

            # PADDING
            elif name == "padding":

                # print parts, len(parts)

                if len(parts)==1:
                    top = bottom = left = right = parts[0]
                elif len(parts)==2:
                    top = bottom = parts[0]
                    left = right = parts[1]
                elif len(parts)==3:
                    top = parts[0]
                    left = right = parts[1]
                    bottom = parts[2]
                elif len(parts)==4:
                    top = parts[0]
                    right = parts[1]
                    bottom = parts[2]
                    left = parts[3]
                else:
                    continue

                dd.append(("padding-left", left, last))
                dd.append(("padding-right", right, last))
                dd.append(("padding-top", top, last))
                dd.append(("padding-bottom", bottom, last))

            # BORDER WIDTH
            elif name == "border-width":

                if len(parts)==1:
                    top = bottom = left = right = parts[0]
                elif len(parts)==2:
                    top = bottom = parts[0]
                    left = right = parts[1]
                elif len(parts)==3:
                    top = parts[0]
                    left = right = parts[1]
                    bottom = parts[2]
                elif len(parts)==4:
                    top = parts[0]
                    right = parts[1]
                    bottom = parts[2]
                    left = parts[3]
                else:
                    continue

                dd.append(("border-left-width", left, last))
                dd.append(("border-right-width", right, last))
                dd.append(("border-top-width", top, last))
                dd.append(("border-bottom-width", bottom, last))

            # BORDER COLOR
            elif name == "border-color":

                if len(parts)==1:
                    top = bottom = left = right = parts[0]
                elif len(parts)==2:
                    top = bottom = parts[0]
                    left = right = parts[1]
                elif len(parts)==3:
                    top = parts[0]
                    left = right = parts[1]
                    bottom = parts[2]
                elif len(parts)==4:
                    top = parts[0]
                    right = parts[1]
                    bottom = parts[2]
                    left = parts[3]
                else:
                    continue

                dd.append(("border-left-color", left, last))
                dd.append(("border-right-color", right, last))
                dd.append(("border-top-color", top, last))
                dd.append(("border-bottom-color", bottom, last))

            # BORDER STYLE
            elif name == "border-color":

                if len(parts)==1:
                    top = bottom = left = right = parts[0]
                elif len(parts)==2:
                    top = bottom = parts[0]
                    left = right = parts[1]
                elif len(parts)==3:
                    top = parts[0]
                    left = right = parts[1]
                    bottom = parts[2]
                elif len(parts)==4:
                    top = parts[0]
                    right = parts[1]
                    bottom = parts[2]
                    left = parts[3]
                else:
                    continue

                dd.append(("border-left-style", left, last))
                dd.append(("border-right-style", right, last))
                dd.append(("border-top-style", top, last))
                dd.append(("border-bottom-style", bottom, last))

            # BORDER
            elif name == "border":

                if parts:
                    part = parts.pop(0)
                    dd.append(("border-left-width", part, last))
                    dd.append(("border-right-width", part, last))
                    dd.append(("border-top-width", part, last))
                    dd.append(("border-bottom-width", part, last))

                if parts:
                    part = parts.pop(0)
                    dd.append(("border-left-style", part, last))
                    dd.append(("border-right-style", part, last))
                    dd.append(("border-top-style", part, last))
                    dd.append(("border-bottom-style", part, last))

                if parts:
                    part = parts.pop(0)
                    dd.append(("border-left-color", part, last))
                    dd.append(("border-right-color", part, last))
                    dd.append(("border-top-color", part, last))
                    dd.append(("border-bottom-color", part, last))

            # BORDER TOP
            elif name == "border-top":

                if parts:
                    part = parts.pop(0)
                    dd.append(("border-top-width", part, last))

                if parts:
                    part = parts.pop(0)
                    dd.append(("border-top-style", part, last))

                if parts:
                    part = parts.pop(0)
                    dd.append(("border-top-color", part, last))

            # BORDER BOTTOM
            elif name == "border-bottom":

                if parts:
                    part = parts.pop(0)
                    dd.append(("border-bottom-width", part, last))

                if parts:
                    part = parts.pop(0)
                    dd.append(("border-bottom-style", part, last))

                if parts:
                    part = parts.pop(0)
                    dd.append(("border-bottom-color", part, last))

            # BORDER LEFT
            elif name == "border-left":

                if parts:
                    part = parts.pop(0)
                    dd.append(("border-left-width", part, last))

                if parts:
                    part = parts.pop(0)
                    dd.append(("border-left-style", part, last))

                if parts:
                    part = parts.pop(0)
                    dd.append(("border-left-color", part, last))

            # BORDER RIGHT
            elif name == "border-right":

                if parts:
                    part = parts.pop(0)
                    dd.append(("border-right-width", part, last))

                if parts:
                    part = parts.pop(0)
                    dd.append(("border-right-style", part, last))

                if parts:
                    part = parts.pop(0)
                    dd.append(("border-right-color", part, last))

            # REST
            else:
                dd.append(d)

        if 0: #declarations!=dd:
            print "###", declarations
            print "#->", dd
        # CSS MODIFY! END
        return dd

import re
_rxhttp = re.compile(r"url\([\'\"]?http\:\/\/[^\/]", re.IGNORECASE|re.DOTALL)

def cleanupCSS(src):
    src = _rxhttp.sub('url(', src)
    return src