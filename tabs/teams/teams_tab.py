import streamlit as st
import pandas as pd

from utils import transform_teams_for_current_week

def display_team_tab(folded_df):
    st.subheader("Teams", anchor=False)
    season_options = sorted(folded_df['season'].unique())
    default_season_idx = season_options.index(max(season_options))
    season = st.selectbox('Select Season:', season_options, index=default_season_idx, key='team_season')
    week_options = sorted(folded_df[folded_df['season'] == season]['week'].unique())
    if season == max(season_options):
        s_df = folded_df[((folded_df['season'] == season)&(folded_df['actual_points'].isnull()))].copy()
        if s_df.shape[0] == 0:
            default_week_idx = week_options.index(max(week_options))
        else:
            default_week_idx = week_options.index(s_df.week.values[0])
    else:
        default_week_idx = week_options.index(max(week_options))
    week = st.selectbox('Select Week:', week_options, index=default_week_idx, key='team_week')
    top_table_cols = [
        'team',
        'expected_points',
        'rating',
        'offensive_rank',
        'defensive_rank',
        'avg_points_over_expected',
        'actual_team_covered_spread',
        'actual_over_covered',
    ]
    st.write(f"Team Ratings Week {week} in the {season} Season")
    filtered_folded_df = transform_teams_for_current_week(folded_df, season, week)
    selected_team = st.dataframe(filtered_folded_df[top_table_cols])
