import sys
import pandas as pd
import subprocess 
from lquota import lquota
from nci_account import nci_account
from nqstat import nqstat

a=nci_account('gb02')

primary_keys = a.keys()

SU=a['usage']

useage_df=pd.DataFrame.from_dict(usage)

SUs_df=pd.DataFrame.from_dict(usage['users'])

storage=a['storage']
b=lquota()

output = subprocess.run("du -hs /g/data/gb02/* | sort -h", capture_output=True, shell=True)

c=output.stdout.decode('utf-8').splitlines()

d = {}

for x in c:
    d[x.split('\t')[0]] = x.split('\t')[1]