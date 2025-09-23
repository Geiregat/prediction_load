import streamlit as st
import pandas as pd

# Interpolation function for load per step
def get_load_per_step(speed, screening_data):
    for i in range(len(screening_data) - 1):
        s1, load1 = screening_data[i]
        s2, load2 = screening_data[i + 1]
        if s1 <= speed <= s2:
            ratio = (speed - s1) / (s2 - s1)
            load = load1 + ratio * (load2 - load1)
            return load
    return screening_data[-1][1]

# Streamlit app
st.title("Run Load Predictor")

st.markdown("### Step 1: Enter your screening data")
st.write("Add rows with speed (km/h) and load per step.")

# Default screening data example
default_data = {
    "Speed (km/h)": [8, 10, 12, 14],
    "Load per step": [1.5, 1.7, 1.9, 2.2],  # example load per step
}
df = st.data_editor(pd.DataFrame(default_data), num_rows="dynamic")

# Convert to list of tuples for interpolation
screening_data = df.to_records(index=False).tolist()
screening_data = [(row[0], row[1]) for row in screening_data]
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
    cadence = st.number_input(f"Cadence (steps/min) for segment {i+1}", min_value=0, max_value=300, value=160)

    load_per_step = get_load_per_step(speed, screening_data)
    segment_load = load_per_step * cadence * duration/2  # total load = load per step * steps/min * minutes
    run_plan.append((speed, duration, load_per_step, cadence, segment_load))

    total_load += segment_load
    total_duration += duration

st.markdown("### Step 3: Results")
results_df = pd.DataFrame(run_plan, columns=["Speed (km/h)", "Duration (min)", "Load per step", "Cadence", "Segment Load"])
st.dataframe(results_df)

st.metric("Total Load", f"{total_load:.1f}")
st.metric("Total Duration", f"{total_duration} min")
