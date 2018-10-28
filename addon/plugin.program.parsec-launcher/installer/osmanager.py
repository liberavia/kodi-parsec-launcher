# -*- coding: utf-8 -*-
"""
os manager
"""
import os
import stat
import shutil
import platform
import xbmc
import xbmcgui
import xbmcaddon
import osmc_installer

addon = xbmcaddon.Addon(id='plugin.program.parsec-launcher')

ADDON_BASE_PATH = xbmc.translatePath(addon.getAddonInfo('Path'))
ADDON_BIN_PATH = os.path.join(ADDON_BASE_PATH, 'bin')


def get_os_installer():
    """
    Checks if plugin runs on right os and release.
    Currently just makes sure this runs on osmc on a raspberry pi

    ;todo when supporting more platforms this has to be more than true/false
    :return bool:
    """

    # is linux
    os_type = platform.system()
    if os_type.lower() != 'linux':
        return False

    # is raspi 3
    machine = platform.machine()
    if machine != 'armv7l':
        return False

    # is osmc
    try:
        platform_info = platform.uname()
        distro_name = platform_info[1]
        if distro_name.lower() != 'osmc':
            return False
    except:
        return False

    return osmc_installer



