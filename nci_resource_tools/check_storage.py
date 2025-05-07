import subprocess
import pandas as pd
import re


def convert_size_to_bytes(size_str):
    """
    Converts size strings like '24.6T', '66.1K', '200.1G' to bytes (float).
    """
    size_str = size_str.strip().upper()
    if size_str.endswith('K'):
        return float(size_str[:-1]) * 1024
    elif size_str.endswith('M'):
        return float(size_str[:-1]) * 1024**2
    elif size_str.endswith('G'):
        return float(size_str[:-1]) * 1024**3
    elif size_str.endswith('T'):
        return float(size_str[:-1]) * 1024**4
    elif size_str.endswith('B'):
        return float(size_str[:-1])  # bytes already
    else:
        # If there's no suffix, assume it's in bytes
        return float(size_str)


def find_largest_users(COE_PROJECTS):
    """
    Find the largest individual users 
    """
  
    du_dict = {}
    headers = ['FILESYSTEM', 'SCAN DATE', 'PROJECT', 'GROUP', 'USER', 'SPACE USED', 'TOTAL SIZE', 'COUNT']

    for project in COE_PROJECTS:
        command = f'nci-files-report -S --project {project} --filesystem gdata'
        #print (f' INFO : Executing {command}')
        output_numeric = subprocess.run(command, capture_output=True, shell=True)
        c=output_numeric.stdout.decode('utf-8').splitlines()
        parsed_data = [re.split(r'\s{2,}|\s(?=\d)', line.strip()) for line in c]
        
        # Split the output and create a dictionary
        d = df = pd.DataFrame(parsed_data[1:], columns = headers)
        d = d.set_index('USER')
        d['TOTAL SIZE'] = d['TOTAL SIZE'].apply(convert_size_to_bytes)
        
        du_dict[project] = d

    return du_dict