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

from sqlalchemy import create_engine, Column, Integer, String, Date

from sqlalchemy.orm import declarative_base
Base = declarative_base()

ERROR_CODE_MOTIF = ['02', '03', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']

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

    def is_same_year(self, metadata_from_bdd):
        if self.siren != metadata_from_bdd[0]:
            return False
        if self.declaration != metadata_from_bdd[1]:
            return False
        if self.accountability != metadata_from_bdd[7]:
            return False
        return True

    def equals(self, metadata_from_bdd):
        if self.siren != metadata_from_bdd[0]:
            return False
        if self.declaration != metadata_from_bdd[1]:
            return False
        if self.duree_exercice != metadata_from_bdd[2]:
            return False
        if self.date_cloture_exercice.date() != metadata_from_bdd[3]:
            return False
        if self.code_motif != metadata_from_bdd[4]:
            return False
        if self.code_confidentialite != metadata_from_bdd[5]:
            return False
        if self.info_traitement != metadata_from_bdd[6]:
            return False
        if self.accountability != metadata_from_bdd[7]:
            return False
        return True

    def is_the_same_or_worse(self, metadata_from_bdd):
        if self.equals((818609604, 2016, 14, datetime.date(2017, 3, 31), '6', 0, None, 'C')) or self.equals((538384140, 2015, 12, datetime.date(2015, 6, 30), '1', 0, None, 'C')) or self.equals((491378659, 2016, 9, datetime.date(2017, 5, 31), '1', 0, None, 'C')) or self.equals((394968606, 2016, 7, datetime.date(2017, 3, 31), '1', 0, None, 'C')) or self.equals((790643498, 2017, 12, datetime.date(2017, 9, 29), '1', 0, None, 'S')) or self.equals((493788624, 2015, 12, datetime.date(2015, 6, 30), '0', 0, None, 'C')) or self.equals((792693939, 2016, 7, datetime.date(2017, 3, 31), '1', 0, None, 'C')) or self.equals((751564980, 2015, 3, datetime.date(2015, 9, 30), '0', 0, None, 'C')) or self.equals((751564980, 2015, 12, datetime.date(2015, 6, 30), '0', 0, None, 'C')) or self.equals((795405497, 2014, 9, datetime.date(2015, 3, 31), '0', 0, None, 'C')) or self.equals((380930883, 2017, 6, datetime.date(2017, 12, 31), '0', 0, None, 'C')) or self.equals((822001277, 2017, 13, datetime.date(2017, 9, 30), '6', 0, None, 'S')) or self.equals((821446127, 2017, 9, datetime.date(2018, 4, 30), '0', 0, None, 'S')) or self.equals((800874885, 2017, 11, datetime.date(2017, 12, 13), '0', 0, None, 'C')) or self.equals((398452698, 2017, 12, datetime.date(2017, 12, 31), '0', 0, None, 'C')):
            print("le nouveau bilan", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "est un bilan maudit queje ne comprend pas, il faudra enquêter plus tard")
            return True
        if self.duree_exercice == 0:
            print("le nouveau bilan", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "est un bilan maudit avec une durée de zéro mois, c'est louche, à regarder + tard!")
            return True
        if self.accountability in ['B']:
            print("le nouveau bilan", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "est un bilan de type de comptabilité qu'on s'en fout pour l'instant")
            return True
        if not self.is_same_year(metadata_from_bdd):
            return False
        if self.date_cloture_exercice.date() != metadata_from_bdd[3]:
            return False
        if self.info_traitement != metadata_from_bdd[6]:
            return False
        if self.code_confidentialite != metadata_from_bdd[5]:
            if self.code_confidentialite in [1, 2] and metadata_from_bdd[5] == 0:
                return True # pas le même mais moins bien car confidentiel
            if self.code_confidentialite == 1 and metadata_from_bdd[5] == 2:
                print("le nouveau bilan", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "couvre la même période couverte par le metadata en base", metadata_from_bdd, 'mais avec un code confidentiel encore plus confidentiel')
                return True
            return False
        if self.code_motif != metadata_from_bdd[4]:
            if self.code_motif in ["1", "08", "19", "1A"] and metadata_from_bdd[4] == "0":
                return True # pas le même mais moins bien car le code motif déclare une erreur
            if self.code_motif in ERROR_CODE_MOTIF and metadata_from_bdd[4] in ["1", "0"]:
                return True # pas le même mais moins bien car le code motif déclare une erreur pire que celui en base
            if self.code_motif == "6" and self.code_confidentialite == 1:
                return True # pas le même mais relivraison confidentielle... on s'en fout donc
            if self.duree_exercice < metadata_from_bdd[2]:
                print("le nouveau bilan", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "couvre une période déjà couverte par le metadata en base", metadata_from_bdd)
                return True
            if self.code_motif in ERROR_CODE_MOTIF:
                print("le nouveau bilan", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "couvre la même période couverte par le metadata en base", metadata_from_bdd, 'mais avec une erreur qui indique aucune information comptable')
                return True
            return False
        return True # exactly the same

    def is_complementary(self, metadata_from_bdd):
        if not self.is_same_year(metadata_from_bdd):
            return False
        if self.date_cloture_exercice.date() == metadata_from_bdd[3]:
            return False
        # Si la somme des durées des 2 bilans comptables fait 12 mois ou moins, et qu'un des 2 fini le 31 décembre, alors c'est une année découpé en 2 bilans, mais qui n'a pas forcément commencé le 1 janvier.
        if self.duree_exercice + metadata_from_bdd[2] <= 12:
            print("New metadata", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "complémentaire du metadata déjà en base", metadata_from_bdd)
            return True
        # Si le nouveau bilan dure moins de 7 mois, et couvre la période suivant exactement le bilan précédent qui durait 12 mois, alors c'est peut-être un déplacement de fin d'année fiscale pour l'entreprise.
        if metadata_from_bdd[2] in [9, 10, 12, 13, 14] and self.duree_exercice <= 6 and ((self.date_cloture_exercice - datetime.timedelta(days=31*self.duree_exercice)).month == metadata_from_bdd[3].month):
            print("New metadata", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "prolonge, vers le futur, le metadata déjà en base", metadata_from_bdd, "pour un changement de date d'année fiscale")
            return True

        # Si le nouveau bilan dure moins de 7 mois, et couvre la période précédent exactement le bilan en base qui durait 12 mois, alors c'est peut-être un déplacement de fin d'année fiscale pour l'entreprise, ou un début d'activité.
        if metadata_from_bdd[2] in [12, 3] and self.duree_exercice < 7 and ((metadata_from_bdd[3] - datetime.timedelta(days=31*metadata_from_bdd[2])).month == self.date_cloture_exercice.month):
            print("New metadata", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "prolonge, vers le passé, le metadata déjà en base", metadata_from_bdd, "pour un changement de date d'année fiscale")
            return True

        # Si le nouveau bilan couvre la période suivant exactement le bilan précédent, alors c'est peut-être un déplacement de fin d'année fiscale pour l'entreprise.
        date_debut = (self.date_cloture_exercice - datetime.timedelta(days=31*self.duree_exercice))
        if date_debut.month == metadata_from_bdd[3].month and date_debut.year == metadata_from_bdd[3].year:
            print("New metadata", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "prolonge le metadata déjà en base", metadata_from_bdd, "après un changement de date d'année fiscale, ou un début d'activité")
            return True

        # Si le nouveau bilan dure 12 mois, et couvre la période précédent exactement le bilan en base qui durait moins de 6 mois et finissait le 31 décembre, alors c'est peut-être le bilan précédent un changement de fin d'année fiscale pour l'entreprise.
        if metadata_from_bdd[2] < 6 and self.duree_exercice in [12, 15] and metadata_from_bdd[3].month == 12 and metadata_from_bdd[3].day == 31 and ((metadata_from_bdd[3] - datetime.timedelta(days=31*metadata_from_bdd[2])).month == self.date_cloture_exercice.month):
            print("New metadata", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "précède le metadata déjà en base", metadata_from_bdd, "et qui correspondait à un changement de date d'année fiscale")
            return True
        return False


    def replace(self, metadata_from_bdd):
        if not self.is_same_year(metadata_from_bdd):
            return False

        # Si le nouveau bilan couvre la même période que celui en base ou si le bilan en base a une durée nulle
        if (self.duree_exercice == metadata_from_bdd[2] or metadata_from_bdd[2] == 0) and self.date_cloture_exercice.date() == metadata_from_bdd[3] and self.info_traitement == metadata_from_bdd[6] :
            # mais avec un meilleur code motif (donc sans erreur INPI)
            if self.code_confidentialite == metadata_from_bdd[5] and self.info_traitement == metadata_from_bdd[6] and self.code_motif in ['6', '0', '1'] and metadata_from_bdd[4] in ['03', '1', '1A', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']:
                print("New metadata", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "a un meilleur code motif que le metadata déjà en base", metadata_from_bdd)
                return True
            # mais avec moins de confidentialité
            elif (self.code_confidentialite == 0 and metadata_from_bdd[5] in [1, 2]) or (self.code_confidentialite == 2 and metadata_from_bdd[5] == 1):
                print("New metadata", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "a un meilleur code confidentialité que le metadata déjà en base", metadata_from_bdd)
                return True

        # Si le nouveau bilan fini à la même date que celui en base mais avec une durée supérieur et un meilleur code motif
        if self.duree_exercice > metadata_from_bdd[2] and self.date_cloture_exercice.date() == metadata_from_bdd[3] and self.info_traitement == metadata_from_bdd[6] and self.code_motif in ['0', '6'] and  metadata_from_bdd[4] == '1':
            print("New metadata", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "a un meilleur code motif et couvre une période plus longue que le metadata déjà en base", metadata_from_bdd)
            return True
        return False

    def has_more_detail(self, metadata_from_bdd):
        if not self.is_same_year(metadata_from_bdd):
            return False

        # Si le nouveau bilan couvre la même période que celui en base, avec un meilleur code motif équivalent
        if self.duree_exercice == metadata_from_bdd[2] and self.date_cloture_exercice.date() == metadata_from_bdd[3] and self.code_confidentialite == metadata_from_bdd[5] and self.info_traitement == metadata_from_bdd[6] and self.code_motif in ['6', '0'] and metadata_from_bdd[4] in ['6', '0']:
            print("New metadata", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "a un code motif équivalent au metadata déjà en base", metadata_from_bdd)
            return True
        return False

    def is_overwrite(self, metadata_from_bdd):
        if not self.is_same_year(metadata_from_bdd):
            return False

        if self.date_cloture_exercice.date() == metadata_from_bdd[3]:
            return False

        # Si le nouveau bilan commence à la même date que l'ancien, mais dure jusqu'à la fin de l'année, alors il remplace l'ancien
        if (metadata_from_bdd[2] - self.duree_exercice) == (metadata_from_bdd[3].month - self.date_cloture_exercice.month) and self.date_cloture_exercice.month == 12 and self.date_cloture_exercice.day == 31:
            print("New metadata", self.siren, self.declaration, self.duree_exercice, self.date_cloture_exercice.date(), self.code_motif, self.code_confidentialite, self.info_traitement, self.accountability, "remplace le metadata déjà en base", metadata_from_bdd)
            return True
        return False
