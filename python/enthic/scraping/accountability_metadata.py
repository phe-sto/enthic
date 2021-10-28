# -*- coding: utf-8 -*-
"""
========================================
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
import datetime
from enum import Enum, auto


from sqlalchemy import create_engine, Column, Integer, String, Date

from sqlalchemy.orm import declarative_base
Base = declarative_base()

ERROR_CODE_MOTIF = ['02', '03', "04", '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']


class MetadataCase(Enum):
    """Enum used to replace or insert data in CSV"""
    COMPLEMENTARY = auto()
    IGNORE = auto()
    REPLACE = auto()
    HAS_MORE_DETAIL = auto()
    OVERWRITE = auto()
    IS_NEW = auto()

class AccountabilityMetadata(Base):

    __tablename__ = 'accountability_metadata'

    siren = Column(type_=Integer, nullable=False, primary_key=True)
    declaration = Column(type_=Integer, nullable=False, primary_key=True)
    duree_exercice = Column(type_=Integer, nullable=False)
    date_cloture_exercice = Column(type_=Date, nullable=False, primary_key=True)
    code_motif = Column(type_=String(5), nullable=False)
    code_confidentialite = Column(type_=Integer, nullable=False)
    info_traitement = Column(type_=String(10), nullable=True)
    accountability = Column(type_=String(1), nullable=False, primary_key=True)

    def __repr__(self):
        return str("({}, {}, {}, {}, {}, {}, {}, {})").format(self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice, self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability)

    def compare(self, metadata_from_bdd):
        if self.siren != metadata_from_bdd[0]:
            return MetadataCase.IS_NEW
        if self.declaration != metadata_from_bdd[1]:
            return MetadataCase.IS_NEW
        if self.accountability != metadata_from_bdd[7]:
            return MetadataCase.IS_NEW
        if self.accountability in ['B']:
            print("le nouveau bilan", self, "est un bilan de type de comptabilité qu'on s'en fout pour l'instant")
            return MetadataCase.IGNORE

        # À ce stade, on sait que les 2 bilans concerne la même année.
        better_code_motif = self.has_less_error(metadata_from_bdd)
        less_confidential = self.has_less_confidentiality(metadata_from_bdd)
        if self.date_cloture_exercice != metadata_from_bdd[3]:
            # Si le nouveau bilan fini à la date de début du bilan en base, il faut les fusionner
            date_debut_bdd = metadata_from_bdd[3] - datetime.timedelta(days=31*metadata_from_bdd[2])
            if date_debut_bdd.month == self.date_cloture_exercice.month and date_debut_bdd.year == self.date_cloture_exercice.year:
                print("New metadata", self, "prolonge, vers le passé, le metadata déjà en base", metadata_from_bdd, "pour un changement de date d'année fiscale")
                return MetadataCase.COMPLEMENTARY
            # Si le nouveau bilan commence à la date de fin du bilan en base, il faut les fusionner
            date_debut_nouveau = (self.date_cloture_exercice - datetime.timedelta(days=31*self.duree_exercice))
            if date_debut_nouveau.month == metadata_from_bdd[3].month and date_debut_nouveau.year == metadata_from_bdd[3].year:
                print("New metadata", self, "prolonge le metadata déjà en base", metadata_from_bdd, "après un changement de date d'année fiscale, ou un début d'activité")
                return MetadataCase.COMPLEMENTARY

            # Si les périodes se chevauchent, on garde le meilleur
            if (self.date_cloture_exercice > date_debut_bdd and self.date_cloture_exercice < metadata_from_bdd[3]) or (metadata_from_bdd[3] > date_debut_nouveau and metadata_from_bdd[3] < self.date_cloture_exercice):
                if better_code_motif and less_confidential:
                    print("New metadata", self, "chevauche la période du metadata déjà en base", metadata_from_bdd, ". On garde le nouveau car il est un peu mieux")
                    return MetadataCase.REPLACE
                else:
                    print("New metadata", self, "chevauche la période du metadata déjà en base", metadata_from_bdd, ". On garde l'ancien car il est un peu moins bien")
                    return MetadataCase.IGNORE

            # Le nouveau bilan n'est pas trop cohérent avec celui en base, mais on l'ajoute si l'INPI ne signale pas d'erreur.
            if self.code_confidentialite == 0 and self.code_motif in ['0', '6'] and self.duree_exercice > 0:
                return MetadataCase.COMPLEMENTARY
            else:
                return MetadataCase.IGNORE

        if self.duree_exercice == metadata_from_bdd[2] and self.code_motif == metadata_from_bdd[4] and self.code_confidentialite == metadata_from_bdd[5]:
            # Tous est identique sauf peut-être le 'info_traitement'!
            return MetadataCase.IGNORE

        if better_code_motif and less_confidential:
            print("le nouveau bilan", self, "couvre la même période que le metadata en base", metadata_from_bdd, 'mais avec un code confidentiel ou motif mieux ou pas pire')
            return MetadataCase.REPLACE
        else:
            print("le nouveau bilan", self, "couvre la même période que le metadata en base", metadata_from_bdd, 'mais avec un code confidentiel ou motif pire')
            return MetadataCase.IGNORE


    def has_less_error(self, metadata_from_bdd):
        if self.code_motif in ['0', '6']:
            return True
        if metadata_from_bdd[4] in ['0', '6']:
            return False
        if self.code_motif in ['1', '1A']:
            return True
        if metadata_from_bdd[4] in ['1', '1A']:
            return False
        if not self.code_motif in ERROR_CODE_MOTIF:
            print("code motif inconnu pour", self)
            exit()
        return False

    def has_less_confidentiality(self, metadata_from_bdd):
        if self.code_confidentialite == 0:
            return True
        if metadata_from_bdd[5] == 0:
            return False
        if self.code_confidentialite == 2:
            return True
        if metadata_from_bdd[5] == 2:
            return False
        if self.code_confidentialite != 1:
            print("code confidentiel inconnu pour", self)
            exit()
        # Les deux sont égaux à 1
        return False
