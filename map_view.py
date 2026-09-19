"""Map View Component for Interactive Traffic Network Visualization.

Renders:
- High-definition Folium Leaflet maps
- 3D PyDeck Smart City Spatial Volume layers
- Plotly 2D topological network schematics
"""

import folium
from folium import plugins
import pydeck as pdk
import pandas as pd
import plotly.graph_objects as go
from typing import Optional
from simulation.network import RoadNetwork
from simulation.events import DynamicEventManager, EmergencyVehicle


def create_folium_map(network: RoadNetwork, event_mgr: Optional[DynamicEventManager] = None) -> folium.Map:
    """Generates an interactive Folium map with road links, signal nodes, and emergency tracking."""
    lats = [node.lat for node in network.intersections.values()]
    lons = [node.lon for node in network.intersections.values()]
    center = [sum(lats) / len(lats), sum(lons) / len(lons)]

    m = folium.Map(
        location=center,
        zoom_start=15,
        tiles="CartoDB positron",
        control_scale=True
    )

    # 1. DRAW ROAD SEGMENTS
    for u, v, data in network.edges:
        node_u = network.intersections[u]
        node_v = network.intersections[v]
        coords = [[node_u.lat, node_u.lon], [node_v.lat, node_v.lon]]
        
        is_accident = False
        is_closure = False
        is_emergency_path = False
        
        if event_mgr and "accident" in event_mgr.active_events:
            acc_edge = event_mgr.active_events["accident"]["edge"]
            if (u, v) == acc_edge or (v, u) == acc_edge:
                is_accident = True

        if event_mgr and "closure" in event_mgr.active_events:
            cl_edge = event_mgr.active_events["closure"]["edge"]
            if (u, v) == cl_edge or (v, u) == cl_edge:
                is_closure = True

        if event_mgr and event_mgr.active_emergency and event_mgr.active_emergency.is_active:
            path = event_mgr.active_emergency.path
            for p_idx in range(len(path) - 1):
                if (u == path[p_idx] and v == path[p_idx + 1]) or (v == path[p_idx] and u == path[p_idx + 1]):
                    is_emergency_path = True
                    break

        if is_closure:
            line_color = "#E53935"
            line_weight = 8
            dash_array = "8, 8"
            popup_text = f"🚧 ROAD CLOSED: Link J{u+1}-J{v+1}"
        elif is_accident:
            line_color = "#FF5722"
            line_weight = 8
            dash_array = "4, 4"
            popup_text = f"💥 ACCIDENT SCENE: Link J{u+1}-J{v+1}"
        elif is_emergency_path:
            line_color = "#00E5FF"
            line_weight = 7
            dash_array = None
            popup_text = f"🚨 EMERGENCY GREEN CORRIDOR: Link J{u+1}-J{v+1}"
        else:
            avg_q = (node_u.total_queue + node_v.total_queue) / 2.0
            if avg_q > 50:
                line_color = "#D32F2F"
                line_weight = 6
            elif avg_q > 25:
                line_color = "#FFA000"
                line_weight = 5
            else:
                line_color = "#2E7D32"
                line_weight = 4
            dash_array = None
            popup_text = f"Road Link J{u+1} ⮂ J{v+1} | Length: {data['distance']}m"

        folium.PolyLine(
            locations=coords,
            color=line_color,
            weight=line_weight,
            opacity=0.85,
            dash_array=dash_array,
            popup=popup_text
        ).add_to(m)

    # 2. DRAW INTERSECTIONS WITH REAL-TIME SIGNAL LIGHTS
    for node_id, node in network.intersections.items():
        ns_color = "green" if node.signal_color['NS'] == 'GREEN' else "red"
        ew_color = "green" if node.signal_color['EW'] == 'GREEN' else "red"
        
        popup_html = f"""
        <div style="font-family:sans-serif; width:190px;">
            <b style="font-size:13px; color:#1E88E5;">{node.name}</b><br>
            <hr style="margin:4px 0;">
            <b>Active Phase:</b> {'Phase 0 (North-South)' if node.active_phase == 0 else 'Phase 1 (East-West)'}<br>
            <b>Signals:</b> NS: <span style="color:{ns_color}; font-weight:bold;">{node.signal_color['NS']}</span> | 
                            EW: <span style="color:{ew_color}; font-weight:bold;">{node.signal_color['EW']}</span><br>
            <b>Queue Lengths:</b><br>
            • N: {int(node.approaches['N'].queue_length)} | S: {int(node.approaches['S'].queue_length)}<br>
            • E: {int(node.approaches['E'].queue_length)} | W: {int(node.approaches['W'].queue_length)}<br>
            <b>Pedestrians:</b> {int(node.approaches['N'].pedestrian_queue + node.approaches['E'].pedestrian_queue)} waiting
        </div>
        """

        folium.CircleMarker(
            location=[node.lat, node.lon],
            radius=14,
            color="#1A237E",
            fill=True,
            fill_color="#283593",
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=240)
        ).add_to(m)

        badge_html = f"""
        <div style="background-color:rgba(15, 23, 42, 0.88); border-radius:6px; padding:2px 5px; color:#fff; font-size:10px; font-weight:bold; border:1px solid #64748B; width:52px; text-align:center;">
            NS <span style="color:{'#00E676' if ns_color == 'green' else '#FF1744'};">●</span> 
            EW <span style="color:{'#00E676' if ew_color == 'green' else '#FF1744'};">●</span>
        </div>
        """
        folium.Marker(
            location=[node.lat + 0.0008, node.lon],
            icon=folium.DivIcon(html=badge_html, icon_size=(54, 20), icon_anchor=(27, 10))
        ).add_to(m)

    # 3. DRAW EMERGENCY AMBULANCE IF ACTIVE
    if event_mgr and event_mgr.active_emergency and event_mgr.active_emergency.is_active:
        em = event_mgr.active_emergency
        curr_id = em.current_intersection
        next_id = em.next_intersection
        
        if next_id is not None:
            n_curr = network.intersections[curr_id]
            n_next = network.intersections[next_id]
            p = em.progress_on_segment
            amb_lat = n_curr.lat + p * (n_next.lat - n_curr.lat)
            amb_lon = n_curr.lon + p * (n_next.lon - n_curr.lon)
        else:
            n_curr = network.intersections[curr_id]
            amb_lat, amb_lon = n_curr.lat, n_curr.lon

        amb_html = f"""
        <div style="font-size:26px; filter: drop-shadow(0 0 8px #FF1744); animation: pulse 1s infinite;">
            🚑
        </div>
        """
        folium.Marker(
            location=[amb_lat, amb_lon],
            icon=folium.DivIcon(html=amb_html, icon_size=(30, 30), icon_anchor=(15, 15)),
            popup=f"<b>Ambulance {em.vehicle_id}</b><br>Priority Green Corridor Engaged<br>Current: J{curr_id+1} ➔ Next: J{next_id+1 if next_id is not None else 'Arrived'}"
        ).add_to(m)

    return m


def create_pydeck_3d_view(network: RoadNetwork, event_mgr: Optional[DynamicEventManager] = None) -> pdk.Deck:
    """Generates a 3D PyDeck visualization with extruded traffic queue pillars and glowing green wave arcs."""
    lats = [node.lat for node in network.intersections.values()]
    lons = [node.lon for node in network.intersections.values()]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)

    # Node data for 3D columns
    node_rows = []
    for i, node in network.intersections.items():
        # Height proportional to queue depth
        elevation = max(20.0, node.total_queue * 15.0)
        # Color: Cyan if EW green, Emerald if NS green
        color = [0, 229, 255, 220] if node.active_phase == 1 else [16, 185, 129, 220]
        node_rows.append({
            "name": node.name,
            "lat": node.lat,
            "lon": node.lon,
            "elevation": elevation,
            "color": color,
            "queue": int(node.total_queue)
        })
    df_nodes = pd.DataFrame(node_rows)

    # Arc data for connections
    arc_rows = []
    for u, v, _ in network.edges:
        nu = network.intersections[u]
        nv = network.intersections[v]
        
        is_emergency = False
        if event_mgr and event_mgr.active_emergency and event_mgr.active_emergency.is_active:
            p = event_mgr.active_emergency.path
            for idx in range(len(p) - 1):
                if (u == p[idx] and v == p[idx + 1]) or (v == p[idx] and u == p[idx + 1]):
                    is_emergency = True
                    break

        arc_color = [255, 23, 68, 255] if is_emergency else [99, 102, 241, 160]
        arc_rows.append({
            "source": [nu.lon, nu.lat],
            "target": [nv.lon, nv.lat],
            "color": arc_color
        })
    df_arcs = pd.DataFrame(arc_rows)

    column_layer = pdk.Layer(
        "ColumnLayer",
        data=df_nodes,
        get_position=["lon", "lat"],
        get_elevation="elevation",
        elevation_scale=1,
        radius=45,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )

    arc_layer = pdk.Layer(
        "ArcLayer",
        data=df_arcs,
        get_source_position="source",
        get_target_position="target",
        get_source_color="color",
        get_target_color="color",
        get_width=5,
        pickable=False,
    )

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=14.5,
        pitch=52,
        bearing=25
    )

    return pdk.Deck(
        layers=[arc_layer, column_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={"html": "<b>{name}</b><br>Queue: {queue} vehicles<br>Height: {elevation}m"}
    )


def create_network_schematic_fig(network: RoadNetwork, event_mgr: Optional[DynamicEventManager] = None) -> go.Figure:
    """Generates a crystal-clear 2D Plotly topological network schematic."""
    fig = go.Figure()

    grid_pos = {
        0: (0.0, 1.0),
        1: (1.0, 1.0),
        2: (2.0, 1.0),
        3: (0.0, 0.0),
        4: (1.0, 0.0),
        5: (2.0, 0.0),
    }

    for u, v, _ in network.edges:
        x0, y0 = grid_pos[u]
        x1, y1 = grid_pos[v]
        
        is_emergency = False
        if event_mgr and event_mgr.active_emergency and event_mgr.active_emergency.is_active:
            path = event_mgr.active_emergency.path
            for i in range(len(path) - 1):
                if (u == path[i] and v == path[i + 1]) or (v == path[i] and u == path[i + 1]):
                    is_emergency = True
                    break

        line_color = "#00E5FF" if is_emergency else "#475569"
        line_width = 6 if is_emergency else 3

        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode="lines",
            line=dict(color=line_color, width=line_width),
            hoverinfo="none",
            showlegend=False
        ))

    node_x = []
    node_y = []
    node_text = []
    node_colors = []

    for i in range(6):
        node = network.intersections[i]
        x, y = grid_pos[i]
        node_x.append(x)
        node_y.append(y)
        
        phase_str = "NS Green" if node.active_phase == 0 else "EW Green"
        node_colors.append("#10B981" if node.active_phase == 0 else "#3B82F6")
        
        total_q = int(node.total_queue)
        node_text.append(f"<b>{node.name}</b><br>Active: {phase_str}<br>Total Queue: {total_q} veh")

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        marker=dict(size=38, color=node_colors, line=dict(color="#FFFFFF", width=2)),
        text=[f"J{i+1}" for i in range(6)],
        textposition="middle center",
        textfont=dict(color="#FFFFFF", size=13, family="Arial Black"),
        hovertext=node_text,
        hoverinfo="text",
        showlegend=False
    ))

    fig.update_layout(
        title="Urban Arterial Network Topology (6 Intersections)",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.3, 2.3]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.3, 1.3]),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="#E2E8F0"),
        height=320
    )

    return fig
