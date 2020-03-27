# -*- coding: utf-8 -*-

"""
====================================================================
Decorator inserting data from the incoming request in another thread
====================================================================
"""
from functools import wraps
from threading import Thread


def insert(*args):
    """
    Insert data from the request in the request table.

       :param args: A tuple, first element is the database, second is the
          request data.
    """
    try:
        if args[1].get('data') and args[1]['data'] != b'':
            request = """INSERT INTO request VALUES ("%s", "%s", "%s", "%s", "%s", "%s", CURRENT_TIMESTAMP)""" % \
                      (args[1]['environ']['REQUEST_METHOD'],
                       args[1]['environ']['PATH_INFO'],
                       args[1]['environ']['REMOTE_ADDR'],
                       args[1]['environ']['REMOTE_PORT'],
                       args[1]['environ']['HTTP_USER_AGENT'],
                       str(args[1]['data']).replace('"', "'"))
        elif args[1]['view_args'] != {}:
            request = """INSERT INTO request VALUES ("%s", "%s", "%s", "%s", "%s", "%s", CURRENT_TIMESTAMP)""" % \
                      (args[1]['environ']['REQUEST_METHOD'],
                       args[1]['environ']['PATH_INFO'],
                       args[1]['environ']['REMOTE_ADDR'],
                       args[1]['environ']['REMOTE_PORT'],
                       args[1]['environ']['HTTP_USER_AGENT'],
                       str(args[1]['view_args']).replace('"', "'"))
        else:
            request = """INSERT INTO request VALUES ("%s", "%s", "%s", "%s", "%s", NULL, CURRENT_TIMESTAMP)""" % \
                      (args[1]['environ']['REQUEST_METHOD'],
                       args[1]['environ']['PATH_INFO'],
                       args[1]['environ']['REMOTE_ADDR'],
                       args[1]['environ']['REMOTE_PORT'],
                       args[1]['environ']['HTTP_USER_AGENT'])
    except KeyError:
        pass
    with args[0].app.app_context():
        cur = args[0].connection.cursor()
        cur.execute(request)
        cur.close()
        args[0].connection.commit()


def insert_request(my_sql_db, request):
    """
    Decorator insert request data in database for further analysis using
    arguments objects of the function.

       :param my_sql_db: The database where the request data is to be inserted.
       :param request: The request object.
       :return: The function decorated.
    """

    def insert_request_func(func):
        """
        Decorator inserting relevant request data timestamped.

           :param func: Function decorated.
           :return: The function decorated.
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper to the insert in another thread to save time.

               :param args: Possible arguments.
               :param kwargs: Possible keyword argument.
               :return: The function decorated.
            """
            Thread(target=insert, args=(my_sql_db, request.__dict__)).start()

            return func(*args, **kwargs)

        return wrapper

    return insert_request_func
