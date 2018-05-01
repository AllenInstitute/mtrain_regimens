###############################################################################
# DoC Gratings
# @author: derricw
# Dec 6 2017
###############################################################################

from camstim.change import DoCTask, DoCGratingStimulus, DoCTrialGenerator
from camstim import Window, Warp
import logging

# Configure logging level
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set up display window
window = Window(fullscr=True, screen=1, monitor='Gamma1.Luminance50', warp=Warp.Spherical)

# Set up Task
params = {}

f = DoCTask(window=window,
            auto_update=True,
            params=params)

t = DoCTrialGenerator(cfg=f.params)  # This also subject to change
f.set_trial_generator(t)

# Set up our DoC stimulus
obj = DoCGratingStimulus(window,
                         tex='sqr',
                         units='deg',
                         size=(300, 300),
                         sf=0.04,)
                         
obj.add_stimulus_group("group0", 'Ori', [0])
obj.add_stimulus_group("group1", 'Ori', [90])

# Add our DoC stimulus to the Task
f.set_stimulus(obj, "grating")

# Run it
f.start()
