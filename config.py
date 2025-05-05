from pathlib import Path
import os

user_id = os.environ['USER']

USE_DU = False
COE_PROJECTS = ['gb02','fy29','if69','ng72','su28']
TMPDIR = Path('/scratch/gb02') / user_id / 'tmp'