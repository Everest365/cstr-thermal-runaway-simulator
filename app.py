import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from physics import run_simulation

st.set_page_config(page_title="CSTR Thermal Runaway Simulator", layout="wide")
st.title("CSTR Process Safety & Thermal Runaway Simulator")
st.markdown("Dynamic mass and energy balance modeling for an exothermic $A \\rightarrow B$ reaction.")

# Sidebar Controls
st.sidebar.header("Operating Conditions")
Tc = st.sidebar.slider("Cooling Jacket Temp, Tc (K)", 280.0, 320.0, 300.0, 0.5)
T0 = st.sidebar.slider("Feed Temperature, T0 (K)", 330.0, 380.0, 350.0, 1.0)
Ca0 = st.sidebar.slider("Feed Concentration, Ca0 (mol/L)", 0.5, 1.5, 1.0, 0.05)
q = st.sidebar.slider("Volumetric Flow Rate, q (L/min)", 50.0, 150.0, 100.0, 5.0)

st.sidebar.header("Failure Scenarios")
pump_failure = st.sidebar.checkbox("Simulate Cooling Pump Failure (t = 3 min)", value=False)

custom = {"T0": T0, "Ca0": Ca0, "q": q}
t, Ca, T = run_simulation(Tc=Tc, custom_params=custom, pump_failure=pump_failure)

max_T = max(T)
runaway_threshold = 400.0

# Key Metrics Row
col1, col2, col3 = st.columns(3)
col1.metric("Peak Reactor Temp", f"{max_T:.1f} K", delta=f"{max_T - T0:.1f} K vs Feed", delta_color="inverse")
col2.metric("Final Conversion", f"{(1 - Ca[-1]/Ca0)*100:.1f}%")
if max_T >= runaway_threshold:
    col3.error("STATUS: THERMAL RUNAWAY")
else:
    col3.success("STATUS: SAFE STEADY STATE")

# Top Row: Time Series Plots
fig = make_subplots(rows=1, cols=2, subplot_titles=("Reactor Temperature (K)", "Reactant Concentration Ca (mol/L)"))
fig.add_trace(go.Scatter(x=t, y=T, name="Temperature", line=dict(color="firebrick", width=3)), row=1, col=1)
fig.add_hline(y=runaway_threshold, line_dash="dash", line_color="orange", annotation_text="Runaway Limit (400 K)", row=1, col=1)
fig.add_trace(go.Scatter(x=t, y=Ca, name="Concentration", line=dict(color="royalblue", width=3)), row=1, col=2)
fig.update_layout(height=400, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# Bottom Row: Phase-Plane Trajectory
st.subheader("Phase-Plane Stability Analysis (T vs. Concentration)")
phase_fig = go.Figure()
phase_fig.add_trace(go.Scatter(
    x=Ca, y=T, mode="lines", name="Trajectory",
    line=dict(color="purple", width=3)
))
phase_fig.add_trace(go.Scatter(
    x=[Ca[0]], y=[T[0]], mode="markers", name="Start (t=0)",
    marker=dict(size=10, color="green")
))
phase_fig.add_trace(go.Scatter(
    x=[Ca[-1]], y=[T[-1]], mode="markers", name="End (t=10m)",
    marker=dict(size=10, color="red")
))
phase_fig.update_layout(
    xaxis_title="Reactant Concentration Ca (mol/L)",
    yaxis_title="Reactor Temperature T (K)",
    height=400
)
st.plotly_chart(phase_fig, use_container_width=True)
