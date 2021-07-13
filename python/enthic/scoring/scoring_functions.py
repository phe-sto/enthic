# -*- coding: utf-8 -*-
"""
====================================================================
Compute statistics from companies's data after complete and check it
====================================================================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
import math


def compute_exploitation_share(data):
    """
    Computes the share score of given data

        :param data: dictionary containing all needed values
        :return: share score value, or NaN if it cannot be computed
    """
    # Retrieve needed values
    participation = data["participation"]
    impot = data["impot"]
    resultat_exploitation = data["resultat_exploitation"]

    # If any values unknown, cannot compute score
    if any(math.isnan(value) for value in [participation, impot, resultat_exploitation]):
        return float('nan')

    # Compute score if possible
    shared_part = participation + impot
    if resultat_exploitation > 0:
        return shared_part / resultat_exploitation

    return float('nan')


def compute_overall_wages_weight(data):
    """
    Computes part of wages in whole company's costs

        :param data: dictionary containing all needed values
        :return: wages part of company's costs, or NaN if it cannot be computed
    """
    cotisations_sociales = data["cotisations_sociales"]
    salaires = data["salaires"]
    charges = data["charges"]

    if math.isnan(charges) or math.isnan(salaires) and math.isnan(cotisations_sociales):
        return float('nan')

    return (salaires + cotisations_sociales) / charges


def compute_wage_quality(data):
    """
    Computes ratio between 'cotisations' and wages

    :param data: dictionary containing all needed values
    :return: the score, or NaN if they cannot be computed
    """
    cotisations_sociales = data["cotisations_sociales"]
    salaires = data["salaires"]

    if math.isnan(salaires):
        return float('nan')

    return cotisations_sociales / salaires


def compute_average_wage(data):
    """
    Computes the average wage

    :param data: dictionary containing all needed values
    :return: average wage value, or NaN if it cannot be computed
    """
    cotisations_sociales = data["cotisations_sociales"]
    salaires = data["salaires"]
    effectifs = data["effectifs"]

    if math.isnan(effectifs) or (math.isnan(cotisations_sociales) and math.isnan(salaires)):
        return float('nan')

    return effectifs / (salaires + cotisations_sociales)


def compute_profit_sharing(data):
    """
    Computes profit's part shared with State and employees

    :param data: dictionary containing all needed values
    :return: part of profit shared, or NaN if it cannot be computed
    """
    participation = data["participation"]
    impot = data["impot"]
    resultat_exceptionnel = data["resultat_exceptionnel"]
    resultat_financier = data["resultat_financier"]
    resultat_exploitation = data["resultat_exploitation"]

    if any(math.isnan(value) for value in [participation, impot, resultat_financier, resultat_exceptionnel, resultat_exploitation]):
        return float('nan')

    if (resultat_financier + resultat_exploitation + resultat_exceptionnel) == 0:
        return float('nan')

    return (participation + impot) / (resultat_financier + resultat_exploitation + resultat_exceptionnel)


def compute_exploitation_part(data):
    """
    Computes part for exploitation in company's 'compte de résultat'

    :param data: dictionary containing all needed values
    :return: part of exploitation, or NaN if it cannot be computed
    """

    return (data["produits_exploitation"] + data["charges_exploitation"]) / (data["produits_exploitation"] + data["charges_exploitation"] + data["produits_exceptionnel"] + data["charges_exceptionnel"] + data["produits_financier"] + data["charges_financier"])


def compute_data_availability(data):
    """
    Computes if data are available

    :param data: dictionary containing all needed values
    :return: data availability
    """

    data_available = 0
    for datum in data :
        if not math.isnan(data[datum]):
            data_available += 1

    return data_available / len(data)
