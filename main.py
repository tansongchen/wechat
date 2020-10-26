'''
生成
'''

import math

varlist = ['main', 'dark', 'light', 'plus', 'minus']
hueDict = {
    '赤': (0, 0.07), 
    '橙': (0.08, 0.05), 
    '黄': (0.12, 0.02), 
    '绿': (0.3, 0.15), 
    '青': (0.5, 0.08), 
    '蓝': (0.6, 0.08), 
    '紫': (0.8, 0.1)
    }
schemeDict = {name: {var: 'hsl(0, 0, 0)' for var in varlist} for name in hueDict}

mainLuminance = 0.5
darkLuminance = 0.2
lightLuminance = 0.8
mainSaturation = 1
darkSaturation = 0.8
vr = 0.2126
vg = 0.7152
vb = 0.0722


def format_hsl(h, s, l):
    return 'hsl(%d, %d%%, %d%%)' % (h * 360, s * 100, l * 100)

def calc_color(t, p, q):
    if t < 1/6:
        return p + ((q - p) * 6 * t)
    elif t < 1/2:
        return q
    elif t < 2/3:
        return p + ((q - p) * (4 - 6 * t))
    else:
        return p

def conv_hsl_to_rgb(h, s, l):
    if l < 0.5:
        q = l * (1 + s)
    else:
        q = l + s - (l * s)
    p = 2 * l - q
    tr = h + 1/3 - math.floor(h + 1/3)
    tg = h
    tb = h - 1/3 - math.floor(h - 1/3)
    return calc_color(tr, p, q), calc_color(tg, p, q), calc_color(tb, p, q)

def linearlize(c):
    if c <= 0.03928:
        return c / 12.92
    else:
        return ((c + 0.055) / 1.055)**2.4 

def calc_y(r, g, b):
    return vr * linearlize(r) + vg * linearlize(g) + vb * linearlize(b)

def solve_luminance_for(h, s, y):
    l1 = 0
    l2 = 1
    
    while l2 - l1 > 0.001:
        lmid = (l1 + l2) / 2
        r, g, b = conv_hsl_to_rgb(h, s, lmid)
        ymid = calc_y(r, g, b)
        if ymid > y:
            l2 = lmid
        else:
            l1 = lmid
    return lmid

for name, (mainHue, deltaHue) in hueDict.items():
    # 主题色
    mainLightness = solve_luminance_for(mainHue, mainSaturation, mainLuminance)
    schemeDict[name]['main'] = format_hsl(mainHue, mainSaturation, mainLightness)
    # 浅色
    lightLightness = solve_luminance_for(mainHue, mainSaturation, lightLuminance)
    schemeDict[name]['light'] = format_hsl(mainHue, mainSaturation, lightLightness)
    # 深色
    darkLightness = solve_luminance_for(mainHue, darkSaturation, darkLuminance)
    schemeDict[name]['dark'] = format_hsl(mainHue, darkSaturation, darkLightness)
    # 位移色
    plusHue = mainHue + deltaHue
    plusLightness = solve_luminance_for(plusHue, mainSaturation, mainLuminance)
    schemeDict[name]['plus'] = format_hsl(plusHue, mainSaturation, plusLightness)
    minusHue = mainHue - deltaHue
    minusLightness = solve_luminance_for(minusHue, mainSaturation, mainLuminance)
    schemeDict[name]['minus'] = format_hsl(minusHue, mainSaturation, minusLightness)

with open('main.css') as f: styleStringWithoutColor = f.read()

for scheme, colorsDict in schemeDict.items():
    styleString = styleStringWithoutColor
    for colorType, colorValue in sorted(colorsDict.items(), reverse=True):
        styleString = styleString.replace(colorType, colorValue)
    with open('build/%s.css' % scheme, 'w') as f: f.write(styleString)
