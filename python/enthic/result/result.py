# -*- coding: utf-8 -*-
"""
======================
Class Result Singleton
======================

PROGRAM BY PAPIT SASU, 2020

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""

from singleton_decorator import singleton


@singleton
class Result:
    """
    Class storing results. Only one result, therefore a singleton. Only get and
    set method no argument on initialization.
    """

    def __init__(self):
        """
        Result class constructor. Initialize attribute only.
        """
        self.avg_dir = None
        self.yearly_avg_dir = None

    @property
    def avg_dir(self):
        """
        avg_dir getter.
        """
        return self.__avg_dir

    @avg_dir.setter
    def avg_dir(self, avg_dir):
        """
        avg_dir setter.

           :param avg_dir: New avg_dir value
        """
        self.__avg_dir = avg_dir

    @property
    def yearly_avg_dir(self):
        """
        yearly_avg_dir getter.
        """
        return self.__yearly_avg_dir

    @yearly_avg_dir.setter
    def yearly_avg_dir(self, yearly_avg_dir):
        """
        yearly_avg_dir setter.

           :param yearly_avg_dir: New yearly_avg_dir tuple direct from sql result.
        """
        try:
            self.__yearly_avg_dir = dict(yearly_avg_dir)
        except TypeError:
            self.__yearly_avg_dir = None


result = Result()
