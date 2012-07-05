#!/usr/bin/env python

import glob
from distutils.core import setup

# TODO: locales
setup(name='gtkvncviewer',
        version='0.5.0',
        description='Simple Gtk+ tool to connect to VNC server',
        author='Clement Lorteau',
        author_email='northern_lights@users.sourceforge.net',
        url='http://cmende.github.com/gtkvncviewer',
        scripts=['gtkvncviewer'],
        license='GPL-2',
        data_files=[('share/gtkvncviewer', ['gtkvncviewer.py']),
            ('share/gtkvncviewer/data', glob.glob('data/*')),
            ('share/applications', ['gtkvncviewer.desktop']),
            ('share/man/man1', ['gtkvncviewer.1'])]
        )
