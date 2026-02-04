import numpy as np
import matplotlib.pyplot as plt

def generate_pss(n_id_2):
    # This generates the 127 active subcarriers for the PSS
    N_ZC = 127
    m = [43, 139, 74][n_id_2]
    n = np.arange(0, N_ZC)
    
    # The Zadoff-Chu Formula
    pss = np.exp(-1j * np.pi * m * n * (n + 1) / N_ZC)
    return pss

def main():
    # Generate the sequence for Sector 0
    pss_127 = generate_pss(0)
    
    # Print a text sample of the first 5 carriers
    print("--- First 5 Subcarriers (Complex Numbers) ---")
    for i in range(5):
        print(f"Carrier {i}: {pss_127[i]:.4f}")

    # Plotting the 127 Carriers
    plt.figure(figsize=(10, 8))

    # Plot 1: Magnitude (Power)
    # Zadoff-Chu sequences have a special property: Constant Amplitude.
    # You should see a perfectly flat line. This means every subcarrier gets equal power.
    plt.subplot(2, 1, 1)
    plt.plot(np.abs(pss_127), 'o-', color='blue')
    plt.title("Magnitude of the 127 Subcarriers (Constant Power)")
    plt.xlabel("Subcarrier Index (0 to 126)")
    plt.ylabel("Amplitude")
    plt.ylim(0, 1.5)
    plt.grid(True)

    # Plot 2: Phase (The Information)
    # This is where the unique "Identity" of the tower lives.
    plt.subplot(2, 1, 2)
    plt.plot(np.angle(pss_127), '.-', color='orange')
    plt.title("Phase of the 127 Subcarriers (The 'Fingerprint')")
    plt.xlabel("Subcarrier Index (0 to 126)")
    plt.ylabel("Phase (Radians)")
    plt.grid(True)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()