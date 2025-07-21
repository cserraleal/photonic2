import streamlit as st
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

st.set_page_config(page_title="Guatemala Map Pin Picker", layout="centered")
st.title("Select Location on Map")

# Default center: Guatemala City
DEFAULT_LAT = 14.6349
DEFAULT_LON = -90.5069

# Initialize session state
if "pin_lat" not in st.session_state:
    st.session_state.pin_lat = DEFAULT_LAT
if "pin_lon" not in st.session_state:
    st.session_state.pin_lon = DEFAULT_LON

# Input: Optional address
address = st.text_input("Enter an address (e.g. 19 Calle 16-29, Zona 7, Mixco, Guatemala):")

# Input: Optional manual coordinates
col1, col2 = st.columns(2)
with col1:
    manual_lat = st.text_input("Latitude (optional):", key="manual_lat")
with col2:
    manual_lon = st.text_input("Longitude (optional):", key="manual_lon")

# If both manual coordinates are entered and valid, update location
if manual_lat and manual_lon:
    try:
        lat_val = float(manual_lat)
        lon_val = float(manual_lon)
        st.session_state.pin_lat = lat_val
        st.session_state.pin_lon = lon_val
        st.success("📍 Pin set from manual coordinates.")
    except ValueError:
        st.warning("⚠️ Please enter valid numbers for latitude and longitude.")

# If address is entered and manual coordinates are not used, geocode it
elif address:
    geolocator = Nominatim(user_agent="streamlit_app")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            st.session_state.pin_lat = location.latitude
            st.session_state.pin_lon = location.longitude
            st.success("📍 Pin set from address.")
        else:
            st.warning("⚠️ Address not found. Try clicking the map instead.")
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        st.error(f"🌐 Geocoding error: {e}")

# Use session state to center map and place marker
lat = st.session_state.pin_lat
lon = st.session_state.pin_lon

# Create satellite map
m = folium.Map(
    location=[lat, lon],
    zoom_start=15,
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri Satellite"
)

# Add marker
folium.Marker([lat, lon], popup="Selected Location").add_to(m)

# Enable map clicks
m.add_child(folium.LatLngPopup())

# Render map
map_data = st_folium(m, width=700, height=500)

# If map is clicked, update coordinates
if map_data and map_data.get("last_clicked"):
    clicked = map_data["last_clicked"]
    st.session_state.pin_lat = clicked["lat"]
    st.session_state.pin_lon = clicked["lng"]
    st.success("📍 Pin updated via map click:")
    st.write(f"Latitude: `{clicked['lat']}`")
    st.write(f"Longitude: `{clicked['lng']}`")
else:
    st.info("📍 Current pin location:")
    st.write(f"Latitude: `{lat}`")
    st.write(f"Longitude: `{lon}`")
