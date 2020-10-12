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

#####

import base64
import sys
import os
import re
import logging

#####

program_name    = 'cb_thunderconvert'
author_mail     = 'camiel@bouchier.be'

this_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
log_dir  = f"{this_dir}/logs"

if not os.path.exists(log_dir) :
    os.makedirs(log_dir)

logger = logging.getLogger(__name__)

#####

id_cblink_hash = {}

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
            '%(asctime)s - %(process)5d - %(levelname)5s - %(lineno)4d : %(message)s')
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
            '%(asctime)s - %(process)5d - %(levelname)5s - %(lineno)4d : %(message)s')
    console_handler.setFormatter(console_formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

#####

if __name__ == '__main__' :

    install_logger()
    logger.info("="*5)
    logger.info(f"Starting {program_name}")

    if len(sys.argv) != 4 :
        logger.error(f"Usage : {sys.argv[0]} InputFile OutputFile Database")

    with open(sys.argv[3], "r", encoding='utf-8') as f_db :
        for line in f_db :
            (cblink, message_id) = line.split(';')
            message_id = message_id.strip('<>\n')
            if message_id not in id_cblink_hash :
                id_cblink_hash[message_id] = cblink
            elif id_cblink_hash[message_id] != cblink :
                new_link = base64.decodebytes(cblink.encode('ascii'))
                old_link = base64.decodebytes(id_cblink_hash[message_id].encode('ascii'))
                the_check = f"Check: {old_link} <> {new_link}"
                logger.debug(the_check)

    nr_replacements = 0

    with open(sys.argv[1], "r", encoding='utf-8') as f_in :
        with open(sys.argv[2], "w", encoding='utf-8') as f_out :
            for line in f_in :
                for the_match in re.finditer(r'\bthunderlink:\/\/([^\s\]]+)', line) :
                    msg_id = the_match.group(1).replace('messageid=', '')
                    try:
                        cblink = id_cblink_hash[msg_id]
                    except KeyError:
                        logger.info(f"Conversion error for {line}")
                        continue
                    line = line.replace(the_match.group(0), f"cbthunderlink://{cblink}")
                    nr_replacements += 1
                f_out.write(line)

    logger.info(f"Converted {nr_replacements} links")
    logger.info(f"Finishing {program_name}")
    logger.info("="*5)

#
# vim: syntax=python ts=4 sw=4 sts=4 sr et columns=100
#
