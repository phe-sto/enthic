# -*- coding: utf-8 -*-
from re import compile, IGNORECASE

from enthic.utils.ok_json_response import OKJSONResponse


class SQLJSONResponseException(Exception):
    """
    Specific exception to SQLJSONResponse.
    """
    pass


class SQLJSONResponse(OKJSONResponse):
    """
    SQL result turn into JSON response via OKJSONResponse class.
    """
    no_select_re = compile(r"^.*(insert|update|drop).*$", IGNORECASE)  # SEARCH FOR UNAUTHORIZED STATEMENT

    def __init__(self, my_sql_db, sql_request, *args):
        """
        Constructor of the SQLJSONResponse class.

           :param my_sql_db: MySQL connection to database.
           :param sql_request: SQL request to execute on the base.
           :param args: Sequence A.K.A argument of the query.
           :raise SQLJSONResponseException: In case of forbidden SQL statement.
           :raise SQLJSONResponseExceptionInjection: In case of possible SQL
              injection.
        """
        ########################################################################
        # CHECK SELECT ONLY
        if SQLJSONResponse.no_select_re.match(sql_request):
            raise SQLJSONResponseException(
                "Unauthorized INSERT or UPDATE or DROP statement, SELECT only."
            )
        else:
            cur = my_sql_db.connection.cursor()
            cur.execute(sql_request % args)
            sql_results = cur.fetchall()
            cur.close()
            response_object = {}
            for sql_result in sql_results:
                if len(sql_result) % 2 != 0:
                    raise SQLJSONResponseException(
                        "SELECT fields 2 by 2 in key/value style."
                    )
                for i in range(0x64):
                    try:
                        response_object[sql_result[i * 2]] = sql_result[i * 2 + 1]
                    except IndexError:
                        break
            OKJSONResponse.__init__(self, response_object)
