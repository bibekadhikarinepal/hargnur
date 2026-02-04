import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate, correlation_lags

# --- CONFIGURATION ---
FILENAME = "capture_5g_n41_2.5GHz.bin" # USE YOUR T-MOBILE FILE HERE
SAMPLE_RATE = 30.72e6
N_ID_2 = 0  # T-Mobile Sector ID (Usually 0, 1, or 2. Try all 3!)

def generate_pss(n_id_2):
    # Generates the 5G PSS Sequence (Zadoff-Chu)
    # This is the "Key" we look for in the noise.
    N_ZC = 127
    m = [43, 139, 74][n_id_2]
    n = np.arange(0, N_ZC)
    pss = np.exp(-1j * np.pi * m * n * (n + 1) / N_ZC)
    return pss

def main():
    print(f"Loading {FILENAME}...")
    # Read 0.1 seconds of data
    count = int(SAMPLE_RATE * 0.1) * 2
    raw = np.fromfile(FILENAME, dtype=np.int16, count=count)
    rx_signal = raw[0::2] + 1j * raw[1::2]
    
    # Generate the "Radar Pulse" (PSS)
    pss_seq = generate_pss(N_ID_2)
    
    # --- RADAR PROCESSING (Matched Filter) ---
    print("Searching for 5G Tower (Correlation)...")
    
    # Correlate the received signal with the known PSS
    # This is like sliding a template over the signal to find matches
    corr = np.abs(correlate(rx_signal, pss_seq, mode='valid'))
    
    # --- VISUALIZATION ---
    plt.figure(figsize=(12, 6))
    
    # Plot 1: The Raw Correlation (The "Radar Returns")
    plt.subplot(2, 1, 1)
    plt.plot(corr)
    plt.title(f"Channel Impulse Response (CSI) - Sector ID {N_ID_2}")
    plt.ylabel("Signal Strength")
    plt.xlabel("Sample Index")
    
    # Plot 2: Zoom in on the strongest peak (The Tower)
    # The 'shape' of this peak contains the multipath info (reflections from walls/people)
    peak_idx = np.argmax(corr)
    window = 200
    if peak_idx > window:
        plt.subplot(2, 1, 2)
        plt.plot(corr[peak_idx-window : peak_idx+window], color='orange')
        plt.title("Zoomed CSI (Multipath Profile)")
        plt.grid(True)
    
    print("Displaying CSI Radar plot...")
    plt.show()

if __name__ == "__main__":
    main()