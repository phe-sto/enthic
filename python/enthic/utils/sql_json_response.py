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
    select_re = compile(r"^.*(insert|update).*$", IGNORECASE)  # SEARCH FOR UNAUTHORIZED STATEMENT

    def __init__(self, my_sql_db, sql_request):
        """
        Constructor of the SQLJSONResponse class.
           :param my_sql_db: MySQL connection to database.
           :param sql_request: SQL request to execute on the base.
           :raise SQLJSONResponseException: In case of Unauthorized SQL request.
        """
        if SQLJSONResponse.select_re.match(sql_request):
            raise SQLJSONResponseException("Unauthorized INSERT or UPDATE statement")
        else:
            cur = my_sql_db.connection.cursor()
            cur.execute(sql_request)
            sql_results = cur.fetchall()
            response_object = {}
            for sql_result in sql_results:
                for i in range(0x64):
                    try:
                        response_object[sql_result[i * 2]] = sql_result[i * 2 + 1]
                    except IndexError:
                        break
            OKJSONResponse.__init__(self, response_object)
