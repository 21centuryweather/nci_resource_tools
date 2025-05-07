import sys
import pandas as pd
from nci_account import nci_account
from config import *

def retrieve_project_data():
    """
    Retrieve SU data storage data from nci_account objects
    """

    SU_df_dict = {}
    grant_dict = {}
    storage_dict = {}

    for project in COE_PROJECTS:
        
        account=nci_account(project)

        storage_dict[project] = account['storage']
        
        grant = account['usage']['total_grant']/1000.
        
        if grant > 0: # Not all projects have compute allocated
        
            SU=account['usage']   
            SUs_df=pd.DataFrame.from_dict(SU['users']).T/1000.
            
            SU_df_dict[project] = SUs_df
            grant_dict[project] = grant
        
            # Rename the index
            SU_df_dict[project].index.rename('user',inplace=True)

    return SU_df_dict, grant_dict, storage_dict


def create_storage_df(storage_dict):
    """
    Create a dictionary of dataframes for storage data
    """

    storage_data = {}

    # Note at this point we assume each project only has one allocation scheme
    # If a project scratch disk exists, there are only one of them

    for project in COE_PROJECTS:

        # Sub-dictionary for each project
        storage_data[project] = {}
        
        # Find gdata disk
        gdata_diskname, = [ key for key in storage_dict[project].keys() if 'gdata' in key ] 

        disks = [gdata_diskname]
        
        # Find scratch disk (if it exists)
        scratch_list = [ key for key in storage_dict[project].keys() if 'scratch' in key ] 

        if scratch_list:
            # Store scratch allocations and usage
            scratch_diskname = scratch_list[0]
            disks.append(scratch_diskname)

        # Store disk allocations and usage. Convert block data to terabytes, and inodes to millions of files.
        for disk in disks:
        
            project_block_allocation = storage_dict[project][disk]['allocations'][0]['block_allocation']/1024/1e9
            project_inode_allocation = storage_dict[project][disk]['allocations'][0]['inode_allocation']/1e6
            project_block_usage = storage_dict[project][disk]['block_usage']/1024/1e9
            project_inode_usage = storage_dict[project][disk]['inode_usage']/1e6
        
            project_usage = { 'block' : project_block_usage, 'inode' : project_inode_usage}
            project_allocation = { 'block' : project_block_allocation, 'inode' : project_inode_allocation}
            
            storage_data[project][disk] = pd.DataFrame.from_dict({'usage' : project_usage, 'allocation' : project_allocation})        

        # Rename disks to generic labels
        storage_data[project]['gdata'] = storage_data[project].pop(gdata_diskname)

        if scratch_list:
            storage_data[project]['scratch'] = storage_data[project].pop(scratch_diskname)

    return storage_data

