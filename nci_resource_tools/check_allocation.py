import pandas as pd
import numpy as np
from html import escape

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

def _user_allocation_data(SU_df_dict1, allocation_df, default_limits=None):
    """Build per-user usage and limits, including users on a default limit."""
    if default_limits is None:
        default_limits = {project: 5 for project in SU_df_dict1.keys()}
    
    user_totals = {}
    for i,project in enumerate(SU_df_dict1.keys()):
        user_totals[project] = SU_df_dict1[project].groupby('user')['usage'].sum()
    
    table_by_user = pd.DataFrame(pd.concat(user_totals)).reset_index(names=['project', 'user'])
    table_by_user['usage'] = table_by_user['usage'].round(1)
    table_by_user = table_by_user.merge(allocation_df, on=['project','user'], how='left')
    
    # Fill missing allocations with project-specific defaults
    table_by_user['allocation'] = table_by_user.apply(
        lambda row: default_limits.get(row['project'], 5) if pd.isna(row['allocation']) else row['allocation'], 
        axis=1
    )
    
    table_by_user['allocation'] = table_by_user['allocation'].round(1)
    table_by_user['status'] = np.where(table_by_user['usage'] > table_by_user['allocation'],
    'Usage exceeds allocation by ' + (table_by_user['usage'] - table_by_user['allocation']).round(1).astype(str),
    'Within the ' + table_by_user['allocation'].astype(str) + ' KSU allocation per quarter')

    table_by_user.columns = [col.capitalize() for col in table_by_user.columns]
    return table_by_user


def create_allocation_overview(SU_df_dict1, allocation_df, default_limits=None):
    """Return a compact HTML summary of current per-user SU allocations."""
    users = _user_allocation_data(SU_df_dict1, allocation_df, default_limits)
    return _allocation_overview_html(users)


def _allocation_overview_html(users):
    """Render an overview from the same columns shown in the user table."""
    ratio = users['Usage'] / users['Allocation'].replace(0, np.nan)
    exceeded = users[ratio > 1].copy()
    exceeded['Percent'] = ratio[ratio > 1]
    exceeded = exceeded.sort_values('Percent', ascending=False)
    near = int(((ratio > .75) & (ratio <= 1)).sum())
    rows = ''.join(
        '<li><span><b>{project}</b> · {user}</span><strong>{percent:.0f}% used</strong></li>'.format(
            project=escape(str(row.Project)),
            user=escape(str(row.User)),
            percent=row.Percent * 100,
        )
        for row in exceeded.head(5).itertuples(index=False)
    )
    if not rows:
        rows = '<li>All users are within their allocations.</li>'
    return (
        '<div class="allocation-overview">'
        '<h3>Allocation watch</h3>'
        '<p>Quarterly SU usage across all users, including default allocations.</p>'
        '<div class="allocation-totals">'
        f'<div><strong>{len(exceeded)}</strong><span>Over allocation</span></div>'
        f'<div><strong>{near}</strong><span>75–100% used</span></div>'
        '</div><ul>' + rows + '</ul></div>'
    )


def create_user_table(SU_df_dict1,
                      allocation_df,
                      default_limits=None
                      ):
    """Create a styled table of usage by user for each project."""
    table_by_user = _user_allocation_data(SU_df_dict1, allocation_df, default_limits)
    def highlight_over_allocation(row):
        warning = 'exceeds' in row['Status']
        return ['color: #B7533D' if warning else '' for _ in row]
    return table_by_user.style.apply(highlight_over_allocation, axis=1).format(precision=1).hide(axis=0)
