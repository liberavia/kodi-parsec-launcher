"""
    Plugin for Launching programs
"""

# -*- coding: UTF-8 -*-
# main imports
import sys
import os
import urllib
import urllib2
import requests
import json
import xbmc
import xbmcgui
import xbmcaddon
import plugintools
import pprint
import time
import threading

# plugin constants
__plugin__ = "Parsec"
__author__ = "liberavia"
__url__ = "https://github.com/liberavia/kodi-parsec"
__git_url__ = "https://github.com/liberavia/kodi-parsec"
__version__ = "0.1.0"

# Constants
MAX_BACKGROUND_REPEATS=30 # which is 5 min waiting
API_BASEURL = "https://parsecgaming.com/v1/"
API_AUTHURL = API_BASEURL + "auth"
API_LIST_COMPUTERS = API_BASEURL + "server-list?include_managed=true"
API_USER_INFO = API_BASEURL + "me"
API_SWITCH_COMPUTER_ON = API_BASEURL + "activate-lease"
API_SWITCH_COMPUTER_OFF = API_BASEURL + "deactivate-lease"
ADDON_BASE_PATH = os.path.dirname(__file__)
ADDON_SCRIPT_PATH = os.path.join(ADDON_BASE_PATH, 'scripts')
THUMBNAIL_PATH = os.path.join(plugintools.get_runtime_path(), "resources", "img")
DEFAULT_FANART = os.path.join(plugintools.get_runtime_path(), "fanart.jpg")
DEFAULT_LOGO = os.path.join(THUMBNAIL_PATH, "parsec-logo.png")
LOGO_SERVER_ON = DEFAULT_LOGO
LOGO_SERVER_OFF = DEFAULT_LOGO
LOGO_SERVER_PENDING = DEFAULT_LOGO
LOGO_SERVER_CONNECT = DEFAULT_LOGO

# Globals
parsec_session_id = False
current_computer = False
dialog = xbmcgui.Dialog()
addon = xbmcaddon.Addon(id='plugin.program.parsec-launcher')
user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0'
parsec_user = ""
parsec_passwd = ""
background_repeats = 0

# Language strings
LANG_TITLE_CONNECT_PARSEC=addon.getLocalizedString(30020).encode('utf-8')
LANG_TITLE_MANAGE_COMPUTERS=addon.getLocalizedString(30021).encode('utf-8')
LANG_TITLE_MANAGE=addon.getLocalizedString(30022).encode('utf-8')
LANG_TITLE_MANAGE_COMPUTER_SWITCH_ON=addon.getLocalizedString(30023).encode('utf-8')
LANG_TITLE_MANAGE_COMPUTER_SWITCH_OFF=addon.getLocalizedString(30024).encode('utf-8')
LANG_TITLE_MANAGE_COMPUTER_IS_PENDING=addon.getLocalizedString(30025).encode('utf-8')
LANG_PARSEC=addon.getLocalizedString(30026).encode('utf-8')
LANG_TITLE_STATUS=addon.getLocalizedString(30027).encode('utf-8')
LANG_TITLE_CREATED=addon.getLocalizedString(30028).encode('utf-8')
LANG_TITLE_LAST_UPDATED=addon.getLocalizedString(30029).encode('utf-8')
LANG_TITLE_PROVIDER=addon.getLocalizedString(30030).encode('utf-8')
LANG_TITLE_MACHINE_TYPE=addon.getLocalizedString(30031).encode('utf-8')
LANG_TITLE_REGION=addon.getLocalizedString(30032).encode('utf-8')
LANG_TITLE_CREDIT=addon.getLocalizedString(30033).encode('utf-8')
LANG_TITLE_PLAYTIME=addon.getLocalizedString(30034).encode('utf-8')
LANG_TITLE_HOURS = addon.getLocalizedString(30035).encode('utf-8')
LANG_TITLE_DOLLAR = addon.getLocalizedString(30036).encode('utf-8')
LANG_TITLE_COMPUTER_INFO = addon.getLocalizedString(30037).encode('utf-8')
LANG_TITLE_USER_INFO = addon.getLocalizedString(30038).encode('utf-8')
LANG_TITLE_USERNAME = addon.getLocalizedString(30039).encode('utf-8')
LANG_MESSAGE_NO_CREDENTIALS=addon.getLocalizedString(30040).encode('utf-8')
LANG_QUESTION_TO_SETTINGS=addon.getLocalizedString(30041).encode('utf-8')
LANG_MESSAGE_WRONG_CREDENTIALS=addon.getLocalizedString(30042).encode('utf-8')
LANG_MESSAGE_COMPUTER_OFF=addon.getLocalizedString(30043).encode('utf-8')
LANG_QUESTION_QUESTION_SWITCH_ON=addon.getLocalizedString(30044).encode('utf-8')
LANG_MESSAGE_COMPUTER_ON=addon.getLocalizedString(30045).encode('utf-8')
LANG_MESSAGE_BACKGROUND_TASK_BREAK=addon.getLocalizedString(30046).encode('utf-8')

LANG_TITLE_MANAGE_COMPUTER_MESSAGE_PENDING=addon.getLocalizedString(30200).encode('utf-8')
LANG_TITLE_MANAGE_COMPUTER_MESSAGE_ON=addon.getLocalizedString(30201).encode('utf-8')
LANG_TITLE_MANAGE_COMPUTER_MESSAGE_OFF=addon.getLocalizedString(30202).encode('utf-8')


def run():
    """
    Entry point of addon

    :return:
    """
    plugintools.log("kodi-parsec.run")

    # Get params
    params = plugintools.get_params()

    if params.get("action") is None:
        main_list(params)
    else:
        action = params.get("action")
        exec action+"(params)"
    plugintools.close_item_list()
    pass


def main_list(params):
    """
    Main menu
    List of available computers

    :param params:
    :return:
    """

    global current_computer
    global parsec_session_id

    user_credentials_available()
    check_credentials()

    computers = get_computers()
    user = get_user_info()

    for index, computer in enumerate(computers):
        current_computer = computer
        numberselect = int(index + 1)
        computer_title = get_computer_title()
        context=get_computer_context_menu(computer, numberselect)
        plugintools.log("parsec computer title is " + computer_title)
        computer_status_logo = get_computer_status_logo()
        user_json = json.dumps(user)
        plugintools.log("user json is : " + user_json)

        plugintools.add_computer_list_item(
            action="manage_computer",
            title=computer_title,
            session_id=parsec_session_id,
            computer=json.dumps(current_computer),
            user=user_json,
            numberselect=numberselect,
            thumbnail=computer_status_logo,
            fanart=DEFAULT_FANART,
            folder=True,
            context=context
        )
    pass


def user_credentials_available():
    """
    Checking if user credentials are set and asking for redirecting to
    settings if no credentials are available

    :return:
    """

    global parsec_user
    global parsec_passwd

    parsec_user = plugintools.get_setting("parsec_user")
    parsec_passwd = plugintools.get_setting("parsec_passwd")
    plugintools.log("parsec checking existance of credentials")
    if parsec_user != "" and parsec_passwd != "":
        return True
    else:
        answer = xbmcgui.Dialog().yesno(
            LANG_PARSEC,
            LANG_MESSAGE_NO_CREDENTIALS,
            LANG_QUESTION_TO_SETTINGS
        )
        if answer == True:
            plugintools.open_settings_dialog()
            redirect_to_beginning()
        return False


def check_credentials():
    """
    Checks if configured credentials are working. If not
    trigger questioning user for reconfiguration

    :return:
    """
    try:
        get_parsec_session_id()
    except:
        answer = xbmcgui.Dialog().yesno(
            LANG_PARSEC,
            LANG_MESSAGE_WRONG_CREDENTIALS,
            LANG_QUESTION_TO_SETTINGS
        )
        if answer == True:
            plugintools.open_settings_dialog()
            redirect_to_beginning()


def get_computer_context_menu(computer, numberselect):
    """
    returns a list of context entries per computer

    :param computer:
    :param numberselect:
    :return:
    """

    global parsec_session_id

    switch_computer_action = get_target_state_action()
    context_label_switch_computer = get_target_title()
    context_url_switch_computer = '%s?action=%s&title=%s&session_id=%s&computer=%s&thumbnail=%s&fanart=%s&numberselect=%s' % (
        sys.argv[0],
        switch_computer_action,
        urllib.quote_plus(context_label_switch_computer),
        urllib.quote_plus(parsec_session_id),
        urllib.quote_plus(json.dumps(computer)),
        urllib.quote_plus(DEFAULT_LOGO),
        urllib.quote_plus(DEFAULT_FANART),
        numberselect,
    )

    connect_action ='connect_to_computer'
    context_label_connect_computer = LANG_TITLE_CONNECT_PARSEC
    context_url_connect_computer = '%s?action=%s&title=%s&session_id=%s&computer=%s&thumbnail=%s&fanart=%s&numberselect=%s' % (
        sys.argv[0],
        connect_action,
        urllib.quote_plus(context_label_connect_computer),
        urllib.quote_plus(parsec_session_id),
        urllib.quote_plus(json.dumps(computer)),
        urllib.quote_plus(DEFAULT_LOGO),
        urllib.quote_plus(DEFAULT_FANART),
        numberselect,
    )

    context_menu = []
    context_menu.append({'label': context_label_switch_computer, 'url': context_url_switch_computer})
    context_menu.append({'label': context_label_connect_computer, 'url': context_url_connect_computer})

    return context_menu


def connect_to_computer(params):
    """
    initializes connection to a running computer

    :param params:
    :return:
    """
    global current_computer
    global parsec_session_id
    global parsec_user
    global parsec_passwd

    parsec_user = plugintools.get_setting("parsec_user")
    parsec_passwd = plugintools.get_setting("parsec_passwd")

    computer_json = params.get('computer')
    parsec_session_id = params.get('session_id')
    current_computer = json.loads(computer_json)
    numberselect = params.get('numberselect')

    instance_running = get_is_instance_running(current_computer)
    instance_off = get_is_instance_off(current_computer)

    if instance_running:
        full_command = "/home/osmc/Scripts/parsec-start/xstart.sh " + parsec_user + " " + parsec_passwd + " " + numberselect
        os.popen(full_command)
    elif instance_off:
        answer = xbmcgui.Dialog().yesno(
            LANG_PARSEC,
            LANG_MESSAGE_COMPUTER_OFF,
            LANG_QUESTION_QUESTION_SWITCH_ON
        )
        if answer == True:
            switch_computer_on(params)
            redirect_to_beginning()
    else:
        xbmcgui.Dialog().ok(LANG_PARSEC, LANG_TITLE_MANAGE_COMPUTER_MESSAGE_PENDING)
        redirect_to_beginning()
    pass


def manage_computer(params):
    # Lists actions for computer
    global current_computer
    global parsec_session_id

    computer_json = params.get('computer')
    parsec_session_id = params.get('session_id')
    current_computer = json.loads(computer_json)
    numberselect = params.get('numberselect')
    user_json = params.get('user')

    target_state_action = get_target_state_action()
    target_state_title = get_target_title()
    computer_status_logo = get_computer_status_logo()

    plugintools.add_computer_list_item(
        action=target_state_action,
        title=target_state_title,
        session_id=parsec_session_id,
        computer=computer_json,
        user=user_json,
        numberselect=numberselect,
        thumbnail=computer_status_logo,
        fanart=DEFAULT_FANART,
        folder=False,
        context=False
    )

    plugintools.add_computer_list_item(
        action='connect_to_computer',
        title=LANG_TITLE_CONNECT_PARSEC,
        session_id=parsec_session_id,
        computer=computer_json,
        user=user_json,
        numberselect=numberselect,
        thumbnail=LOGO_SERVER_CONNECT,
        fanart=DEFAULT_FANART,
        folder=False,
        context=False
    )


def redirect_to_beginning():
    """
    redirects user to start of the app

    :return:
    """
    redirect_url = '%s?action=%s' % (sys.argv[0], '')

    xbmc.executebuiltin("Container.Update(%s)" % redirect_url)


def redirect_to_main_list(params):
    """
    Redirecting to main list with all available params

    :param params:
    :return:
    """

    global parsec_session_id

    redirect_url = '%s?action=%s&title=%s&session_id=%s&computer=%s&thumbnail=%s&fanart=%s&numberselect=%s' % (
        sys.argv[0],
        'main_list',
        urllib.quote_plus(params.get('title')),
        urllib.quote_plus(parsec_session_id),
        urllib.quote_plus(params.get('computer')),
        urllib.quote_plus(params.get('thumbnail')),
        urllib.quote_plus(params.get('fanart')),
        urllib.quote_plus(params.get('numberselect')),
    )

    xbmc.executebuiltin("Container.Update(%s)" % redirect_url)


def switch_computer_on(params):
    # trigger switching on the computer
    global current_computer
    global parsec_session_id
    computer_json = params.get('computer')
    parsec_session_id = params.get('session_id')
    current_computer = json.loads(computer_json)
    computer_id = current_computer['lease']
    switch_computer_state('on', computer_id)

    trigger_notification(LANG_TITLE_MANAGE_COMPUTER_MESSAGE_ON)
    redirect_to_main_list(params)
    pass


def switch_computer_off(params):
    # trigger switching off the computer
    global current_computer
    global parsec_session_id
    computer_json = params.get('computer')
    parsec_session_id = params.get('session_id')
    current_computer = json.loads(computer_json)
    computer_id = current_computer['lease']
    switch_computer_state('off', computer_id)

    trigger_notification(LANG_TITLE_MANAGE_COMPUTER_MESSAGE_OFF)
    redirect_to_main_list(params)
    pass


def switch_computer_pending(params):
    trigger_notification(LANG_TITLE_MANAGE_COMPUTER_MESSAGE_PENDING)
    pass


def get_computer_title():
    global current_computer
    # returns computer name
    computer_title = current_computer['name'] + " (" + current_computer['status'] + ")"

    return computer_title


def get_computer_status_logo():
    """
    Returns matching logo to current computer status

    :return:
    """

    global current_computer
    computer = current_computer

    if computer['status'] == 'off':
        status_logo = LOGO_SERVER_OFF
    elif computer['status'] == 'on':
        status_logo = LOGO_SERVER_ON
    else:
        status_logo = LOGO_SERVER_PENDING

    return status_logo


def get_target_state_action():
    """
    Returns action method string matching to target

    :return:
    """
    global current_computer
    computer = current_computer

    target_state_action = 'switch_computer'
    if computer['status'] == 'off':
        target_state_action += '_on'
    elif computer['status'] == 'on':
        target_state_action += '_off'
    else:
        target_state_action += '_pending'

    return target_state_action


def get_target_title():
    """
    Return target state label text matching to current
    computer status

    :return:
    """

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
    """
    Returns list of available computers and their metadata

    :return:
    """

    session_id = get_parsec_session_id()
    plugintools.log("Received parsec sessionid for getting list of computers:" + session_id)
    computers = get_parsec_request_result(session_id, API_LIST_COMPUTERS)

    return computers


def get_user_info():
    """
    Returns infos of logged in parsec user

    :return:
    """

    session_id = get_parsec_session_id()
    plugintools.log("Received parsec sessionid for fetching user:" + session_id)
    user = get_parsec_request_result(session_id, API_USER_INFO)
    return user


def get_parsec_request_result(session_id, url):
    """
    requesting parsec by providing session and url

    :param session_id:
    :param url:
    :return list:
    """

    values = {}
    header = {
        'User-Agent': user_agent,
        'x-parsec-session-id': session_id
    }

    response = requests.get(url, params=values, headers=header)
    result = response.json()

    return result


def get_parsec_session_id():
    """
    Central method for generating/offering parsec session id

    :return:
    """
    global parsec_session_id

    if parsec_session_id == False:
        parsec_user = plugintools.get_setting("parsec_user")
        parsec_passwd = plugintools.get_setting("parsec_passwd")

        values = {'email': parsec_user,
                  'password': parsec_passwd,
                  'expiration_type': 'short'}
        headers = {'User-Agent': user_agent}

        data = urllib.urlencode(values)
        req = urllib2.Request(API_AUTHURL, data, headers)
        response = urllib2.urlopen(req)

        data = json.load(response)
        parsec_session_id = data['session_id']

    plugintools.log("Received parsec sessionid:" + parsec_session_id)
    return parsec_session_id


def switch_computer_state(target_state, computer_id):
    """
    Switch state of given computer to target state (on/off)

    :param target_state:
    :param computer_id:
    :return:
    """

    if target_state == 'on':
        url = API_SWITCH_COMPUTER_ON
    else:
        url = API_SWITCH_COMPUTER_OFF

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
    background_target_state_create(target_state, computer_id)


def background_target_state_create(target_state, computer_id):
    """
    Creates background instance for placing a thread to check until
    target state has been reached

    :param target_state:
    :param computer_id:
    :return:
    """

    global background_repeats

    background_repeats = 0

    if target_state == 'on':
        LANG_ACTION = LANG_TITLE_MANAGE_COMPUTER_MESSAGE_ON
    else:
        LANG_ACTION = LANG_TITLE_MANAGE_COMPUTER_MESSAGE_OFF

    background_dialog = xbmcgui.DialogProgressBG()
    background_dialog.create(LANG_PARSEC, LANG_ACTION)
    background_dialog.update(50, LANG_PARSEC, LANG_ACTION)
    background_process = threading.Thread(target=background_target_state_update, args=(target_state, computer_id, background_dialog,))
    background_process.start()
    pass


def background_target_state_update(target_state, computer_id, background_dialog):
    """
    Polling given instance until target_stage has been reached

    :param target_state:
    :param computer_id:
    :param background_dialog:
    :return:
    """

    if target_state == 'on':
        LANG_ACTION_DONE = LANG_MESSAGE_COMPUTER_ON
    else:
        LANG_ACTION_DONE = LANG_MESSAGE_COMPUTER_OFF

    computers = get_computers()

    for computer in computers:
        task_done = background_target_reached(computer, target_state, computer_id)
        if task_done:
            background_dialog.update(100, LANG_PARSEC, LANG_ACTION_DONE)
            trigger_notification(LANG_ACTION_DONE)
            background_dialog.close()
            xbmc.executebuiltin('Container.Update')
            return

    time.sleep(10)
    background_target_state_update(target_state, computer_id, background_dialog)
    pass


def background_target_reached(computer, target_state, target_id):
    """
    checks if computer instance matches with target_state and target_id

    :param computer:
    :param target_state:
    :param target_id:
    :return:
    """

    if computer['status'] == target_state and computer['lease'] == target_id:
        return True
    if background_repeats >= MAX_BACKGROUND_REPEATS:
        trigger_notification(LANG_MESSAGE_BACKGROUND_TASK_BREAK)
        return True
    return False


def get_is_instance_running(computer):
    """
    Checks state of given computer is on

    :param computer:
    :return:
    """

    if computer['status'] == 'on':
        return True
    return False


def get_is_instance_off(computer):
    """
    Checks state of given computer is off
    :param computer:
    :return:
    """

    if computer['status'] == 'off':
        return True
    return False


def trigger_notification(message, time=5000):
    """
    Trigger notification with given message for given time in milliseconds

    :param message:
    :param time:
    :return:
    """

    __addonname__ = addon.getAddonInfo('name')
    __icon__ = addon.getAddonInfo('icon')

    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (__addonname__, message, time, __icon__))
    pass

# script starts from the end ;-)
run()
