# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [VisualBehavior_Task1A_v1.0.0] - 2018-10-22

### Added
- Added countdown stimulus to start of each ophys behavior session.
- Added fingerprint stimulus to end of each ophys behavior session.
- Added "omitted flashes" to ophys sessions with 5% omission probability.

### Changed
- Disabled warmup trials on physiology stages and "handoff ready" stage of training.
- Disabled automatic progression between physiology stages.
- Revised naming conventions of stages. Training stages are prefaced with "TRAINING_" and physiology sessions are prefaced with "OPHYS_".
- Modified ophys stimulus sequence to interleave passive sessions between active of the same image set.
- Changed ophys stage names to be all unique (0-7).
- Switched ophys stage B to use image_set_d_parameters instead of image_set_c_parameters.

## [VisualBehavior_Task1A_v0.3.1] - 2018-09-05

### Changed
- Fixed error in file paths for physiology image sets.

## [VisualBehavior_Task1A_v0.3.0] - 2018-08-16

### Changed
- Uses geometric sampling on stages with flashed images or gratings.
- Ends trials relative to end of response window rather than trial start.
- Expand start_stop_padding to 300 seconds.
- Disables `min_no_lick_time`.

## [VisualBehavior_Task1A_v0.2.4] - 2018-08-08

### Added
- Adds habituation stage.

## [VisualBehavior_Task1A_v0.2.3] - 2018-07-26

### Added
- Adds 300ms timeout.

## [VisualBehavior_Task1A_v0.2.2] - 2018-07-09

### Changed
- Fixes misnamed condition to leave "0_gratings_autorewards_15min" stage.

## [VisualBehavior_Task1A_v0.2.1] - 2018-07-09

### Changed
- Fixes image file paths for Windows.

## [VisualBehavior_Task1A_v0.2.0] - 2018-06-11

### Changed
- Major refactor of planned training for production.


[VisualBehavior_Task1A_v1.0.0]: https://github.com/AllenInstitute/mtrain_regimens/compare/VisualBehavior_Task1A_v0.3.1...VisualBehavior_Task1A_v1.0.0
[VisualBehavior_Task1A_v0.3.1]: https://github.com/AllenInstitute/mtrain_regimens/compare/VisualBehavior_Task1A_v0.3.0...VisualBehavior_Task1A_v0.3.1
[VisualBehavior_Task1A_v0.3.0]: https://github.com/AllenInstitute/mtrain_regimens/compare/VisualBehavior_Task1A_v0.2.4...VisualBehavior_Task1A_v0.3.0
[VisualBehavior_Task1A_v0.2.4]: https://github.com/AllenInstitute/mtrain_regimens/compare/VisualBehavior_Task1A_v0.2.3...VisualBehavior_Task1A_v0.2.4
[VisualBehavior_Task1A_v0.2.3]: https://github.com/AllenInstitute/mtrain_regimens/compare/VisualBehavior_Task1A_v0.2.2...VisualBehavior_Task1A_v0.2.3
[VisualBehavior_Task1A_v0.2.2]: https://github.com/AllenInstitute/mtrain_regimens/compare/VisualBehavior_Task1A_v0.2.1...VisualBehavior_Task1A_v0.2.2
[VisualBehavior_Task1A_v0.2.1]: https://github.com/AllenInstitute/mtrain_regimens/compare/VisualBehavior_Task1A_v0.2.0...VisualBehavior_Task1A_v0.2.1
[VisualBehavior_Task1A_v0.2.0]: https://github.com/AllenInstitute/mtrain_regimens/compare/v0.1.3...VisualBehavior_Task1A_v0.2.0
