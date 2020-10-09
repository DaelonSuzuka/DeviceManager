from qt import *


darkPalette = QStyleFactory.create('fusion').standardPalette()


light = QColor('#525252')
mid = QColor('#414141')
dark = QColor('#313131')
accent= QColor('#ca3e47')

class colors:
    navy = '#001f3f'
    blue = '#0074D9'
    aqua = '#7FDBFF'
    teal = '#39CCCC'
    olive = '#3D9970'
    green = '#2ECC40'
    lime = '#01FF70'
    yellow = '#FFDC00'
    orange = '#FF851B'
    red = '#FF4136'
    maroon = '#85144b'
    fuchsia = '#F012BE'
    purple = '#B10DC9'
    black = '#111111'
    gray = '#AAAAAA'
    silver = '#DDDDDD'
    white = '#FFFFFF'

class qcolors:
    navy = QColor('#001f3f')
    blue = QColor('#0074D9')
    aqua = QColor('#7FDBFF')
    teal = QColor('#39CCCC')
    olive = QColor('#3D9970')
    green = QColor('#2ECC40')
    lime = QColor('#01FF70')
    yellow = QColor('#FFDC00')
    orange = QColor('#FF851B')
    red = QColor('#FF4136')
    maroon = QColor('#85144b')
    fuchsia = QColor('#F012BE')
    purple = QColor('#B10DC9')
    black = QColor('#111111')
    gray = QColor('#AAAAAA')
    silver = QColor('#DDDDDD')
    white = QColor('#FFFFFF')


# base
darkPalette.setColor(QPalette.WindowText, QColor(180, 180, 180))
darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
darkPalette.setColor(QPalette.Light, QColor(180, 180, 180))
darkPalette.setColor(QPalette.Midlight, QColor(90, 90, 90))
darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
darkPalette.setColor(QPalette.Text, QColor(180, 180, 180))
darkPalette.setColor(QPalette.BrightText, QColor(180, 180, 180))
darkPalette.setColor(QPalette.ButtonText, QColor(180, 180, 180))
darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
darkPalette.setColor(QPalette.HighlightedText, QColor(180, 180, 180))
darkPalette.setColor(QPalette.Link, QColor(56, 252, 196))
darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
darkPalette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
darkPalette.setColor(QPalette.ToolTipText, QColor(180, 180, 180))

# disabled
darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
darkPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
darkPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))
