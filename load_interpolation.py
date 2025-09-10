import streamlit as st
import pandas as pd

# Convert min/km (minutes + seconds) to km/h
def minpkm_to_kmh(minutes, seconds):
    total_min = minutes + seconds / 60
    return 60 / total_min if total_min != 0 else 0

# Interpolation function (only load now)
def get_load(speed_kmh, screening_data):
    for i in range(len(screening_data) - 1):
        s1_kmh, load1 = screening_data[i]
        s2_kmh, load2 = screening_data[i + 1]
        if s1_kmh <= speed_kmh <= s2_kmh:
            ratio = (speed_kmh - s1_kmh) / (s2_kmh - s1_kmh)
            load = load1 + ratio * (load2 - load1)
            return load
    return screening_data[-1][1]

# Streamlit app
st.title("Run Load Predictor")

st.markdown("### Step 1: Enter your screening data")
st.write("Add rows with speed (min/km) and load per minute. Enter minutes and seconds separately.")

# Default screening data example
default_data = {
    "Minutes": [7, 6, 5, 4],
    "Seconds": [30, 0, 0, 18],  # converted from 7:30, 6:00, 5:00, 4:18 min/km
    "Load": [100, 150, 200, 260],
}
df = st.data_editor(pd.DataFrame(default_data), num_rows="dynamic")

# Convert screening data to km/h internally
screening_data = df.to_records(index=False).tolist()
screening_data = [(minpkm_to_kmh(row[0], row[1]), row[2]) for row in screening_data]
screening_data.sort(key=lambda x: x[0])  # sort by km/h

st.markdown("### Step 2: Enter your run plan")
n_segments = st.number_input("How many segments in your run?", min_value=1, max_value=30, value=1)

run_plan = []
total_load = 0
total_duration = 0

for i in range(n_segments):
    st.subheader(f"Segment {i+1}")
    minutes = st.number_input(f"Minutes per km for segment {i+1}", min_value=1, max_value=20, value=6)
    seconds = st.number_input(f"Seconds per km for segment {i+1}", min_value=0, max_value=59, value=0)
    speed_kmh = minpkm_to_kmh(minutes, seconds)
    duration = st.number_input(f"Duration (minutes) for segment {i+1}", min_value=1, max_value=300, value=30)
    cadence = st.number_input(f"Cadence for segment {i+1}", min_value=0, max_value=300, value=0)

    load = get_load(speed_kmh, screening_data)
    segment_load = load * duration
    run_plan.append((f"{minutes}:{seconds:02d}", duration, load, cadence, segment_load))

    total_load += segment_load
    total_duration += duration

st.markdown("### Step 3: Results")
results_df = pd.DataFrame(run_plan, columns=["Speed (min/km)", "Duration (min)", "Load/min", "Cadence", "Segment Load"])
st.dataframe(results_df)

st.metric("Total Load", f"{total_load:.1f}")
st.metric("Total Duration", f"{total_duration} min")
