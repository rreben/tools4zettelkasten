# app.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license


from . import cli
import logging


class ZettelkastenTools:

    @staticmethod
    def run():
        logging.basicConfig(level=logging.DEBUG)
        cli.messages()
