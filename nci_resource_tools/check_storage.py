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

def convert_bytes_to_size(size_bytes):
    for unit, factor in (('T', 1024**4), ('G', 1024**3),
                         ('M', 1024**2), ('K', 1024)):
        if size_bytes >= factor:
            return f'{size_bytes / factor:.1f}{unit}'
    return f'{size_bytes:.0f}B'

def find_largest_users(COE_PROJECTS, filesystem='gdata', convert_to_bytes=True):
    """
    Find the largest individual users 
    """
  
    du_dict = {}
    headers = ['FILESYSTEM', 'SCAN DATE', 'PROJECT', 'GROUP', 'USER', 'SPACE USED', 'TOTAL SIZE', 'COUNT']

    for project in COE_PROJECTS:
        command = f'nci-files-report -S --project {project} --filesystem {filesystem}'
        #print (f' INFO : Executing {command}')
        output_numeric = subprocess.run(command, capture_output=True, shell=True)
        c=output_numeric.stdout.decode('utf-8').splitlines()
        parsed_data = [re.split(r'\s{2,}|\s(?=\d)', line.strip()) for line in c]
        
        # Split the output and create a dictionary
        d = df = pd.DataFrame(parsed_data[1:], columns = headers)
        d = d.set_index('USER')

        if convert_to_bytes:
            d['TOTAL SIZE'] = d['TOTAL SIZE'].apply(convert_size_to_bytes)
        
        du_dict[project] = d

    return du_dict



def load_storage_allocations(DATA_PATH):
    allocation_storage = pd.read_csv( DATA_PATH / 'storage_request.csv',skipinitialspace=True)
    allocation_storage['end_date'] = pd.to_datetime(
        allocation_storage['end_date'],
        errors='coerce'
    )

    today = pd.Timestamp(dt.datetime.today().date())
    allocation_storage['valid'] = (
        allocation_storage['end_date'].isna()
        | (allocation_storage['end_date'] > today)
    )

    allocation_storage['allocation'] = (
        allocation_storage['allocation'].astype(str) + 'G'
    )

    allocation_storage.loc[~allocation_storage['valid'], 'allocation'] = '0G'


    allocation_storage = (
        allocation_storage[['project', 'user', 'allocation']]
        .rename(columns={
            'project': 'Project',
            'user': 'User',
            'allocation': 'Allocation'
        })
    )
    return allocation_storage


def create_table_storage_user(storage_usage, 
                      allocation_storage=None,
                      gdata_default_limits=None,
                      scratch_default_limits=None
                      ):
    """
    Create a table of storage usage by user for a given project
    """  

    user_storage_dict = {}
    for project in ['gb02','fy29','if69','ng72']:
    
        user_totals = (
            storage_usage[project]
            .reset_index()
            .groupby(['USER', 'FILESYSTEM', 'SCAN DATE'])['TOTAL SIZE']
            .sum()
        )
        user_storage_dict[project] = user_totals
    
    user_storage_df = (
        pd.concat(user_storage_dict, names=['project'])
        .rename('Total')
        .rename_axis(['Project', 'User', 'Filesystem', 'Date'])
        .reset_index()
    )

    user_storage_df = user_storage_df[
        user_storage_df['Total'] >= 1024**2
    ].copy()

    user_storage_df = user_storage_df.merge(
        allocation_storage, on=["Project", "User"], how="left",
    )

        # Fill missing allocations with project-specific defaults
    def default_allocation(row):
        if not pd.isna(row['Allocation']):
            return row['Allocation']

        limits = {
            'gdata': gdata_default_limits,
            'scratch': scratch_default_limits,
        }.get(str(row['Filesystem']).lower()) or {}

        filesystem = str(row['Filesystem']).strip().lower()
        project = str(row['Project']).strip().lower()

        if 'scratch' in filesystem:
            limits = scratch_default_limits or {}
        elif 'gdata' in filesystem:
            limits = gdata_default_limits or {}
        else:
            limits = {}

        return limits.get(project, '500G')

    user_storage_df['Allocation'] = user_storage_df.apply(
        default_allocation,
        axis=1
    )

    user_storage_df['Allocation'] = user_storage_df['Allocation'].apply(convert_size_to_bytes)

    exceeds_allocation = user_storage_df['Total'] > user_storage_df['Allocation']
    excess = (
        user_storage_df['Total'] - user_storage_df['Allocation']
    ).apply(convert_bytes_to_size)

    user_storage_df['Status'] = np.where(
        exceeds_allocation,
        'Usage exceeds allocation by ' + excess,
        'Within the ' + user_storage_df['Allocation'].apply(convert_bytes_to_size)
        + ' for the project'
    )

    user_storage_df = user_storage_df.sort_values(
        by=['Project', 'Filesystem', 'Total'],
        ascending=[True, True, False]
    )

    user_storage_df['Total'] = (
        user_storage_df['Total']
        .apply(convert_bytes_to_size)
    )

    user_storage_df['Allocation'] = (
        user_storage_df['Allocation']
        .apply(convert_bytes_to_size)
    )

    def highlight_over_allocation(row):
        warning = 'exceeds' in row['Status']
        return ['color: #B7533D' if warning else '' for _ in row]
    return user_storage_df.style.apply(highlight_over_allocation, axis=1).format(precision=1).hide(axis=0)