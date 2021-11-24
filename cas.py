#! /usr/bin/env python3
"""
# Created by Radek
"""
import datetime


class Cas:
    """vrací aktuální čas a datum
    # Použití:
    # print(Cas()) --> 07:49 17.06.2021
    """

    def __init__(self):
        self.__cas: datetime = datetime.datetime.now()

    def __repr__(self):
        return "{:02}:{:02} {:02}.{:02}.{}".format(self.__cas.hour,
                                                   self.__cas.minute,
                                                   self.__cas.day,
                                                   self.__cas.month,
                                                   self.__cas.year)
