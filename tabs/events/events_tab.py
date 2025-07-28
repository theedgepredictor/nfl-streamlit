import streamlit as st
import pandas as pd
from utils import transform_teams_for_current_week

def display_event_tab(dataset_df, folded_df):
    st.subheader("Events", anchor=False)
    season_options = sorted(dataset_df['season'].unique())
    default_season_idx = season_options.index(max(season_options))
    season = st.selectbox('Select Season:', season_options, index=default_season_idx, key='event_season')
    week_options = sorted(dataset_df[dataset_df['season'] == season]['week'].unique())
    if season == max(season_options):
        s_df = dataset_df[((dataset_df['season'] == season)&(dataset_df['actual_away_points'].isnull()))].copy()
        if s_df.shape[0] == 0:
            default_week_idx = week_options.index(max(week_options))
        else:
            default_week_idx = week_options.index(s_df.week.values[0])
    else:
        default_week_idx = week_options.index(max(week_options))
    week = st.selectbox('Select Week:', week_options, index=default_week_idx, key='event_week')
    top_table_cols = [
        'away_rating', 'away_team', 'home_rating', 'home_team', 'spread_line', 'expected_spread',
        'actual_away_spread', 'total_line', 'expected_total', 'actual_point_total',
        'away_expected_points', 'actual_away_points', 'home_expected_points', 'actual_home_points',
    ]
    folded_table_cols = [
        'rating', 'offensive_rank', 'defensive_rank', 'actual_team_covered_spread', 'actual_over_covered',
        'avg_points_over_expected', 'expected_points', 'expected_q1_points', 'expected_q2_points',
        'expected_q3_points', 'expected_q4_points', 'expected_q5_points', 'expected_carries',
        'expected_rushing_yards', 'expected_rushing_tds', 'expected_completions', 'expected_attempts',
        'expected_passing_yards', 'expected_passing_tds', 'expected_time_of_possession',
        'expected_turnover', 'expected_field_goal_made'
    ]
    filtered_df = dataset_df[((dataset_df['season'] == season)&(dataset_df['week'] == week))].copy()
    if season < dataset_df.season.max() or (season == dataset_df.season.max() and week < dataset_df[((dataset_df['season'] == season)&(dataset_df['actual_away_points'].isnull()))].week.max() - 1):
        # You may want to import make_evaluation_report if needed
        pass
    st.write(f"Games for Week {week} in the {season} Season")
    selected_game = st.dataframe(filtered_df[top_table_cols], selection_mode="single-row")
    if selected_game:
        print(selected_game)
    selected_row = st.selectbox('Select a Game:', filtered_df.index)
    if selected_row is not None:
        st.write(f"Selected Game: {filtered_df.loc[selected_row, 'home_team']} vs {filtered_df.loc[selected_row, 'away_team']}")
        filtered_folded_df = transform_teams_for_current_week(folded_df, season, week)
        game = filtered_folded_df[filtered_folded_df.game_id == selected_row].copy()
        game.index = game.team
        st.table(game[folded_table_cols].T)
