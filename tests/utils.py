import os
import yaml

def load_regimen():
    regimen_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'regimen.yml',
    )

    with open(regimen_path, 'r') as f:
        regimen_data = yaml.load(f)

    return regimen_data
