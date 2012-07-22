# extract translations from interface file
intltool-extract --type=gettext/glade gtkvncviewer.ui

# build pot file
xgettext --copyright-holder="Christoph Mende" --language=Python --keyword=_ --output=po/gtkvncviewer.pot gtkvncviewer gtkvncviewer.ui.h

# update po files
pushd po
for i in *.po; do
	lang=${i/.po}
	echo "Updating ${lang}"
	intltool-update -d -g gtkvncviewer -o ${i} ${i/.po}
done
popd
