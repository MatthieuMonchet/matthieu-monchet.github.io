# -*- coding: utf-8 -*-

from flask import Flask
import json
import requests
import pandas as pd
import folium
from folium.plugins import MarkerCluster

parkings = "https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=disponibilite-parkings&q=&rows=1000&facet=libelle&facet=ville&facet=etat"
r_parkings = requests.get(parkings)
df_parkings = pd.json_normalize(r_parkings.json(),record_path="records")

def colors(x,y):
  if x/y > 0.2:
    return "green"
  if x/y < 0.2 and x/y > 0.1:
    return "orange"
  if x/y < 0.1 :
    return "red"

app = Flask(__name__)

@app.route("/")

def home():


    map =folium.Map(location=[50.636788993222, 3.0730428283576],zoom_start=14)

    folium.TileLayer().add_to(map) # Sets Tile Theme to (Dark Theme)
    mc = MarkerCluster()
    for index, row in df_parkings.iterrows():
        mc.add_child(folium.Marker(location=[row['fields.geometry.coordinates'][1],row['fields.geometry.coordinates'][0]],
                              tooltip=row["fields.libelle"],
                              icon=folium.Icon(color=colors(row["fields.dispo"],row["fields.max"]),
                              icon="info-sign")))
        folium.Circle(location=[row['fields.geometry.coordinates'][1],row['fields.geometry.coordinates'][0]],
                 color=colors(row["fields.dispo"],row["fields.max"]),
                 fill=True,
                 fill_color=colors(row["fields.dispo"],row["fields.max"]),
                 radius=row["fields.max"]/30).add_to(map)
        map.add_child(mc)


    return map._repr_html_()

if __name__ == "__main__":
    app.run(debug=True)


