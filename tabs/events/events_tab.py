# events_tab.py
import streamlit as st
import pandas as pd
from utils import transform_teams_for_current_week
from st_aggrid import AgGrid, JsCode, GridUpdateMode

# ===================== CSS (center everything, sane widths) =====================
def _inject_table_css():
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
      .stApp, .ag-theme-material {
        --data-positive: 34,197,94;
        --data-negative: 239,68,68;
        --data-muted: 107,114,128;
        --border: 229,231,235;
        font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
      }

      .ag-root-wrapper {
        border-radius: 12px !important;
        border: 1px solid rgba(var(--border),1) !important;
        overflow: hidden !important;
        box-shadow: 0 1px 2px rgba(0,0,0,.04);
      }

      /* Center every header & group header */
      .ag-header-cell, .ag-header-group-cell {
        border-right: 1px solid rgba(var(--border),1) !important;
      }
      .ag-header-cell-label, .ag-header-group-cell-label {
        font-weight: 600 !important;
        color: rgba(17,24,39,.8) !important;
        font-size: 12px !important;
        width: 100%;
        justify-content: center !important; /* center header text */
        text-align: center !important;
      }
      .ag-header, .ag-header-viewport, .ag-header-row { background: #fff !important; }
      .ag-header { position: sticky; top: 0; z-index: 3; border-bottom: 1px solid rgba(var(--border),1) !important; }

      /* Rows & cells (center content) */
      .ag-row {
        background: #fff !important;
        transition: background-color .12s ease;
        border-bottom: 1px solid rgba(var(--border),1) !important;
      }
      .ag-row-hover { background: rgba(243,244,246,.6) !important; }
      .ag-cell {
        padding: 0 !important;
        height: 42px !important;
        line-height: 42px !important;
        display: flex; align-items: center; justify-content: center; /* center cells */
        font-size: 13px; color: rgba(17,24,39,.9);
        text-align: center;
      }

      /* Hide text search/floating filters & sidebar */
      .ag-floating-filter, .ag-floating-filter-body, .ag-floating-filter-input { display: none !important; }
      .ag-side-bar, .ag-tool-panel-wrapper, .ag-side-buttons { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# ===================== JS Styles & Renderers =====================
RANK_CELL_STYLE = JsCode("""
function(params) {
  if (params.value == null) return {};
  const v = Number(params.value);
  if (isNaN(v)) return {};
  const t = Math.min(1, Math.max(0, (v - 1) / 31.0)); // 1..32 -> 0..1
  const r = Math.round(255 * t);
  const g = Math.round(255 * (1 - t));
  return { backgroundColor: `rgba(${r},${g},0,0.20)`, fontWeight: 600, borderRadius: '8px' };
}""")

RATING_CELL_STYLE = JsCode("""
function(params) {
  if (params.value == null) return {};
  const min = params.context.minRating ?? 0.0;
  const max = params.context.maxRating ?? 1.0;
  const span = Math.max(1e-9, max - min);
  const t = Math.min(1, Math.max(0, (Number(params.value) - min) / span)); // 0 low, 1 high
  const r = Math.round(255 * (1 - t));
  const g = Math.round(255 * t);
  return { backgroundColor: `rgba(${r},${g},0,0.20)`, fontWeight: 600, borderRadius: '8px' };
}""")

EXPECTED_VS_LINE_STYLE = JsCode("""
function(params) {
  const f = params.colDef.field;
  if (!params.data) return {};
  if (f === 'expected_spread' && params.data.spread_line != null) {
    const a = Math.abs(Number(params.value) - Number(params.data.spread_line));
    if (a <= 1) return { backgroundColor: 'rgba(239,68,68,0.12)', borderRadius: '8px' };
    if (a >= 3) { const k = Math.min(1, (a - 3)/3)*0.25; return { backgroundColor: `rgba(34,197,94,${0.10+k})`, borderRadius: '8px' }; }
    return {};
  }
  if (f === 'expected_total' && params.data.total_line != null) {
    const a = Math.abs(Number(params.value) - Number(params.data.total_line));
    if (a <= 2) return { backgroundColor: 'rgba(239,68,68,0.12)', borderRadius: '8px' };
    if (a >= 5) { const k = Math.min(1, (a - 5)/3)*0.25; return { backgroundColor: `rgba(34,197,94,${0.10+k})`, borderRadius: '8px' }; }
    return {};
  }
  return {};
}""")

TEAM_CELL = JsCode("""
class TeamCellRenderer {
  init(params) {
    const team = params.value ?? '';
    const record = params.data && params.data.team_record ? params.data.team_record : '';
    const wrap = document.createElement('div');
    wrap.style.display='grid'; wrap.style.gridTemplateRows='1fr 1fr'; wrap.style.alignItems='center'; wrap.style.textAlign='center';
    const nameEl = document.createElement('div');
    nameEl.textContent = team || ''; nameEl.style.fontWeight='700'; nameEl.style.color='rgb(17,24,39)'; nameEl.style.lineHeight='1'; nameEl.style.fontSize='13px';
    const recEl = document.createElement('div');
    recEl.textContent = record || ''; recEl.style.color='rgba(107,114,128,.9)'; recEl.style.fontSize='12px'; recEl.style.lineHeight='1';
    wrap.appendChild(nameEl); wrap.appendChild(recEl);
    this.eGui = wrap;
  }
  getGui(){ return this.eGui; }
}
""")

DETAIL_CELL_STYLE = JsCode("""
function(params){
  if (!params || params.colDef.field === 'Stat') return {};
  const label = (params.data && String(params.data.Stat || '')).toLowerCase();
  const v = Number(params.value);
  if (isNaN(v)) return {};
  if (label.includes('offensive rank') || label.includes('defensive rank')) {
    const t = Math.min(1, Math.max(0, (v - 1) / 31.0));
    const r = Math.round(255 * t), g = Math.round(255 * (1 - t));
    return { backgroundColor: `rgba(${r},${g},0,0.20)`, fontWeight: 600, borderRadius: '8px' };
  }
  if (label === 'rating') {
    const min = params.context.minRating ?? 0.0, max = params.context.maxRating ?? 1.0;
    const span = Math.max(1e-9, max - min);
    const t = Math.min(1, Math.max(0, (v - min) / span));
    const r = Math.round(255 * (1 - t)), g = Math.round(255 * t);
    return { backgroundColor: `rgba(${r},${g},0,0.20)`, fontWeight: 600, borderRadius: '8px' };
  }
  return {};
}
""")

# Two-decimal formatter for all cells
TWO_DEC_FMT = JsCode("""
function(params){
  const v = params.value;
  if (v == null) return '';
  const n = Number(v);
  if (isNaN(n)) return String(v);
  return n.toFixed(2);
}
""")

# ===================== helpers =====================
def _ensure_game_id(df: pd.DataFrame) -> pd.DataFrame:
    return df if 'game_id' in df.columns else df.reset_index().rename(columns={'index': 'game_id'})

def _rating_min_max(df: pd.DataFrame, cols) -> tuple[float, float]:
    vals = []
    for c in cols:
        if c in df.columns:
            vals.extend(df[c].dropna().tolist())
    return (0.0, 1.0) if not vals else (float(min(vals)), float(max(vals)))

def _get_selected_rows(resp):
    sel = resp.get("selected_rows") if isinstance(resp, dict) else getattr(resp, "selected_rows", None)
    if isinstance(sel, pd.DataFrame):
        return [] if sel.empty else sel.to_dict(orient="records")
    if sel is None:
        return []
    if isinstance(sel, list):
        return sel
    try:
        return list(sel)
    except Exception:
        return []

def _calc_height(n_rows: int, row_px: int = 42, pad_px: int = 120, cap_px: int = 1500) -> int:
    return min(cap_px, max(260, n_rows * row_px + pad_px))

# ===================== columnDefs for ONLY included columns =====================
def _build_grouped_column_defs(included_cols: list[str]):
    present = set(included_cols)
    def has(c): return c in present

    team_col = {
        "headerName": "",
        "field": "matchup_display",
        "pinned": "left",
        "cellRenderer": TEAM_CELL,
        "minWidth": 180, "maxWidth": 220,
    } if has("matchup_display") else None

    ratings_group = {"headerName":"Ratings","children":[]}
    if has("away_rating"): ratings_group["children"].append({"headerName":"Away","field":"away_rating"})
    if has("home_rating"): ratings_group["children"].append({"headerName":"Home","field":"home_rating"})
    if not ratings_group["children"]: ratings_group = None

    off_rank_group = {"headerName":"Offensive Rank","children":[]}
    if has("away_offensive_rank"): off_rank_group["children"].append({"headerName":"Away","field":"away_offensive_rank"})
    if has("home_offensive_rank"): off_rank_group["children"].append({"headerName":"Home","field":"home_offensive_rank"})
    if not off_rank_group["children"]: off_rank_group = None

    def_rank_group = {"headerName":"Defensive Rank","children":[]}
    if has("away_defensive_rank"): def_rank_group["children"].append({"headerName":"Away","field":"away_defensive_rank"})
    if has("home_defensive_rank"): def_rank_group["children"].append({"headerName":"Home","field":"home_defensive_rank"})
    if not def_rank_group["children"]: def_rank_group = None

    spread_group = {"headerName":"Spread","children":[]}
    if has("spread_line"): spread_group["children"].append({"headerName":"Line","field":"spread_line"})
    if has("expected_spread"): spread_group["children"].append({"headerName":"Expected","field":"expected_spread"})
    if has("actual_away_spread"): spread_group["children"].append({"headerName":"Actual","field":"actual_away_spread"})
    if not spread_group["children"]: spread_group = None

    total_group = {"headerName":"Total","children":[]}
    if has("total_line"): total_group["children"].append({"headerName":"Line","field":"total_line"})
    if has("expected_total"): total_group["children"].append({"headerName":"Expected","field":"expected_total"})
    if has("actual_point_total"): total_group["children"].append({"headerName":"Actual","field":"actual_point_total"})
    if not total_group["children"]: total_group = None

    points_group = {"headerName":"Expected Points","children":[]}
    if has("away_expected_points"): points_group["children"].append({"headerName":"Away","field":"away_expected_points"})
    if has("home_expected_points"): points_group["children"].append({"headerName":"Home","field":"home_expected_points"})
    if not points_group["children"]: points_group = None

    cols = [c for c in [team_col, ratings_group, off_rank_group, def_rank_group, spread_group, total_group, points_group] if c]
    return cols

def _augment_column_defs(column_defs, hide_fields=(), pinned_left=(), rank_cols=(), rating_cols=(), style_expected=True):
    def apply_to_leaf(col):
        field = col.get("field")
        if not field: return
        if field in hide_fields: col["hide"] = True
        if field in pinned_left: col["pinned"] = "left"
        if field in set(rank_cols or []): col["cellStyle"] = RANK_CELL_STYLE
        if field in set(rating_cols or []): col["cellStyle"] = RATING_CELL_STYLE
        if style_expected and field in {"expected_spread","expected_total"}: col["cellStyle"] = EXPECTED_VS_LINE_STYLE
        # Keep sane column widths (prevents 4 cols from filling the whole page)
        col.setdefault("minWidth", 90)
        col.setdefault("maxWidth", 180 if field != "matchup_display" else 240)

    def walk(defs):
        for d in defs:
            if "children" in d and isinstance(d["children"], list):
                walk(d["children"])
            else:
                apply_to_leaf(d)
    walk(column_defs)
    return column_defs

def _ensure_checkbox_on_first_leaf(column_defs):
    def first_leaf(defs):
        for d in defs:
            if "children" in d and isinstance(d["children"], list) and d["children"]:
                leaf = first_leaf(d["children"])
                if leaf: return leaf
            elif "field" in d:
                return d
        return None
    leaf = first_leaf(column_defs)
    if leaf is not None:
        leaf["checkboxSelection"] = True
        leaf.setdefault("headerCheckboxSelection", False)
        leaf.setdefault("headerCheckboxSelectionFilteredOnly", False)
        leaf.setdefault("minWidth", max(leaf.get("minWidth", 90), 140))

def _build_grid(
    df_view: pd.DataFrame,
    *,
    theme: str = "material",
    column_defs=None,
    pinned_left=('away_team','home_team'),
    rank_cols=None,
    rating_cols=None,
    style_expected=True,
    key=None,
    selection=True,
    min_rating=0.0,
    max_rating=1.0,
    height=None,
    fit_columns=True,
):
    if column_defs is None:
        column_defs = [{"field": c, "headerName": c.replace("_", " ").title()} for c in df_view.columns]

    _augment_column_defs(
        column_defs,
        hide_fields=("game_id",),
        pinned_left=pinned_left or (),
        rank_cols=rank_cols or (),
        rating_cols=rating_cols or (),
        style_expected=style_expected,
    )

    if selection:
        _ensure_checkbox_on_first_leaf(column_defs)

    get_row_id = None
    if "game_id" in df_view.columns:
        get_row_id = JsCode("function(p){return p.data && p.data.game_id!=null? String(p.data.game_id): String(p.rowIndex);} ")

    grid_options = {
        "defaultColDef": {
            "resizable": True,
            "sortable": True,
            "filter": True,
            "floatingFilter": False,
            "valueFormatter": TWO_DEC_FMT,   # two decimals everywhere
        },
        "columnDefs": column_defs,
        "rowHeight": 42,
        "animateRows": True,
        "sideBar": False,
        "context": {"minRating": min_rating, "maxRating": max_rating},
        "headerHeight": 34,
        "groupHeaderHeight": 26,
        "rowSelection": "single" if selection else "none",
        "suppressRowClickSelection": False,
        "pagination": False,
        "paginationAutoPageSize": True,
        # Make columns use available width but respect maxWidth caps.
        "suppressHorizontalScroll": False,
    }
    if get_row_id is not None:
        grid_options["getRowId"] = get_row_id

    if height is None:
        height = _calc_height(len(df_view))

    return AgGrid(
        df_view,
        gridOptions=grid_options,
        theme=theme,
        fit_columns_on_grid_load=fit_columns,   # True -> stretch to fill; caps keep them reasonable
        enable_enterprise_modules=False,
        allow_unsafe_jscode=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED if selection else GridUpdateMode.NO_UPDATE,
        height=height,
        key=key,
        custom_css={},
    )

# ===================== main render (centered + responsive width) =====================
def _render_games_with_detail(filtered_df: pd.DataFrame, folded_df: pd.DataFrame, view: str, theme: str, state_key: str):
    _inject_table_css()

    df = _ensure_game_id(filtered_df).copy()

    # Team display
    df['matchup_display'] = df.apply(lambda r: f"{r.get('away_team','')} @ {r.get('home_team','')}".strip(' @'), axis=1)
    if 'team_record' not in df.columns:
        df['team_record'] = ""

    # Presets (only include columns needed for each view)
    rank_cols = ['away_offensive_rank','away_defensive_rank','home_offensive_rank','home_defensive_rank']
    line_cols = ['spread_line','expected_spread','actual_away_spread','total_line','expected_total','actual_point_total']
    rating_cols = ['away_rating','home_rating']
    base_cols = ['matchup_display','game_id','season','week','away_team','home_team','team_record']

    presets = {
        "All": base_cols + rating_cols + rank_cols + line_cols,
        "Ranks": base_cols + rank_cols,
        "Lines": base_cols + line_cols,
        "Ratings": base_cols + rating_cols,
    }
    cols_to_show = [c for c in presets.get(view, presets["All"]) if c in df.columns]
    df_view = df[cols_to_show].copy()

    # determine middle column width: if many columns, give more width to reduce horiz scroll
    ncols = len(df_view.columns)
    left, middle, right = (1, 3, 1) if ncols <= 8 else (0.5, 8, 0.5)
    c1, c2, c3 = st.columns([left, middle, right], vertical_alignment="center")

    min_rating, max_rating = _rating_min_max(df_view, rating_cols)
    column_defs = _build_grouped_column_defs(df_view.columns.tolist())

    main_height = _calc_height(len(df_view), pad_px=140, cap_px=1200)
    with c2:
        resp = _build_grid(
            df_view,
            theme=theme,
            column_defs=column_defs,
            pinned_left=('matchup_display',),
            rank_cols=rank_cols if view in ("All","Ranks") else None,
            rating_cols=rating_cols if view in ("All","Ratings") else None,
            style_expected=(view in ("All","Lines")),
            key=f"{state_key}_{view}_grid",
            selection=True,
            min_rating=min_rating,
            max_rating=max_rating,
            height=main_height,
            fit_columns=True,  # stretch when it can; maxWidth caps keep it tidy with few cols
        )

    # Selection -> transposed detail (Away | Stat | Home)
    selected_rows = _get_selected_rows(resp)
    selected_game_id = selected_rows[0].get("game_id") if (isinstance(selected_rows, list) and selected_rows and isinstance(selected_rows[0], dict)) else None

    if selected_game_id is not None:
        st.markdown("#### Game Detail")
        cur_season = int(df_view['season'].iloc[0]) if 'season' in df_view.columns else None
        cur_week = int(df_view['week'].iloc[0]) if 'week' in df_view.columns else None

        folded_cur = transform_teams_for_current_week(folded_df, cur_season, cur_week)
        game = folded_cur[folded_cur.game_id == selected_game_id].copy()

        for c in ['offensive_rank','defensive_rank']:
            if c in game.columns:
                game[c] = game[c].astype('Int64')

        folded_table_cols = [
            'team','rating','offensive_rank','defensive_rank','actual_team_covered_spread','actual_over_covered',
            'avg_points_over_expected','expected_points','expected_q1_points','expected_q2_points',
            'expected_q3_points','expected_q4_points','expected_q5_points','expected_carries',
            'expected_rushing_yards','expected_rushing_tds','expected_completions','expected_attempts',
            'expected_passing_yards','expected_passing_tds','expected_time_of_possession',
            'expected_turnover','expected_field_goal_made'
        ]
        folded_cols_present = [c for c in folded_table_cols if c in game.columns]
        game_view = game[folded_cols_present].copy()

        f_min_rating, f_max_rating = _rating_min_max(game_view, ['rating'])

        # Determine away/home names from the selected row in the TOP table
        top_row = df[df["game_id"] == selected_game_id].iloc[0]
        away_name = str(top_row.get("away_team", "Away"))
        home_name = str(top_row.get("home_team", "Home"))

        # Transpose to vertical and order columns: Away | Stat | Home
        if 'team' in game_view.columns:
            tdf = game_view.set_index('team').T
        else:
            tdf = game_view.T  # fallback
        tdf.index.name = 'Stat'
        game_view_t = tdf.reset_index()

        # Make sure both columns exist; if not, create empty
        if away_name not in game_view_t.columns:
            game_view_t[away_name] = pd.NA
        if home_name not in game_view_t.columns:
            game_view_t[home_name] = pd.NA

        # Clean stat labels
        game_view_t['Stat'] = game_view_t['Stat'].astype(str).str.replace('_',' ').str.title()

        # Reorder to Away | Stat | Home
        ordered_cols = [away_name, 'Stat', home_name]
        # plus keep any other columns (if present) after these
        extra_cols = [c for c in game_view_t.columns if c not in ordered_cols]
        game_view_t = game_view_t[ordered_cols + extra_cols]

        # Col defs centered; color ranks/ratings via DETAIL_CELL_STYLE on team columns
        detail_defs = [
            {"headerName": away_name, "field": away_name, "cellStyle": DETAIL_CELL_STYLE, "minWidth": 120, "maxWidth": 180},
            {"headerName": "Stat", "field": "Stat", "pinned": "left", "minWidth": 220, "maxWidth": 260},
            {"headerName": home_name, "field": home_name, "cellStyle": DETAIL_CELL_STYLE, "minWidth": 120, "maxWidth": 180},
        ]
        # any extras after home (leave centered but without color style)
        for c in extra_cols:
            detail_defs.append({"headerName": str(c), "field": str(c), "minWidth": 120, "maxWidth": 180})

        # Centered container; widen if many stats so more fits horizontally
        n_detail_cols = len(detail_defs)
        ld, md, rd = (1, 3, 1) if n_detail_cols <= 6 else (0.25, 7.5, 0.25)
        c1d, c2d, c3d = st.columns([ld, md, rd], vertical_alignment="center")
        with c2d:
            detail_height = _calc_height(len(game_view_t), pad_px=160, cap_px=1500)
            _build_grid(
                game_view_t,
                theme=theme,
                column_defs=detail_defs,
                pinned_left=('Stat',),
                rank_cols=None,
                rating_cols=None,
                style_expected=False,
                key=f"{state_key}_{view}_detail_grid_{selected_game_id}",
                selection=False,
                min_rating=f_min_rating,
                max_rating=f_max_rating,
                height=detail_height,
                fit_columns=True,
            )

# ===================== public entry =====================
def display_event_tab(dataset_df: pd.DataFrame, folded_df: pd.DataFrame):
    st.subheader("Events", anchor=False)

    season_options = sorted(dataset_df['season'].unique())
    default_season_idx = season_options.index(max(season_options))
    season = st.selectbox('Select Season:', season_options, index=default_season_idx, key='event_season')

    week_options = sorted(dataset_df[dataset_df['season'] == season]['week'].unique())
    if season == max(season_options):
        s_df = dataset_df[((dataset_df['season'] == season) & (dataset_df['actual_away_points'].isnull()))].copy()
        if s_df.shape[0] == 0:
            default_week_idx = week_options.index(max(week_options))
        else:
            default_week_idx = week_options.index(s_df.week.values[0])
    else:
        default_week_idx = week_options.index(max(week_options))
    week = st.selectbox('Select Week:', week_options, index=default_week_idx, key='event_week')

    filtered_df = dataset_df[((dataset_df['season'] == season) & (dataset_df['week'] == week))].copy()

    for col in ['away_offensive_rank','away_defensive_rank','home_offensive_rank','home_defensive_rank']:
        if col in filtered_df.columns:
            filtered_df[col] = filtered_df[col].astype('Int64')
    for col in ['spread_line','expected_spread','total_line','expected_total']:
        if col in filtered_df.columns:
            filtered_df[col] = filtered_df[col].round(2)

    st.write(f"Games for Week {week} in the {season} Season")

    tab_all, tab_ranks, tab_lines, tab_ratings = st.tabs(["All", "Ranks", "Lines", "Ratings"])
    with tab_all:
        _render_games_with_detail(filtered_df, folded_df, view="All", theme="material", state_key="events")
    with tab_ranks:
        _render_games_with_detail(filtered_df, folded_df, view="Ranks", theme="material", state_key="events")
    with tab_lines:
        _render_games_with_detail(filtered_df, folded_df, view="Lines", theme="material", state_key="events")
    with tab_ratings:
        _render_games_with_detail(filtered_df, folded_df, view="Ratings", theme="material", state_key="events")
