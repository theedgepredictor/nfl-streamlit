import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from nfl_data_loader.utils.utils import find_year_for_season, find_week_for_season

# Report tab for boom/bust analysis


def generate_weekly_boom_bust_candidates(df, season, week, n=10, positions=None):
    """
    Generate boom and bust candidate dataframes for a given season/week.
    Expects df to be the player-level dataframe (same as used for ECR view).
    Positions: optional list of positions to include (e.g. ['RB','WR']). If None, include all.
    Returns (boom_df, bust_df) or (empty, empty) if insufficient data.
    """
    # Work on a copy
    dfw = df.copy()
    # Filter to season/week
    dfw = dfw[(dfw.get('season') == season) & (dfw.get('week') == week)].copy()

    # Column fallbacks
    ecr_col = 'ecr' if 'ecr' in dfw.columns else ('ECR' if 'ECR' in dfw.columns else None)
    proj_col = 'projected_points' if 'projected_points' in dfw.columns else None

    # Required columns check
    required = [ecr_col, proj_col, 'breakout_likelihood', 'bust_likelihood']
    if None in required[:2] or not all(col in dfw.columns for col in ['breakout_likelihood', 'bust_likelihood']):
        return pd.DataFrame(), pd.DataFrame()

    pos_map = {
        'RB': 8,
        'WR': 7,
        'TE': 6,
        'D/ST': 5,
        'K': 5,
        'QB': 10
    }

    general_cols = [
        'espn_id',
        'player_id',
        'name',
        'position',
        ecr_col,
        'player_owned_avg',
        proj_col,
    ]

    suffix_cols = [
        'opponent_name',
        'opposition_rank',
        'data_timestamp'
    ]

    boom_dfs = []
    bust_dfs = []

    filter_check = dfw[(dfw['breakout_likelihood'].notnull()) & (dfw['bust_likelihood'].notnull())].copy()
    if filter_check.shape[0] < 40:
        return pd.DataFrame(), pd.DataFrame()

    for pos, projected_points_threshold in pos_map.items():
        # respect requested positions list if provided
        if positions is not None and pos not in positions:
            continue
        if proj_col not in dfw.columns:
            continue
        filtered_df = dfw[(dfw['position'] == pos) & (dfw[proj_col] >= projected_points_threshold)].copy()
        if filtered_df.empty:
            continue
        filtered_df = filtered_df.sort_values(['breakout_likelihood'], ascending=False).head(n)
        cols = [c for c in general_cols + ['breakout_likelihood', 'projection_high_score'] + suffix_cols if c in filtered_df.columns]
        boom_dfs.append(filtered_df[cols])

    for pos, projected_points_threshold in pos_map.items():
        # respect requested positions list if provided
        if positions is not None and pos not in positions:
            continue
        if proj_col not in dfw.columns:
            continue
        filtered_df = dfw[(dfw['position'] == pos) & (dfw[proj_col] >= projected_points_threshold)].copy()
        if filtered_df.empty:
            continue
        filtered_df = filtered_df.sort_values(['bust_likelihood'], ascending=False).head(n)
        cols = [c for c in general_cols + ['bust_likelihood', 'projection_low_score'] + suffix_cols if c in filtered_df.columns]
        bust_dfs.append(filtered_df[cols])

    boom_df = pd.concat(boom_dfs, ignore_index=True) if boom_dfs else pd.DataFrame()
    bust_df = pd.concat(bust_dfs, ignore_index=True) if bust_dfs else pd.DataFrame()
    return boom_df, bust_df


def display_reports_tab(player_df, dataset_df, seasons):
    st.subheader("Reports")

    # Subtabs inside Reports
    ecr_tab, boom_tab = st.tabs(["ECR vs Projections", "Boom / Bust"])

    with ecr_tab:
        season_options = sorted(seasons)
        default_season = max(season_options)
        season = st.selectbox("Select Season:", season_options, index=season_options.index(default_season))

        view_mode = st.selectbox("View Mode:", ["Total", "Average per Week", "Single Week"], index=1)

        week = None
        if view_mode == "Single Week":
            week_options = sorted(dataset_df[dataset_df['season'] == season]['week'].unique())
            if week_options:
                week = st.selectbox("Select Week:", week_options, index=len(week_options)-1)

        st.write("## ECR vs Projections")
        col1, col2 = st.columns([3,1])

        with col2:
            st.write("Controls")
            top_n = st.number_input('Show top N players by projection', min_value=5, max_value=200, value=25)
            threshold = st.slider('Min projected points', 0.0, 100.0, 9.9, step=1.0)
            st.write('Positions')
            show_qb = st.checkbox('QB', value=True)
            show_rb = st.checkbox('RB', value=True)
            show_wr = st.checkbox('WR', value=True)
            show_te = st.checkbox('TE', value=True)
            show_k = st.checkbox('K', value=True)
            show_dst = st.checkbox('D/ST', value=True)
            score_metric = st.selectbox('Score metric:', [
                'ECR / Projected (rank-to-points ratio)',
                'Projected / (ECR + 1) (favours high points & good rank)'
            ])
            scoring_mode = st.selectbox('Scoring Mode', ['PPR', '1/2 PPR', 'STANDARD'], index=0)

        positions_selected = []
        if show_qb:
            positions_selected.append('QB')
        if show_rb:
            positions_selected.append('RB')
        if show_wr:
            positions_selected.append('WR')
        if show_te:
            positions_selected.append('TE')
        if show_k:
            positions_selected.append('K')
        if show_dst:
            positions_selected.append('D/ST')

        # season filtered df
        df = player_df[player_df['season'] == season].copy()
        df_season = df.copy()


        if scoring_mode == 'PPR':
            use_col = 'projected_points_ppr'
        elif scoring_mode == '1/2 PPR':
            use_col = 'projected_points_half_ppr'
        else:
            use_col = 'projected_points_standard'

        agg_total = df_season.groupby(['player_id','name','team','position'], as_index=False)[use_col].sum().rename(columns={use_col:'projected_points_total'})
        agg_avg = df_season.groupby(['player_id','name','team','position'], as_index=False)[use_col].mean().rename(columns={use_col:'projected_points_avg'})

        if 'ECR' in df_season.columns:
            ecr = df_season[['player_id','ECR']].drop_duplicates(subset=['player_id'])
        elif 'ecr' in df_season.columns:
            ecr = df_season[['player_id','ecr']].drop_duplicates(subset=['player_id']).rename(columns={'ecr':'ECR'})
        else:
            ecr = pd.DataFrame(columns=['player_id','ECR'])

        if view_mode == 'Single Week' and week is not None:
            df_week = df_season[df_season['week'] == week].copy()
            merged = df_week.groupby(['player_id','name','team','position'], as_index=False)[use_col].first().rename(columns={use_col:'projected_points_avg'})
            merged['projected_points_total'] = merged['projected_points_avg']
            merged = pd.merge(merged, ecr, on='player_id', how='left')
        else:
            merged = pd.merge(agg_total, agg_avg, on=['player_id','name','team','position'], how='left')
            merged = pd.merge(merged, ecr, on='player_id', how='left')

        if 'ECR' in merged.columns:
            merged = merged[merged['ECR'].notna()].copy()

        if view_mode == 'Total':
            x_col = 'projected_points_total'
            x_label = 'Projected Points (Total)'
        else:
            x_col = 'projected_points_avg'
            x_label = 'Projected Points (Avg per Week)'

        plot_df = merged.copy()
        plot_df = plot_df.dropna(subset=[x_col])
        plot_df['ECR_plot'] = plot_df['ECR'].fillna(9999)

        plot_filtered = plot_df.copy()
        if positions_selected:
            plot_filtered = plot_filtered[plot_filtered['position'].isin(positions_selected)]

        position_domain = ['QB','RB','WR','TE','K','D/ST']
        position_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

        with col1:
            base = alt.Chart(plot_filtered).mark_circle(size=60).encode(
                x=alt.X(x_col, title=x_label),
                y=alt.Y('ECR_plot', title='ECR (lower = better)'),
                color=alt.Color('position:N', scale=alt.Scale(domain=position_domain, range=position_colors), legend=alt.Legend(title='Position')),
                tooltip=['name','team','position', x_col, 'ECR']
            ).interactive()
            st.altair_chart(base, use_container_width=True)

        table_df = plot_df.copy()
        if positions_selected:
            table_df = table_df[table_df['position'].isin(positions_selected)]

        table_df = table_df.dropna(subset=['ECR', x_col]).copy()
        table_df = table_df[table_df[x_col] > 0]
        table_df['ECR_filled'] = table_df['ECR']

        if score_metric.startswith('Projected /'):
            table_df['value_score'] = table_df[x_col] / (table_df['ECR_filled'] + 1)
            ascending = False
        else:
            table_df['value_score'] = table_df['ECR_filled'] / table_df[x_col]
            ascending = False

        table_df = table_df[table_df[x_col] >= threshold]
        table_df = table_df.sort_values('value_score', ascending=ascending).head(top_n)

        st.write("### Players: high projection per ECR")
        if not table_df.empty:
            table_df = table_df.loc[:, ~table_df.columns.duplicated()]
            display_cols = [c for c in ['name','team','position', x_col, 'ECR', 'value_score'] if c in table_df.columns]
            st.dataframe(table_df[display_cols])
        else:
            st.write('No players match the filters')

        st.markdown("""
        This report compares Expert Consensus Ranking (ECR) to projected fantasy points.
        Use the controls to switch between total, average, or a single-week snapshot. The table shows players who look undervalued by ECR relative to their projected fantasy output.
        """)

    with boom_tab:
        st.write("Generate a weekly Boom / Bust report for the selected season/week.")
        # Allow explicit selection of season and week for the Boom/Bust report.
        # Default to current season/week using nfl_data_loader helpers if available.
        all_seasons = sorted(seasons)
        default_season = None
        try:
            default_season = find_year_for_season()
            if default_season not in all_seasons:
                default_season = max(all_seasons)
        except Exception:
            default_season = max(all_seasons)

        bb_season = st.selectbox('Boom/Bust Season', all_seasons, index=all_seasons.index(default_season))

        # Weeks in dataset for the selected season
        bb_week_options = sorted(dataset_df[dataset_df['season'] == bb_season]['week'].unique())
        # default week: try to use find_week_for_season, otherwise last available
        default_week = None
        try:
            default_week = find_week_for_season()
            if default_week not in bb_week_options:
                default_week = bb_week_options[-1]
        except Exception:
            default_week = bb_week_options[-1] if bb_week_options else None

        if default_week is not None:
            bb_week = st.selectbox('Boom/Bust Week', bb_week_options, index=bb_week_options.index(default_week))
        else:
            bb_week = st.selectbox('Boom/Bust Week', bb_week_options)

        # N and positions controls
        st.write('Boom / Bust report options')
        n_val = st.number_input('Top N per position', min_value=1, max_value=100, value=10)
        positions_available = sorted(player_df['position'].dropna().unique()) if 'position' in player_df.columns else ['QB','RB','WR','TE','K','D/ST']
        # Map common variations if needed
        positions_selected = st.multiselect('Positions to include', options=positions_available, default=['RB','WR','TE'])

        st.write(f"Generating Boom / Bust candidates for Season {bb_season} Week {bb_week} (Top {n_val} per position)")
        boom_df, bust_df = generate_weekly_boom_bust_candidates(player_df, bb_season, bb_week, n=int(n_val), positions=positions_selected)

        if boom_df.empty and bust_df.empty:
            st.write("Insufficient data to generate boom/bust candidates for this week.")
        else:
            st.write("### Boom candidates")
            if not boom_df.empty:
                st.dataframe(boom_df)
            else:
                st.write("No boom candidates")

            st.write("### Bust candidates")
            if not bust_df.empty:
                st.dataframe(bust_df)
            else:
                st.write("No bust candidates")
