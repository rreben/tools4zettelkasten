# app.py

from . import cli
import logging


class ZettelkastenTools:

    @staticmethod
    def run():
        logging.basicConfig(level=logging.DEBUG)
        cli.messages()
