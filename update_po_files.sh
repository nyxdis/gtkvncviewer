#!/bin/sh
intltool-extract --type=gettext/glade data/gtkvncviewer.glade
xgettext --copyright-holder="Clement Lorteau" --language=Python --keyword=_ --keyword=N_ --output=po/gtkvncviewer.pot gtkvncviewer.py data/gtkvncviewer.glade.h
