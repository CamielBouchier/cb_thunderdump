# -*- coding: utf-8 -*-

#
#
# $BeginLicense$
#
# (C) 2020 by Camiel Bouchier (camiel@bouchier.be)
#
# This file is part of cb_thunderdump.
# All rights reserved.
#
# $EndLicense$
#
#

#
# ATTENTION for 2 important remarks :
#    1. Do NOT use 'print', console loggers or anything else that writes to stdout.
#       It will jeopardize the communication to cb_background.js!
#    2. Note that running python with the `-u` flag is required on Windows,
#       Forces stdin, stdout and stderr to be totally unbuffered and in binary mode.
#

#####

import json
import sys
import struct
import os
import logging

if sys.platform == "win32" :
    import winreg
    import ctypes

#####

program_name    = 'cb_thunderdump'
author_mail     = 'camiel@bouchier.be'
db_name         = "database.txt"

this_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
log_dir  = f"{this_dir}/logs"

if not os.path.exists(log_dir) :
    os.makedirs(log_dir)

logger = logging.getLogger(__name__)

#####

def get_log_filename() :

    log_filename = os.path.join(log_dir, "%s.log" % (program_name))
    return log_filename

#####

def install_logger() :

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(get_log_filename(), mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
            '%(asctime)s - %(process)5d - %(levelname)s - %(lineno)4d : %(message)s')
    file_handler.setFormatter(file_formatter)

    root_logger.addHandler(file_handler)

#####

if __name__ == '__main__' :

    install_logger()
    logger.info("="*100)
    logger.info(f"Starting {program_name} ({sys.argv})")

    if len(sys.argv) > 1 and sys.argv[1] in ["register", "unregister"] :

        # Registering (currently windows specific only)
        # (in this branch it is OK to use stdout => interactive)

        if sys.platform == "win32" :

            if not ctypes.windll.shell32.IsUserAnAdmin() :
                print("This must be run as administrator. You are just a mortal.")
                sys.exit()

            # We are setting up ourselves in the registry.
            print("Changing the registry")

            # This are the keys for the native messaging registration.
            key = r'SOFTWARE\Mozilla\NativeMessagingHosts\cb_thunderdump'
            
            for K in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE] :

                if sys.argv[1] in ["register"] :
                    try :
                        reg_key = winreg.OpenKey(K, key, 0, winreg.KEY_ALL_ACCESS)
                    except FileNotFoundError :
                        reg_key = winreg.CreateKey(K, key)
                    val = os.path.join(this_dir, "cb_thunderdump.json")
                    winreg.SetValueEx(reg_key, None, 0, winreg.REG_SZ, val)
                    winreg.CloseKey(reg_key)

                if sys.argv[1] in ["unregister"] :
                    try :
                        reg_key = winreg.OpenKey(K, key, 0, winreg.KEY_ALL_ACCESS)
                        winreg.DeleteKey(reg_key, "")
                        winreg.CloseKey(reg_key)
                    except FileNotFoundError :
                        pass

            print("Registry change finished")

    else :

        # We are the instance interfacing with background.js
        # Await the list of links and drop it to a file database.

        logger.info("Interfacing with background.js")

        while True :

            raw_length = sys.stdin.buffer.read(4)
            if not raw_length:
                sys.exit(0)
            message_length = struct.unpack('=I', raw_length)[0]
            message = sys.stdin.buffer.read(message_length).decode("utf-8")
            link_list = json.loads(message)['link_list']

            # Write the file database
            fn = os.path.join(this_dir, db_name)
            with open(fn, "w" , encoding='utf-8') as f : 
                for link in link_list :
                    print(link, file=f)

            # Confirm back.
            encoded_content = json.dumps({
                'cb_confirm' : len(link_list),
                'db_name'    : fn}).encode("utf-8")
            encoded_length = struct.pack('=I', len(encoded_content))
            sys.stdout.buffer.write(encoded_length)
            sys.stdout.buffer.write(struct.pack(str(len(encoded_content))+"s", encoded_content))
            sys.stdout.buffer.flush()

    logger.info("Finishing {}".format(program_name))
    logger.info("="*100)

#
# vim: syntax=python ts=4 sw=4 sts=4 sr et columns=100
#
