# Noisy monitor diagnosis

This package helps users diagnose and fix noisy monitors in WhyLabs. This workflow has the following steps: 
* Identify the noisiest monitors for a selected organization and dataset, and choose one to diagnose.
* Identify the noisiest segment of the monitor to be the diagnostic segment.
* Within that segment, identify the noisiest columns.
* Identify the conditions contributing to the noise in the diagnostic segment and noisiest columns.
* Determine the appropriate action to take to fix the conditions contributing to the noise.
* Apply the actions to the monitor.

Most of the above steps are automated by the monitor diagnoser for common noise conditions, although in some cases the 
diagnoser may not match the dataset to any known conditions. Users will also usually need to manually consider the 
most appropriate action to take to fix the monitor. A recommender is provided to suggest reasonable actions 
and to automate some of the basic actions. We are happy to work with you to improve the diagnoser in such cases.

See [diagnoser.ipynb](/examples/example_notebooks/diagnoser.ipynb) for an end-to-end example of identifying noisy
monitors, diagnosing the conditions contributing to noise, and getting recommendations for fixing them.

See [customized_diagnoser.ipynb](/examples/example_notebooks/customized_diagnoser.ipynb) for an example of how to 
customize the diagnosis for your specific needs.

