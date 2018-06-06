#!/usr/bin/env python

import os
import click
import yaml
import json
import requests
import datetime as dt


@click.command()
@click.option('--regimen_yml', help='Path to regimen file.')
@click.option('--stage', default=None, help='The stage to generate.')
@click.option('--script_out', default=None, help='Where to write the script.')
@click.option('--params_out', default=None, help='Where to write the parameters.')
@click.option('--mouse', default=None, help='Mouse directory to put it in.')
def hello(regimen_yml, stage, script_out, params_out, mouse):

    if mouse is not None:
        mouse_dir = '/allen/programs/braintv/workgroups/neuralcoding/Behavior/Data/{}'
        params_out = os.path.join(mouse_dir.format(mouse),'adjustment')
        script_out = os.path.join(mouse_dir.format(mouse),'scriptlog')

    with open(regimen_yml, 'r') as f:
        regimen = yaml.load(f)

    # print regimen.keys()
    # regimen =
    if stage is None:
        print '\n'.join(regimen['stages'].keys())
        stage = click.prompt('please select a stage', type=str)

    print stage

    script_url = regimen['stages'][stage]['script']
    params = regimen['stages'][stage]['parameters']


    timestamp = dt.datetime.now().strftime('%y%m%d%H%M%S')

    r = requests.get(script_url, allow_redirects=True)
    if script_out is None:
        script_out = os.getcwd()
    script_dest = os.path.join(script_out,'{}_{}.py'.format(timestamp,stage))
    with open(script_dest,'wb') as f:
        f.write(r.content)

    if params_out is None:
        params_out = os.getcwd()
    params_dest = os.path.join(params_out,'{}_{}.json'.format(timestamp,stage))
    with open(params_dest,'wb') as f:
        json.dump(
            params,
            f,
            sort_keys=True,
            indent=4
        )

if __name__ == '__main__':
    hello()
