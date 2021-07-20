# -*- coding: utf-8 -*-
"""
====================================================================
====================================================================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
import csv
import io
import codecs
from enthic.database.fetch import fetchall
from enthic.utils.conversion import get_corresponding_ape_codes


def get_financial_data_by_siren(siren):
    # Get data
    sql_arguments = {"siren" : siren}
    sql_query = "SELECT * FROM `bundle` WHERE siren = %(siren)s"
    result = fetchall(sql_query, args=sql_arguments)
    return result


def get_financial_data_by_ape(real_ape):
    # Fetch all score of a given type, and for specified economic sector (APE)
    ape_stringlist = get_corresponding_ape_codes(real_ape)
    sql_args = {"ape_list": tuple(ape_stringlist)}
    sql_query = """SELECT bundle.siren, declaration, accountability, bundle, amount
                     FROM `bundle`
                     INNER JOIN identity ON bundle.siren = identity.siren
                     WHERE identity.ape IN %(ape_list)s"""
    result = fetchall(sql_query, args=sql_args)
    return result

def convert_to_csv_stream(data):
    # Open bytes stream
    stream = io.BytesIO()
    stream_writer = codecs.getwriter('utf-8')
    # Convert to String stream
    buffer = stream_writer(stream)
    # Write data
    writer = csv.writer(buffer, delimiter=';')
    writer.writerow(["siren", "annee", "type de comptabilite", "code compta", "valeur"])
    writer.writerows(data)

    # Send data to client
    stream.seek(0)
    return stream
