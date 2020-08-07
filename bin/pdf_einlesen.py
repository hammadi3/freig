import logging

import pandas as pd
import pdfplumber
import click

log = logging.getLogger(__name__)


def freigabe_einlesen():
    filename = 'RC42-20-0225.pdf'
    filename_encoded = r'\{}'.format(filename)
    path = r'C:\Users\z003vvwd\Desktop{}'.format(filename_encoded)

    with pdfplumber.open(path) as pdf:
        text = [page.extract_text() for page in pdf.pages]
        table = [page.extract_table() for page in pdf.pages]
        return text, table


if __name__ == "__main__":
    try:
        click.echo(freigabe_einlesen())
    except Exception as err:
        click.echo("Failed!", err=True)
        click.echo(str(err), err=True)
        exit(1)
