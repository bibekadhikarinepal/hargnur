import numpy as np
import matplotlib.pyplot as plt
import os

# --- Configuration (Matches your capture) ---
FILENAME = "capture_5g_3.8GHz.bin"
SAMPLE_RATE = 30.72e6  # 30.72 MHz
CENTER_FREQ = 3800.036e6 # 3.8 GHz
DURATION_TO_PLOT = 0.05 # Reduced to 0.05s to keep it fast

def load_and_plot():
    # Fix for Wayland/Ubuntu warning
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    
    print(f"Loading data from {FILENAME}...")
    
    # 1. Read the raw binary file
    try:
        # We only read the first chunk to save memory
        num_samples_to_read = int(SAMPLE_RATE * DURATION_TO_PLOT)
        count = num_samples_to_read * 2 # *2 because each sample has I and Q parts
        
        raw_data = np.fromfile(FILENAME, dtype=np.int16, count=count)
    except FileNotFoundError:
        print("Error: File not found! Make sure the .bin file is in the same folder.")
        return

    # 2. Convert to Complex Numbers (I + jQ)
    # Even indices are Real (I), Odd indices are Imaginary (Q)
    try:
        iq_data = raw_data[0::2] + 1j * raw_data[1::2]
    except IndexError:
        print("Error: File is too short or empty.")
        return
    
    print(f"Loaded {len(iq_data)} samples. Generating Spectrogram...")

    # 3. Plotting
    plt.figure(figsize=(12, 6))
    
    # --- THE FIX IS HERE: Changed 'fc' to 'Fc' ---
    Pxx, freqs, bins, im = plt.specgram(
        iq_data, 
        NFFT=1024, 
        Fs=SAMPLE_RATE, 
        Fc=CENTER_FREQ,  # Capital F is required!
        cmap='inferno'
    )
    
    plt.title(f"5G Spectrum Capture (Center: {CENTER_FREQ/1e6:.2f} MHz)")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Frequency (Hz)")
    
    # Add a colorbar
    cbar = plt.colorbar(im)
    cbar.set_label("Power (dB)")
    
    print("Displaying plot...")
    plt.show()

if __name__ == "__main__":
    load_and_plot()