import streamlit as st
import folium
from folium import Popup, Icon
from folium.features import CustomIcon

from streamlit_folium import folium_static
import requests
from espn_api_orm.league.api import ESPNLeagueAPI
from espn_api_orm.consts import ESPNSportLeagueTypes, ESPNSportTypes

_BASE_URL = 'https://raw.githubusercontent.com/theedgepredictor'
geocoded_url = f'{_BASE_URL}/venue-data-pump/main/data/geocoding.json'

def create_sports_leagues_dict():
    sports_leagues = {}
    for attr in ESPNSportLeagueTypes:
        value = attr.value
        sport, league = value.split('/')
        if sport not in sports_leagues:
            sports_leagues[sport] = []
        sports_leagues[sport].append(league)
    return sports_leagues

sports_leagues = create_sports_leagues_dict()
sports_leagues = {
    "football": ["nfl", "college-football"]
}

@st.cache_data(ttl=3600)
def fetch_data(url, cache_key=None):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []

class TeamVenueUI:
    def __init__(self):
        self.geocoded_locations = fetch_data(geocoded_url, cache_key='geocoded_locations')
        self.venues = {}
        self.teams_info = []
        self.seasons = []
        self.season_data = []

    def update_state(self):
        st.session_state['selected_sport'] = st.selectbox("Select Sport", list(sports_leagues.keys()), key='sport_select', on_change=self.on_sport_change)
        if 'selected_sport' in st.session_state:
            st.session_state['selected_league'] = st.selectbox("Select League", sports_leagues[st.session_state['selected_sport']], key='league_select', on_change=self.on_league_change)
        if 'selected_league' in st.session_state:
            venues_url = f'{_BASE_URL}/venue-data-pump/main/data/{st.session_state["selected_sport"]}/{st.session_state["selected_league"]}/venues.json'
            teams_info_url = f'{_BASE_URL}/team-data-pump/main/data/{st.session_state["selected_sport"]}/{st.session_state["selected_league"]}/teams.json'
            self.venues = fetch_data(venues_url, cache_key='venues')
            self.teams_info = fetch_data(teams_info_url, cache_key='teams_info')
            sport = ESPNSportTypes(st.session_state['selected_sport'])
            league_api = ESPNLeagueAPI(sport, st.session_state["selected_league"])
            self.seasons = [str(i) for i in league_api.get_seasons() if i >= 2002]
            st.session_state['selected_season'] = st.selectbox("Select Season", self.seasons, key='season_select', on_change=self.on_season_change)
            if 'selected_season' in st.session_state:
                season_data_url = f'{_BASE_URL}/team-data-pump/main/data/{st.session_state["selected_sport"]}/{st.session_state["selected_league"]}/{st.session_state["selected_season"]}/teams.json'
                self.season_data = fetch_data(season_data_url, cache_key='season_data')

    def on_sport_change(self):
        if 'selected_sport' in st.session_state and st.session_state['selected_sport'] != st.session_state['sport_select']:
            if 'selected_league' in st.session_state:
                del st.session_state['selected_league']
            if 'selected_season' in st.session_state:
                del st.session_state['selected_season']
            self.seasons = []

    def on_league_change(self):
        if 'selected_league' in st.session_state and st.session_state['selected_league'] != st.session_state['league_select']:
            if 'selected_season' in st.session_state:
                del st.session_state['selected_season']
            self.seasons = []

    def on_season_change(self):
        if 'selected_season' in st.session_state and st.session_state['selected_season'] != st.session_state['season_select']:
            if 'selected_season' in st.session_state:
                del st.session_state['selected_season']

    def get_team_location(self, venue_id):
        if str(venue_id) in self.venues:
            geocoding_id = self.venues[str(venue_id)]['geocodingId']
            if geocoding_id in self.geocoded_locations:
                location = self.geocoded_locations[geocoding_id]
                return location
        return None

    def render_map(self):
        if self.season_data:
            lat_lon_pairs = []
            m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
            for season_team in self.season_data:
                team_id = season_team['teamId']
                team_info = next((team for team in self.teams_info if team['id'] == team_id), None)
                if team_info:
                    team_name = team_info['displayName']
                    venue_id = team_info['venueId']
                    location = self.get_team_location(venue_id)
                    location_name = location['name'] if location else None
                    location_address = location['codedAddress'] if location else None
                    lat, lon = (location['latitude'], location['longitude']) if location else (None, None)
                    if lat and lon:
                        lat_lon_pairs.append((lat, lon))
                        popup_html = f"""
                            <h1>{location_name}</h1><br>
                            Address: {location_address} <br>
                            <p>Home of the {team_name}</p>
                        """
                        if team_info.get("logo"):
                            icon_obj = CustomIcon(team_info["logo"], icon_size=(40, 40))
                        else:
                            icon_obj = Icon(
                                color='white',
                                icon_color="#" + team_info["color"] if team_info["color"] else "black",
                                icon='football',
                                prefix='fa'
                            )
                        folium.Marker(
                            location=[lat, lon],
                            popup=Popup(html=popup_html),
                            icon=icon_obj
                        ).add_to(m)
            if lat_lon_pairs:
                avg_lat = sum([pair[0] for pair in lat_lon_pairs]) / len(lat_lon_pairs)
                avg_lon = sum([pair[1] for pair in lat_lon_pairs]) / len(lat_lon_pairs)
                m.location = [avg_lat, avg_lon]
            folium_static(m, width=None, height=700)

    def run(self):
        self.update_state()
        self.render_map()

def display_venues_tab():
    st.subheader("Venues", anchor=False)
    app = TeamVenueUI()
    app.run()
