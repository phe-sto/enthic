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
from enthic.tree_french_compte_de_resultat import TREE_VIEW


def convert_data_to_tree(raw_data):
    """
    Returns given data as a tree like "tree_french_compte_de_resultat"

        :param raw_data : data as enthic API returns it
        :return: given data as a tree
    """
    new_tree = TREE_VIEW
    recursive_fill_tree(new_tree, raw_data)
    return new_tree


def recursive_fill_tree(tree_item, raw_data):
    """
    Fill the given item with data from raw_data
        :param tree_item : item to fill, and its children
        :param raw_data : data in Enthic API format
    """

    # Begin to fill children if there are children
    if 'children' in tree_item:
        for child_name in tree_item["children"]:
            recursive_fill_tree(tree_item["children"][child_name], raw_data)

    # Find corresponding value from raw_data to add to tree_item
    i = 0
    while i < len(raw_data):
        for code in raw_data[i]:
            if code in tree_item["codeLiasses"]:
                tree_item['data'] = raw_data[i][code]
                tree_item['data']["status"] = "official"
                tree_item['data']['code'] = code
                del raw_data[i]
                break
        i = i + 1


def check_tree_data(tree_item):
    """
    Check and complete data in the given tree_item

        :param tree_item : item of a tree like the one in "tree_french_compte_de_resultat.py" file,
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


def compute_annual_share_score(tree):
    """
    Computes the share score of given data

        :param tree: data from which compute the score
    """
    # Retrieve needed values
    participation = tree['children']['ParticipationSalariesAuxResultats']['data']['value']
    impot = tree['children']['ImpotsSurLesBenefices']['data']['value']
    resultat_financier = tree['children']['ResultatExceptionnel']['data']['value']
    resultat_exceptionnel = tree['children']['ResultatAvantImpot']['children']['ResultatFinancier']['data']['value']
    resultat_exploitation = tree['children']['ResultatAvantImpot']['children']['ResultatExploitation']['data']['value']

    # If any values unknown, cannot compute score
    if any(math.isnan(value) for value in [participation, impot, resultat_financier, resultat_exceptionnel, resultat_exploitation]):
        return float('nan')

    # Compute score if possible
    shared_part = participation + impot
    resultat_capitaux = resultat_financier + resultat_exceptionnel
    if shared_part >= 0:
        if resultat_capitaux <= 0 and resultat_exploitation != 0:
            return shared_part / resultat_exploitation

    return float('nan')


def compute_salary_scores(tree):
    """
    Computes some scores related to salary
        :param tree: data from which compute the score
    """
    charges = tree['children']['ResultatAvantImpot']['children']['ResultatExploitation']['children']['ChargesExploitation']

    cotisations_sociales = charges['children']['ChargesSociales']['data']['value']
    salaires = charges['children']['SalairesEtTraitements']['data']['value']

    salary_level = float('nan')
    salary_percent = float('nan')
    if not any(math.isnan(value) for value in [cotisations_sociales, salaires]) and salaires > 0:
        salary_level = cotisations_sociales / salaires
        if not math.isnan(charges['data']['value']):
            salary_percent = (cotisations_sociales + salaires) / charges['data']['value']

    return salary_level, salary_percent


def compute_company_statistics(company_data):
    """
    Computes some statistics and scores from the given company's data
        :param company_data: data from which compute statistics and score
    """
    result_list = []
    for one_year_data in company_data.json['declarations']:
        financial_data = one_year_data['financial_data']
        tree = convert_data_to_tree(financial_data)
        check_tree_data(tree)
        share_score = compute_annual_share_score(tree)
        salary_level, salary_percent = compute_salary_scores(tree)
        result_list.append({"year" : one_year_data['declaration']['value'],
                            "share_score" : share_score,
                            "salary_level" : salary_level,
                            "salary_percent" : salary_percent})

    return result_list
