from cmath import nan
from ctypes import sizeof
from multiprocessing.sharedctypes import Value
from statistics import mode
from tempfile import SpooledTemporaryFile
import dash
from dash import Dash, html, dcc, Output, Input, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from tenacity import before_log
import utilities as ut
import numpy as np
import os
import re

app = Dash(__name__)


list_of_subjects = []
subj_numbers = []
number_of_subjects = 0

folder_current = os.path.dirname(__file__)
print(folder_current)
folder_input_data = os.path.join(folder_current, "input_data")
for file in os.listdir(folder_input_data):
    
    if file.endswith(".csv"):
        number_of_subjects += 1
        file_name = os.path.join(folder_input_data, file)
        print(file_name)
        list_of_subjects.append(ut.Subject(file_name))


df = list_of_subjects[0].subject_data


for i in range(number_of_subjects):
    subj_numbers.append(int(list_of_subjects[i].subject_id))

data_names = ["SpO2 (%)" ,"Temp (C)","Blood Flow (ml/s)"]
algorithm_names = ['min','max']
blood_flow_functions = ['CMA','SMA','Show Limits']


fig0= go.Figure()
fig1= go.Figure()
fig2= go.Figure()
fig3= go.Figure()

fig0 = px.line(df, x="Time (s)", y = "SpO2 (%)")
fig1 = px.line(df, x="Time (s)", y = "Temp (C)")
fig2 = px.line(df, x="Time (s)", y = "Blood Flow (ml/s)")
fig3 = px.line(df, x="Time (s)", y = "Blood Flow (ml/s)")

app.layout = html.Div(children=[
    html.H1(children='Cardiopulmonary Bypass Dashboard'),

    html.Div(children='''
        Hier könnten Informationen zum Patienten stehen....
    '''),

    dcc.Checklist(
    id= 'checklist-algo',
    options=algorithm_names,
    inline=False
    ),

    html.Div([
        dcc.Dropdown(options = subj_numbers, placeholder='Select a subject', value='1', id='subject-dropdown'),
    html.Div(id='dd-output-container')
    ],
        style={"width": "15%"}
    ),

    dcc.Graph(
        id='dash-graph0',
        figure=fig0
    ),

    dcc.Graph(
        id='dash-graph1',
        figure=fig1
    ),
    dcc.Graph(
        id='dash-graph2',
        figure=fig2
    ),

    dcc.Checklist(
        id= 'checklist-bloodflow',
        options=blood_flow_functions,
        inline=False
    ),
    dcc.Graph(
        id='dash-graph3',
        figure=fig3
    )
])
### Callback Functions ###
## Graph Update Callback
@app.callback(
    # In- or Output('which html element','which element property')
    Output('dash-graph0', 'figure'),
    Output('dash-graph1', 'figure'),
    Output('dash-graph2', 'figure'),
    Input('subject-dropdown', 'value'),
    Input('checklist-algo','value')
)
def update_figure(value, algorithm_checkmarks):
    print("Current Subject: ",value)
    print("current checked checkmarks are: ", algorithm_checkmarks)
    
    ts = list_of_subjects[int(value)-1].subject_data
    #SpO2
    fig0 = px.line(ts, x="Time (s)", y = data_names[0])
    # Blood Flow
    fig1 = px.line(ts, x="Time (s)", y = data_names[1])
    # Blood Temperature
    fig2 = px.line(ts, x="Time (s)", y = data_names[2])

    ### Aufgabe 2: Min / Max ###
    if ('min' in algorithm_checkmarks):     #Checks for 'min' in algorithm_checkmarks
        print("min")
        MinPos = ut.ShowMinimum(ts).to_numpy()  #X-Positionen der Minimalen Werte als Numpy Array
        MinPos = np.delete(MinPos, 0)           #Erster Wert ist Minimum von der Zeit, wird nicht benötigt
        MinValues = []                            #Leeres Array für Minimalwerte Erstellen

        for i in range(3):                      #Minimale Werte in Array übertragen
            MinValues.append((ts.at[MinPos[i], data_names[i]]))

        fig0.add_trace(go.Scatter(name = 'Minimum', x = [MinPos[0]], y=[MinValues[0]], mode = 'markers', marker_symbol = 'triangle-down', marker_size = 10, marker_color='orange'))
        fig1.add_trace(go.Scatter(name = 'Minimum', x = [MinPos[1]], y=[MinValues[1]], mode = 'markers', marker_symbol = 'triangle-down', marker_size = 10, marker_color='orange'))
        fig2.add_trace(go.Scatter(name = 'Minimum', x = [MinPos[2]], y=[MinValues[2]], mode = 'markers', marker_symbol = 'triangle-down', marker_size = 10, marker_color='orange'))
        
    if('max' in algorithm_checkmarks):      #Checks for 'max' in algorithm_checkmarks 
        print("max")
        MaxPos = ut.ShowMaximum(ts).to_numpy()  #X-Positionen der Maximalen Werte als Numpy Array
        MaxPos = np.delete(MaxPos,0)            #Erster Wert ist Maximum von der Zeit, wird nicht benötigt
        MaxValues = []

        for i in range(3):                      #Maximale Werte in Array übertragen
            MaxValues.append((ts.at[MaxPos[i], data_names[i]]))
        
        fig0.add_trace(go.Scatter(name = 'Maximum', x = [MaxPos[0]], y=[MaxValues[0]], mode = 'markers', marker_symbol = 'triangle-up', marker_size = 10, marker_color='springgreen'))
        fig1.add_trace(go.Scatter(name = 'Maximum', x = [MaxPos[1]], y=[MaxValues[1]], mode = 'markers', marker_symbol = 'triangle-up', marker_size = 10, marker_color='springgreen'))
        fig2.add_trace(go.Scatter(name = 'Maximum', x = [MaxPos[2]], y=[MaxValues[2]], mode = 'markers', marker_symbol = 'triangle-up', marker_size = 10, marker_color='springgreen'))
        
    return fig0, fig1, fig2 


## Blodflow Simple Moving Average Update
@app.callback(
    # In- or Output('which html element','which element property')
    Output('dash-graph3', 'figure'),
    Input('subject-dropdown', 'value'),
    Input('checklist-bloodflow','value')
)
def bloodflow_figure(value, bloodflow_checkmarks):
    
    ## Calculate Moving Average: Aufgabe 2
    print(bloodflow_checkmarks)
    bf = list_of_subjects[int(value)-1].subject_data
    fig3 = px.line(bf, x="Time (s)", y="Blood Flow (ml/s)")

    if('SMA' in bloodflow_checkmarks):
        bf = list_of_subjects[int(value)-1].subject_data
        bf["Blood Flow (ml/s) - SMA"] = ut.calculate_SMA(bf["Blood Flow (ml/s)"], 10)
        fig3.add_trace(go.Scatter(name = "SMA - Blood Flow",x = bf["Time (s)"], y = bf["Blood Flow (ml/s) - SMA"], marker_color = 'magenta'))

    if ('CMA' in bloodflow_checkmarks):
        bf = list_of_subjects[int(value)-1].subject_data
        bf["Blood Flow (ml/s) - CMA"] = ut.calculate_CMA(bf["Blood Flow (ml/s)"],2)
        fig3 = px.line(bf, x = "Time (s)", y = "Blood Flow (ml/s) - CMA")

    if ('Show Limits' in bloodflow_checkmarks):                  #Überprüfe, ob 'Show Limits' angekreuzt wurde
        Avg = float(bf[['Blood Flow (ml/s)']].mean())           #Durchschnitt des Blutflusses berechnen
        UpperLimit = Avg * 1.15                                 #Obere 15% grenze berechnen
        LowerLimit = Avg * 0.85                                 #untere 15% grenze berechnen
        
        # Linien zeichnen
        fig3.add_trace(go.Scatter(name = "Durchschnitt", x = [0, 481], y = [Avg, Avg], mode = "lines", marker_color = "red"))
        fig3.add_trace(go.Scatter(name = "Oberes 15% Interval", x = [0, 481], y = [UpperLimit, UpperLimit], mode = "lines", marker_color='springgreen'))
        fig3.add_trace(go.Scatter(name = "Unteres 15% Interval", x = [0, 481], y = [LowerLimit, LowerLimit], mode = "lines", marker_color='orange'))
        
        if('SMA' in bloodflow_checkmarks):                                    #Überprüfe, ob 'SMA' zusätzlich angekreuzt wurde
            CritVal = bf[(bf["Blood Flow (ml/s) - SMA"] > UpperLimit) | (bf["Blood Flow (ml/s) - SMA"] < LowerLimit)] #Kritische Werte aus SMA filtern
            #print(CritVal['SMA'])
            LegendName = "Dauer Kritischer Werte: " + str(CritVal["Blood Flow (ml/s) - SMA"].count()) +'s'
            fig3.add_trace(go.Scatter(name = LegendName, x = CritVal['Time (s)'], y = CritVal["Blood Flow (ml/s) - SMA"], mode = "markers", marker_color='red'))
            
    return fig3

if __name__ == '__main__':
    app.run_server(debug=True)