import streamlit as st
import pandas as pd

# Interpolation function
def get_load_and_cadence(speed, screening_data):
    for i in range(len(screening_data) - 1):
        s1, load1, cad1 = screening_data[i]
        s2, load2, cad2 = screening_data[i + 1]
        if s1 <= speed <= s2:
            # Linear interpolation
            ratio = (speed - s1) / (s2 - s1)
            load = load1 + ratio * (load2 - load1)
            cadence = cad1 + ratio * (cad2 - cad1)
            return load, cadence
    return screening_data[-1][1], screening_data[-1][2]


# Streamlit app
st.title("Run Load Predictor")

st.markdown("### Step 1: Enter your screening data")
st.write("Add rows with speed (km/h), load, and cadence.")

# Default screening data example
default_data = {
    "Speed (km/h)": [8, 10, 12, 14],
    "Load": [100, 150, 200, 260],
    "Cadence": [160, 165, 170, 175],
}
df = st.data_editor(pd.DataFrame(default_data), num_rows="dynamic")

# Convert to list of tuples for interpolation
screening_data = df.to_records(index=False).tolist()
screening_data = [(row[0], row[1], row[2]) for row in screening_data]
screening_data.sort(key=lambda x: x[0])  # sort by speed

st.markdown("### Step 2: Enter your run plan")
n_segments = st.number_input("How many segments in your run?", min_value=1, max_value=10, value=1)

run_plan = []
total_load = 0
total_duration = 0

for i in range(n_segments):
    st.subheader(f"Segment {i+1}")
    speed = st.number_input(f"Speed (km/h) for segment {i+1}", min_value=1.0, max_value=30.0, value=10.0)
    duration = st.number_input(f"Duration (minutes) for segment {i+1}", min_value=1, max_value=300, value=30)

    load, cadence = get_load_and_cadence(speed, screening_data)
    segment_load = load * duration
    run_plan.append((speed, duration, load, cadence, segment_load))

    total_load += segment_load
    total_duration += duration

st.markdown("### Step 3: Results")
results_df = pd.DataFrame(run_plan, columns=["Speed (km/h)", "Duration (min)", "Load/min", "Cadence", "Segment Load"])
st.dataframe(results_df)

st.metric("Total Load", f"{total_load:.1f}")
st.metric("Total Duration", f"{total_duration} min")
