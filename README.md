# kaggle-notebook-similarity

This script checks for exact line matches between a specified Jupyter Notebook (.ipynb) and all Notebooks/Python Scripts (.py) submitted to a specified competition. Useful to review submissions and make sure they are not copied from another source.

Requires the [Kaggle API library](https://github.com/Kaggle/kaggle-api), which can be installed by running `python -m pip install kaggle` in a Command Prompt / Terminal. Make sure to also set up your access token as described in the link.

To run the script, open the containing directory and run `python main.py <competition_name> <reference_notebook_name>`.
