# mtrain_regimens

This repository contains training regimens for the Visual Behavior project.

- `regimen.yml` - This file specifies a full training regimen.
- `scripts/` - This folder contains useful scripts.
- `tests/` - This folder contains test scripts to help ensure that the regimen is properly formatted for mtrain and can run in production.

## v2 scripts
camstim v2 scripts need to be installed locally in order to work. If a referenced script is just a filename and is postfixed with _v2 it is likely a v2 script and hopefully exists [here](https://github.com/AllenInstitute/camstim-scripts/tree/master/v2) with the same name.

## Regimen names and semantic versioning

For the Visual Behavior pipeline, we use a naming convention of `{project_name}_{task_name}_{semantic_version}` for regimens.

- `project_name` is the name of the project this regimen is associated with. In this case, `VisualBehavior`.
- `task_name` is the name of the task that the regimen implements, e.g. `Task1A`
- `semantic_version` is a version of the regimen which conforms to [Semantic Versioning](https://semver.org/spec/v2.0.0.html), adapted somewhat from software versioning.

Under semantic versioning, a "major revision" occurs when we make changes that are NOT backward compatible. For the purposes of mtrain regimens, this is most appropriate whenever we make substantial changes to stage parameters, transition logic, and/or stage names such that there is not a clear mapping between every stage in the last version and the new version of the regimen. Changes in stage names here are a clear change that warrant a major revision, since any code downstream that relies on stage names to measure time on each stage and time to reach imaging criteria, for example, will break with the new stage names. Similarly, we can't just "migrate all mice to the the new regimen" without giving him a mapping of how the old stage names correspond to these stage names.

A minor revision might be e.g. keeping the stage names but tweaking timing parameters or adding the countdown to behavior sessions. It's clear how to migrate a mouse from 0.2.x to 0.3.x because there is correspondence in the stage names. And while the parameters might have changed, they didn't change the "essence" of the stage.

Patch revisions (v0.3.1) occur when a bug is identified in a regimen and fixed. All the stage names stay the same & it's clear how to migrate a mouse between the stages. These are instances where we know that we want every mouse on v0.x.0 to move to v0.x.1. Moreover, we can safely assume that all mice on a given minor revision should be running on the latest patch revision. As soon as we know that we don't need to roll back, v0.x.0 is considered deprecated and can be de-activated in the mtrain service.


## Viewing a regimen

To easily view a regimen as a JSON, the following script will print the regiment to the console.

```
python scripts/make_regimen_json.py
```

You can also pass in a specific stage to print with the `--stage` keyword.

```
python scripts/make_regimen_json.py --stage=TRAINING_1_gratings
```

If you wish to create a json file (e.g. for easy viewing in Atom or Sublime), you can do the following:

```
python scripts/make_regimen_json.py > regimen.json
```


## Updating a regimen

1. Create a branch.
2. Change things in `regimen.yml`.
3. Use `python scripts/make_script_and_params.py` to generate a script and json file to test manually (see below).
4. Repeat 2 & 3 until you are happy with the regimen.
3. Run `make test` to ensure that the regimen is conformant.
4. Update the name of the regimen, using semantic versioning.
6. Add an entry to the CHANGELOG.
7. Commit your changes & push them.
8. Open a Pull Request & get someone to review the changes.
9. After review and merge, tag the commit with a repo tag that matches the name from #4
10. Run scripts/upload_regimen.py (use the dry-run flag, to run the upload script, with all functionalty except the actual upload.
``` Python
python upload_regimen.py -r <tag name here> --dry-run=True
```

## Updating the script

Scripts can live on any URL. We are using the stash repo at http://stash.corp.alleninstitute.org/projects/VB/repos/visual_behavior_scripts/browse

## Updating criteria

Criteria are defined as functions in mtrain. This requires changes to mtrain itself, which needs to be coordinated with Nicholas Cain in Technology.

## Manually testing a regimen

The script `scripts/make_script_and_params.py` can be used to generate a script and json file like the camstim agent expects for any stage in the regimen.

### Generating the script and json file

These steps can happen on any computer.

Install [click](https://click.palletsprojects.com/en/7.x/) if you don't already have it.

``` Bash
pip install click
```

Run `scripts/make_script_and_params.py`, passing in the path to the regimen yaml file as a keyword argument.

``` Bash
cd utilities
python make_script_and_params.py --regimen_yml ../regimen.yml --stage OPHYS_1_images_a
```

If you do not pass a stage, you will be prompted to select one. By default, it will drop the script and json for this stage in your current working directory. You can also customize where to place them. See the help to understand other parameters.

``` Bash
python make_script_and_params.py --help
```

### Running the script and json file

On the rig where you want to test the scripts, make sure you have the latest version of camstim installed: http://aibspi.corp.alleninstitute.org/braintv/camstim/

``` cmd
conda create -n camstim python=2
activate camstim
git clone http://aibspi.corp.alleninstitute.org/braintv/camstim.git
cd camstim
pip install -e ./
```

Run the script that was generated, passing in the json file as the sole argument.

```
activate camstim
python 181022110055_OPHYS_1_images_a.py 181022110055_OPHYS_1_images_a.json
```

## Adding the regimen to the mtrain service

Talk to Nick

## Viewing mice currently in mtrain


```
python scripts/mtrain_view_mice.py
```

## Migrating mice to new regimen

Do a dry run (a fake username and password is fine for this)

```
python scripts/mtrain_bulk_migration.py --source OldRegimenName --target NewRegimen
```

Does everything look right?

![Make it so](https://media.giphy.com/media/VLoN2iW8ii3wA/giphy.gif)

```
python scripts/mtrain_bulk_migration.py --source OldRegimenName --target NewRegimen --dry-run False
```

## Using pre-commit hooks

Create a symbolic link from pre-commit to the .git/hooks folder to ensure that the md5 of the files are consistent with those stated in teh repos
