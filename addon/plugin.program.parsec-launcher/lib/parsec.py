# -*- coding: utf-8 -*-
"""
parsec related functions
"""

import json
import urllib
import urllib2
import requests
import xbmc
import xbmc
import xbmcgui
import xbmcaddon
import time
import threading
import addonlang
import addonutils


# Constants
MAX_BACKGROUND_REPEATS=30 # which is 5 min waiting
API_BASEURL = "https://parsecgaming.com/v1/"
API_AUTHURL = API_BASEURL + "auth"
API_LIST_COMPUTERS = API_BASEURL + "server-list?include_managed=true"
API_USER_INFO = API_BASEURL + "me"
API_SWITCH_COMPUTER_ON = API_BASEURL + "activate-lease"
API_SWITCH_COMPUTER_OFF = API_BASEURL + "deactivate-lease"
API_USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0'

# Globals
parsec_session_id = False
parsec_user = ""
parsec_passwd = ""
background_repeats = 0


def get_computer_info(computer_json, user_json):
    """
    Returns information about the computer as a formatted string

    :param computer_json:
    :param user_json:
    :return string:
    """

    computer = json.loads(computer_json)
    user = json.loads(user_json)

    credits_dollar = float(float(user['credits'])/100)
    credits_dollar = str(credits_dollar)
    credits_dollar = addonlang.LANG_TITLE_DOLLAR + credits_dollar
    play_time = str(user['play_time']/60/60) + " " + addonlang.LANG_TITLE_HOURS

    # building string
    computer_info = ""
    computer_info += addonlang.LANG_TITLE_USER_INFO
    computer_info += "\n"
    computer_info += addonlang.LANG_TITLE_USERNAME + ": " + user['name'] + "\n"
    computer_info += addonlang.LANG_TITLE_CREDIT + ": " + credits_dollar + "\n"
    computer_info += addonlang.LANG_TITLE_PLAYTIME + ": " + play_time + "\n"
    computer_info += addonlang.LANG_TITLE_COMPUTER_INFO
    computer_info += "\n"
    computer_info += addonlang.LANG_TITLE_STATUS + ": " + computer['status'] + "\n"
    computer_info += addonlang.LANG_TITLE_CREATED + ": " + computer['created_at'] + "\n"
    computer_info += addonlang.LANG_TITLE_LAST_UPDATED + ": " + computer['updated_at'] + "\n"
    computer_info += addonlang.LANG_TITLE_PROVIDER + ": " + computer['managed']['provider_name'] + "\n"
    computer_info += addonlang.LANG_TITLE_MACHINE_TYPE + ": " + computer['managed']['machine_type'] + "\n"
    computer_info += addonlang.LANG_TITLE_REGION + ": " + computer['managed']['region'] + "\n"

    return computer_info


def get_computers():
    """
    Returns list of available computers and their metadata

    :return json:
    """

    session_id = get_parsec_session_id()
    addonutils.log("Received parsec sessionid for getting list of computers:" + session_id)
    computers = get_parsec_request_result(session_id, API_LIST_COMPUTERS)

    return computers


def get_user_info():
    """
    Returns infos of logged in parsec user

    :return json:
    """

    session_id = get_parsec_session_id()
    addonutils.log("Received parsec sessionid for fetching user:" + session_id)
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
        'User-Agent': API_USER_AGENT,
        'x-parsec-session-id': session_id
    }

    response = requests.get(url, params=values, headers=header)
    result = response.json()

    return result


def get_parsec_session_id():
    """
    Central method for generating/offering parsec session id

    :return string:
    """
    global parsec_session_id

    if parsec_session_id == False:
        parsec_user = addonutils.get_setting("parsec_user")
        parsec_passwd = addonutils.get_setting("parsec_passwd")

        values = {'email': parsec_user,
                  'password': parsec_passwd,
                  'expiration_type': 'short'}
        headers = {'User-Agent': API_USER_AGENT}

        data = urllib.urlencode(values)
        req = urllib2.Request(API_AUTHURL, data, headers)
        response = urllib2.urlopen(req)

        data = json.load(response)
        parsec_session_id = data['session_id']

    addonutils.log("Received parsec sessionid:" + parsec_session_id)

    return parsec_session_id


def switch_computer_state(target_state, computer_id):
    """
    Switch state of given computer to target state (on/off)

    :param target_state:
    :param computer_id:
    :return void:
    """

    if target_state == 'on':
        url = API_SWITCH_COMPUTER_ON
    else:
        url = API_SWITCH_COMPUTER_OFF

    values = {
        'id': computer_id
    }
    headers = {
        'User-Agent': API_USER_AGENT,
        'x-parsec-session-id': parsec_session_id
    }

    data = urllib.urlencode(values)

    req = urllib2.Request(url, data, headers)
    urllib2.urlopen(req)
    background_target_state_create(target_state, computer_id)

    pass


def background_target_state_create(target_state, computer_id):
    """
    Creates background instance for placing a thread to check until
    target state has been reached

    :param target_state:
    :param computer_id:
    :return void:
    """

    global background_repeats

    background_repeats = 0

    if target_state == 'on':
        LANG_ACTION = addonlang.LANG_TITLE_MANAGE_COMPUTER_MESSAGE_ON
    else:
        LANG_ACTION = addonlang.LANG_TITLE_MANAGE_COMPUTER_MESSAGE_OFF

    background_dialog = xbmcgui.DialogProgressBG()
    background_dialog.create(addonlang.LANG_PARSEC, LANG_ACTION)
    background_dialog.update(50, addonlang.LANG_PARSEC, LANG_ACTION)
    background_process = threading.Thread(target=background_target_state_update, args=(target_state, computer_id, background_dialog,))
    background_process.start()

    pass


def background_target_state_update(target_state, computer_id, background_dialog):
    """
    Polling given instance until target_stage has been reached

    :param target_state:
    :param computer_id:
    :param background_dialog:
    :return void:
    """

    if target_state == 'on':
        LANG_ACTION_DONE = addonlang.LANG_MESSAGE_COMPUTER_ON
    else:
        LANG_ACTION_DONE = addonlang.LANG_MESSAGE_COMPUTER_OFF

    computers = get_computers()

    for computer in computers:
        task_done = background_target_reached(computer, target_state, computer_id)
        if task_done:
            background_dialog.update(100, addonlang.LANG_PARSEC, LANG_ACTION_DONE)
            addonutils.trigger_notification(LANG_ACTION_DONE)
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
    :return bool:
    """

    if computer['status'] == target_state and computer['lease'] == target_id:
        return True
    if background_repeats >= MAX_BACKGROUND_REPEATS:
        addonutils.trigger_notification(
            addonlang.LANG_MESSAGE_BACKGROUND_TASK_BREAK
        )
        return True
    return False


def get_is_instance_running(computer):
    """
    Checks state of given computer is on

    :param computer:
    :return bool:
    """

    if computer['status'] == 'on':
        return True
    return False


def get_is_instance_off(computer):
    """
    Checks state of given computer is off
    :param computer:
    :return bool:
    """

    if computer['status'] == 'off':
        return True
    return False
