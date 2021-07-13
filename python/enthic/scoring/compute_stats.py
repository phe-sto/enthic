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
from enthic.scoring.tree_french_income_statement import TREE_VIEW


def convert_data_to_tree(raw_data):
    """
    Returns given data as a tree like "tree_french_income_statement"

        :param raw_data : data as enthic API returns it
        :return: given data as a tree
    """
    new_tree = TREE_VIEW
    recursive_fill_tree(new_tree, raw_data)
    return new_tree


def recursive_fill_tree(tree_item, raw_data):
    """
    Fill the given tree_item with data from raw_data
        :param tree_item : item to fill, and its children
        :param raw_data : data in Enthic API format
    """

    # Begin to fill children if there are children
    if 'children' in tree_item:
        for child_name in tree_item["children"]:
            recursive_fill_tree(tree_item["children"][child_name], raw_data)

    # Find corresponding value from raw_data to add to tree_item
    for code in raw_data:
        if code in tree_item["codeLiasses"]:
            tree_item['data'] = raw_data[code]
            tree_item['data']["status"] = "official"
            tree_item['data']['code'] = code
            del raw_data[code]
            break

def check_tree_data(tree_item):
    """
    Check and complete data in the given tree_item

        :param tree_item : item of a tree like the one in "tree_french_income_statement.py" file,
           where every child should have been filled with data, which consist of a new member like :
            data = {
              code : string,
              description : string,
              value : integer,
              status : "official"
            }
    """
    if 'data' not in tree_item:
        tree_item['data'] = {
            "code": tree_item['codeLiasses'],
            "description": "non fourni",
            "value": float('nan'),
            "status": "missing"}

    if "sign" not in tree_item:
        tree_item['sign'] = 1

    if "children" not in tree_item:
        return

    for child_name in tree_item['children']:
        check_tree_data(tree_item['children'][child_name])

    # Accepted amount of difference when checking parent value against it's children
    relative_error = 0.005
    absolute_error = 10

    # Compute ourself tree_item's value from its children
    computed_sum = 0  # Result from official children's value
    computed_sum_from_computed = 0  # Result from computed children's value
    computed_sum_without_sign = 0  # Result by adding all children (no substraction)
    child_missing_count = 0  # Count of child without value officially given
    for child_name in tree_item['children']:
        child = tree_item['children'][child_name]
        if math.isnan(child['data']['value']):
            child_missing_count += 1
            if "computedValue" in child['data']:
                computed_sum_from_computed += child['data']['computedValue'] * child['sign']
        else:
            computed_sum += child['data']['value'] * child['sign']
            computed_sum_from_computed += child['data']['value'] * child['sign']
            computed_sum_without_sign += child['data']['value']

    if not math.isnan(tree_item['data']['value']):
        value = tree_item['data']['value']
        if value == 0:
            value = 0.01
        # If official value match computed value from official children's value with less than 0.5% error
        if (abs((computed_sum - value) / value) < relative_error
                or abs(computed_sum - value) < absolute_error):
            tree_item['data']['status'] = "checked"
            # Fix children values if needed
            if child_missing_count > 0:
                for child_name in tree_item['children']:
                    set_to_zero_computed(tree_item['children'][child_name])

        # If official value match computed value from computed children's value with less than 0.5% error
        elif (abs((computed_sum_from_computed - value) / value) < relative_error
              or abs(computed_sum_from_computed - value) < absolute_error):
            tree_item['data']['status'] = "checked"
            # Fix children values if needed
            for child_name in tree_item['children']:
                child_data = tree_item['children'][child_name]['data']
                if math.isnan(child_data['value']):
                    child_data['status'] = "computed"
                    if 'computedValue' in child_data:
                        child_data['value'] = child_data['computedValue']
                    else:
                        child_data['value'] = 0

            computed_sum = computed_sum_from_computed
        # If there is only on value missing from children, set this child's value equal to the computed difference
        elif child_missing_count == 1:
            for child_name in tree_item['children']:
                child_data = tree_item['children'][child_name]['data']
                if math.isnan(child_data["value"]):
                    child_data['computedValue'] = (value - computed_sum) / child['sign']
                    child_data['value'] = child_data['computedValue']
                    child_data['status'] = "computed"
                    tree_item['data']['status'] = "checked"
                    break

        # If official value match computed value by adding all children's value (no substraction) with less than 0.5% error
        elif abs((computed_sum_without_sign - value) / value) < relative_error or abs(computed_sum_without_sign - value) < absolute_error:
            tree_item['data']['status'] = "checked"
            # Fix children sign and/or set to zero missing values if any
            for child_name in tree_item['children']:
                flip_sign(tree_item['children'][child_name])
                set_to_zero_computed(tree_item['children'][child_name])
        elif abs((computed_sum - value) / value) > 100:
            tree_item['data']['status'] = "error"
        else:
            tree_item['data']['status'] = "error"

    if computed_sum != tree_item['data']['value']:
        tree_item['data']['computedValue'] = computed_sum_from_computed


def set_to_zero_computed(tree_item):
    """
    set value of given item and it's children to zero when it hasn't another value

        :param tree_item : item to set to zero
    """
    if math.isnan(tree_item['data']['value']) and ('computedValue' not in tree_item['data'] or tree_item['data']['computedValue'] == 0):
        tree_item['data']['value'] = 0
        tree_item['data']['status'] = "computed"
        if 'children' in tree_item:
            for child_name in tree_item['children']:
                set_to_zero_computed(tree_item['children'][child_name])


def flip_sign(item):
    """
    Flip sign of given item

        :param item : item to flip
    """
    if item['sign'] == -1:
        item['data']['value'] = -item['data']['value']
        item['data']['status'] = "signFlipped"

def gather_data_to_compute(tree, raw):
    root = tree['children']
    resultat_avant_impot = root['ResultatAvantImpot']['children']
    result = {
        "participation" : root['ParticipationSalariesAuxResultats']['data']['value'],
        "impot" : root['ImpotsSurLesBenefices']['data']['value'],
        "resultat_exceptionnel" : root['ResultatExceptionnel']['data']['value'],
        "produits_exceptionnel" : root['ResultatExceptionnel']['children']['ProduitsExceptionnels']['data']['value'],
        "charges_exceptionnel" : root['ResultatExceptionnel']['children']['ChargesExceptionnelles']['data']['value'],
        "resultat_financier" : resultat_avant_impot['ResultatFinancier']['data']['value'],
        "produits_financier" : resultat_avant_impot['ResultatFinancier']['children']['ProduitsFinanciers']['data']['value'],
        "charges_financier" : resultat_avant_impot['ResultatFinancier']['children']['ChargesFinancieres']['data']['value'],
        "resultat_exploitation" : resultat_avant_impot['ResultatExploitation']['data']['value'],
        "produits_exploitation" : resultat_avant_impot['ResultatExploitation']['children']['ProduitsExploitation']['data']['value'],
        "charges_exploitation" : resultat_avant_impot['ResultatExploitation']['children']['ChargesExploitation']['data']['value'],
    }

    charges = resultat_avant_impot['ResultatExploitation']['children']['ChargesExploitation']

    result["charges"] = charges['data']['value']
    result["cotisations_sociales"] = charges['children']['ChargesSociales']['data']['value']
    result["salaires"] = charges['children']['SalairesEtTraitements']['data']['value']

    if "YP" in raw :
        result["effectifs"] = raw["YP"]["value"]
    elif "376" in raw :
        result["effectifs"] = raw["376"]["value"]
    else:
        result["effectifs"] = float('nan')

    return result
