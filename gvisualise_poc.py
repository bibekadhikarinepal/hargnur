import numpy as np
import matplotlib.pyplot as plt
import os

# --- CONFIGURATION ---
DATASET_FILE = "csi_dataset_poc.npy"

def main():
    if not os.path.exists(DATASET_FILE):
        print(f"Error: {DATASET_FILE} not found!")
        return

    # 1. Load the Data
    print(f"Loading {DATASET_FILE}...")
    dataset = np.load(DATASET_FILE, allow_pickle=True)
    
    print(f"Total Samples: {len(dataset)}")

    # 2. Separate by Class
    empty_samples = []
    human_samples = []

    for entry in dataset:
        label = entry['label_obj'].lower()
        csi = entry['csi']
        
        if label == 'empty':
            empty_samples.append(csi)
        elif label == 'human':
            # You can filter by grid location here if you want
            # if entry['label_x'] == 2 and entry['label_y'] == 2:
            human_samples.append(csi)

    # Convert to numpy arrays for math
    empty_arr = np.array(empty_samples)
    human_arr = np.array(human_samples)

    print(f"Found {len(empty_arr)} 'Empty' samples.")
    print(f"Found {len(human_arr)} 'Human' samples.")

    if len(empty_arr) == 0:
        print("Error: No 'empty' samples found. Cannot compare.")
        return

    # 3. Visualization
    plt.figure(figsize=(14, 8))

    # --- Plot 1: Raw Waveforms (Overlay) ---
    plt.subplot(2, 2, 1)
    # Plot first 10 samples of each to avoid clutter
    for i in range(min(10, len(empty_arr))):
        plt.plot(empty_arr[i], color='blue', alpha=0.3, linewidth=1)
    for i in range(min(10, len(human_arr))):
        plt.plot(human_arr[i], color='red', alpha=0.3, linewidth=1)
    
    # Fake legend
    plt.plot([], [], color='blue', label='Empty Room')
    plt.plot([], [], color='red', label='Human Present')
    plt.title("Raw CSI Fingerprints (Overlay)")
    plt.legend()
    plt.grid(True)

    # --- Plot 2: Average Signal Comparison ---
    plt.subplot(2, 2, 2)
    avg_empty = np.mean(empty_arr, axis=0)
    
    if len(human_arr) > 0:
        avg_human = np.mean(human_arr, axis=0)
        plt.plot(avg_empty, color='blue', label='Avg Empty', linewidth=2)
        plt.plot(avg_human, color='red', label='Avg Human', linewidth=2)
        plt.title("Average Fingerprint Comparison")
        plt.legend()
        plt.grid(True)
    else:
        plt.text(0.5, 0.5, "No Human Data", ha='center')

    # --- Plot 3: The "Subtraction" (What the Radar Sees) ---
    plt.subplot(2, 1, 2)
    if len(human_arr) > 0:
        # Absolute difference between Human and Empty
        diff_signal = np.abs(avg_human - avg_empty)
        
        plt.fill_between(range(len(diff_signal)), diff_signal, color='orange', alpha=0.6)
        plt.plot(diff_signal, color='orange')
        plt.title("The 'Human Signal' (Background Subtraction)")
        plt.ylabel("Signal Change Magnitude")
        plt.xlabel("Delay Index (Distance)")
        plt.grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()