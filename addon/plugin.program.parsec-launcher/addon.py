"""
    Plugin for Launching programs
"""

# -*- coding: UTF-8 -*-
# main imports
import sys
import os
import urllib
import urllib2
import json
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

API_BASEURL = "https://parsecgaming.com/v1/"
API_AUTHURL = API_BASEURL + "auth"
API_LIST_COMPUTERS = API_BASEURL + "server-list?include_managed=true"
API_SWITCH_COMPUTER_ON = API_BASEURL + "activate-lease"
API_SWITCH_COMPUTER_OFF = API_BASEURL + "deactivate-lease"

THUMBNAIL_PATH = os.path.join(plugintools.get_runtime_path() ,"resources" , "img")
DEFAULT_FANART = os.path.join(plugintools.get_runtime_path(), "fanart.jpg")
DEFAULT_LOGO = os.path.join(THUMBNAIL_PATH,"parsec-logo.png")
LOGO_SERVER_ON = DEFAULT_LOGO
LOGO_SERVER_OFF = DEFAULT_LOGO
LOGO_SERVER_PENDING = DEFAULT_LOGO

parsec_session_id = False
current_computer = False
dialog = xbmcgui.Dialog()
addon = xbmcaddon.Addon(id='plugin.program.parsec-launcher')

# MAIN MENU
LANG_TITLE_LAUNCH_PARSEC=addon.getLocalizedString(30020).encode('utf-8')
LANG_TITLE_MANAGE_COMPUTERS=addon.getLocalizedString(30021).encode('utf-8')
LANG_TITLE_MANAGE=addon.getLocalizedString(30022).encode('utf-8')
LANG_TITLE_MANAGE_COMPUTER_SWITCH_ON=addon.getLocalizedString(30023).encode('utf-8')
LANG_TITLE_MANAGE_COMPUTER_SWITCH_OFF=addon.getLocalizedString(30024).encode('utf-8')
LANG_TITLE_MANAGE_COMPUTER_IS_PENDING=addon.getLocalizedString(30025).encode('utf-8')
LANG_TITLE_MANAGE_COMPUTER_MESSAGE_PENDING=addon.getLocalizedString(30200).encode('utf-8')
LANG_TITLE_MANAGE_COMPUTER_MESSAGE_ON=addon.getLocalizedString(30201).encode('utf-8')
LANG_TITLE_MANAGE_COMPUTER_MESSAGE_OFF=addon.getLocalizedString(30202).encode('utf-8')


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
    plugintools.add_item(action="launch_parsec", title=LANG_TITLE_LAUNCH_PARSEC, thumbnail=DEFAULT_LOGO , fanart=DEFAULT_LOGO , folder=False)
    plugintools.add_item(action="manage_computers", title=LANG_TITLE_MANAGE_COMPUTERS, thumbnail=DEFAULT_LOGO , fanart=DEFAULT_LOGO , folder=True)


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


def manage_computers(params):
    # List of available computers
    global current_computer
    global parsec_session_id
    plugintools.set_view(plugintools.THUMBNAIL)
    computers = get_computers()

    for computer in computers:
        current_computer = computer
        computer_title = get_computer_title()
        plugintools.log("parsec computer title is " + computer_title)
        computer_status_logo = get_computer_status_logo()
        plugintools.add_item(
            action="manage_computer",
            title=computer_title,
            thumbnail=computer_status_logo,
            fanart=DEFAULT_FANART,
            extra=json.dumps(current_computer),
            session_id=parsec_session_id,
            folder=True
        )


def manage_computer(params):
    # Lists actions for computer
    global current_computer
    global parsec_session_id
    computer_json = params.get('extra')
    parsec_session_id = params.get('session_id')
    current_computer = json.loads(computer_json)

    target_state_action = get_target_state_action()
    target_state_title = get_target_title()
    computer_status_logo = get_computer_status_logo()
    plugintools.add_item(
        action=target_state_action,
        title=target_state_title,
        thumbnail=computer_status_logo,
        fanart=DEFAULT_FANART,
        extra=computer_json,
        session_id=parsec_session_id,
        folder=False
    )


def switch_computer_on(params):
    # trigger switching on the computer
    global current_computer
    global parsec_session_id
    computer_json = params.get('extra')
    parsec_session_id = params.get('session_id')
    current_computer = json.loads(computer_json)
    computer_id = current_computer['lease']
    switch_computer_state('on', computer_id)
    xbmc.executebuiltin(
        'Notification('+LANG_TITLE_MANAGE_COMPUTER_MESSAGE_ON+',5000,'+DEFAULT_LOGO+')'
    )
    pass


def switch_computer_off(params):
    # trigger switching off the computer
    global current_computer
    global parsec_session_id
    computer_json = params.get('extra')
    parsec_session_id = params.get('session_id')
    current_computer = json.loads(computer_json)
    computer_id = current_computer['lease']
    switch_computer_state('off', computer_id)
    xbmc.executebuiltin(
        'Notification('+LANG_TITLE_MANAGE_COMPUTER_MESSAGE_OFF+',5000,'+DEFAULT_LOGO+')'
    )
    pass


def switch_computer_pending(params):
    # just pass this. working is already in progress
    xbmc.executebuiltin(
        'Notification('+LANG_TITLE_MANAGE_COMPUTER_MESSAGE_PENDING+',5000,'+DEFAULT_LOGO+')'
    )
    pass


def get_computer_title():
    global current_computer
    # returns computer name
    computer_title = current_computer['name'] + " (" + current_computer['status'] + ")"

    return computer_title


def get_computer_status_logo():
    global current_computer
    computer = current_computer

    # Return matching title to current state
    if computer['status'] == 'off':
        status_logo = LOGO_SERVER_OFF
    elif computer['status'] == 'on':
        status_logo = LOGO_SERVER_ON
    else:
        status_logo = LOGO_SERVER_PENDING

    return status_logo


def get_target_state_action():
    global current_computer
    computer = current_computer

    # Returns action method string to be target
    target_state_action = 'switch_computer'
    if computer['status'] == 'off':
        target_state_action += '_on'
    elif computer['status'] == 'on':
        target_state_action += '_off'
    else:
        target_state_action += '_pending'

    return target_state_action


def get_target_title():
    # Return matching title to current state
    global current_computer
    computer = current_computer

    if computer['status'] == 'off':
        target_title = LANG_TITLE_MANAGE_COMPUTER_SWITCH_ON
    elif computer['status'] == 'on':
        target_title = LANG_TITLE_MANAGE_COMPUTER_SWITCH_OFF
    else:
        target_title = LANG_TITLE_MANAGE_COMPUTER_IS_PENDING

    return target_title


def get_computers():
    # Returns list wit available computers and their metadata
    session_id = get_parsec_session_id()
    plugintools.log("Received parsec sessionid:" + session_id)
    computers = get_computers_by_session(session_id)

    return computers


def get_computers_by_session(session_id):
    # Using session id for retrievin list of machines
    user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0)'
    values = {}
    headers = {
        'User-Agent': user_agent,
        'x-parsec-session-id': session_id
    }

    data = urllib.urlencode(values)
    req = urllib2.Request(API_LIST_COMPUTERS, data, headers)
    response = urllib2.urlopen(req)
    computers = json.load(response)

    return computers


def get_parsec_session_id():
    # fetches current session id or creates it
    global parsec_session_id

    if parsec_session_id == False:
        parsec_user = plugintools.get_setting("parsec_user")
        parsec_passwd = plugintools.get_setting("parsec_passwd")

        user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
        values = {'email': parsec_user,
                  'password': parsec_passwd,
                  'expiration_type': 'short'}
        headers = {'User-Agent': user_agent}

        data = urllib.urlencode(values)
        req = urllib2.Request(API_AUTHURL, data, headers)
        response = urllib2.urlopen(req)

        data = json.load(response)
        parsec_session_id = data['session_id']

    return parsec_session_id


def switch_computer_state(target_state, computer_id):
    if target_state == 'on':
        url = API_SWITCH_COMPUTER_ON
    else:
        url = API_SWITCH_COMPUTER_OFF

    user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0)'
    values = {
        'id': computer_id
    }
    headers = {
        'User-Agent': user_agent,
        'x-parsec-session-id': parsec_session_id
    }

    data = urllib.urlencode(values)

    req = urllib2.Request(url, data, headers)
    urllib2.urlopen(req)


def get_is_instance_running():
    return True


run()
