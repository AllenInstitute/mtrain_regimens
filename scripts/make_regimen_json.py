#!/usr/bin/env python
from __future__ import print_function
import os
import click
import yaml
import json


@click.command()
@click.option('--regimen_yml', default=None, help='Path to regimen file.')
@click.option('--stage', default=None, help='The stage to dump.')
def dump_regimen(regimen_yml, stage):

    if regimen_yml is None:
        dirname = os.path.dirname(__file__)
        regimen_yml = os.path.join(dirname,'..','regimen.yml')

    with open(regimen_yml, 'r') as f:
        regimen = yaml.load(f)

    if stage is None:
        regimen = {k: regimen[k] for k in ('name', 'stages', 'transitions')}
    else:
        regimen = regimen['stages'][stage]

    regimen = json.dumps(
        regimen,
        sort_keys=True,
        indent=4
    )
    print(regimen)


if __name__ == '__main__':
    dump_regimen()
