"""
    Plugin for Launching programs
"""

# -*- coding: UTF-8 -*-
# main imports
import sys
import os
import xbmc
import xbmcgui
import xbmcaddon
import plugintools

# plugin constants
__plugin__ = "Parsec"
__author__ = "liberavia"
__url__ = "https://github.com/liberavia/kodi-parsec"
__git_url__ = "https://github.com/liberavia/kodi-parsec"
__credits__ = "mcobit"
__version__ = "0.0.1"

THUMBNAIL_PATH = os.path.join(plugintools.get_runtime_path() ,"resources" , "img")
FANART = os.path.join(plugintools.get_runtime_path() , "fanart.jpg")

dialog = xbmcgui.Dialog()
addon = xbmcaddon.Addon(id='plugin.program.parsec-launcher')

# MAIN MENU
LANG_TITLE_LAUNCH_PARSEC=addon.getLocalizedString(30020).encode('utf-8')

# Entry point
def run():
	plugintools.log("kodi-parsec.run")

	# Get params
	params = plugintools.get_params()

	if params.get("action") is None:
		main_list(params)
	else:
		action = params.get("action")
		exec action+"(params)"
	plugintools.close_item_list()

def main_list(params):
	# Main menu
	plugintools.set_view(plugintools.THUMBNAIL)
	thumbnail_parsec_logo = os.path.join(THUMBNAIL_PATH,"parsec-logo.png")
	plugintools.add_item(action="launch_parsec", title=LANG_TITLE_LAUNCH_PARSEC, thumbnail=thumbnail_parsec_logo , fanart=thumbnail_parsec_logo , folder=False)

def launch_parsec(params):
	instance_running = get_is_instance_running()
	if instance_running:
		parsec_user = plugintools.get_setting("parsec_user")
		parsec_passwd = plugintools.get_setting("parsec_passwd")
		plugintools.log("parsec checking existance of credentials")
		if parsec_user != "" and parsec_passwd != "":
			full_command = "/home/osmc/Scripts/parsec-start/xstart.sh " + parsec_user +  " " + parsec_passwd
			output=os.popen(full_command).read()
			#dialog.ok("Starting X11",output)
			#print output
		else:
			plugintools.message("parsec", "Please add your parsec credentials in addon settings")

def get_is_instance_running():
	return True

run()
