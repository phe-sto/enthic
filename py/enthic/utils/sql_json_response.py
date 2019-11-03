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

    def __init__(self, my_sql_db, sql_request, *keys):
        """
        Constructor of the SQLJSONResponse class.
           :param my_sql_db: MySQL connection to database.
           :param sql_request: SQL request to execute on the base.
           :param keys: Keys of JSON to create.
           :raise SQLJSONResponseException: In case of Unauthorized SQL request.
        """
        if SQLJSONResponse.select_re.match(sql_request):
            raise SQLJSONResponseException("Unauthorized INSERT or UPDATE statement")
        else:
            cur = my_sql_db.connection.cursor()
            cur.execute(sql_request)
            sql_results = cur.fetchall()
            response_list = []  # TUPLE CANNOT ASSIGN NEED A LIST TO MODIFY RESPONSE
            for sql_result in sql_results:
                response_list.append(dict(zip(keys, sql_result)))  # TUPLE TO DICTIONARY
            OKJSONResponse.__init__(self, response_list)
