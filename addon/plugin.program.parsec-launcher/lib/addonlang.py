# -*- coding: utf-8 -*-
"""
Addon language strings
"""

import xbmcaddon


addon = xbmcaddon.Addon(id='plugin.program.parsec-launcher')


def translate_code(code):
    return addon.getLocalizedString(code).encode('utf-8')


# Language strings
LANG_CONNECT_PARSEC = translate_code(30020)
LANG_MANAGE_COMPUTERS = translate_code(30021)
LANG_MANAGE = translate_code(30022)
LANG_MANAGE_COMPUTER_SWITCH_ON = translate_code(30023)
LANG_MANAGE_COMPUTER_SWITCH_OFF = translate_code(30024)
LANG_MANAGE_COMPUTER_IS_PENDING = translate_code(30025)
LANG_PARSEC = translate_code(30026)
LANG_STATUS = translate_code(30027)
LANG_CREATED = translate_code(30028)
LANG_LAST_UPDATED = translate_code(30029)
LANG_PROVIDER = translate_code(30030)
LANG_MACHINE_TYPE = translate_code(30031)
LANG_REGION = translate_code(30032)
LANG_CREDIT = translate_code(30033)
LANG_PLAYTIME = translate_code(30034)
LANG_HOURS = translate_code(30035)
LANG_DOLLAR = translate_code(30036)
LANG_COMPUTER_INFO = translate_code(30037)
LANG_USER_INFO = translate_code(30038)
LANG_USERNAME = translate_code(30039)

LANG_MESSAGE_COMPUTER_PENDING = translate_code(30200)
LANG_MESSAGE_COMPUTER_SWITCHED_ON = translate_code(30201)
LANG_MESSAGE_COMPUTER_SWITCHED_OFF = translate_code(30202)
LANG_MESSAGE_LOCKED = translate_code(30203)
LANG_MESSAGE_LOCKED_UPDATE_WORK = translate_code(30204)
LANG_MESSAGE_MISSING_PACKAGES = translate_code(30205)
LANG_MESSAGE_INSTALL_MISSING = translate_code(30207)
LANG_MESSAGE_NO_CREDENTIALS = translate_code(30208)
LANG_MESSAGE_WRONG_CREDENTIALS = translate_code(30209)
LANG_MESSAGE_COMPUTER_OFF = translate_code(30210)
LANG_MESSAGE_COMPUTER_ON = translate_code(30211)
LANG_MESSAGE_BACKGROUND_TASK_BREAK = translate_code(30212)
LANG_MESSAGE_LOCKED = translate_code(30213)
LANG_MESSAGE_WRONG_PLATFORM = translate_code(30214)

LANG_QUESTION_TO_SETTINGS = translate_code(30500)
LANG_QUESTION_QUESTION_SWITCH_ON = translate_code(30501)
LANG_QUESTION_INSTALL_MISSING_PACKAGES = translate_code(30502)

