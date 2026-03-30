#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           STRIKE-VECTOR AI GUIDANCE — KAGGLE TRAINING SUITE                ║
║                                                                            ║
║  Trains a Deep Neural Network to learn optimal BVR missile guidance        ║
║  commands from 692,000+ expert APNG demonstrations.                        ║
║                                                                            ║
║  Features:                                                                 ║
║    • Optuna Hyperparameter Tuning (automated architecture search)          ║
║    • 1000-Epoch GPU-Accelerated Training                                   ║
║    • 20 Advanced Statistical & Diagnostic Visualizations                   ║
║    • Final .pth Model Export for local simulator integration               ║
╚══════════════════════════════════════════════════════════════════════════════╝

INSTRUCTIONS:
  1. Upload 'training_dataset.npz' as a Kaggle Dataset
  2. Enable GPU Accelerator (Settings → Accelerator → GPU T4x2)
  3. Run All Cells
  4. Download 'trained_missile_brain.pth' from the Output section
"""

# ============================================================================
# SECTION 0: ENVIRONMENT SETUP
# ============================================================================
import subprocess, sys

def install_if_missing(pkg, import_name=None):
    try:
        __import__(import_name or pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])

install_if_missing("optuna")
install_if_missing("seaborn")

import os
import time
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MaxNLocator
import seaborn as sns
import optuna
from optuna.trial import Trial
optuna.logging.set_verbosity(optuna.logging.WARNING)
import warnings
warnings.filterwarnings('ignore')

# Style
sns.set_theme(style="darkgrid", palette="coolwarm")
plt.rcParams.update({
    'figure.facecolor': '#0a0e1a',
    'axes.facecolor': '#0d1117',
    'axes.edgecolor': '#30363d',
    'axes.labelcolor': '#c9d1d9',
    'text.color': '#c9d1d9',
    'xtick.color': '#8b949e',
    'ytick.color': '#8b949e',
    'grid.color': '#21262d',
    'figure.dpi': 120,
    'font.size': 10,
    'font.family': 'monospace',
})

CYAN = '#00d4ff'
RED = '#ff4444'
GREEN = '#00ff66'
AMBER = '#ffaa00'
PURPLE = '#a855f7'

print("=" * 70)
print("  STRIKE-VECTOR AI GUIDANCE — KAGGLE TRAINING SUITE")
print("=" * 70)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"  Device: {device}")
if device.type == 'cuda':
    print(f"  GPU: {torch.cuda.get_device_name(0)}")
    print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
print("=" * 70)


# ============================================================================
# SECTION 1: DATA LOADING & EXPLORATION
# ============================================================================
print("\n📦 SECTION 1: Loading Training Dataset...")

# Kaggle dataset path — adjust if needed
DATA_PATHS = [
    '/kaggle/input/strike-vector-training/training_dataset.npz',
    '/kaggle/input/training_dataset.npz',
    'training_dataset.npz',
    '../input/strike-vector-training/training_dataset.npz',
    '../input/training-dataset/training_dataset.npz',
]

data_path = None
for p in DATA_PATHS:
    if os.path.exists(p):
        data_path = p
        break

if data_path is None:
    # Try to find it anywhere in /kaggle/input
    for root, dirs, files in os.walk('/kaggle/input'):
        for f in files:
            if f == 'training_dataset.npz':
                data_path = os.path.join(root, f)
                break
        if data_path:
            break

assert data_path is not None, "❌ training_dataset.npz not found! Upload it as a Kaggle Dataset."

data = np.load(data_path)
states_raw = data['states'].astype(np.float32)
actions_raw = data['actions'].astype(np.float32)

N_SAMPLES, STATE_DIM = states_raw.shape
_, ACTION_DIM = actions_raw.shape

print(f"  Loaded: {data_path}")
print(f"  Samples: {N_SAMPLES:,}")
print(f"  State dim: {STATE_DIM} → [rel_pos(3), rel_vel(3), missile_vel(3), target_accel(3)]")
print(f"  Action dim: {ACTION_DIM} → [a_cmd_x, a_cmd_y, a_cmd_z]")
print(f"  Data size: {states_raw.nbytes / 1e6:.1f} MB states + {actions_raw.nbytes / 1e6:.1f} MB actions")


# ============================================================================
# SECTION 2: DATA STATISTICS & VISUALIZATION 1-5
# ============================================================================
print("\n📊 SECTION 2: Dataset Statistics & Exploratory Visualizations...")

STATE_LABELS = [
    'Rel Pos X', 'Rel Pos Y', 'Rel Pos Z',
    'Rel Vel X', 'Rel Vel Y', 'Rel Vel Z',
    'Msl Vel X', 'Msl Vel Y', 'Msl Vel Z',
    'Tgt Acc X', 'Tgt Acc Y', 'Tgt Acc Z',
]
ACTION_LABELS = ['Cmd AX (m/s²)', 'Cmd AY (m/s²)', 'Cmd AZ (m/s²)']

# Print state statistics
print("\n  State Feature Statistics:")
print(f"  {'Feature':<14} {'Mean':>10} {'Std':>10} {'Min':>10} {'Max':>10}")
print("  " + "-" * 56)
for i, label in enumerate(STATE_LABELS):
    col = states_raw[:, i]
    print(f"  {label:<14} {col.mean():>10.1f} {col.std():>10.1f} {col.min():>10.1f} {col.max():>10.1f}")

print("\n  Action Statistics:")
for i, label in enumerate(ACTION_LABELS):
    col = actions_raw[:, i]
    print(f"  {label:<16} mean={col.mean():>8.1f}  std={col.std():>8.1f}  range=[{col.min():.0f}, {col.max():.0f}]")


# ── VIZ 1: State Feature Distributions ──
fig, axes = plt.subplots(3, 4, figsize=(18, 10))
fig.suptitle('VIZ 1: State Feature Distributions', fontsize=16, color=CYAN, fontweight='bold')
for i, (ax, label) in enumerate(zip(axes.flat, STATE_LABELS)):
    data_col = states_raw[::10, i]  # subsample for speed
    ax.hist(data_col, bins=80, color=CYAN, alpha=0.7, edgecolor='none')
    ax.set_title(label, fontsize=9, color=AMBER)
    ax.ticklabel_format(style='scientific', axis='x', scilimits=(-2, 3))
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('viz01_state_distributions.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 1 saved: viz01_state_distributions.png")


# ── VIZ 2: Action Command Distributions ──
fig, axes = plt.subplots(1, 3, figsize=(16, 4))
fig.suptitle('VIZ 2: Guidance Command Distributions', fontsize=14, color=CYAN, fontweight='bold')
colors = [CYAN, AMBER, GREEN]
for i, (ax, label) in enumerate(zip(axes, ACTION_LABELS)):
    data_col = actions_raw[::10, i]
    ax.hist(data_col, bins=100, color=colors[i], alpha=0.7, edgecolor='none')
    ax.set_title(label, fontsize=10, color=colors[i])
    ax.axvline(0, color='white', linewidth=0.5, linestyle='--', alpha=0.5)
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig('viz02_action_distributions.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 2 saved: viz02_action_distributions.png")


# ── VIZ 3: Correlation Heatmap (State → Action) ──
fig, ax = plt.subplots(figsize=(14, 10))
combined = np.concatenate([states_raw[::50], actions_raw[::50]], axis=1)
all_labels = STATE_LABELS + ACTION_LABELS
corr = np.corrcoef(combined.T)
sns.heatmap(corr, ax=ax, xticklabels=all_labels, yticklabels=all_labels,
            cmap='coolwarm', center=0, vmin=-1, vmax=1, annot=True, fmt='.2f',
            annot_kws={'size': 7}, linewidths=0.5, linecolor='#21262d')
ax.set_title('VIZ 3: State-Action Correlation Heatmap', fontsize=14, color=CYAN, fontweight='bold')
plt.tight_layout()
plt.savefig('viz03_correlation_heatmap.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 3 saved: viz03_correlation_heatmap.png")


# ── VIZ 4: Range-to-Target Distribution ──
ranges = np.linalg.norm(states_raw[:, :3], axis=1)
fig, ax = plt.subplots(figsize=(10, 4))
ax.hist(ranges, bins=100, color=PURPLE, alpha=0.8, edgecolor='none')
ax.set_xlabel('Range to Target (m)')
ax.set_ylabel('Sample Count')
ax.set_title('VIZ 4: Range-to-Target Distribution in Training Data', fontsize=14, color=CYAN, fontweight='bold')
ax.axvline(ranges.mean(), color=AMBER, linestyle='--', label=f'Mean: {ranges.mean():.0f}m')
ax.legend()
plt.tight_layout()
plt.savefig('viz04_range_distribution.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 4 saved: viz04_range_distribution.png")


# ── VIZ 5: Command Magnitude vs Range ──
cmd_magnitude = np.linalg.norm(actions_raw, axis=1) / 9.81  # in G
fig, ax = plt.subplots(figsize=(10, 5))
subsample = np.random.choice(len(ranges), min(50000, len(ranges)), replace=False)
scatter = ax.scatter(ranges[subsample] / 1000, cmd_magnitude[subsample], 
                     c=cmd_magnitude[subsample], cmap='inferno', s=0.5, alpha=0.3)
ax.set_xlabel('Range to Target (km)')
ax.set_ylabel('Command Magnitude (G)')
ax.set_title('VIZ 5: Guidance Command Intensity vs Range', fontsize=14, color=CYAN, fontweight='bold')
plt.colorbar(scatter, ax=ax, label='G-Load')
plt.tight_layout()
plt.savefig('viz05_cmd_vs_range.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 5 saved: viz05_cmd_vs_range.png")


# ============================================================================
# SECTION 3: DATA NORMALIZATION
# ============================================================================
print("\n⚙️  SECTION 3: Normalizing Data...")

state_mean = states_raw.mean(axis=0)
state_std = states_raw.std(axis=0)
state_std[state_std < 1e-6] = 1.0

action_mean = actions_raw.mean(axis=0)
action_std = actions_raw.std(axis=0)
action_std[action_std < 1e-6] = 1.0

states_norm = (states_raw - state_mean) / state_std
actions_norm = (actions_raw - action_mean) / action_std

norm_params = {
    'state_mean': state_mean,
    'state_std': state_std,
    'action_mean': action_mean,
    'action_std': action_std,
}

# Train/Val split
n = len(states_norm)
indices = np.random.permutation(n)
split = int(0.9 * n)
train_idx, val_idx = indices[:split], indices[split:]

X_train = torch.FloatTensor(states_norm[train_idx]).to(device)
y_train = torch.FloatTensor(actions_norm[train_idx]).to(device)
X_val = torch.FloatTensor(states_norm[val_idx]).to(device)
y_val = torch.FloatTensor(actions_norm[val_idx]).to(device)

print(f"  Train: {len(X_train):,} samples | Val: {len(X_val):,} samples")
print(f"  Data moved to: {device}")


# ============================================================================
# SECTION 4: MODEL ARCHITECTURE
# ============================================================================
print("\n🧠 SECTION 4: Neural Network Architecture...")

class MissileGuidanceNet(nn.Module):
    """Deep MLP for missile guidance command prediction."""
    
    def __init__(self, input_dim=12, output_dim=3, hidden_sizes=[256, 512, 512, 256, 128],
                 dropout=0.1, use_layer_norm=True):
        super().__init__()
        layers = []
        prev_size = input_dim
        for i, h in enumerate(hidden_sizes):
            layers.append(nn.Linear(prev_size, h))
            if use_layer_norm:
                layers.append(nn.LayerNorm(h))
            layers.append(nn.ReLU())
            if i < len(hidden_sizes) - 1:
                layers.append(nn.Dropout(dropout))
            prev_size = h
        layers.append(nn.Linear(prev_size, output_dim))
        self.net = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.net(x)


# ============================================================================
# SECTION 5: OPTUNA HYPERPARAMETER TUNING
# ============================================================================
print("\n🔬 SECTION 5: Optuna Hyperparameter Tuning (40 trials)...")
print("  This will find the optimal architecture automatically.\n")

OPTUNA_EPOCHS = 30  # Quick epochs for tuning
OPTUNA_TRIALS = 40

def create_model_from_trial(trial: Trial):
    n_layers = trial.suggest_int('n_layers', 3, 6)
    hidden_sizes = []
    for i in range(n_layers):
        h = trial.suggest_categorical(f'hidden_{i}', [64, 128, 256, 512])
        hidden_sizes.append(h)
    dropout = trial.suggest_float('dropout', 0.0, 0.3)
    use_ln = trial.suggest_categorical('layer_norm', [True, False])
    return MissileGuidanceNet(STATE_DIM, ACTION_DIM, hidden_sizes, dropout, use_ln)

def optuna_objective(trial: Trial):
    model = create_model_from_trial(trial).to(device)
    lr = trial.suggest_float('lr', 1e-4, 5e-3, log=True)
    wd = trial.suggest_float('weight_decay', 1e-6, 1e-3, log=True)
    batch_size = trial.suggest_categorical('batch_size', [1024, 2048, 4096])
    
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    criterion = nn.MSELoss()
    
    train_ds = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, drop_last=True)
    
    for epoch in range(OPTUNA_EPOCHS):
        model.train()
        for Xb, yb in train_loader:
            optimizer.zero_grad()
            loss = criterion(model(Xb), yb)
            loss.backward()
            optimizer.step()
    
    model.eval()
    with torch.no_grad():
        val_loss = criterion(model(X_val), y_val).item()
    
    return val_loss

study = optuna.create_study(direction='minimize', study_name='missile_guidance_hpo')
study.optimize(optuna_objective, n_trials=OPTUNA_TRIALS, show_progress_bar=True)

best_params = study.best_params
print(f"\n  ✅ Best Trial: #{study.best_trial.number}")
print(f"  Best Val Loss: {study.best_value:.6f}")
print(f"  Best Params:")
for k, v in best_params.items():
    print(f"    {k}: {v}")


# ── VIZ 6: Optuna Optimization History ──
fig, ax = plt.subplots(figsize=(12, 5))
trials = study.trials
trial_numbers = [t.number for t in trials]
trial_values = [t.value for t in trials if t.value is not None]
trial_nums_valid = [t.number for t in trials if t.value is not None]
ax.scatter(trial_nums_valid, trial_values, c=CYAN, s=20, alpha=0.7, zorder=2)
ax.plot(trial_nums_valid, trial_values, color=CYAN, alpha=0.3, linewidth=1)
best_so_far = [min(trial_values[:i+1]) for i in range(len(trial_values))]
ax.plot(trial_nums_valid, best_so_far, color=GREEN, linewidth=2, label='Best So Far')
ax.set_xlabel('Trial Number')
ax.set_ylabel('Validation Loss')
ax.set_title('VIZ 6: Optuna Optimization History', fontsize=14, color=CYAN, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.savefig('viz06_optuna_history.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 6 saved: viz06_optuna_history.png")


# ── VIZ 7: Optuna Hyperparameter Importance ──
fig, ax = plt.subplots(figsize=(10, 6))
try:
    importances = optuna.importance.get_param_importances(study)
    params = list(importances.keys())
    values = list(importances.values())
    colors_bar = [CYAN if v > 0.1 else AMBER for v in values]
    ax.barh(params, values, color=colors_bar, alpha=0.8, edgecolor='none')
    ax.set_xlabel('Importance')
    ax.set_title('VIZ 7: Hyperparameter Importance', fontsize=14, color=CYAN, fontweight='bold')
except:
    ax.text(0.5, 0.5, 'Not enough trials for importance', transform=ax.transAxes,
            ha='center', va='center', fontsize=14, color=AMBER)
plt.tight_layout()
plt.savefig('viz07_param_importance.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 7 saved: viz07_param_importance.png")


# ============================================================================
# SECTION 6: FULL 1000-EPOCH TRAINING WITH BEST HYPERPARAMETERS
# ============================================================================
print("\n🚀 SECTION 6: Full 1000-Epoch Training with Optimal Hyperparameters...")

# Build the best model from Optuna results
n_layers_best = best_params.get('n_layers', 5)
hidden_best = [best_params.get(f'hidden_{i}', 256) for i in range(n_layers_best)]
dropout_best = best_params.get('dropout', 0.1)
ln_best = best_params.get('layer_norm', True)
lr_best = best_params.get('lr', 1e-3)
wd_best = best_params.get('weight_decay', 1e-4)
bs_best = best_params.get('batch_size', 2048)

model = MissileGuidanceNet(STATE_DIM, ACTION_DIM, hidden_best, dropout_best, ln_best).to(device)
total_params = sum(p.numel() for p in model.parameters())
print(f"  Architecture: {hidden_best}")
print(f"  Parameters: {total_params:,}")
print(f"  LR: {lr_best:.5f} | WD: {wd_best:.6f} | BS: {bs_best} | Dropout: {dropout_best:.3f}")

EPOCHS = 1000
optimizer = optim.AdamW(model.parameters(), lr=lr_best, weight_decay=wd_best)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS, eta_min=1e-6)
criterion = nn.MSELoss()

train_ds = TensorDataset(X_train, y_train)
train_loader = DataLoader(train_ds, batch_size=bs_best, shuffle=True, drop_last=True)

# Training history
history = {
    'train_loss': [],
    'val_loss': [],
    'lr': [],
    'grad_norms': [],
}

best_val_loss = float('inf')
best_epoch = 0

print(f"\n{'Epoch':>6} | {'Train Loss':>12} | {'Val Loss':>12} | {'LR':>10} | {'Grad Norm':>10} | {'Time':>6}")
print("-" * 72)

start_time = time.time()

for epoch in range(1, EPOCHS + 1):
    model.train()
    epoch_loss = 0.0
    batches = 0
    total_grad_norm = 0.0
    
    for Xb, yb in train_loader:
        optimizer.zero_grad()
        pred = model(Xb)
        loss = criterion(pred, yb)
        loss.backward()
        
        # Track gradient norms
        grad_norm = 0.0
        for p in model.parameters():
            if p.grad is not None:
                grad_norm += p.grad.data.norm(2).item() ** 2
        grad_norm = grad_norm ** 0.5
        total_grad_norm += grad_norm
        
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        
        epoch_loss += loss.item()
        batches += 1
    
    scheduler.step()
    avg_train = epoch_loss / max(batches, 1)
    avg_grad = total_grad_norm / max(batches, 1)
    
    model.eval()
    with torch.no_grad():
        val_loss = criterion(model(X_val), y_val).item()
    
    lr_now = scheduler.get_last_lr()[0]
    
    history['train_loss'].append(avg_train)
    history['val_loss'].append(val_loss)
    history['lr'].append(lr_now)
    history['grad_norms'].append(avg_grad)
    
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        best_epoch = epoch
        torch.save({
            'model_state_dict': model.state_dict(),
            'norm_params': {k: v.tolist() for k, v in norm_params.items()},
            'input_dim': STATE_DIM,
            'output_dim': ACTION_DIM,
            'hidden_sizes': hidden_best,
            'dropout': dropout_best,
            'layer_norm': ln_best,
            'epoch': epoch,
            'val_loss': val_loss,
            'optuna_best_params': best_params,
        }, 'trained_missile_brain.pth')
    
    if epoch % 50 == 0 or epoch == 1 or epoch == EPOCHS:
        elapsed = time.time() - start_time
        print(f"{epoch:>6} | {avg_train:>12.6f} | {val_loss:>12.6f} | {lr_now:>10.2e} | {avg_grad:>10.4f} | {elapsed:>5.0f}s")

total_time = time.time() - start_time
print(f"\n{'=' * 72}")
print(f"  ✅ TRAINING COMPLETE!")
print(f"  Total Time: {total_time:.1f}s ({total_time/60:.1f} min)")
print(f"  Best Epoch: {best_epoch} | Best Val Loss: {best_val_loss:.6f}")
print(f"  Model saved: trained_missile_brain.pth")
print(f"{'=' * 72}")


# ============================================================================
# SECTION 7: POST-TRAINING VISUALIZATIONS (VIZ 8-20)
# ============================================================================
print("\n📊 SECTION 7: Post-Training Diagnostics (13 visualizations)...")

# Load best model for evaluation
checkpoint = torch.load('trained_missile_brain.pth', map_location=device, weights_only=False)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# Generate predictions on validation set
with torch.no_grad():
    val_preds_norm = model(X_val).cpu().numpy()
    val_true_norm = y_val.cpu().numpy()

# Denormalize
val_preds_real = val_preds_norm * action_std + action_mean
val_true_real = val_true_norm * action_std + action_mean
errors_real = val_preds_real - val_true_real


# ── VIZ 8: Loss Curve (Train vs Validation) ──
fig, ax = plt.subplots(figsize=(14, 5))
epochs_range = range(1, EPOCHS + 1)
ax.plot(epochs_range, history['train_loss'], color=CYAN, alpha=0.7, linewidth=1, label='Train Loss')
ax.plot(epochs_range, history['val_loss'], color=AMBER, alpha=0.9, linewidth=1.5, label='Val Loss')
ax.axvline(best_epoch, color=GREEN, linestyle='--', alpha=0.5, label=f'Best Epoch: {best_epoch}')
ax.set_xlabel('Epoch')
ax.set_ylabel('MSE Loss')
ax.set_title('VIZ 8: Training Loss Curve (1000 Epochs)', fontsize=14, color=CYAN, fontweight='bold')
ax.set_yscale('log')
ax.legend()
plt.tight_layout()
plt.savefig('viz08_loss_curve.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 8 saved: viz08_loss_curve.png")


# ── VIZ 9: Learning Rate Schedule ──
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(epochs_range, history['lr'], color=PURPLE, linewidth=1.5)
ax.set_xlabel('Epoch')
ax.set_ylabel('Learning Rate')
ax.set_title('VIZ 9: Cosine Annealing Learning Rate Schedule', fontsize=14, color=CYAN, fontweight='bold')
ax.set_yscale('log')
plt.tight_layout()
plt.savefig('viz09_lr_schedule.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 9 saved: viz09_lr_schedule.png")


# ── VIZ 10: Gradient Norm Flow ──
fig, ax = plt.subplots(figsize=(14, 4))
ax.plot(epochs_range, history['grad_norms'], color=RED, alpha=0.6, linewidth=0.8)
ax.set_xlabel('Epoch')
ax.set_ylabel('Avg Gradient Norm')
ax.set_title('VIZ 10: Gradient Norm Flow (Health Check)', fontsize=14, color=CYAN, fontweight='bold')
ax.axhline(1.0, color=GREEN, linestyle='--', alpha=0.3, label='Clip threshold')
ax.legend()
plt.tight_layout()
plt.savefig('viz10_gradient_norms.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 10 saved: viz10_gradient_norms.png")


# ── VIZ 11: Predicted vs True Scatter (per axis) ──
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('VIZ 11: AI Predicted vs Ground Truth Commands', fontsize=14, color=CYAN, fontweight='bold')
colors_ax = [CYAN, AMBER, GREEN]
axis_names = ['AX (North)', 'AY (East)', 'AZ (Down)']
subsample_viz = np.random.choice(len(val_true_real), min(20000, len(val_true_real)), replace=False)
for i, (ax, name) in enumerate(zip(axes, axis_names)):
    true_g = val_true_real[subsample_viz, i] / 9.81
    pred_g = val_preds_real[subsample_viz, i] / 9.81
    ax.scatter(true_g, pred_g, c=colors_ax[i], s=0.5, alpha=0.2)
    lims = [min(true_g.min(), pred_g.min()), max(true_g.max(), pred_g.max())]
    ax.plot(lims, lims, 'w--', linewidth=0.8, alpha=0.5, label='Perfect')
    r2 = 1 - np.sum((true_g - pred_g)**2) / (np.sum((true_g - true_g.mean())**2) + 1e-8)
    ax.set_title(f'{name}  R²={r2:.4f}', fontsize=10, color=colors_ax[i])
    ax.set_xlabel('True (G)')
    ax.set_ylabel('Predicted (G)')
    ax.legend(fontsize=8)
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig('viz11_pred_vs_true.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 11 saved: viz11_pred_vs_true.png")


# ── VIZ 12: Error Distribution Histograms ──
fig, axes = plt.subplots(1, 3, figsize=(16, 4))
fig.suptitle('VIZ 12: Prediction Error Distributions', fontsize=14, color=CYAN, fontweight='bold')
for i, (ax, name) in enumerate(zip(axes, axis_names)):
    err_g = errors_real[:, i] / 9.81
    ax.hist(err_g, bins=100, color=colors_ax[i], alpha=0.7, edgecolor='none')
    ax.axvline(0, color='white', linewidth=0.5, linestyle='--')
    ax.set_title(f'{name}  μ={err_g.mean():.3f}G  σ={err_g.std():.3f}G', fontsize=9, color=colors_ax[i])
    ax.set_xlabel('Error (G)')
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig('viz12_error_distributions.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 12 saved: viz12_error_distributions.png")


# ── VIZ 13: Error Heatmap (X vs Y vs Z) ──
fig, ax = plt.subplots(figsize=(8, 6))
err_corr = np.corrcoef(errors_real.T)
sns.heatmap(err_corr, ax=ax, xticklabels=axis_names, yticklabels=axis_names,
            cmap='RdBu_r', center=0, annot=True, fmt='.3f', linewidths=1, linecolor='#30363d',
            vmin=-1, vmax=1)
ax.set_title('VIZ 13: Error Cross-Correlation Matrix', fontsize=14, color=CYAN, fontweight='bold')
plt.tight_layout()
plt.savefig('viz13_error_heatmap.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 13 saved: viz13_error_heatmap.png")


# ── VIZ 14: Error vs Range-to-Target ──
val_states_real = states_raw[val_idx]
val_ranges = np.linalg.norm(val_states_real[:, :3], axis=1)
error_mag_g = np.linalg.norm(errors_real, axis=1) / 9.81
fig, ax = plt.subplots(figsize=(12, 5))
subsample_r = np.random.choice(len(val_ranges), min(30000, len(val_ranges)), replace=False)
ax.scatter(val_ranges[subsample_r] / 1000, error_mag_g[subsample_r], 
           c=error_mag_g[subsample_r], cmap='hot', s=0.5, alpha=0.3)
ax.set_xlabel('Range to Target (km)')
ax.set_ylabel('Command Error Magnitude (G)')
ax.set_title('VIZ 14: AI Error vs Range to Target', fontsize=14, color=CYAN, fontweight='bold')
plt.tight_layout()
plt.savefig('viz14_error_vs_range.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 14 saved: viz14_error_vs_range.png")


# ── VIZ 15: Weight Histograms ──
fig, axes = plt.subplots(2, 3, figsize=(16, 8))
fig.suptitle('VIZ 15: Network Weight Distributions (Layer-by-Layer)', fontsize=14, color=CYAN, fontweight='bold')
weight_layers = [(name, param.data.cpu().numpy().flatten()) 
                 for name, param in model.named_parameters() if 'weight' in name and param.dim() >= 2]
for idx, (ax, (name, weights)) in enumerate(zip(axes.flat, weight_layers[:6])):
    ax.hist(weights, bins=80, color=[CYAN, AMBER, GREEN, PURPLE, RED, CYAN][idx], alpha=0.7, edgecolor='none')
    ax.set_title(f'{name}\nμ={weights.mean():.4f} σ={weights.std():.4f}', fontsize=8)
for ax in axes.flat[len(weight_layers):]:
    ax.set_visible(False)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('viz15_weight_histograms.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 15 saved: viz15_weight_histograms.png")


# ── VIZ 16: Command Magnitude Comparison ──
true_mag_g = np.linalg.norm(val_true_real, axis=1) / 9.81
pred_mag_g = np.linalg.norm(val_preds_real, axis=1) / 9.81
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(true_mag_g, bins=100, color=CYAN, alpha=0.5, label='Ground Truth (APNG)', edgecolor='none')
ax.hist(pred_mag_g, bins=100, color=AMBER, alpha=0.5, label='AI Predicted', edgecolor='none')
ax.set_xlabel('Command Magnitude (G)')
ax.set_ylabel('Count')
ax.set_title('VIZ 16: G-Load Distribution: AI vs Expert', fontsize=14, color=CYAN, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.savefig('viz16_gload_comparison.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 16 saved: viz16_gload_comparison.png")


# ── VIZ 17: Target Acceleration Correlation ──
val_target_accel = val_states_real[:, 9:12]
target_accel_mag = np.linalg.norm(val_target_accel, axis=1) / 9.81
fig, ax = plt.subplots(figsize=(10, 5))
subsample_ta = np.random.choice(len(target_accel_mag), min(30000, len(target_accel_mag)), replace=False)
ax.scatter(target_accel_mag[subsample_ta], error_mag_g[subsample_ta],
           c=PURPLE, s=0.5, alpha=0.3)
ax.set_xlabel('Target Acceleration (G)')
ax.set_ylabel('AI Error (G)')
ax.set_title('VIZ 17: AI Error vs Target Evasion Intensity', fontsize=14, color=CYAN, fontweight='bold')
plt.tight_layout()
plt.savefig('viz17_error_vs_evasion.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 17 saved: viz17_error_vs_evasion.png")


# ── VIZ 18: Residual QQ Plot ──
from scipy import stats
fig, axes = plt.subplots(1, 3, figsize=(16, 4))
fig.suptitle('VIZ 18: Residual QQ Plots (Normality Check)', fontsize=14, color=CYAN, fontweight='bold')
for i, (ax, name) in enumerate(zip(axes, axis_names)):
    err_g_axis = errors_real[::10, i] / 9.81
    stats.probplot(err_g_axis, dist="norm", plot=ax)
    ax.set_title(name, fontsize=10, color=colors_ax[i])
    ax.get_lines()[0].set_color(colors_ax[i])
    ax.get_lines()[0].set_markersize(1)
    ax.get_lines()[1].set_color('white')
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig('viz18_qq_plots.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 18 saved: viz18_qq_plots.png")


# ── VIZ 19: Cumulative Error Distribution (CDF) ──
fig, ax = plt.subplots(figsize=(10, 5))
sorted_err = np.sort(error_mag_g)
cdf = np.arange(1, len(sorted_err) + 1) / len(sorted_err)
ax.plot(sorted_err, cdf, color=CYAN, linewidth=2)
# Mark key percentiles
for pct, color in [(0.50, AMBER), (0.90, GREEN), (0.95, RED), (0.99, PURPLE)]:
    val = sorted_err[int(pct * len(sorted_err))]
    ax.axhline(pct, color=color, linestyle='--', alpha=0.5)
    ax.axvline(val, color=color, linestyle='--', alpha=0.5)
    ax.annotate(f'P{int(pct*100)}: {val:.2f}G', xy=(val, pct), fontsize=9,
                color=color, xytext=(10, 5), textcoords='offset points')
ax.set_xlabel('Error Magnitude (G)')
ax.set_ylabel('Cumulative Probability')
ax.set_title('VIZ 19: Cumulative Error Distribution (CDF)', fontsize=14, color=CYAN, fontweight='bold')
plt.tight_layout()
plt.savefig('viz19_error_cdf.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 19 saved: viz19_error_cdf.png")


# ── VIZ 20: Final Model Performance Dashboard ──
fig = plt.figure(figsize=(18, 10))
fig.suptitle('VIZ 20: STRIKE-VECTOR AI MODEL — FINAL PERFORMANCE DASHBOARD',
             fontsize=16, color=CYAN, fontweight='bold', y=0.98)

gs = gridspec.GridSpec(2, 3, hspace=0.35, wspace=0.3)

# Panel 1: Loss curve
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(range(1, EPOCHS+1), history['train_loss'], color=CYAN, alpha=0.6, linewidth=0.8, label='Train')
ax1.plot(range(1, EPOCHS+1), history['val_loss'], color=AMBER, linewidth=1.2, label='Val')
ax1.set_yscale('log')
ax1.set_title('Loss Curve', color=CYAN, fontsize=11)
ax1.legend(fontsize=8)

# Panel 2: Pred vs True (magnitude)
ax2 = fig.add_subplot(gs[0, 1])
sub = np.random.choice(len(true_mag_g), min(10000, len(true_mag_g)), replace=False)
ax2.scatter(true_mag_g[sub], pred_mag_g[sub], c=GREEN, s=0.5, alpha=0.2)
ax2.plot([0, true_mag_g.max()], [0, true_mag_g.max()], 'w--', linewidth=0.5)
r2_total = 1 - np.sum((true_mag_g - pred_mag_g)**2) / (np.sum((true_mag_g - true_mag_g.mean())**2) + 1e-8)
ax2.set_title(f'Cmd Magnitude R²={r2_total:.4f}', color=GREEN, fontsize=11)
ax2.set_xlabel('True (G)')
ax2.set_ylabel('Pred (G)')

# Panel 3: Error histogram
ax3 = fig.add_subplot(gs[0, 2])
ax3.hist(error_mag_g, bins=100, color=RED, alpha=0.7, edgecolor='none')
ax3.axvline(np.median(error_mag_g), color=AMBER, linestyle='--', label=f'Median: {np.median(error_mag_g):.2f}G')
ax3.set_title('Error Distribution', color=RED, fontsize=11)
ax3.legend(fontsize=8)

# Panel 4: Error vs Range
ax4 = fig.add_subplot(gs[1, 0])
sub2 = np.random.choice(len(val_ranges), min(15000, len(val_ranges)), replace=False)
ax4.scatter(val_ranges[sub2]/1000, error_mag_g[sub2], c=PURPLE, s=0.3, alpha=0.2)
ax4.set_title('Error vs Range', color=PURPLE, fontsize=11)
ax4.set_xlabel('Range (km)')
ax4.set_ylabel('Error (G)')

# Panel 5: Gradient norms
ax5 = fig.add_subplot(gs[1, 1])
ax5.plot(range(1, EPOCHS+1), history['grad_norms'], color=AMBER, alpha=0.5, linewidth=0.5)
ax5.set_title('Gradient Health', color=AMBER, fontsize=11)

# Panel 6: Summary text
ax6 = fig.add_subplot(gs[1, 2])
ax6.axis('off')
summary_text = (
    f"MODEL SUMMARY\n"
    f"{'─'*30}\n"
    f"Architecture: {hidden_best}\n"
    f"Parameters: {total_params:,}\n"
    f"Best Epoch: {best_epoch}/{EPOCHS}\n"
    f"Best Val Loss: {best_val_loss:.6f}\n"
    f"Training Time: {total_time:.0f}s\n"
    f"R² (magnitude): {r2_total:.4f}\n"
    f"Median Error: {np.median(error_mag_g):.3f} G\n"
    f"P95 Error: {sorted_err[int(0.95*len(sorted_err))]:.3f} G\n"
    f"P99 Error: {sorted_err[int(0.99*len(sorted_err))]:.3f} G\n"
    f"{'─'*30}\n"
    f"Device: {device}\n"
    f"Samples: {N_SAMPLES:,}\n"
    f"Optuna Trials: {OPTUNA_TRIALS}"
)
ax6.text(0.1, 0.95, summary_text, transform=ax6.transAxes, fontsize=10,
         color=CYAN, fontfamily='monospace', verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='#0d1117', edgecolor=CYAN, alpha=0.8))

plt.savefig('viz20_final_dashboard.png', bbox_inches='tight')
plt.show()
print("  ✅ VIZ 20 saved: viz20_final_dashboard.png")


# ============================================================================
# SECTION 8: MODEL EXPORT & FINAL REPORT
# ============================================================================
print("\n" + "=" * 70)
print("  📦 FINAL MODEL EXPORT")
print("=" * 70)

# Verify model file exists
model_size = os.path.getsize('trained_missile_brain.pth') / 1024
print(f"  Model file: trained_missile_brain.pth ({model_size:.1f} KB)")
print(f"  Best epoch: {best_epoch}")
print(f"  Val loss: {best_val_loss:.6f}")
print(f"\n  📥 DOWNLOAD 'trained_missile_brain.pth' FROM THE OUTPUT SECTION")
print(f"     Then place it inside: strike-vector/ai_training/trained_missile_brain.pth")
print(f"     The simulator will automatically load it when you select 'AI NEURAL NET'!")

print("\n" + "=" * 70)
print("  ✅ ALL 20 VISUALIZATIONS GENERATED SUCCESSFULLY!")
print("  ✅ HYPERPARAMETER TUNING COMPLETE!")
print("  ✅ 1000-EPOCH TRAINING COMPLETE!")
print("  ✅ MODEL EXPORTED: trained_missile_brain.pth")
print("=" * 70)
