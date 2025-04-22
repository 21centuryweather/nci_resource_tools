import subprocess xs
import pandas as pd
from config import *

def run_du(project):
    """
    Find the largest individual users of each projects allocation. 
    Given this takes a while, we do this in parallel.
    """

    command = f'du -s /g/data/{project}/* | sort -h'

    output = subprocess.run(command, capture_output=True, shell=True)

    c=output.stdout.decode('utf-8').splitlines()

    

    # Split the output and create a dictionary
    d = {}
    for x in c:
        d[x.split('/')[-1]] = x.split('\t')[0]

    user_storage = pd.DataFrame.from_dict(d,orient='index')