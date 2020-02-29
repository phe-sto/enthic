# -*- coding: utf-8 -*-
"""
============================================================
Generic classes representing a company and their function(s)
============================================================

PROGRAM BY PAPIT SASU, 2020

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""

from re import compile

from enthic.ape import ape_code
from enthic.database.sql_data import SQLData
from enthic.ontology import ONTOLOGY
from enthic.result.result import result
from enthic.score.classification import DistributionClassification
from enthic.utils.error_json_response import ErrorJSONResponse
from enthic.utils.ok_json_response import OKJSONResponse
from flask import abort

year_re = compile(r"^\d{4}$")  # REGEX OF A YEAR
siren_re = compile(r"^\d{9}$")  # REGEX OF A SIREN
denomination_re = compile(r"^[a-zA-Z0-9_ ]*$")  # REGEX OF A SIREN


class YearCompany:
    """
    Company data for a given year.
    """
    __slots__ = ('year',)

    def __init__(self, year):
        """
        Constructor, check the format of the year passed. Year set as attribute
        if correct.

           :param year: String that to match ^\\d{4}$.
        """
        if year_re.match(year) is None:  # CHECK YEAR FORMAT
            abort(ErrorJSONResponse("Year format is not ^\\d{4}$"))
        else:
            self.year = year


class DenominationCompany:
    """
    Denomination defined company.
    """

    def __init__(self, denomination):
        """
        Constructor, check the format of the denomination passed.
        Denomination set as attribute if correct.

           :param year: String that to match ^[a-zA-Z0-9_ ]*$.
        """
        if denomination_re.match(denomination) is None:  # CHECK denomination FORMAT
            abort(ErrorJSONResponse("Denomination format is not ^[a-zA-Z0-9_ ]*$"))
        else:
            self.denomination = denomination


class SirenCompany:
    """
    Siren defined company.
    """

    def __init__(self, siren):
        """
        Constructor, check the format of the siren passed. Year set as attribute
        if correct.

           :param siren: String that to match ^\\d{9}$.
        """
        if siren_re.match(siren) is None:  # CHECK SIREN FORMAT
            abort(ErrorJSONResponse("SIREN for is wrong, must match ^\\d{9}$."))
        else:
            self.siren = siren


class CompanyIdentity(object):
    """
    Identity data of the Company.
    """

    def __init__(self, *args):
        """
        Constructor initialising attributes as value/description pair.

           :param args: a tuple coming SQL result, each result being
              [[bundle, calculation, amount]...].
        """
        self.siren = {"value": args[0], "description": "SIREN"}
        self.denomination = {"value": args[1], "description": "Dénomination"}
        try:
            self.ape = {
                "value": "{}, {}".format(args[2], ape_code[args[2]]),
                "description": "Code Activité Principale Exercée (NAF)"}
        except KeyError:
            self.ape = {"value": "{}, Code APE inconnu".format(args[2]),
                        "description": "Code Activité Principale Exercée (NAF)"}
        self.postal_code = {"value": args[3], "description": "Code Postal"}
        self.town = {"value": args[4], "description": "Commune"}
        self.accountability = {"value": "{}, {}".format(args[5],
                                                        ONTOLOGY["accounting"][
                                                            args[5]]["description"]),
                               "description": "Type de comptabilité"}
        self.devise = {"value": args[6], "description": "Devise"}


class Bundle:
    """
    All the bundle declared and scoring of a company. Can be several year, one
    or average
    """

    def __init__(self, *args):
        """
        Constructor initialising attributes as value/description pair.

           :param args: a tuple coming SQL result, each result being
              [identity.siren, denomination, ape, postal_code, town,
              accountability, devise].
        """
        bundles = {}
        declaration = None
        for tup_bundle in args:
            ####################################################################
            # BUNDLE FROM DATABASE
            bundle = str(tup_bundle[0]).lower()
            if str(tup_bundle[1]) not in bundles:
                declaration = str(tup_bundle[1])
                bundles[declaration] = {}
            try:
                value = round(tup_bundle[2], 2)
                for accounting in ONTOLOGY["accounting"].keys():
                    try:
                        bundles[declaration][bundle] = {
                            "value": value,
                            "description":
                                ONTOLOGY["accounting"][accounting]["code"][
                                    bundle]
                        }
                    except KeyError:
                        pass
                ################################################################
                # SCORE RELATED CALCULATION
                if bundle == "dir" and result.avg_dir[1] is not None:
                    if value > result.avg_dir[1] - result.avg_dir[1] * 0.1:
                        distribution = DistributionClassification.TIGHT
                    elif result.avg_dir[1] - result.avg_dir[1] * 0.1 <= value <= \
                            result.avg_dir[1] + result.avg_dir[1] * 0.1:
                        distribution = DistributionClassification.AVERAGE
                    elif result.avg_dir[1] + result.avg_dir[1] * 0.1 > value:
                        distribution = DistributionClassification.GOOD
                    else:
                        distribution = DistributionClassification.UNKNOWN
                    bundles[declaration][bundle] = {
                        "value": distribution.value,
                        "description":
                            ONTOLOGY["scoring"]["distribution"][
                                "description"]}
            except TypeError:  # IN CASE OF NO BUNDLE
                continue
        for _declaration, _bundles in bundles.items():
            setattr(self, _declaration, _bundles)


class UniqueBundleCompany(OKJSONResponse, SQLData):
    """
    Company data returned with a unique bundle as attribute. Inherit from
    OKJSONResponse to return a JSON and SQLData because of base data..
    """

    def __init__(self, sql_request):
        """
        Constructor assigning CompanyIdentity and only Bundle

           :param sql_request: SQL request of the Company data to execute as a string.

        .. code-block:: json

           {
              "gan" : {
                 "value" : 2976860,
                 "description" : "Gain d'une companie, actuellement le chiffre d'affaire uniquement FJ"
              },
              "ape" : {
                 "description" : "Code Activité Principale Exercée (NAF)",
                 "value" : "7311Z, Activités des agences de publicité"
              },
              "di" : {
                 "value" : 499,
                 "description" : "Résultat de l’exercice (bénéfice ou perte)"
              },
              "town" : {
                 "description" : "Commune",
                 "value" : "ERMONT"
              },
              "denomination" : {
                 "value" : "MRG PROMOTION",
                 "description" : "Dénomination"
              },
              "siren" : {
                 "description" : "SIREN",
                 "value" : "307034421"
              },
              "devise" : {
                 "value" : "EUR",
                 "description" : "Devise"
              },
              "postal_code" : {
                 "description" : "Code Postal",
                 "value" : "95120"
              },
              "dir" : {
                 "value" : 0.01,
                 "description" : "Distribution ratio, (FY + HJ) / GAN, i.e pondération de dis par le chiffre d'affaire"
              }
           }
        """
        SQLData.__init__(self, sql_request)
        OKJSONResponse.__init__(self, {**CompanyIdentity(*self.sql_results[0][:7]).__dict__,
                                       **Bundle(
                                           *[bundle[7:] for bundle in
                                             list(self.sql_results)]).__dict__[
                                           self.sql_results[0][8]]})


class MultipleBundleCompany(OKJSONResponse, SQLData):
    """
    Company data returned with array of Bundle for each declaration. Inherit from
    OKJSONResponse to return a JSON and SQLData because of base data.

    .. code-block:: json

       {
          "gan" : {
             "value" : 2976860,
             "description" : "Gain d'une companie, actuellement le chiffre d'affaire uniquement FJ"
          },
          "ape" : {
             "description" : "Code Activité Principale Exercée (NAF)",
             "value" : "7311Z, Activités des agences de publicité"
          },
          "di" : {
             "value" : 499,
             "description" : "Résultat de l’exercice (bénéfice ou perte)"
          },
          "town" : {
             "description" : "Commune",
             "value" : "ERMONT"
          },
          "financial_data" : [
              {
                 "dir" : {
                    "value" : 0.03,
                    "description" : "Distribution ratio, (FY + HJ) / GAN, i.e pondération de dis par le chiffre d'affaire"
                 },
                 "dis" : {
                    "value" : 34974,
                    "description" : "Somme des distributions, FY + HJ"
                 },
                 "di" : {
                    "description" : "Résultat de l’exercice (bénéfice ou perte)",
                    "value" : -129783
                 },
                 "gan" : {
                    "description" : "Gain d'une companie, actuellement le chiffre d'affaire uniquement FJ",
                    "value" : 1196260
                 },
                 "declaration" : {
                    "value" : 2015,
                    "description" : "Année de déclaration"
                 }
              }
           ]
       }


    """
    __slots__ = ('financial_data',)

    def __init__(self, sql_request):
        """
        Constructor assigning CompanyIdentity and an array of
        Bundles.

           :param sql_request: SQL request of the Company data to execute as a string.
        """
        SQLData.__init__(self, sql_request)
        _bundles = Bundle(*[bundle[7:] for bundle in list(self.sql_results)]).__dict__
        self.financial_data = {"financial_data": []}
        for year, _bundle in _bundles.items():
            self.financial_data["financial_data"].append(
                {**{"declaration": {"value": int(year), "description": "Année de déclaration"}},
                 **_bundle})
        OKJSONResponse.__init__(self,
                                {**CompanyIdentity(
                                    *self.sql_results[0][:7]).__dict__,
                                 **self.financial_data})
