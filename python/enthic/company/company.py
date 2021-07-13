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
from flask import abort

from enthic.database.fetch import fetchall
from enthic.database.mysql_data import SQLData
from enthic.ontology import ONTOLOGY, APE_CODE, CODE_MOTIF, CODE_CONFIDENTIALITE, INFO_TRAITEMENT, SCORE_DESCRIPTION
from enthic.utils.error_json_response import ErrorJSONResponse
from enthic.utils.INPI_data_enhancer import decrypt_code_motif
from enthic.utils.ok_json_response import OKJSONResponse


year_re = compile(r"^\d{4}$")  # REGEX OF A YEAR
denomination_re = compile(r"^.*$")  # TODO: DEFINE A SAFER REGEX FOR DENOMINATION


class JSONGenKey:
    """
    Generic keys found in the JSON response
    """
    VALUE = "value"
    DESCRIPTION = "description"
    ACCOUNT = "account"
    CODE = "code"


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


class CompanyIdentity():
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
            self.ape = {JSONGenKey.VALUE: APE_CODE[args[2]][1] + " (" + str(APE_CODE[args[2]][0]) + ")",
                        JSONGenKey.DESCRIPTION: "Code Activité Principale Exercée (NAF)",
                        JSONGenKey.CODE: APE_CODE[args[2]][0]}
        except KeyError:
            self.ape = {JSONGenKey.VALUE: "{}, Code APE inconnu".format(args[2]),
                        JSONGenKey.DESCRIPTION: "Code Activité Principale Exercée (NAF)"}
        self.postal_code = {JSONGenKey.VALUE: args[3], JSONGenKey.DESCRIPTION: "Code Postal"}
        self.town = {JSONGenKey.VALUE: args[4], JSONGenKey.DESCRIPTION: "Commune"}
        self.devise = {JSONGenKey.VALUE: "Euro", JSONGenKey.DESCRIPTION: "Devise"}


class Bundle():
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
                att_declaration[ONTOLOGY["accounting"][int_account]["code"][int_bundle][0]] = {
                        JSONGenKey.ACCOUNT: ONTOLOGY["accounting"][int_account][1],
                        JSONGenKey.VALUE: amount,
                        JSONGenKey.DESCRIPTION:
                            ONTOLOGY["accounting"][int_account]["code"][int_bundle][
                                1]
                    }
            else:
                setattr(self, str_declaration, {
                    ONTOLOGY["accounting"][int_account]["code"][int_bundle][0]: {
                        JSONGenKey.ACCOUNT: ONTOLOGY["accounting"][int_account][1],
                        JSONGenKey.VALUE: amount,
                        JSONGenKey.DESCRIPTION:
                            ONTOLOGY["accounting"][int_account]["code"][int_bundle][
                                1]
                    }
                })

def get_accountability_metadata(siren):
    """
    Return all Accountability Metadata for the matching company

        :param siren : siren to look for the corresponding company_siren
        :return: company's metadata in a nice JSON-like structure
    """
    sql_request = """
        SELECT declaration, code_motif, code_confidentialite, info_traitement
        FROM `accountability_metadata`
        WHERE siren = %s"""
    raw_results = fetchall(sql_request, (siren,))

    pretty_results =  {}
    for declaration, code_motif, code_confidentialite, info_traitement in raw_results:
        str_year = str(declaration)
        decrypted_code_motif = decrypt_code_motif(code_motif)
        pretty_results[str_year] = {
            "code_motif" : {
                JSONGenKey.VALUE: decrypted_code_motif
            },
            "code_confidentialite" : {
                JSONGenKey.VALUE: code_confidentialite,
                JSONGenKey.DESCRIPTION:CODE_CONFIDENTIALITE[code_confidentialite]
            }
        }

        if decrypted_code_motif in CODE_MOTIF:
            pretty_results[str_year]["code_motif"][JSONGenKey.DESCRIPTION] = CODE_MOTIF[decrypted_code_motif]

        if info_traitement != "rien" :
            pretty_results[str_year]["info_traitement"] = {
                JSONGenKey.VALUE: info_traitement
            }
            if info_traitement in INFO_TRAITEMENT:
                pretty_results[str_year]["info_traitement"][JSONGenKey.DESCRIPTION] = INFO_TRAITEMENT[info_traitement]

    return pretty_results


def get_company_annual_stats(siren):
    """
    Return all annual statistics available for the matching company

        :param siren : siren to look for the corresponding company_siren
        :return: company's metadata in a nice JSON-like structure
    """
    sql_request = """
        SELECT declaration, value, stats_type
        FROM `annual_statistics`
        WHERE annual_statistics.siren = %s;"""
    raw_results = fetchall(sql_request, (siren,))

    pretty_results =  {}
    for declaration, value, stats_type in raw_results:
        str_year = str(declaration)
        if not str_year in pretty_results :
            pretty_results[str_year] = {}

        pretty_results[str_year][stats_type] = {
                JSONGenKey.VALUE : value
            }
        pretty_results[str_year][stats_type].update(SCORE_DESCRIPTION[stats_type])
    return pretty_results


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
            "financial_data": {
                "di": {
                    "account": "Compte annuel complet",
                    "value": -261053.0,
                    "description": "Résultat de l\u2019exercice (bénéfice ou perte)"
                },
                "fs": {
                    "account": "Compte annuel complet",
                    "value": 11836.0,
                    "description": "Achats de marchandises (y compris droits de douane)"
                }
            }
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
            "declarations": {
                "2016" : {
                    "financial_data": {
                        "di": {
                            "account": "Compte annuel complet",
                            "value": -261053.0,
                            "description": "Résultat de l\u2019exercice (bénéfice ou perte)"
                        }
                    }
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
        self.declarations = {"declarations": {}}
        for year, _bundle in _bundles.items():
            self.declarations["declarations"][year] = {"financial_data": _bundle}

        # Add annual statistics to company's data structure, if there is (i.e if there is financial data)
        if _bundles:
            annual_stats = get_company_annual_stats(self.sql_results[0][0])
            for year, statsdata in annual_stats.items():
                if year in self.declarations["declarations"]:
                    self.declarations["declarations"][year]["statistics"] = statsdata
                else:
                    self.declarations["declarations"][year] = { "statistics" : statsdata}

        # Add metadata to company's data structure
        accountability_metadata = get_accountability_metadata(self.sql_results[0][0])
        for year, metadata in accountability_metadata.items():
            if year in self.declarations["declarations"]:
                self.declarations["declarations"][year]["metadata"] = metadata
            else:
                self.declarations["declarations"][year] = { "metadata" : metadata}

        OKJSONResponse.__init__(self, {**CompanyIdentity(*self.sql_results[0][:7]).__dict__,
                                       **self.declarations})
