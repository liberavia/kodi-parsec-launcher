"""
    Addon for managing and connecting to parsec instances
"""

# -*- coding: UTF-8 -*-
# main imports
import sys
import os
import stat
import shutil
import urllib
import urllib2
import requests
import json
import pprint
import xbmc
import xbmcgui
import xbmcaddon
from lib import addonutils
from lib import addonlang
from lib import parsec

# plugin constants
__plugin__ = "Parsec"
__author__ = "liberavia"
__url__ = "https://github.com/liberavia/kodi-parsec"
__git_url__ = "https://github.com/liberavia/kodi-parsec"
__version__ = "0.1.0"

ADDON_BASE_PATH = os.path.dirname(__file__)
ADDON_BIN_PATH = os.path.join(ADDON_BASE_PATH, 'bin')
THUMBNAIL_PATH = os.path.join(addonutils.get_runtime_path(), "resources", "img")
DEFAULT_FANART = os.path.join(addonutils.get_runtime_path(), "fanart.jpg")
DEFAULT_LOGO = os.path.join(THUMBNAIL_PATH, "parsec-logo.png")
LOGO_SERVER_ON = DEFAULT_LOGO
LOGO_SERVER_OFF = DEFAULT_LOGO
LOGO_SERVER_PENDING = DEFAULT_LOGO
LOGO_SERVER_CONNECT = DEFAULT_LOGO

# Globals
addon = xbmcaddon.Addon(id='plugin.program.parsec-launcher')
current_computer = False


def run():
    """
    Entry point of addon

    :return:
    """
    addonutils.log("kodi-parsec.run")

    # Get params
    params = addonutils.get_params()

    if params.get("action") is None:
        main_list(params)
    else:
        action = params.get("action")
        exec action+"(params)"

    addonutils.close_item_list()


def check_install():
    """
    perform install checks

    :return:
    """

    check_bin_executable()


def check_bin_executable():
    """
    Make sure scripts are executable

    :return:
    """

    for binfile in os.listdir(ADDON_BIN_PATH):
        if os.path.isfile(binfile):
            os.chmod(binfile, st.st_mode | stat.S_IEXEC)


def main_list(params):
    """
    Main menu
    List of available computers

    :param params:
    :return:
    """

    addonutils.clear_cache()

    user_credentials_available()
    check_credentials()

    computers = parsec.get_computers()
    user = parsec.get_user_info()

    for index, computer in enumerate(computers):
        current_computer = computer
        numberselect = int(index + 1)
        computer_title = get_computer_title()
        context = get_computer_context_menu(computer, numberselect)
        addonutils.log("parsec computer title is " + computer_title)
        computer_status_logo = get_computer_status_logo()
        user_json = json.dumps(user)
        addonutils.log("user json is : " + user_json)

        addonutils.add_computer_list_item(
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

    parsec_user = addonutils.get_setting("parsec_user")
    parsec_passwd = addonutils.get_setting("parsec_passwd")
    addonutils.log("parsec checking existance of credentials")
    if parsec_user != "" and parsec_passwd != "":
        return True
    else:
        answer = xbmcgui.Dialog().yesno(
            addonlang.LANG_PARSEC,
            addonlang.LANG_MESSAGE_NO_CREDENTIALS,
            addonlang.LANG_QUESTION_TO_SETTINGS
        )
        if answer == True:
            addonutils.open_settings_dialog()
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
            addonlang.LANG_PARSEC,
            addonlang.LANG_MESSAGE_WRONG_CREDENTIALS,
            addonlang.LANG_QUESTION_TO_SETTINGS
        )
        if answer == True:
            addonutils.open_settings_dialog()
            redirect_to_beginning()


def get_computer_context_menu(computer, numberselect):
    """
    returns a list of context entries per computer

    :param computer:
    :param numberselect:
    :return:
    """

    session_id = parsec.get_parsec_session_id()

    switch_computer_action = get_target_state_action()
    context_label_switch_computer = get_target_title()
    context_url_switch_computer = '%s?action=%s&title=%s&session_id=%s&computer=%s&thumbnail=%s&fanart=%s&numberselect=%s' % (
        sys.argv[0],
        switch_computer_action,
        urllib.quote_plus(context_label_switch_computer),
        urllib.quote_plus(session_id),
        urllib.quote_plus(json.dumps(computer)),
        urllib.quote_plus(DEFAULT_LOGO),
        urllib.quote_plus(DEFAULT_FANART),
        numberselect,
    )

    connect_action ='connect_to_computer'
    context_label_connect_computer = addonlang.LANG_TITLE_CONNECT_PARSEC
    context_url_connect_computer = '%s?action=%s&title=%s&session_id=%s&computer=%s&thumbnail=%s&fanart=%s&numberselect=%s' % (
        sys.argv[0],
        connect_action,
        urllib.quote_plus(context_label_connect_computer),
        urllib.quote_plus(session_id),
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

    parsec_user = addonutils.get_setting("parsec_user")
    parsec_passwd = addonutils.get_setting("parsec_passwd")

    computer_json = params.get('computer')
    current_computer = json.loads(computer_json)
    numberselect = params.get('numberselect')

    instance_running = get_is_instance_running(current_computer)
    instance_off = get_is_instance_off(current_computer)

    start_command = ADDON_BIN_PATH + "/xstart.sh "

    connect_params = []
    connect_params.append(parsec_user)
    connect_params.append(parsec_passwd)
    connect_params.append(numberselect)
    connect_params.append(ADDON_BIN_PATH)

    if instance_running:
        full_command = start_command + ' ' + ' '.join(connect_params)
        os.popen(full_command)
    elif instance_off:
        answer = xbmcgui.Dialog().yesno(
            addonlang.LANG_PARSEC,
            addonlang.LANG_MESSAGE_COMPUTER_OFF,
            addonlang.LANG_QUESTION_QUESTION_SWITCH_ON
        )
        if answer == True:
            switch_computer_on(params)
            redirect_to_beginning()
    else:
        xbmcgui.Dialog().ok(
            addonlang.LANG_PARSEC,
            addonlang.LANG_TITLE_MANAGE_COMPUTER_MESSAGE_PENDING
        )
        redirect_to_beginning()
    pass


def manage_computer(params):
    """
    Lists actions for computer

    :param params:
    :return:
    """

    computer_json = params.get('computer')
    parsec_session_id = params.get('session_id')
    numberselect = params.get('numberselect')
    user_json = params.get('user')

    target_state_action = get_target_state_action()
    target_state_title = get_target_title()
    computer_status_logo = get_computer_status_logo()

    addonutils.add_computer_list_item(
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

    addonutils.add_computer_list_item(
        action='connect_to_computer',
        title=addonlang.LANG_TITLE_CONNECT_PARSEC,
        session_id=parsec_session_id,
        computer=computer_json,
        user=user_json,
        numberselect=numberselect,
        thumbnail=LOGO_SERVER_CONNECT,
        fanart=DEFAULT_FANART,
        folder=False,
        context=False
    )

    pass


def redirect_to_beginning():
    """
    redirects user to start of the app

    :return:
    """

    redirect_url = '%s?action=%s' % (sys.argv[0], '')

    xbmc.executebuiltin("Container.Update(%s)" % redirect_url)

    pass


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

    pass


def switch_computer_on(params):
    """
    trigger switching on the computer

    :param params:
    :return:
    """

    global current_computer
    global parsec_session_id
    computer_json = params.get('computer')
    parsec_session_id = params.get('session_id')
    current_computer = json.loads(computer_json)
    computer_id = current_computer['lease']
    switch_computer_state('on', computer_id)

    addonutils.trigger_notification(
        addonlang.LANG_TITLE_MANAGE_COMPUTER_MESSAGE_ON
    )
    redirect_to_main_list(params)

    pass


def switch_computer_off(params):
    """
    trigger switching off the computer

    :param params:
    :return:
    """

    global current_computer
    global parsec_session_id
    computer_json = params.get('computer')
    parsec_session_id = params.get('session_id')
    current_computer = json.loads(computer_json)
    computer_id = current_computer['lease']
    switch_computer_state('off', computer_id)

    addonutils.trigger_notification(
        addonlang.LANG_TITLE_MANAGE_COMPUTER_MESSAGE_OFF
    )
    redirect_to_main_list(params)

    pass


def switch_computer_pending(params):
    """
    trigger switching notify user that machines current state
    is pending

    :param params:
    :return:
    """

    addonutils.trigger_notification(
        addonlang.LANG_TITLE_MANAGE_COMPUTER_MESSAGE_PENDING
    )

    pass


def get_computer_title():
    """
    Returns title of current computer

    :return:
    """

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

    if current_computer['status'] == 'off':
        status_logo = LOGO_SERVER_OFF
    elif current_computer['status'] == 'on':
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

    target_state_action = 'switch_computer'
    if current_computer['status'] == 'off':
        target_state_action += '_on'
    elif current_computer['status'] == 'on':
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

    if current_computer['status'] == 'off':
        target_title = addonlang.LANG_TITLE_MANAGE_COMPUTER_SWITCH_ON
    elif current_computer['status'] == 'on':
        target_title = addonlang.LANG_TITLE_MANAGE_COMPUTER_SWITCH_OFF
    else:
        target_title = addonlang.LANG_TITLE_MANAGE_COMPUTER_IS_PENDING

    return target_title


# script starts from the end ;-)
run()
