# -*- coding: utf-8 -*-
"""
===================================
Useful queries on the MySQL database
===================================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""

from enthic.database.fetch import fetchall


def pre_cast_integer(probe):
    """
    A str that cannot be casted as integer is set to 0 in MySQL. This Function
    return None (NULL SQL equivalent) if not castable.

       :param probe: SQL probe to cast or not.
    """
    return str(probe) if probe.__class__ is int else probe if probe.isnumeric() is True else None


def query_companies(probe, limit, ape_code=[], offset=0):
    """
    List the result of the search in the database.

       :param probe: A string to match.
       :param limit: Integer, the limit of result to return.
       :param ape_code: List of APE codes to match or None
       :param offset: Integer, offset of the select SQL request.
    """
    sql_query_select_part = "SELECT siren, denomination, ape, postal_code, town FROM identity"
    sql_query_count = "SELECT COUNT(*) FROM identity"

    sql_query_probe_condition = '1'
    sql_arguments = {}
    if probe:
        sql_query_probe_condition = "denomination LIKE %(probe)s OR MATCH(denomination) AGAINST (%(probe)s IN NATURAL LANGUAGE MODE)"
        sql_arguments['probe'] = str(probe) + '%'
        # If probe is an interger, it might be a siren number, so we add this condition to the query
        if pre_cast_integer(probe):
            sql_query_probe_condition = "siren = %(siren)s OR " + sql_query_probe_condition
            sql_arguments['siren'] = int(probe)

    sql_query_ape_code_condition = "1"
    if len(ape_code) > 1:
        sql_query_ape_code_condition = "ape IN {}".format(tuple(ape_code))
    elif len(ape_code) == 1:
        sql_query_ape_code_condition = "ape = {}".format(ape_code[0])

    sql_query_condition = " WHERE (" + sql_query_probe_condition + ") AND (" + sql_query_ape_code_condition + ") "
    sql_query_limit_and_offset = " LIMIT {} OFFSET {};".format(limit, offset)

    with application.app_context():
        count = fetchall(sql_query_count + sql_query_condition, args=sql_arguments)
        companies = fetchall(sql_query_select_part + sql_query_condition + sql_query_limit_and_offset, args=sql_arguments)

    return (count[0][0], companies)


def query_siren(first_letters):
    """
    Get siren of companies whose denomination starts with the given first letters

        :param first_letters: A string to match companies name.

        :return: list of siren number of companies found
    """
    first_letters += '%'
    with application.app_context():
        siren_list = fetchall("""SELECT siren
                        FROM identity
                        WHERE denomination LIKE %s LIMIT 1000000""", (first_letters,))

    return siren_list
