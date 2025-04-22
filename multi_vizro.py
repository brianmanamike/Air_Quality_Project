import requests
import pandas as pd
import webbrowser
import threading
import time

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data

# STEP 1: Authenticate and fetch sensor data
login_url = "https://server.uzimaconnect.com/api/users/login"
login_data = {
    "email": "diana.evans1@example.com",
    "password": "SecurePassword123"
}
login_response = requests.post(login_url, json=login_data)
token = login_response.json()["token"]

headers = {"Authorization": f"Bearer {token}"}
readings_url = "https://server.uzimaconnect.com/api/sensor_readings"
response = requests.get(readings_url, headers=headers)
df = pd.DataFrame(response.json())
df["timestamp"] = pd.to_datetime(df["timestamp"])

# PAGE 1 - Air Quality Overview by Site
page1 = vm.Page(
    title="Air Quality Overview by Site",
    components=[
        vm.Card(text="This dashboard provides insights into environmental indicators like air pollutants, humidity, and temperature, grouped by site."),
        vm.Graph(
            id="hist_chart",
            figure=px.histogram(df, x="facility_name", y="humidity", color="facility_name", barmode="group", template="plotly_white")
            .update_layout(font=dict(family="Trebuchet MS", size=14, color="#333"), xaxis_title="Facility Name", xaxis_tickangle=45, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, visible=False))
        ),
        vm.Graph(
            id="boxplot",
            figure=px.box(df, x="facility_name", y="humidity", color="facility_name", template="plotly_white")
            .update_layout(font=dict(family="Trebuchet MS", size=14, color="#333"), xaxis_title="Facility Name", yaxis_title="Humidity (%)", xaxis_tickangle=45, legend=dict(visible=False))
        ),
        vm.Button(text="📥 Download CSV", actions=[vm.Action(function=export_data(data=df, file_format="csv", filename="air_quality_data.csv"))])
    ],
    controls=[vm.Filter(column="facility_name", selector=vm.Dropdown(value=["ALL"]))]
)

# PAGE 2 - PM25 Over Time and Site Comparison
page2 = vm.Page(
    title="PM25 Over Time and Site Comparison",
    path="timestamp-vs-pm25",
    components=[
        vm.Graph(
            id="line_chart",
            figure=px.line(df, x="timestamp", y="pm25", title="PM25 Over Time", template="plotly_white")
            .update_layout(font=dict(family="Trebuchet MS", size=14, color="#333"), xaxis_title="Timestamp", yaxis_title="PM25 (µg/m³)", xaxis_tickangle=45, showlegend=False)
        ),
        vm.Graph(
            id="boxplot_pm25",
            figure=px.box(df, x="facility_name", y="pm25", color="facility_name", title="PM25 Distribution by Facility", template="plotly_white")
            .update_layout(font=dict(family="Trebuchet MS", size=14, color="#333"), xaxis_title="Facility Name", yaxis_title="PM25 (µg/m³)", xaxis_tickangle=45, legend=dict(visible=False))
        ),
        vm.Button(text="📥 Download CSV", actions=[vm.Action(function=export_data(data=df, file_format="csv", filename="pm25_data.csv"))])
    ]
)

# PAGE 3 - CO2 Levels Over Time
page3 = vm.Page(
    title="CO2 Levels Over Time",
    path="co2-levels",
    components=[
        vm.Graph(
            id="area_chart",
            figure=px.area(df, x="timestamp", y="co2", title="CO2 Levels Over Time", template="plotly_white")
            .update_layout(font=dict(family="Trebuchet MS", size=14, color="#333"), xaxis_title="Timestamp", yaxis_title="CO2 (ppm)", xaxis_tickangle=45, showlegend=False)
        ),
        vm.Button(text="📥 Download CSV", actions=[vm.Action(function=export_data(data=df, file_format="csv", filename="co2_data.csv"))])
    ]
)

# PAGE 4 - Temperature Over Time with Site Filter + VOCs vs Temperature Scatter Plot
page4 = vm.Page(
    title="Temperature Over Time by Site",
    path="temperature-over-time",
    components=[
        vm.Graph(
            id="temperature_line_chart",
            figure=px.line(df, x="timestamp", y="temperature", color="facility_name", title="Temperature Trends by Site", template="plotly_white")
            .update_layout(font=dict(family="Trebuchet MS", size=14, color="#333"), xaxis_title="Timestamp", yaxis_title="Temperature (°C)", xaxis_tickangle=45, legend_title_text="Facility")
        ),
        vm.Graph(
            id="scatter_voc_temp",
            figure=px.scatter(df, x="temperature", y="vocs", color="facility_name", title="VOCs vs Temperature by Site", template="plotly_white")
            .update_layout(font=dict(family="Trebuchet MS", size=14, color="#333"), xaxis_title="Temperature (°C)", yaxis_title="VOCs (ppb)", legend_title_text="Facility")
        ),
        vm.Button(text="📥 Download CSV", actions=[vm.Action(function=export_data(data=df, file_format="csv", filename="temperature_vocs_data.csv"))])
    ],
    controls=[vm.Filter(column="facility_name", selector=vm.Dropdown(value=["ALL"]))]
)

# Dashboard object
dashboard = vm.Dashboard(
    title="Environmental Monitoring Dashboard",
    pages=[page1, page2, page3, page4],
    navigation=vm.Navigation(nav_selector=vm.NavBar())
)

# Open browser function
def open_browser():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8050")

# Entry point
if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    Vizro().build(dashboard).run(host="127.0.0.1", port=8051, use_reloader=False)


