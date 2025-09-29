import pandas as pd
import numpy as np

# Create a dictionary of allocation vs usage dataframes

def check_allocation(grant_dict,
                     SU_df_dict,
                     allocation_df,
                     ):
    """
    Computes usage against approved allocation specified in dashboard.ipynb
    """

    alloc_df_dict = {}
    for project in grant_dict.keys():
        
        # Compute allocation usage
        alloc_check_df = SU_df_dict[project].merge(allocation_df.xs(project,level='project'),on='user')
        alloc_check_df['consumed'] = alloc_check_df['usage']/alloc_check_df['allocation']*100
        
        # Check user allocations
        WARNING_THRESHOLD=75.0
        CRITICAL_THRESHOLD=100.0
        for ix, row in alloc_check_df.iterrows():
            
            if row['consumed'] > CRITICAL_THRESHOLD:
                print (f"CRITICAL : {ix} has consumed {row['consumed']:.2f}% of their {project} SU allocation")
            elif row['consumed'] > WARNING_THRESHOLD:
                print (f"WARNING : {ix} has consumed {row['consumed']:.2f}% of their {project} SU allocation")
        
        # Check project allocations against granted kSU
        if alloc_check_df['allocation'].sum() > grant_dict[project]:
            print (f'WARNING : User allocations to {project} have exceeded its granted amount!')   
        
        alloc_df_dict[project] = alloc_check_df

    return alloc_df_dict 

def create_user_table(SU_df_dict1, 
                      allocation_df,
                      ):

    """
    Create a table of usage by user for a given project
    """   
    user_totals = {}
    for i,project in enumerate(SU_df_dict1.keys()):
        
        user_totals[project] = SU_df_dict1[project].groupby('user')['usage'].sum()

    table_by_user = pd.DataFrame(pd.concat(user_totals)).reset_index(names=['project', 'user'])

    table_by_user['usage'] = table_by_user['usage'].round(1)
    table_by_user = table_by_user.merge(allocation_df, on=['project','user'], how='left').fillna(5)
    table_by_user['allocation'] = table_by_user['allocation'].round(1)
    table_by_user['status'] = np.where(table_by_user['usage'] > table_by_user['allocation'],
    'Usage exceeds allocation by ' + (table_by_user['usage'] - table_by_user['allocation']).round(1).astype(str),
    'Within 5 KSU allocation per quarter')

    # # Format table
    table_by_user.columns = [col.capitalize() for col in table_by_user.columns]

    def highlight_over_allocation(row):
        warning = 'exceeds' in row['Status']
        return ['color: #B7533D' if warning else '' for _ in row]

    return table_by_user.style.apply(highlight_over_allocation, axis=1).format(precision=1).hide(axis=0)