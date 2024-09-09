import streamlit as st
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import pandas as pd

# Login-Funktion
def login(username_v, passwort_v):
    try:
        # Initialisiere GIS
        gis = GIS(username=username_v, password=passwort_v)
        return gis
    except Exception as e:
        st.error(f"Login fehlgeschlagen: {e}")
        return None

# Funktion zur Konvertierung des DataFrames in Features
def df_to_features(df):
    features = []
    for _, row in df.iterrows():
        feature = {
            "attributes": row.to_dict()
        }
        features.append(feature)
    return features

# Funktion zum Hochladen der Features in den Feature Layer
def update_features(layer, features):
    result = layer.edit_features(updates=features)
    return result

# Streamlit-App-Layout
st.title("Nebenflächenberechnung")

#Initialisierung Session states: 
if 'df' not in st.session_state:
    st.session_state.df = None
if 'gis' not in st.session_state:
    st.session_state.gis = None
if 'flayer' not in st.session_state:
    st.session_state.flayer = None

# Eingabefelder für Benutzername und Passwort
username_v = st.text_input("Benutzername")
passwort_v = st.text_input("Passwort", type="password")

# Knopf zum Einloggen
if st.button('Einloggen'):
    gis = login(username_v, passwort_v)
    if gis:
        st.session_state.gis = gis
        st.success("Erfolgreich eingeloggt.")
    else:
        st.session_state.gis = None

# Knopf zum Daten abrufen
if st.session_state.gis is not None and st.button('Daten herunterladen'):
    # Feature Layer abrufen
    item_id = "99c41e925ec4402886932319b5b80c3f"
    table_item = st.session_state.gis.content.get(item_id)
    st.session_state.flayer = table_item.layers[0]

    # Features als DataFrame herunterladen
    st.session_state.df = pd.DataFrame.spatial.from_layer(st.session_state.flayer)
    st.success("Daten erfolgreich heruntergeladen.")


if st.session_state.df is not None: 

    # Create the grouped DataFrame
    grouped_df = st.session_state.df.groupby(['haus', 'category', 'Faktor'])['Area_srf'].sum().reset_index()
    grouped_df = st.data_editor(grouped_df)

    if st.button("Nebenfläche aktualisieren"):
        # Perform the left join
        df_join = grouped_df[['haus', 'category', 'Faktor']]
        st.session_state.df_update = st.session_state.df
        st.session_state.df_update = st.session_state.df_update.drop(columns='Faktor', errors='ignore')
        st.session_state.df_update = st.session_state.df_update.merge(df_join, on=['haus', 'category'], how='left')
        st.session_state.df_update['NF'] = st.session_state.df_update['Faktor'] * st.session_state.df_update['Area_srf']
        #st.session_state.df_update.head()
        columns_to_display = ['OBJECTID', 'haus', 'category', 'Faktor','Area_srf', 'NF']
        st.write(st.session_state.df_update[columns_to_display])

    # Button zum Hochladen der Daten
    if st.button("Daten hochladen"):
        edited_features = df_to_features(st.session_state.df_update)
        update_result = update_features(st.session_state.flayer, edited_features)
        if update_result['updateResults'][0]['success']:
            st.success("Daten erfolgreich hochgeladen!")
        else:
            st.error("Fehler beim Hochladen der Daten!")





