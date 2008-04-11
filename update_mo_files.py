#!/usr/bin/env python
import os

os.rmdir("locale")
os.mkdir("locale")
files = os.listdir("po")
for i in range(len(files)):
	if (files[i].endswith(".po")):
		short = files[i].split(".po")
		short = short[0]
		os.mkdir("locale/"+short)
		os.mkdir("locale/"+short+"/LC_MESSAGES")
		os.system('msgfmt --output-file=locale/'+short+'/LC_MESSAGES/gtkvncviewer.mo po/'+files[i])
