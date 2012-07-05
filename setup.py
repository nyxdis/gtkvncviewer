#!/usr/bin/env python

import glob, os
from distutils.core import setup

# generate .mo files
if not os.path.exists('locale'):
    os.mkdir('locale')

for po in glob.glob('po/*.po'):
    lang = po[3:-3]
    if not os.path.exists('locale/' + lang):
        os.mkdir('locale/' + lang)
    mo = 'locale/' + lang + '/gtkvncviewer.mo'
    print "Generating", mo
    os.system('msgfmt %s -o %s' % (po, mo))

# TODO: autogenerate locales file list
setup(name='gtkvncviewer',
        version='0.5.0',
        description='Simple Gtk+ tool to connect to VNC server',
        author='Clement Lorteau',
        author_email='northern_lights@users.sourceforge.net',
        url='http://cmende.github.com/gtkvncviewer',
        scripts=['gtkvncviewer'],
        license='GPL-2',
        data_files=[('share/gtkvncviewer', glob.glob('gtkvncviewer.glade')),
            ('share/pixmaps', glob.glob('pixmaps/*')),
            ('share/applications', ['gtkvncviewer.desktop']),
            ('share/man/man1', ['gtkvncviewer.1']),
            ('share/locale/de/LC_MESSAGES', ['locale/de/gtkvncviewer.mo']),
            ]
        )
