import numpy as np
import os
import subprocess
import time
import matplotlib.pyplot as plt
from scipy.signal import correlate, find_peaks

# ==========================================
# 1. POC CONFIGURATION
# ==========================================
# File Paths
DATASET_FILE = "csi_dataset_poc.npy"
TEMP_BIN = "temp_capture.bin"

# Radio Settings (T-Mobile 5G n41)
FREQ = 2536e6        # 2.536 GHz
RATE = 30.72e6       # 30.72 Msps
GAIN = 50            # dB
DURATION = 1.0       # Seconds per capture
N_ID_2 = 0           # Sector ID (0, 1, or 2). Found in your previous scan.

# Processing Settings
PEAK_THRESHOLD = 0.3 # Ignore peaks smaller than 30% of max signal
WINDOW_SIZE = 64     # Number of samples to keep around the peak (The "Fingerprint")

# ==========================================
# 2. THE SIGNAL PROCESSING ENGINE
# ==========================================
def generate_pss(n_id_2):
    """Generates the 5G Primary Synchronization Signal (Zadoff-Chu)"""
    N_ZC = 127
    m = [43, 139, 74][n_id_2]
    n = np.arange(0, N_ZC)
    return np.exp(-1j * np.pi * m * n * (n + 1) / N_ZC)

def capture_signal():
    """Calls the C++ tool to capture raw IQ samples"""
    if os.path.exists(TEMP_BIN):
        os.remove(TEMP_BIN)

    cmd = [
        "sudo", "/usr/lib/uhd/examples/rx_samples_to_file",
        "--freq", str(FREQ),
        "--rate", str(RATE),
        "--gain", str(GAIN),
        "--nsamps", str(int(RATE * DURATION)),
        "--type", "short",
        "--file", TEMP_BIN
    ]
    
    print(f"   [Radio] Capturing {DURATION}s @ {FREQ/1e9:.3f} GHz...")
    # Run silently
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    
    if result.returncode != 0:
        print("   [Error] Capture failed. Is the B210 plugged in?")
        return None
    return TEMP_BIN

def extract_csi(filename):
    """Reads binary file, finds 5G frames, extracts Channel Impulse Response"""
    try:
        raw = np.fromfile(filename, dtype=np.int16)
    except FileNotFoundError:
        return None

    # Convert to Complex IQ
    rx_signal = raw[0::2] + 1j * raw[1::2]
    
    # 1. Matched Filter (Find the PSS)
    pss_seq = generate_pss(N_ID_2)
    corr = np.abs(correlate(rx_signal, pss_seq, mode='valid'))
    
    # 2. Peak Detection
    peaks, _ = find_peaks(corr, height=np.max(corr) * PEAK_THRESHOLD, distance=RATE*0.015)
    
    if len(peaks) == 0:
        print("   [Warning] No 5G Signal Found! Check Antenna or N_ID_2.")
        return None

    # 3. CSI Extraction (The "Fingerprint")
    csi_stack = []
    for p in peaks:
        # Extract a window around the peak
        if p - WINDOW_SIZE > 0 and p + WINDOW_SIZE < len(corr):
            # We save the MAGNITUDE (easier for first-pass ML)
            # You can change this to save complex numbers later if needed
            snapshot = corr[p - WINDOW_SIZE : p + WINDOW_SIZE]
            csi_stack.append(snapshot)
            
    # Return the AVERAGE fingerprint of this capture (Noise Reduction)
    if len(csi_stack) > 0:
        return np.mean(csi_stack, axis=0)
    else:
        return None

# ==========================================
# 3. THE DATA COLLECTION LOOP
# ==========================================
def main():
    # Load existing dataset
    if os.path.exists(DATASET_FILE):
        dataset = np.load(DATASET_FILE, allow_pickle=True).tolist()
        print(f"Loaded existing dataset: {len(dataset)} samples.")
    else:
        dataset = []
        print("Created new dataset.")

    print("\n=== 5G CSI DATA COLLECTOR (POC) ===")
    print("Commands: 'q' to quit, 'view' to test signal, or enter Object Name.\n")

    while True:
        obj_name = input("\n[Input] Object Name (e.g., 'human', 'empty'): ").strip()
        
        if obj_name.lower() == 'q':
            break
            
        if obj_name.lower() == 'view':
            # Diagnostic Mode: Just plot the CSI without saving
            capture_signal()
            csi = extract_csi(TEMP_BIN)
            if csi is not None:
                plt.plot(csi)
                plt.title("Current CSI Fingerprint")
                plt.show()
            continue

        # Coordinate Input
        try:
            x_coord = int(input("   [Input] Grid X (0-4): "))
            y_coord = int(input("   [Input] Grid Y (0-4): "))
        except ValueError:
            print("   [Error] Invalid number.")
            continue

        input(f"   >>> Place '{obj_name}' at ({x_coord},{y_coord}) and press ENTER...")
        
        # --- EXECUTE ---
        capture_signal()
        csi_data = extract_csi(TEMP_BIN)
        
        if csi_data is not None:
            # Save format
            entry = {
                "csi": csi_data,          # The Fingerprint (Feature Vector)
                "label_obj": obj_name,    # Class Label
                "label_x": x_coord,       # Regression Target 1
                "label_y": y_coord,       # Regression Target 2
                "timestamp": time.time()
            }
            dataset.append(entry)
            
            # Save immediately to disk
            np.save(DATASET_FILE, dataset)
            print(f"   [Success] Sample Saved! Total Dataset: {len(dataset)}")
        else:
            print("   [Fail] Sample Discarded (Bad Signal).")

if __name__ == "__main__":
    main()