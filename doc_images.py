###############################################################################
# DoC Images
# @author: derricw
# Dec 6 2017
###############################################################################

from camstim.change import DoCTask, DoCImageStimulus, DoCTrialGenerator
from camstim import Window, Warp
import logging

# Configure logging level
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set up display window (This may become unnecessary in future release)
window = Window(fullscr=True, screen=1, monitor='Gamma1.Luminance50', warp=Warp.Spherical)

# Set up Task
params = {}

f = DoCTask(window=window,
            auto_update=True,
            params=params)

t = DoCTrialGenerator(cfg=f.params) # This also subject to change
f.set_trial_generator(t)

# Set up our DoC stimulus
img_data = "//allen/aibs/mpe/Software/stimulus_files/nimages_0_20170714.zip"
obj = DoCImageStimulus(window,
                       image_set=img_data,
                       sampling="random")

# Add our DoC stimulus to the Task
f.set_stimulus(obj, "images")

# Run it
f.start()
