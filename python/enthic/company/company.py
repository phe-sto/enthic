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

from enthic.database.mysql_data import SQLData
from enthic.ontology import ONTOLOGY, APE_CODE
from enthic.utils.error_json_response import ErrorJSONResponse
from enthic.utils.ok_json_response import OKJSONResponse
from flask import abort

year_re = compile(r"^\d{4}$")  # REGEX OF A YEAR
denomination_re = compile(r"^.*$")  # TODO: DEFINE A SAFER REGEX FOR DENOMINATION


class JSONGenKey:
    """
    Generic keys found in the JSON response
    """
    VALUE = "value"
    DESCRIPTION = "description"
    ACCOUNT = "account"


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

           :param denomination: String that to match ^.*$.
        """
        if denomination_re.match(denomination) is None:  # CHECK denomination FORMAT
            abort(ErrorJSONResponse("Denomination format is not ^.*$"))
        else:
            self.denomination = denomination


class SirenCompany:
    """
    Siren defined company.
    """

    def __init__(self, siren):
        """
        Constructor, check the the siren passed. Siren set as attribute
        if correct.

           :param siren: Integer between 0 and 1000000000 (excluded).
        """
        if 0 <= siren < 1000000000:  # CHECK SIREN
            self.siren = siren
        else:
            abort(ErrorJSONResponse("SIREN not between 0 and 1000000000 (excluded)"))


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
        self.siren = {JSONGenKey.VALUE: "%09d" % args[0], JSONGenKey.DESCRIPTION: "SIREN"}
        self.denomination = {JSONGenKey.VALUE: args[1], JSONGenKey.DESCRIPTION: "Dénomination"}
        try:
            self.ape = {JSONGenKey.VALUE: APE_CODE[args[2]][1],
                        JSONGenKey.DESCRIPTION: "Code Activité Principale Exercée (NAF)"}
        except KeyError:
            self.ape = {JSONGenKey.VALUE: "{}, Code APE inconnu".format(args[2]),
                        JSONGenKey.DESCRIPTION: "Code Activité Principale Exercée (NAF)"}
        self.postal_code = {JSONGenKey.VALUE: args[3], JSONGenKey.DESCRIPTION: "Code Postal"}
        self.town = {JSONGenKey.VALUE: args[4], JSONGenKey.DESCRIPTION: "Commune"}
        self.devise = {JSONGenKey.VALUE: "Euro", JSONGenKey.DESCRIPTION: "Devise"}


class Bundle(object):
    """
    All the bundle declared and scoring of a company. Can be several year, one
    or average
    """

    def __init__(self, *args):
        """
        Constructor initialising attributes as value/description pair.

           :param args: a tuple coming SQL result, each result being
              (accountability, bundle, declaration, amount).
        """
        _gan, _dis, _dir = (None,) * 3
        for int_account, int_bundle, declaration, amount in args:
            if None in [int_account, int_bundle, declaration, amount]:
                continue
            ####################################################################
            # ACCOUNTING
            str_declaration = str(declaration)
            if hasattr(self, str_declaration) is True:
                att_declaration = object.__getattribute__(self, str_declaration)
                att_declaration.append({
                    ONTOLOGY["accounting"][int_account]["code"][int_bundle][0]: {
                        JSONGenKey.ACCOUNT: ONTOLOGY["accounting"][int_account][1],
                        JSONGenKey.VALUE: amount,
                        JSONGenKey.DESCRIPTION:
                            ONTOLOGY["accounting"][int_account]["code"][int_bundle][
                                1]
                    }
                })
            else:
                setattr(self, str_declaration, [{
                    ONTOLOGY["accounting"][int_account]["code"][int_bundle][0]: {
                        JSONGenKey.ACCOUNT: ONTOLOGY["accounting"][int_account][1],
                        JSONGenKey.VALUE: amount,
                        JSONGenKey.DESCRIPTION:
                            ONTOLOGY["accounting"][int_account]["code"][int_bundle][
                                1]
                    }
                }])


class UniqueBundleCompany(OKJSONResponse, SQLData):
    """
    Company data returned with a unique bundle as attribute. Inherit from
    OKJSONResponse to return a JSON and SQLData because of base data..
    """

    def __init__(self, sql_request, args):
        """
        Constructor assigning CompanyIdentity and only Bundle

           :param sql_request: SQL request of the Company data to execute as a string.

    .. code-block:: json

        {
            "siren": {
                "value": "005420120",
                "description": "SIREN"
            },
            "denomination": {
                "value": "STE DES SUCRERIES DU MARQUENTERRE",
                "description": "Dénomination"
            },
            "ape": {
                "value": "Activités des sièes sociaux",
                "description": "Code Activité Principale Exercée (NAF)"
            },
            "postal_code": {
                "value": "62140",
                "description": "Code Postal"
            },
            "town": {
                "value": "MARCONNELLE",
                "description": "Commune"
            },
            "devise": {
                "value": "Euro",
                "description": "Devise"
            },
            "financial_data": [
                {
                    "di": {
                        "account": "Compte annuel complet",
                        "value": -261053.0,
                        "description": "Résultat de l\u2019exercice (bénéfice ou perte)"
                    }
                },
                {
                    "fs": {
                        "account": "Compte annuel complet",
                        "value": 11836.0,
                        "description": "Achats de marchandises (y compris droits de douane)"
                    }
                }
            ]
        }
        """
        SQLData.__init__(self, sql_request, args)
        if None in self.sql_results[0]:
            OKJSONResponse.__init__(self, CompanyIdentity(*self.sql_results[0][:5]).__dict__)

        else:
            OKJSONResponse.__init__(self, {**CompanyIdentity(*self.sql_results[0][:5]).__dict__,
                                           **{"financial_data": Bundle(*[bundle[5:] for bundle in
                                                                         self.sql_results]).__dict__[
                                               self.sql_results[0][7]]}})


class MultipleBundleCompany(OKJSONResponse, SQLData):
    """
    Company data returned with array of Bundle for each declaration. Inherit from
    OKJSONResponse to return a JSON and SQLData because of base data.

    .. code-block:: json

        {
            "siren": {
                "value": "005420120",
                "description": "SIREN"
            },
            "denomination": {
                "value": "STE DES SUCRERIES DU MARQUENTERRE",
                "description": "Dénomination"
            },
            "ape": {
                "value": "Activités des sièes sociaux",
                "description": "Code Activité Principale Exercée (NAF)"
            },
            "postal_code": {
                "value": "62140",
                "description": "Code Postal"
            },
            "town": {
                "value": "MARCONNELLE",
                "description": "Commune"
            },
            "devise": {
                "value": "Euro",
                "description": "Devise"
            },
            "declarations": [
                {
                    "declaration": {
                        "value": 2016,
                        "description": "Année de déclaration"
                    },
                    "financial_data": [
                        {
                            "di": {
                                "account": "Compte annuel complet",
                                "value": -261053.0,
                                "description": "Résultat de l\u2019exercice (bénéfice ou perte)"
                            }
                        }
                    ]
                }
            ]
        }
    """
    __slots__ = ('declarations',)

    def __init__(self, sql_request, args):
        """
        Constructor assigning CompanyIdentity and an array of
        Bundles.

           :param sql_request: SQL request of the Company data to execute as a string.
        """
        SQLData.__init__(self, sql_request, args)
        _bundles = Bundle(*[bundle[5:] for bundle in self.sql_results]).__dict__
        self.declarations = {"declarations": []}
        for year, _bundle in _bundles.items():
            self.declarations["declarations"].append(
                {"declaration": {JSONGenKey.VALUE: int(year),
                                 JSONGenKey.DESCRIPTION: "Année de déclaration"},
                 "financial_data": _bundle},
            )
        OKJSONResponse.__init__(self, {**CompanyIdentity(*self.sql_results[0][:7]).__dict__,
                                       **self.declarations})
