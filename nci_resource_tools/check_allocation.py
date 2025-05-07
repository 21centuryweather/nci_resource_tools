import pandas as pd

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