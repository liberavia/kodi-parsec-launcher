# -*- coding: utf-8 -*-
"""
Addonutils for parsec launcher. Based on  plugintools v. 1.0.8
"""

import xbmc
import xbmcplugin
import xbmcaddon
import xbmcgui
import addonlang
import parsec

import urllib
import urllib2
import re
import sys
import os
import time
import socket
from StringIO import StringIO
import gzip
import pprint
import base64
import json

module_log_enabled = False
http_debug_log_enabled = False

f = open(os.path.join(os.path.dirname(__file__), "..", "addon.xml"))
data = f.read()
f.close()

addon_id = find_single_match(data, 'id="([^"]+)"')
if addon_id == "":
    addon_id = find_single_match(data, "id='([^']+)'")

__settings__ = xbmcaddon.Addon(id=addon_id)
__language__ = __settings__.getLocalizedString


def log(message):
    """
    Write into kodi log

    :param message:
    :return:
    """

    xbmc.log(message)


def _log(message):
    """
    Write into kodi log with module prefix

    :param message:
    :return:
    """

    if module_log_enabled:
        #message = message.encode('utf-8')
        xbmc.log("plugintools."+message)


def clear_cache():
    """
    Clearing cache for making sure lists will be reloaded
    at this point

    :return:
    """

    path = xbmc.translatePath('special://temp')

    if os.path.exists(path):
        for f in os.listdir(path):
            fpath = os.path.join(path, f)
            try:
                if os.path.isfile(fpath):
                    if not fpath.lower().endswith('.log'):
                        os.unlink(fpath)
                elif os.path.isdir(fpath):
                    shutil.rmtree(fpath)
            except Exception as e:
                log(e)


def get_params():
    """
    Helper for fetching all params into a single list param

    :return:
    """

    _log("get_params")
    
    param_string = sys.argv[2]
    
    _log("get_params "+str(param_string))
    
    commands = {}

    if param_string:
        split_commands = param_string[param_string.find('?') + 1:].split('&')
    
        for command in split_commands:
            _log("get_params command="+str(command))
            if len(command) > 0:
                if "=" in command:
                    split_command = command.split('=')
                    key = split_command[0]
                    value = urllib.unquote_plus(split_command[1])
                    commands[key] = value
                else:
                    commands[command] = ""
    
    _log("get_params "+repr(commands))

    return commands


def add_computer_list_item(action="", title="", thumbnail="", fanart="", session_id="", numberselect="", computer=None, user=None, info_labels=None, folder=True, context=False):
    """
    Adds a list item of type computer (fake video entry)

    :param action:
    :param title:
    :param thumbnail:
    :param fanart:
    :param session_id:
    :param numberselect:
    :param computer:
    :param user:
    :param info_labels:
    :param folder:
    :param context:
    :return:
    """
    listitem = xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)

    if info_labels is None:
        info_labels = {"Title": title, "Plot": parsec.get_computer_info(computer, user)}

    listitem.setInfo("video", info_labels)

    if fanart != "":
        listitem.setProperty('fanart_image', fanart)
        xbmcplugin.setPluginFanart(int(sys.argv[1]), fanart)

    if context:
        context_entries = []

        for context_entry in context:
            context_label = context_entry.get('label')
            context_url = context_entry.get('url')
            runner = "XBMC.RunPlugin(" + str(context_url) + ", "")"
            context_entries.append((str(context_label), runner,))

        listitem.addContextMenuItems(context_entries)

    itemurl = '%s?action=%s&title=%s&session_id=%s&computer=%s&user=%s&thumbnail=%s&fanart=%s&numberselect=%s' % (
        sys.argv[0],
        action,
        urllib.quote_plus(title),
        urllib.quote_plus(session_id),
        urllib.quote_plus(computer),
        urllib.quote_plus(user),
        urllib.quote_plus(thumbnail),
        urllib.quote_plus(fanart),
        numberselect,
    )
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=itemurl, listitem=listitem, isFolder=folder)


def close_item_list():
    """
    Closing list of items

    :return:
    """

    _log("close_item_list")

    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)


def get_temp_path():
    _log("get_temp_path")

    dev = xbmc.translatePath( "special://temp/" )
    _log("get_temp_path ->'"+str(dev)+"'")

    return dev


def get_runtime_path():
    _log("get_runtime_path")

    dev = xbmc.translatePath( __settings__.getAddonInfo('Path') )
    _log("get_runtime_path ->'"+str(dev)+"'")

    return dev


def get_data_path():
    _log("get_data_path")

    dev = xbmc.translatePath( __settings__.getAddonInfo('Profile') )
    
    if not os.path.exists(dev):
        os.makedirs(dev)

    _log("get_data_path ->'"+str(dev)+"'")

    return dev


def get_setting(name):
    _log("get_setting name='"+name+"'")

    dev = __settings__.getSetting( name )

    _log("get_setting ->'"+str(dev)+"'")

    return dev


def set_setting(name,value):
    _log("set_setting name='"+name+"','"+value+"'")

    __settings__.setSetting( name,value )


def open_settings_dialog():
    _log("open_settings_dialog")

    __settings__.openSettings()


def get_localized_string(code):
    _log("get_localized_string code="+str(code))

    dev = __language__(code)

    try:
        dev = dev.encode("utf-8")
    except:
        pass

    _log("get_localized_string ->'"+dev+"'")

    return dev


def keyboard_input(default_text="", title="", hidden=False):
    _log("keyboard_input default_text='"+default_text+"'")

    keyboard = xbmc.Keyboard(default_text,title,hidden)
    keyboard.doModal()
    
    if (keyboard.isConfirmed()):
        tecleado = keyboard.getText()
    else:
        tecleado = ""

    _log("keyboard_input ->'"+tecleado+"'")

    return tecleado


def message(text1, text2="", text3=""):
    """
    Show infomessage for acknowledgement

    :param text1:
    :param text2:
    :param text3:
    :return:
    """

    _log("message text1='"+text1+"', text2='"+text2+"', text3='"+text3+"'")

    if text3=="":
        xbmcgui.Dialog().ok( text1 , text2 )
    elif text2=="":
        xbmcgui.Dialog().ok( "" , text1 )
    else:
        xbmcgui.Dialog().ok( text1 , text2 , text3 )


def message_yes_no(text1, text2="", text3=""):

    _log("message_yes_no text1='"+text1+"', text2='"+text2+"', text3='"+text3+"'")

    if text3=="":
        yes_pressed = xbmcgui.Dialog().yesno( text1 , text2 )
    elif text2=="":
        yes_pressed = xbmcgui.Dialog().yesno( "" , text1 )
    else:
        yes_pressed = xbmcgui.Dialog().yesno( text1 , text2 , text3 )

    return yes_pressed


def trigger_notification(message, time=5000):
    """
    Trigger notification with given message for given time in milliseconds

    :param message:
    :param time:
    :return:
    """
    addon = xbmcaddon.Addon(id='plugin.program.parsec-launcher')
    __addonname__ = addon.getAddonInfo('name')
    __icon__ = addon.getAddonInfo('icon')

    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (__addonname__, message, time, __icon__))
    pass


def selector(option_list,title="Select one"):
    _log("selector title='"+title+"', options="+repr(option_list))

    dia = xbmcgui.Dialog()
    selection = dia.select(title,option_list)

    return selection
