import streamlit as st
import pandas as pd

POSITION_STAT_MAP = {
    "QB": [
        'projected_passing_completions',
        'projected_passing_attempts',
        'projected_passing_yards',
        'projected_passing_touchdowns',
        'projected_passing_interceptions',
        'projected_rushing_attempts',
        'projected_rushing_yards',
        'projected_rushing_touchdowns',
        'projected_fumbles',

    ],
    "RB": [
        'projected_rushing_attempts',
        'projected_rushing_yards',
        'projected_rushing_touchdowns',
        'projected_fumbles',
        'projected_receiving_targets',
        'projected_receiving_yards',
        'projected_receiving_touchdowns'
    ],
    "WR": [
        'projected_receiving_targets',
        'projected_receiving_yards',
        'projected_receiving_touchdowns',
        'projected_fumbles',
        'projected_rushing_attempts',
        'projected_rushing_yards',
        'projected_rushing_touchdowns',
    ],
    "TE": [
        'projected_receiving_targets',
        'projected_receiving_yards',
        'projected_receiving_touchdowns',
        'projected_fumbles',
        'projected_rushing_attempts',
        'projected_rushing_yards',
        'projected_rushing_touchdowns',


    ],
    "K": [
        'projected_made_field_goals',
        'projected_attempted_field_goals',
        'projected_missed_field_goals',
        'projected_made_extra_points',
        'projected_attempted_extra_points',
        'projected_missed_extra_points'
    ],
    "D/ST": [
        'projected_defensive_points_allowed',
        'projected_defensive_yards_allowed',
        #'projected_defensive_solo_tackles',
        #'projected_defensive_assisted_tackles',
        'projected_defensive_total_tackles',
        'projected_defensive_interceptions',
        'projected_defensive_fumbles',
        'projected_defensive_sacks',
        'projected_defensive_touchdowns',
        'projected_defensive_passes_defensed',
    ]
}

def display_event_player_tab(dataset_df, event_player_df):
    st.subheader("Event Players", anchor=False)
    
    # Filter controls
    season_options = sorted(dataset_df['season'].unique())
    default_season_idx = season_options.index(max(season_options))
    season = st.selectbox('Select Season:', season_options, index=default_season_idx, key='event_player_season')
    
    week_options = sorted(dataset_df[dataset_df['season'] == season]['week'].unique())
    default_week_idx = week_options.index(max(week_options))
    week = st.selectbox('Select Week:', week_options, index=default_week_idx, key='event_player_week')
    
    # Filter events for selected season and week
    filtered_events = dataset_df[
        (dataset_df['season'] == season) & 
        (dataset_df['week'] == week)
    ].copy()
    
    # Create game selection options
    game_options = [f"{row['away_team']} @ {row['home_team']}" for _, row in filtered_events.iterrows()]
    selected_game = st.selectbox('Select Game:', game_options, key='event_player_game')
    
    if selected_game:
        away_team, home_team = selected_game.split(' @ ')
        
        # Filter player data for selected teams
        away_players = event_player_df[
            (event_player_df['season'] == season) & 
            (event_player_df['week'] == week) & 
            (event_player_df['team'] == away_team)
        ].copy()
        
        home_players = event_player_df[
            (event_player_df['season'] == season) & 
            (event_player_df['week'] == week) & 
            (event_player_df['team'] == home_team)
        ].copy()

        # --- Aggregation helpers ---
        def safe_sum(df, col):
            return df[col].sum() if col in df.columns else 0

        def aggregate_offense(players_df):
            off_pos = ['QB', 'RB', 'WR', 'TE','D/ST']
            off_players = players_df[players_df['position'].isin(off_pos)]

            # TDs can be split across passing/rushing/receiving depending on position
            total_pass_tds = safe_sum(off_players, 'projected_passing_touchdowns')
            total_rush_tds = safe_sum(off_players, 'projected_rushing_touchdowns')
            total_def_tds = safe_sum(off_players, 'projected_defensive_touchdowns')
            total_pass_yds = safe_sum(off_players, 'projected_passing_yards')
            total_rush_yds = safe_sum(off_players, 'projected_rushing_yards')
            total_rec_yds = safe_sum(off_players, 'projected_receiving_yards')

            # Kickers (FGs / XPs)
            kickers = players_df[players_df['position'] == 'K']
            total_made_fgs = safe_sum(kickers, 'projected_made_field_goals')
            total_made_xps = safe_sum(kickers, 'projected_made_extra_points')

            total_score = total_rush_tds * 6 + total_pass_tds * 6 + total_def_tds * 6 + total_made_fgs * 3 + total_made_xps

            return {
                'proj_score': total_score,
                'pass_tds': total_pass_tds,
                'rush_tds': total_rush_tds,
                'def_tds': total_def_tds,
                'pass_yds': total_pass_yds,
                'rush_yds': total_rush_yds,
                'rec_yds': total_rec_yds,
                'made_fgs': total_made_fgs,
                'made_xps': total_made_xps
            }

        # Compute aggregates for both sides
        away_off = aggregate_offense(away_players)
        home_off = aggregate_offense(home_players)

        # Build matchup table: offense vs opponent DST
        matchup_rows = [
            {
                'team': away_team,
                'proj_score': away_off['proj_score'],
                'pass_tds': away_off['pass_tds'],
                'rush_tds': away_off['rush_tds'],
                'def_tds': away_off['def_tds'],
                'pass_yds': away_off['pass_yds'],
                'rush_yds': away_off['rush_yds'],
                'rec_yds': away_off['rec_yds'],
                'made_fgs': away_off['made_fgs'],
                'made_xps': away_off['made_xps'],
            },
            {
                'team': home_team,
                'proj_score': home_off['proj_score'],
                'pass_tds': home_off['pass_tds'],
                'rush_tds': home_off['rush_tds'],
                'def_tds': home_off['def_tds'],
                'pass_yds': home_off['pass_yds'],
                'rush_yds': home_off['rush_yds'],
                'rec_yds': home_off['rec_yds'],
                'made_fgs': home_off['made_fgs'],
                'made_xps': home_off['made_xps'],
            }
        ]

        matchup_df = pd.DataFrame(matchup_rows)

        # Display matchup summary above player lists
        st.write("### Offense vs Defense Matchup Summary")
        st.dataframe(matchup_df.set_index('team'))
        
        # Display side by side comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(away_team)
            for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST']:
                st.write(f"### {pos}")
                pos_players = away_players[away_players['position'] == pos]
                cols = ['name', 'projected_points','ecr'] + POSITION_STAT_MAP[pos]
                if not pos_players.empty:
                    st.dataframe(pos_players[cols])
        
        with col2:
            st.subheader(home_team)
            for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST']:
                st.write(f"### {pos}")
                pos_players = home_players[home_players['position'] == pos]
                cols = ['name', 'projected_points','ecr'] + POSITION_STAT_MAP[pos]

                if not pos_players.empty:
                    st.dataframe(pos_players[cols])

def display_player_tab(player_df):
    st.subheader("Players", anchor=False)
    
    # Filter controls
    season_options = sorted(player_df['season'].unique())
    default_season_idx = season_options.index(max(season_options))
    season = st.selectbox('Select Season:', season_options, index=default_season_idx, key='player_season')
    
    week_options = sorted(player_df[player_df['season'] == season]['week'].unique())
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_weeks = st.multiselect('Select Weeks:', week_options, 
                                      default=[max(week_options)],
                                      key='player_weeks_multi',
                                      help="Select one or more weeks. Select all weeks to see season totals.")
    with col2:
        agg_type = st.selectbox("Aggregation:", ["Average", "Total"], 
                               index=1 if len(selected_weeks) == len(week_options) else 0)
    
    # If no weeks selected, default to all weeks with Total aggregation
    if not selected_weeks:
        selected_weeks = week_options
        agg_type = "Total"
    
    # Filter type selection
    filter_type = st.radio("Filter by:", ["Team", "Position"])

    # Filter data for selected season and weeks
    filtered_df = player_df[
        (player_df['season'] == season) & 
        (player_df['week'].isin(selected_weeks))
    ].copy()
    
    # Aggregate data if multiple weeks selected
    if len(selected_weeks) > 1:
        # Get non-stat columns that should be grouped
        group_cols = ['name', 'team', 'position']
        # Get stat columns that should be aggregated
        stat_cols = ['projected_points'] + [col for pos in POSITION_STAT_MAP.values() for col in pos]
        
        # Create aggregation dictionary
        if agg_type == "Average":
            agg_dict = {col: 'mean' for col in stat_cols}
        else:  # Total
            agg_dict = {col: 'sum' for col in stat_cols}
        
        # Add non-stat columns to keep
        for col in group_cols:
            agg_dict[col] = 'first'
        
        # Perform aggregation
        filtered_df = filtered_df.groupby(['team', 'position', 'name'], as_index=False).agg(agg_dict)

    # Sort the dataframe by projected points
    filtered_df = filtered_df.sort_values('projected_points', ascending=False)
    
    if filter_type == "Team":
        team_options = sorted(filtered_df['team'].unique())
        selected_team = st.selectbox('Select Team:', team_options)
        filtered_df = filtered_df[filtered_df['team'] == selected_team]
        
        # Group by position
        for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST']:
            pos_players = filtered_df[filtered_df['position'] == pos]
            if not pos_players.empty:
                st.write(f"### {pos}")
                st.dataframe(pos_players[['name', 'projected_points',] + POSITION_STAT_MAP[pos]])
    
    else:  # Position
        pos_options = ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST']
        selected_pos = st.multiselect('Select Positions:', pos_options,
                                    help="Select one or more positions. Clear selection to see all positions.")
        
        if selected_pos:  # If positions are selected
            filtered_df = filtered_df[filtered_df['position'].isin(selected_pos)]
        
        # Show all players of selected positions
        for pos in (selected_pos if selected_pos else pos_options):
            pos_players = filtered_df[filtered_df['position'] == pos]
            if not pos_players.empty:
                st.write(f"### {pos}")
                st.dataframe(pos_players[['team', 'name', 'projected_points'] + POSITION_STAT_MAP[pos]])
