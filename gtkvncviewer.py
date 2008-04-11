#!/usr/bin/env python

import sys
try:
 	import pygtk
  	pygtk.require("2.0")
except:
  	pass
try:
	import gtk
  	import gtk.glade
	import gtkvnc
	import gconf
	import gnomekeyring
except:
	sys.exit(1)
try:
	import LaunchpadIntegration
	launchpad = True
except:
	launchpad = False

import os

#internat'
import locale
import gettext
APP = 'gtkvncviewer'
DIR = 'locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
gtk.glade.bindtextdomain(APP, DIR)
gtk.glade.textdomain(APP)
gettext.install(APP, DIR, unicode=1)
#lang = gettext.translation(APP, DIR, languages=['ar'])
#lang.install()
_ = gettext.gettext

class GtkVncViewer:

	def __init__(self):	
		#build GUI
		self.gladefile = "data/gtkvncviewer.glade"  
	        self.wTree = gtk.glade.XML(self.gladefile) 
		self.dialog = self.wTree.get_widget("connectDialog")
		self.about = self.wTree.get_widget("aboutDialog")
		self.window = self.wTree.get_widget("window")
		self.window_label = self.wTree.get_widget("window_label")
		self.layout = self.wTree.get_widget("viewport1")
		self.scrolledwindow = self.wTree.get_widget("scrolledwindow1")
		self.iconview = self.wTree.get_widget("iconview1")
		self.vnc=gtkvnc.Display()
		self.model = gtk.ListStore (str,str,str,gtk.gdk.Pixbuf)
		self.iconview.set_model(self.model)
		self.iconview.set_text_column(0)
		self.iconview.set_pixbuf_column(3)
		self.helpMenu = self.wTree.get_widget("helpMenu")
		self.helpButton = self.wTree.get_widget("helpButton")
		self.helpMenu.attach_to_widget(self.helpButton, None)
		if (launchpad):
			LaunchpadIntegration.set_sourcepackagename("gtkvncviewer")
			LaunchpadIntegration.add_items(self.helpMenu,0,False,False)
		else:
			self.helpButton.set_sensitive(False)
		
		if (self.dialog):
			self.window.connect("destroy", gtk.main_quit)
			#Create our dictionay and connect it
			dic = { "on_quitButton_clicked" : gtk.main_quit,
				"on_aboutButton_clicked" : self.show_about_dialog,
				"on_aboutDialog_response" : self.handle_about_dialog_answer,
				"on_aboutDialog_delete_event" : self.hide_about_dialog,
				"on_connectButton_clicked" : self.vncconnect,
				"on_window_delete_event" : self.close_window,
				"on_disconnectButton_clicked" : self.disconnect,
				"on_addButton_clicked" : self.add_server,
				"on_iconview1_selection_changed" : self.selected,
				"on_iconview1_item_activated" : self.activated,
				"on_delButton_clicked" : self.delete_clicked,
				"on_screenshotButton_clicked" : self.screenshot,
				"on_helpButton_clicked" : self.helpMenuPop}
			self.wTree.signal_autoconnect(dic)
			self.dialog.show()
		
		#read stored credentials
		GCONF_AUTH_KEY = "/apps/gtkvncviewer"
		keyring = gnomekeyring.get_default_keyring_sync()
		gconfclient = gconf.client_get_default()
		gconfclient.add_dir (GCONF_AUTH_KEY,
			gconf.CLIENT_PRELOAD_RECURSIVE)
		entries = gconfclient.all_entries(GCONF_AUTH_KEY)
		if len(entries) == 0:
			return #found nothing
		for i in range(len(entries)):
			server = entries[i].get_key()
			server = server.replace (GCONF_AUTH_KEY+"/", "")
			auth_token = entries[i].get_value().get_int()
			if auth_token > 0:
				try:
					secret = gnomekeyring.item_get_info_sync(keyring, auth_token).get_secret()
				except gnomekeyring.DeniedError:
					username = None
					password = None
					auth_token = 0
					print _("gnome-keyring access denied")
				else:
					username, password = secret.split('\n')
			else:
				username = None
				password = None
			pixbuf = self.iconview.render_icon(gtk.STOCK_NETWORK, gtk.ICON_SIZE_BUTTON)
			self.model.append([server, username, password, pixbuf])
	
	def helpMenuPop (self, data):
		self.helpMenu.popup(None, None, None, 0, 0, gtk.get_current_event_time())
	
	def screenshot (self, data):
		homeDir = os.environ.get('HOME', None)
		pix = self.vnc.get_pixbuf()
        	pix.save(homeDir+"/vnc.png", "png", { "tEXt::Generator App": "gtkvncviewer" })
		dialog = gtk.MessageDialog (self.window,
			gtk.MESSAGE_INFO,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.BUTTONS_OK,
			_("Screenshot saved in")+" "+homeDir+"/vnc.png")
		dialog.run()
		dialog.destroy()

	def delete_clicked (self, data):		
		select = self.iconview.get_selected_items()
		if len(select) == 0:
			print _("nothing to delete")
			return

		i = select[0][0]
		iter = self.model.get_iter(i)
		s = self.model.get(iter,0,1,2)
		server = s[0]
		
		#ask confirmation
		dialog = gtk.MessageDialog (self.window,
			gtk.MESSAGE_QUESTION,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.BUTTONS_YES_NO,
			_("Are you sure you want remove")+" \""+server+"\" ?")
		r = dialog.run()
		dialog.destroy()
		if (r == gtk.RESPONSE_NO):
			print _("deletion canceled")
		else:
			GCONF_AUTH_KEY = "/apps/gtkvncviewer"	
			gconfclient = gconf.client_get_default()
			gconfclient.add_dir (GCONF_AUTH_KEY,
				gconf.CLIENT_PRELOAD_RECURSIVE)
			entry = gconfclient.get_entry(GCONF_AUTH_KEY+"/"+server,
				"", False)
			server = entry.get_key()
			server = server.replace (GCONF_AUTH_KEY+"/", "")
			auth_token = entry.get_value().get_int()
			if auth_token > 0:
				try:
					#delete gnome-keyring entry
					keyring = gnomekeyring.get_default_keyring_sync()
					gnomekeyring.item_delete_sync(keyring, auth_token)
					#delete gconf entry
					gconfclient.unset(GCONF_AUTH_KEY+"/"+server)
					#remove from icon view
					select = self.iconview.get_selected_items()
					if len(select) == 0:
						return
					i = select[0][0]
					iter = self.model.get_iter(i)
					self.model.remove(iter)
					print server+" deleted"
				except gnomekeyring.DeniedError:
					auth_token = 0
					print _("gnome-keyring access denied, could not delete")
			else:
				print _("gconf read error, could not delete")

	def activated (self, widget, data):
		self.vncconnect(self.window)

	def selected (self, data):
		username = self.wTree.get_widget("usernameEntry")
		password = self.wTree.get_widget("pwdEntry")
		server = self.wTree.get_widget("serverEntry")
		select = self.iconview.get_selected_items()
		if len(select) == 0:
			return
		i = select[0][0]
		iter = self.model.get_iter(i)
		s = self.model.get(iter,0,1,2)
		server.set_text(s[0])
		if (s[1] != None):
			username.set_text(s[1])
		else:
			username.set_text("")
		if (s[2] != None):
			password.set_text(s[2])
		else:
			password.set_text("")
	
	def add_server (self, data):

		#add it to the iconview
		pixbuf = self.iconview.render_icon(gtk.STOCK_NETWORK, gtk.ICON_SIZE_BUTTON)
		username = self.wTree.get_widget("usernameEntry").get_text()
		password = self.wTree.get_widget("pwdEntry").get_text()
		server = self.wTree.get_widget("serverEntry").get_text()
		if server == "":
			return
		self.model.append([server, username, password, pixbuf])

		#now save it in gnome-keyring
		GCONF_AUTH_KEY = "/apps/gtkvncviewer/"+server
		keyring = gnomekeyring.get_default_keyring_sync()
		auth_token = gnomekeyring.item_create_sync(
                	keyring,
                	gnomekeyring.ITEM_GENERIC_SECRET,
                	"gtkvncviewer VNC server credentials ("+server+")",
                	dict(appname="gtkvncviewer, vnc server credentials"),
			"\n".join((username, password)), True)
           	gconf.client_get_default().set_int(GCONF_AUTH_KEY, auth_token)

	def quit():
		self.vnc.close()
		print "Bye."
		if (self.window):
			self.window.destroy()

	def close_window(self, widget, data):
		quit()
	
	def disconnect(self, data):
		quit()

	def handle_about_dialog_answer(self, widget, data):
		if(data==-6):
			self.about.hide()

	def show_about_dialog(self, widget):
		self.about.show()

	def hide_about_dialog(self, widget, data):
		self.about.hide()
		return True

	def vncconnect(self, window):
		#layout = self.wTree.get_widget("viewport1")
		self.dialog.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
		#self.layout.add(self.vnc)
		#self.vnc.realize()
		username = self.wTree.get_widget("usernameEntry").get_text()
		password = self.wTree.get_widget("pwdEntry").get_text()
		server = self.wTree.get_widget("serverEntry").get_text()
		self.vnc.set_credential(gtkvnc.CREDENTIAL_USERNAME, username)
		self.vnc.set_credential(gtkvnc.CREDENTIAL_PASSWORD, password)
		self.vnc.set_credential(gtkvnc.CREDENTIAL_CLIENTNAME, "gtkvncviewer")
		print "Connecting to %s..." % server
		self.vnc.open_host(server, "5900")
		#vnc.connect("vnc-auth-credential", self.vnc_auth_cred)
		self.vnc.connect("vnc-connected", self.vnc_connected, self)
		self.vnc.connect("vnc-initialized", self.vnc_initialized, self.window, username, server, self.dialog, self.window_label, self.scrolledwindow)
		self.vnc.connect("vnc-disconnected", self.vnc_disconnected, self.dialog, self)

	def vnc_initialized (src, vnc, window, username, server, dialog, window_label, scrolled_window):
		print _("Connection initialized")
		title = "%s@%s - gtkvncviewer" % (username, server)
		dialog.hide()
		window.set_title(title)
		window_label.set_markup ("<big><b>%s@%s</b></big>" % (username, server))
		window.show_all()
		window.resize (vnc.get_width(), vnc.get_height())
		vnc.grab_focus()
		
	def vnc_disconnected(src, vnc, window, self):
		print _("Disconnected")
		dialog = gtk.MessageDialog (window,
			gtk.MESSAGE_INFO,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.BUTTONS_OK,
			_("You have been disconnected"))
		dialog.run()
		dialog.destroy()
		self.vnc.destroy()
		self.vnc=gtkvnc.Display()
		window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.ARROW))

	def vnc_connected(src, data, self):
		print _("Connected")
		self.layout.add(self.vnc)
		self.vnc.realize()

if __name__ == "__main__":
	instance = GtkVncViewer()
	gtk.main()
