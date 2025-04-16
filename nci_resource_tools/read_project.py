import sys
import pandas as pd
import subprocess 
from lquota import lquota
from nci_account import nci_account

a=nci_account('gb02')

primary_keys = a.keys()

SU=a['usage']

useage_df=pd.DataFrame.from_dict(SU)

SUs_df=pd.DataFrame.from_dict(SU['users']).T

storage=a['storage']
b=lquota()

output = subprocess.run("du -hs /g/data/gb02/* | sort -h", capture_output=True, shell=True)

c=output.stdout.decode('utf-8').splitlines()

d = {}

for x in c:
    d[x.split('/')[-1]] = x.split('\t')[0]

user_storage = pd.DataFrame.from_dict(d,orient='index')