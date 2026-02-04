# hargnur

Proof‑of‑concept 5G CSI capture and visualization pipeline. This project includes scripts to capture IQ samples, extract CSI fingerprints, build a small dataset, and visualize it.

## What’s included
- [poc_collector.py](poc_collector.py) — capture IQ data, extract CSI, and store labeled samples in [csi_dataset_poc.npy](csi_dataset_poc.npy).
- [csi_reader.py](csi_reader.py) — matched filter visualization on a recorded .bin capture.
- [visualizebin.py](visualizebin.py) — spectrogram visualization of a .bin capture.
- [visualize_csi_dataset.py](visualize_csi_dataset.py) — generates plots from the CSI dataset into [plots](plots).
- [scanner.py](scanner.py) — scan for 5G carriers (if applicable in your setup).

## Requirements
Python 3.8+ and the packages listed in [requirement.txt](requirement.txt).

## Step‑by‑step

### 1) Install dependencies
```bash
pip install -r requirement.txt
```

### 2) Visualize the existing CSI dataset
This reads [csi_dataset_poc.npy](csi_dataset_poc.npy) and writes PNG plots to [plots](plots).
```bash
python3 visualize_csi_dataset.py
```
Outputs:
- [plots/sample_traces.png](plots/sample_traces.png)
- [plots/heatmap.png](plots/heatmap.png)
- [plots/avg_by_label.png](plots/avg_by_label.png)
- [plots/positions.png](plots/positions.png)

### 3) Visualize a captured .bin file (spectrogram)
Edit the filename at the top of [visualizebin.py](visualizebin.py), then run:
```bash
python3 visualizebin.py
```

### 4) Inspect CSI from a recorded .bin capture
Edit the filename and sector ID in [csi_reader.py](csi_reader.py), then run:
```bash
python3 csi_reader.py
```

### 5) Collect new CSI samples (requires USRP/compatible SDR)
This uses UHD tools to capture IQ samples and will write/append to [csi_dataset_poc.npy](csi_dataset_poc.npy).
```bash
python3 poc_collector.py
```
Notes:
- You may need `sudo` access for the UHD capture tool.
- Adjust `FREQ`, `RATE`, `GAIN`, and `N_ID_2` in [poc_collector.py](poc_collector.py) to match your band and sector.

## Troubleshooting
- If `git push` fails, confirm your remote URL and authentication.
- If plots don’t appear, ensure you have matplotlib installed and the dataset exists.