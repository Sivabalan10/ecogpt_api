# -*- coding: utf-8 -*-
"""GAIT Analysis.ipynb



Original file is located at
    https://colab.research.google.com/drive/15UVQWIbjpI8eMr1Mb71icJgwEXQf2fmd
"""

!pip install numpy scipy matplotlib

import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

# ---------------------
# Simulation Functions

def simulate_normal_walking():
    np.random.seed(42)
    t = np.linspace(0, 10, 500)  # 10 seconds at 50 Hz
    # Simulate rhythmic walking: sine wave ~1.5 Hz with small noise.
    data = 0.5 * np.sin(2 * np.pi * 1.5 * t) + 0.05 * np.random.randn(len(t))
    return t, data

def simulate_shaking():
    np.random.seed(7)
    t = np.linspace(0, 10, 500)  # 10 seconds at 50 Hz
    # Simulate shaking: random noise with sporadic, high peaks.
    data = 0.3 * np.random.randn(len(t))
    # Introduce random high spikes:
    for i in range(len(t)):
        if np.random.rand() > 0.95:
            data[i] += np.random.uniform(0.8, 1.5)
    return t, data

# ---------------------
# Signal processing: smoothing function
def smooth_signal(data, cutoff=3, fs=50, order=2):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return signal.filtfilt(b, a, data)

# ---------------------
# Gait analysis: detect peaks and check for irregularities.
def analyze_gait(time_data, accel_data, fs=50):
    smoothed = smooth_signal(accel_data, cutoff=3, fs=fs, order=2)
    # Detect peaks (steps)
    peaks, properties = signal.find_peaks(smoothed, height=0.3, distance=20)

    # Compute intervals between peaks (in seconds)
    peak_intervals = np.diff(peaks) / fs
    # Compute variance of the peak amplitudes
    peak_amplitudes = properties["peak_heights"]
    amplitude_variance = np.var(peak_amplitudes)

    # Define thresholds (these values are examples and can be calibrated)
    interval_threshold_min = 0.4
    interval_threshold_max = 1.2
    amplitude_variance_threshold = 0.05  # low variance expected for normal walking

    irregular_intervals = np.any((peak_intervals < interval_threshold_min) | (peak_intervals > interval_threshold_max))
    irregular_amplitudes = amplitude_variance > amplitude_variance_threshold

    gait_valid = not (irregular_intervals or irregular_amplitudes)

    # Prepare results dictionary
    result = {
        "num_steps": len(peaks),
        "peak_intervals": peak_intervals,
        "amplitude_variance": amplitude_variance,
        "gait_valid": gait_valid,
        "smoothed_data": smoothed,
        "peaks": peaks
    }
    return result

def print_analysis(label, result):
    print(f"--- {label} ---")
    print("Detected Steps:", result["num_steps"])
    print("Peak Intervals (s):", result["peak_intervals"])
    print("Variance of Peak Amplitudes:", result["amplitude_variance"])
    if result["gait_valid"]:
        print("Gait Analysis: Data appears to be from genuine walking.\n")
    else:
        print("Gait Analysis: Data appears to be suspicious (possibly shaking).\n")

def plot_results(label, time_data, smoothed_data, peaks):
    plt.figure(figsize=(12, 4))
    plt.plot(time_data, smoothed_data, label="Smoothed Data")
    plt.scatter(time_data[peaks], smoothed_data[peaks], color='red', label="Detected Peaks")
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration (m/s²)")
    plt.title(label)
    plt.legend()
    plt.show()

# ---------------------
# Run both simulations sequentially

# Normal Walking Simulation
time_walking, accel_walking = simulate_normal_walking()
result_walking = analyze_gait(time_walking, accel_walking, fs=50)
print_analysis("Normal Walking", result_walking)
plot_results("Normal Walking", time_walking, result_walking["smoothed_data"], result_walking["peaks"])

# Shaking Simulation
time_shaking, accel_shaking = simulate_shaking()
result_shaking = analyze_gait(time_shaking, accel_shaking, fs=50)
print_analysis("Suspicious Shaking", result_shaking)
plot_results("Suspicious Shaking", time_shaking, result_shaking["smoothed_data"], result_shaking["peaks"])

