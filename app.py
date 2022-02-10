# -*- coding: utf-8 -*-

from flask import Flask
import json
import requests
import pandas as pd
import folium
from folium.plugins import MarkerCluster

# Récupération via l'API parkings et création du df après formatage du json

parkings = "https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=disponibilite-parkings&q=&rows=1000&facet=libelle&facet=ville&facet=etat"
r_parkings = requests.get(parkings)
df_parkings = pd.json_normalize(r_parkings.json(),record_path="records")

# Récupération via l'API parkings et création du df après formatage du json

velos = "https://opendata.lillemetropole.fr/explore/dataset/vlille-realtime/download/?format=json&timezone=Europe/Paris&lang=fr"
r_velos = requests.get(velos)
df_velos = pd.json_normalize(r_velos.json())

# création des couleurs pour les parkings

def colors(x,y):
  if x/y > 0.2:
    return "green"
  if x/y < 0.2 and x/y > 0.1:
    return "orange"
  if x/y < 0.1 :
    return "red"
  if x <= 5 :
    return "black"

# création des couleurs pour les vélos

def colors_velos(x):
  if x > 4:
    return "green"
  if x <= 4 and x > 2:
    return "orange"
  if x <= 2 and x > 0:
    return "red"
  if x == 0:
    return "black"

app = Flask(__name__)

@app.route("/")

def home():


    map =folium.Map(location=[50.636788993222, 3.0730428283576],zoom_start=14)

# mise en place de cercle pour les places de parkings
# taille du cercle Capacité max du parking
# couleur du cercle pourcentage de places restantes

    mc_parkings = MarkerCluster()
    for index, row in df_parkings.iterrows():
        mc_parkings.add_child(folium.Marker(location=[row['fields.geometry.coordinates'][1],row['fields.geometry.coordinates'][0]],
                                            popup=f'<strong>{row["fields.libelle"]},\n{row["fields.dispo"]} places dispo</strong>',
                                            tooltip='<strong>Click here to see Popup</strong>',
                                            icon=folium.Icon(color=colors(row["fields.dispo"],row["fields.max"]),
                                                             icon="info-sign")))
                    
        folium.Circle(location=[row['fields.geometry.coordinates'][1],row['fields.geometry.coordinates'][0]],
                      color=colors(row["fields.dispo"],row["fields.max"]),
                      fill=True,
                      fill_color=colors(row["fields.dispo"],row["fields.max"]),
                      radius=row["fields.max"]/30).add_to(map)

    map.add_child(mc_parkings)

# mise en place de cercle pour les vélos
# taille du cercle Nombre de places disponibles
# couleur du cercle Nombre de vélos disponibles



    for index, row in df_velos.iterrows():

        folium.Circle(location=[row["fields.geo"][0],row["fields.geo"][1]],
                      color=colors_velos(row["fields.nbvelosdispo"]),
                      popup=f'<strong>{row["fields.nom"]},\n{row["fields.nbvelosdispo"]} vélos dispo,\n{row["fields.nbplacesdispo"]} places dispo</strong>',
                      tooltip='<strong>Click here to see Popup</strong>',
                      fill=True,fill_color=colors_velos(row["fields.nbvelosdispo"]),
                      radius=row["fields.nbplacesdispo"]).add_to(map)

# Ajout du choix de type de carte
    folium.TileLayer('Stamen Terrain').add_to(map)
    folium.TileLayer('Stamen Toner').add_to(map)
    folium.TileLayer('Stamen Water Color').add_to(map)
    folium.TileLayer('cartodbpositron').add_to(map)
    folium.TileLayer('cartodbdark_matter').add_to(map)
    folium.LayerControl().add_to(map)


    return map._repr_html_()

if __name__ == "__main__":
    app.run(debug=True)


