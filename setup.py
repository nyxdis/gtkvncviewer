#!/usr/bin/env python

import glob, os
from distutils.command.install import install as _install
from distutils.core import Command, setup

class install(_install):
    def build_locales(self):
        # generate .mo files
        if not os.path.exists('locale'):
            os.mkdir('locale')

        for po in glob.glob('po/*.po'):
            lang = po[3:-3]
            if not os.path.exists('locale/' + lang):
                os.mkdir('locale/' + lang)
            mo = 'locale/' + lang + '/gtkvncviewer.mo'
            print("Generating %s" % mo)
            os.system('msgfmt %s -o %s' % (po, mo))

    def run(self):
        self.build_locales()
        _install.run(self)

class update_po(Command):
    user_options = [
            ('pot', None, "Generate po/gtkvncviewer.pot"),
            ('po', None, "Update po/*.po"),
            ]

    boolean_options = ['pot', 'po']

    def initialize_options(self):
        self.pot = True
        self.po = True

    def finalize_options(self):
        pass

    def update_pot(self):
        os.system("intltool-extract --type=gettext/glade gtkvncviewer.ui")
        os.system("xgettext --copyright-holder=\"Christoph Mende\" --language=Python --keyword=_ --output=po/gtkvncviewer.pot gtkvncviewer gtkvncviewer.ui.h")

    def update_po(self):
        os.chdir("po")
        for po in glob.glob("*.po"):
            lang = po[:-3]
            print("Updating %s" % lang)
            os.system("intltool-update -d -g gtkvncviewer -o %s %s" % (po, lang))

    def run(self):
        if self.pot:
            self.update_pot()
        if self.po:
            self.update_po()

# TODO: autogenerate locales file list
setup(name='gtkvncviewer',
        version='0.5.0',
        description="Simple Gtk+ tool to connect to VNC server",
        author="Christoph Mende",
        author_email="mende.christoph@gmail.com",
        url="http://cmende.github.com/gtkvncviewer",
        scripts=['gtkvncviewer'],
        license='GPL-2',
        data_files=[('share/gtkvncviewer', glob.glob('gtkvncviewer.ui')),
            ('share/pixmaps', glob.glob('pixmaps/*')),
            ('share/applications', ['gtkvncviewer.desktop']),
            ('share/man/man1', ['gtkvncviewer.1']),
            ('share/locale/de/LC_MESSAGES', ['locale/de/gtkvncviewer.mo']),
            ],
        cmdclass={'install': install,
            'update_po': update_po},
        )
