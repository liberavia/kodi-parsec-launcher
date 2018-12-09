import os
import sys
import stat
import time
import threading
import platform
import xbmc
import xbmcgui
import xbmcaddon
from lib import addonlang
from lib import addonutils

addon = xbmcaddon.Addon(id='plugin.program.parsec-launcher')
installed_packages = False

ADDON_BASE_PATH = xbmc.translatePath(addon.getAddonInfo('Path'))
ADDON_BIN_PATH = os.path.join(ADDON_BASE_PATH, 'bin')
ADDON_LOCK_FILE = '/tmp/kodi_parsec_launcher.lock'
ADDON_INSTALLED_TMP_FILE = '/tmp/installed_packages'

MANDATORY_PACKAGES = (
    'parsec',
    'lxde-core',
    'xserver-xorg',
    'xinit',
    'fbi',
    'libinput-dev',
    'openbox',
    'expect',
    'python-pip'
)

PIP_PACKAGES = (
    'evdev',
    'setuptools'
)


def complete_install_check():
    """
    perform install checks

    :return:
    """

    set_bin_executable()
    packages_installed = all_packages_installed()

    if packages_installed:
        return

    answer = xbmcgui.Dialog().yesno(
        addonlang.LANG_PARSEC,
        addonlang.LANG_MESSAGE_MISSING_PACKAGES,
        addonlang.LANG_QUESTION_INSTALL_MISSING_PACKAGES
    )
    if answer:
        start_background_update()
        addonutils.redirect_to_kodi_main()


def start_background_update():
    """
    Starts background action of installing missing packages

    :return:
    """

    background_dialog = xbmcgui.DialogProgressBG()
    background_dialog.create(addonlang.LANG_PARSEC, addonlang.LANG_MESSAGE_INSTALL_MISSING)
    background_dialog.update(5, addonlang.LANG_PARSEC, addonlang.LANG_MESSAGE_INSTALL_MISSING)
    background_process = threading.Thread(
        target=install_missing_packages,
        args=(background_dialog, 5)
    )
    background_process.start()

    pass


def all_packages_installed():
    """
    Checks if there are missing packages
    :return:
    """

    missing_packages = get_missing_packages()

    if len(missing_packages) == 0:
        return True
    return False


def set_bin_executable():
    """
    Make sure scripts are executable

    :return:
    """

    for binfile in os.listdir(ADDON_BIN_PATH):
        if os.path.isfile(binfile):
            os.chmod(binfile, st.st_mode | stat.S_IEXEC)


def install_missing_packages(background_dialog, current_progress):
    """
    Determines and installs all missing packages and limit
    progress notification to set maximum

    :return:
    """
    # addonutils.lock_addon(True)

    progress_max = 90

    remaining_progress = progress_max - current_progress

    missing_packages = get_missing_packages()
    addonutils.log('Parsec: Missing packages: ' + ', '.join(missing_packages))
    progress_step = float(remaining_progress / len(missing_packages))
    addonutils.log('Parsec: Progress step: ' + str(progress_step))

    for missing_package in missing_packages:
        current_progress = get_next_progress(
            current_progress,
            progress_step,
            progress_max
        )
        addonutils.log('Parsec: Current progress: ' + str(current_progress))

        install_package_message = str(addonlang.LANG_INSTALL) + " " + str(missing_package)
        addonutils.log('Parsec: Display install message: ' + install_package_message)

        background_dialog.update(
            int(current_progress),
            addonlang.LANG_PARSEC,
            install_package_message
        )
        install_package(missing_package)

    background_dialog.close()
    os.remove(ADDON_INSTALLED_TMP_FILE)
    # addonutils.lock_addon(False)
    pass


def get_next_progress(progress_current, progress_step, progress_max):
    """
    calculates next progress step and make sure it will be
    less than 100

    :param progress_current:
    :param float progress_step:
    :return int:
    """

    next_progress = progress_current + round(progress_step)
    if next_progress >= progress_max:
        next_progress = progress_max

    return next_progress


def install_package(package_name):
    """
    Installs given package on the system

    :param package_name:
    :return:
    """

    if package_name == 'parsec':
        install_parsec()
        return

    command_options = ' -q -y '
    command = 'sudo DEBIAN_FRONTEND=noninteractive apt-get install' + command_options
    install_command = command + package_name

    addonutils.log('Parsec performing install command: ' + install_command)
    os.system(install_command)


def install_parsec():
    """
    Downloads and installs parsec

    :return:
    """

    download_command = 'wget -q https://s3.amazonaws.com/parsec-build/package/parsec-rpi.deb -P /tmp/ 2>&1'
    addonutils.log('Parsec: Downloading parsec with: ' + download_command)
    os.system(download_command)
    install_command = 'sudo dpkg -i /tmp/parsec-rpi.deb'
    addonutils.log('Parsec: Installing parsec with: ' + install_command)
    os.system(install_command)


def get_missing_packages():
    """
    Returns list of packages that are mandatory but currently
    not installed

    :return list:
    """

    installed = get_installed_packages()
    missing = []

    for needed in MANDATORY_PACKAGES:
        if needed not in installed:
            missing.append(needed)

    return missing


def get_installed_packages():
    """
    Delivers installed packages as list

    :return list:
    """

    global installed_packages

    if not installed_packages:
        installed_packages = []
        if not os.path.isfile(ADDON_INSTALLED_TMP_FILE):
            os.popen('apt list --installed > ' + ADDON_INSTALLED_TMP_FILE, 'r', 1)

        with open(ADDON_INSTALLED_TMP_FILE) as f:
            for line in f:
                line_parts = line.split('/')
                package_name = line_parts[0]
                if package_name != '':
                    installed_packages.append(package_name)

    return installed_packages

