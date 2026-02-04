import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATAFILE = 'csi_dataset_poc.npy'
OUTDIR = 'plots'

os.makedirs(OUTDIR, exist_ok=True)


def load_dataset(path):
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return None
    data = np.load(path, allow_pickle=True)
    try:
        data = data.tolist()
    except Exception:
        pass
    return data


def to_arrays(dataset):
    csi_list = []
    labels_obj = []
    labels_x = []
    labels_y = []

    for entry in dataset:
        # Support both dict entries and plain arrays
        if isinstance(entry, dict) and 'csi' in entry:
            csi = np.asarray(entry['csi'])
            labels_obj.append(entry.get('label_obj', ''))
            labels_x.append(entry.get('label_x', np.nan))
            labels_y.append(entry.get('label_y', np.nan))
        else:
            csi = np.asarray(entry)
            labels_obj.append('')
            labels_x.append(np.nan)
            labels_y.append(np.nan)

        csi_list.append(csi)

    # Pad or trim to consistent length
    lengths = [len(x) for x in csi_list]
    if len(lengths) == 0:
        return None, None, None, None
    L = max(lengths)
    matrix = np.zeros((len(csi_list), L))
    for i, v in enumerate(csi_list):
        arr = np.asarray(v)
        if len(arr) < L:
            matrix[i, :len(arr)] = arr
        else:
            matrix[i, :] = arr[:L]

    return matrix, np.array(labels_obj), np.array(labels_x), np.array(labels_y)


def plot_sample_traces(mat, outdir, n=6):
    fig, ax = plt.subplots(figsize=(8, 4))
    n = min(n, mat.shape[0])
    for i in range(n):
        ax.plot(mat[i], label=f'sample {i}')
    ax.set_title('CSI sample traces (magnitude)')
    ax.set_xlabel('Subcarrier / Bin Index')
    ax.set_ylabel('Magnitude')
    ax.legend(ncol=2, fontsize='small')
    fig.tight_layout()
    p = os.path.join(outdir, 'sample_traces.png')
    fig.savefig(p)
    plt.close(fig)
    print('Wrote', p)


def plot_heatmap(mat, outdir):
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(mat, aspect='auto', cmap='viridis')
    ax.set_title('CSI heatmap (samples x subcarrier)')
    ax.set_ylabel('Sample Index')
    ax.set_xlabel('Subcarrier / Bin Index')
    fig.colorbar(im, ax=ax, label='Magnitude')
    fig.tight_layout()
    p = os.path.join(outdir, 'heatmap.png')
    fig.savefig(p)
    plt.close(fig)
    print('Wrote', p)


def plot_average_by_label(mat, labels, outdir):
    unique = np.unique(labels)
    unique = [u for u in unique if u != '']
    if len(unique) == 0:
        print('No object labels found; skipping average-by-label plot.')
        return
    fig, ax = plt.subplots(figsize=(8, 4))
    for u in unique:
        idx = np.where(labels == u)[0]
        avg = mat[idx].mean(axis=0)
        ax.plot(avg, label=str(u))
    ax.set_title('Average CSI by object label')
    ax.set_xlabel('Subcarrier / Bin Index')
    ax.set_ylabel('Magnitude')
    ax.legend()
    fig.tight_layout()
    p = os.path.join(outdir, 'avg_by_label.png')
    fig.savefig(p)
    plt.close(fig)
    print('Wrote', p)


def plot_xy_scatter(xs, ys, labels, outdir):
    if np.all(np.isnan(xs)) or np.all(np.isnan(ys)):
        print('No XY coordinates found; skipping scatter plot.')
        return
    fig, ax = plt.subplots(figsize=(6, 6))
    sc = ax.scatter(xs, ys, c=np.arange(len(xs)), cmap='tab20', s=40)
    ax.set_title('Measurement positions (x,y)')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    fig.colorbar(sc, ax=ax, label='Sample index')
    fig.tight_layout()
    p = os.path.join(outdir, 'positions.png')
    fig.savefig(p)
    plt.close(fig)
    print('Wrote', p)


def main():
    dataset = load_dataset(DATAFILE)
    if dataset is None:
        return

    mat, labels_obj, labels_x, labels_y = to_arrays(dataset)
    if mat is None:
        print('Dataset is empty or invalid.')
        return

    print(f'Loaded dataset with {mat.shape[0]} samples, each length {mat.shape[1]}')

    plot_sample_traces(mat, OUTDIR, n=6)
    plot_heatmap(mat, OUTDIR)
    plot_average_by_label(mat, labels_obj, OUTDIR)
    plot_xy_scatter(labels_x.astype(float), labels_y.astype(float), labels_obj, OUTDIR)

    print('\nAll plots saved to', OUTDIR)


if __name__ == '__main__':
    main()
