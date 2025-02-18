import comtrade
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.fftpack import fft
import os
from scipy.signal import find_peaks


class ComtradeAnalyzer:
    def __init__(self, cfg_file, dat_file):
        self.cfg_file = cfg_file
        self.dat_file = dat_file
        self.data = comtrade.Comtrade()
        self.data.load(cfg_file, dat_file)
        self.time = np.array(self.data.time)

    def get_waveforms(self):
        """Extract and return voltage and current waveforms"""
        voltages = []
        currents = []
        voltage_labels = []
        current_labels = []

        for i, name in enumerate(self.data.analog_channel_ids):
            if "V" in name:  # Assuming voltage channels contain 'V'
                voltages.append(self.data.analog[i])
                voltage_labels.append(name)
            elif "I" in name:  # Assuming current channels contain 'I'
                currents.append(self.data.analog[i])
                current_labels.append(name)

        return np.array(voltages), np.array(currents), voltage_labels, current_labels

    def detect_sags_swells(self, threshold=0.1):
        """Detect voltage sags and swells based on deviation threshold"""
        voltages, _, voltage_labels, _ = self.get_waveforms()
        nominal_voltage = np.max(voltages, axis=1)  # Approximate nominal voltage

        events = []
        for i, v in enumerate(voltages):
            sag_indices = np.where(v < (1 - threshold) * nominal_voltage[i])[0]
            swell_indices = np.where(v > (1 + threshold) * nominal_voltage[i])[0]

            if sag_indices.size > 0:
                events.append([voltage_labels[i], "Voltage Sag", self.time[sag_indices[0]]])
            if swell_indices.size > 0:
                events.append([voltage_labels[i], "Voltage Swell", self.time[swell_indices[0]]])

        return events

    def compute_harmonics(self, sampling_rate):
        """Compute harmonic content using FFT"""
        voltages, _, voltage_labels, _ = self.get_waveforms()
        harmonics = []

        for i, v in enumerate(voltages):
            fft_values = np.abs(fft(v))
            freq = np.fft.fftfreq(len(self.time), d=1 / sampling_rate)
            harmonics.append(pd.DataFrame({"Frequency (Hz)": freq[:len(freq) // 2],
                                           f"{voltage_labels[i]} Harmonics": fft_values[:len(freq) // 2]}))

        return harmonics

    def compute_power_factor(self):
        """Compute power factor using voltage and current phase differences"""
        voltages, currents, voltage_labels, current_labels = self.get_waveforms()
        power_factors = []

        for v, i, v_label, i_label in zip(voltages, currents, voltage_labels, current_labels):
            phase_v = np.angle(fft(v)[1])  # Extracting fundamental frequency phase
            phase_i = np.angle(fft(i)[1])
            pf = np.cos(phase_v - phase_i)
            power_factors.append([v_label, i_label, pf])

        return power_factors

    def plot_waveforms(self):
        """Plot voltage and current waveforms"""
        voltages, currents, voltage_labels, current_labels = self.get_waveforms()

        plt.figure(figsize=(10, 5))
        for v, label in zip(voltages, voltage_labels):
            plt.plot(self.time, v, label=label)
        plt.title("Voltage Waveforms")
        plt.xlabel("Time (s)")
        plt.ylabel("Voltage (V)")
        plt.legend()
        plt.show()

        plt.figure(figsize=(10, 5))
        for i, label in zip(currents, current_labels):
            plt.plot(self.time, i, label=label)
        plt.title("Current Waveforms")
        plt.xlabel("Time (s)")
        plt.ylabel("Current (A)")
        plt.legend()
        plt.show()

    def save_to_csv(self, output_path, sampling_rate):
        """Save parsed data, events, harmonics, and power factor analysis to CSV files"""
        voltages, currents, voltage_labels, current_labels = self.get_waveforms()
        events = self.detect_sags_swells()
        power_factors = self.compute_power_factor()
        harmonics = self.compute_harmonics(sampling_rate)

        # Save Waveform Data
        waveform_file = os.path.join(output_path, "waveforms.csv")
        waveform_data = pd.DataFrame({"Timestamp": self.time})
        for i, label in enumerate(voltage_labels):
            waveform_data[label] = voltages[i]
        for i, label in enumerate(current_labels):
            waveform_data[label] = currents[i]
        waveform_data.to_csv(waveform_file, index=False)
        print(f"Waveforms saved to {waveform_file}")

        # Save Events
        events_file = os.path.join(output_path, "events.csv")
        event_data = pd.DataFrame(events, columns=["Channel", "Event Type", "Timestamp"])
        event_data.to_csv(events_file, index=False)
        print(f"Events saved to {events_file}")

        # Save Power Factor Data
        power_factor_file = os.path.join(output_path, "power_factor.csv")
        pf_data = pd.DataFrame(power_factors, columns=["Voltage Channel", "Current Channel", "Power Factor"])
        pf_data.to_csv(power_factor_file, index=False)
        print(f"Power factor saved to {power_factor_file}")

        # Save Harmonics Data
        for i, df in enumerate(harmonics):
            harmonics_file = os.path.join(output_path, f"harmonics_{voltage_labels[i]}.csv")
            df.to_csv(harmonics_file, index=False)
            print(f"Harmonics for {voltage_labels[i]} saved to {harmonics_file}")


# Usage Example:
cfg_path = os.path.abspath("Comtrade_Repository/wv00000061.cfg") # Use file name in the Comtrade Repository folder
dat_path = os.path.abspath("Comtrade_Repository/wv00000061.dat") # Use file name in the Comtrade Repository folder

analyzer = ComtradeAnalyzer(cfg_path, dat_path)
analyzer.plot_waveforms()
print("Detected Events:", analyzer.detect_sags_swells())
print("Power Factor:", analyzer.compute_power_factor())

output_dir = "Analysis_Output" # this is the folder where the output CSV files you love so much will be located! LOL
os.makedirs(output_dir, exist_ok=True)
analyzer.save_to_csv(output_dir, sampling_rate=1000)
