# -*- coding: utf-8 -*-
"""
========================================
Download daily zip files from INPI's FTP
========================================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""

from os.path import dirname, join, basename, abspath, pardir, getsize
import os
from glob import glob
import subprocess
from argparse import ArgumentParser
from io import BytesIO
import sys
from json import load
from ftplib import FTP_TLS
import shutil
import urllib
import wget
from py7zr import SevenZipFile
from logging import info, error

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from accountability_metadata import AccountabilityMetadata
from bundle_ORM import Bundle


################################################################################
# READ CONFIGURATION
with open(join(dirname(__file__), "../", "configuration.json")) as json_configuration_file:
    CONFIG = load(json_configuration_file)

def bdd_connexion():
    return create_engine("mysql+pymysql://" + CONFIG["mySQL"]["enthic"]["user"] + ":" + CONFIG["mySQL"]["enthic"]["password"] + "@" + CONFIG["mySQL"]["enthic"]["host"] + "/enthic")

ENGINE = bdd_connexion()
SESSION = Session(ENGINE)

def get_existing_metadata():
    info("Getting all existing metadata")
    results = ENGINE.execute("SELECT * FROM `accountability_metadata`").fetchall()
    info("Got " + str(len(results)) + " metadata")
    return results

def get_metadata(siren):
    select_request = select(AccountabilityMetadata).where(AccountabilityMetadata.siren == siren)
    results = ENGINE.execute(select_request).fetchall()
    return results

def save_company_to_database(siren, denomination, ape, postal_code, town):
    sql_insert_query = """INSERT INTO `identity`(`siren`, `denomination`, `ape`, `postal_code`, `town`)
                          VALUES (%(siren)s, %(denomination)s, %(ape)s, %(postal_code)s, %(town)s)"""
    sql_args = {
        "siren" : siren,
        "denomination" : denomination,
        "ape" : ape,
        "postal_code" : postal_code,
        "town" : town
    }
    ENGINE.execute(sql_insert_query, sql_args)


def save_metadata_ORM(metadata_object):
    SESSION.add(metadata_object)
    SESSION.flush()

def save_metadata_to_database(siren, declaration, duree_exercice, code_motif, code_confidentialite, info_traitement, date_cloture_exercice):
    sql_insert_query = """INSERT INTO `accountability_metadata` (`siren`, `declaration`, `duree_exercice`, `date_cloture_exercice`, `code_motif`, `code_confidentialite`, `info_traitement`)
        VALUES (%(siren)s, %(declaration)s, %(duree_exercice)s, %(date_cloture_exercice)s, %(code_motif)s, %(code_confidentialite)s, %(info_traitement)s)"""

    sql_args = {
        "siren" : siren,
        "declaration": declaration,
        "duree_exercice": duree_exercice,
        "code_motif" : code_motif,
        "code_confidentialite" : code_confidentialite,
        "info_traitement" : info_traitement,
        "date_cloture_exercice" : date_cloture_exercice
    }
    SESSION.execute(sql_insert_query, sql_args)

def save_bundle_to_database(siren, declaration, accountability, bundle, amount):
    new_bundle = Bundle(siren=siren, declaration=declaration, accountability=accountability, bundle=bundle, amount=amount)
    SESSION.add(new_bundle)
    SESSION.flush()

def sum_bundle_into_database(siren, declaration, accountability, bundle, amount):
    existing_bundle = SESSION.execute(select(Bundle).where(Bundle.siren == siren, Bundle.declaration == declaration, Bundle.accountability == accountability, Bundle.bundle == bundle)).fetchall()
    try:
        if len(existing_bundle) == 1:
            existing_bundle[0][0].amount += float(amount)
            SESSION.flush()
        elif len(existing_bundle) == 0:
            save_bundle_to_database(siren, declaration, accountability, bundle, amount)
        else :
            print("plusieurs bundles identiques?", existing_bundle)
            exit()
    except AttributeError as e:
        print(existing_bundle)
        print(existing_bundle[0])
        print(existing_bundle[0][0])
        raise e


def replace_bundle_into_database(siren, declaration, accountability, bundle, amount, add_detail_mode):
    existing_bundle = SESSION.execute(select(Bundle).where(Bundle.siren == siren, Bundle.declaration == declaration, Bundle.accountability == accountability, Bundle.bundle == bundle)).fetchall()
    if len(existing_bundle) == 1:
        if add_detail_mode and abs(existing_bundle[0][0].amount - float(amount)) > 10:
            print("Différences entre bundles alors que ça devrait être pareil", existing_bundle[0][0].amount, amount)
        existing_bundle[0][0].amount = float(amount)
        SESSION.flush()
    elif len(existing_bundle) == 0:
        save_bundle_to_database(siren, declaration, accountability, bundle, amount)
    else :
        print("plusieurs bundles identiques?", existing_bundle)
        exit()

def replace_metadata_ORM(metadata, metadata_to_replace):
    existing_metadata_list = SESSION.execute(select(AccountabilityMetadata).where(AccountabilityMetadata.siren == metadata.siren, AccountabilityMetadata.declaration == metadata.declaration, AccountabilityMetadata.accountability == metadata.accountability, AccountabilityMetadata.date_cloture_exercice == metadata_to_replace[3])).fetchall()
    metadata_to_replace = None
    if len(existing_metadata_list) == 1:
        metadata_to_replace = existing_metadata_list[0][0]
    elif len(existing_metadata_list) == 0:
        print("Aucun metadata ne correspond à ", metadata)
        exit()
    else :
        for existing_metadata in existing_metadata_list:
            SESSION.delete(existing_metadata[0])
        metadata_to_replace = existing_metadata[0]

    metadata_to_replace.code_motif = metadata.code_motif
    metadata_to_replace.code_confidentialite = metadata.code_confidentialite
    metadata_to_replace.info_traitement = metadata.info_traitement
    metadata_to_replace.date_cloture_exercice = metadata.date_cloture_exercice
    metadata_to_replace.duree_exercice = metadata.duree_exercice
    SESSION.flush()
