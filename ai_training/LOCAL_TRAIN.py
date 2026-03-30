"""
╔══════════════════════════════════════════════════════════════╗
║  STRIKE-VECTOR AI Missile Guidance — LOCAL GPU TRAINING     ║
║  Architecture: 12→256→512→512→256→128→3 (565K params)       ║
║  Just run: python LOCAL_TRAIN.py                            ║
╚══════════════════════════════════════════════════════════════╝

Requirements: pip install torch numpy matplotlib seaborn scipy optuna
Place training_dataset.npz in same folder as this script.
Output: trained_missile_brain.pth (same folder)
"""

import subprocess, sys, os, time, warnings
import numpy as np

# ── Auto-install missing packages ──
def pip_install(pkg):
    try: __import__(pkg)
    except ImportError:
        print(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', pkg])

pip_install('torch')
pip_install('optuna')
pip_install('seaborn')
pip_install('scipy')

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import matplotlib
matplotlib.use('Agg')  # headless rendering for lab PCs
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)
warnings.filterwarnings('ignore')

# ── Styling ──
sns.set_theme(style='darkgrid', palette='coolwarm')
plt.rcParams.update({
    'figure.facecolor':'#0a0e1a','axes.facecolor':'#0d1117','axes.edgecolor':'#30363d',
    'axes.labelcolor':'#c9d1d9','text.color':'#c9d1d9','xtick.color':'#8b949e',
    'ytick.color':'#8b949e','grid.color':'#21262d','figure.dpi':120,'font.size':10,
    'font.family':'monospace'
})
CYAN,RED,GREEN,AMBER,PURPLE = '#00d4ff','#ff4444','#00ff66','#ffaa00','#a855f7'
ax_colors = [CYAN, AMBER, GREEN]

# ══════════════════════════════════════════════════════════════
# STEP 1: DEVICE SETUP
# ══════════════════════════════════════════════════════════════
print("=" * 60)
print("  STRIKE-VECTOR AI — LOCAL GPU TRAINING")
print("=" * 60)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'\n🖥️  Device: {device}')
if device.type == 'cuda':
    print(f'   GPU: {torch.cuda.get_device_name(0)}')
    print(f'   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
else:
    print("⚠️  WARNING: No GPU detected! Training will be SLOW on CPU.")

# ══════════════════════════════════════════════════════════════
# STEP 2: LOAD DATA
# ══════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(SCRIPT_DIR, 'training_dataset.npz')

if not os.path.exists(data_path):
    # Search nearby
    for root, dirs, files in os.walk(SCRIPT_DIR):
        for f in files:
            if f == 'training_dataset.npz':
                data_path = os.path.join(root, f)
                break
        if os.path.exists(data_path): break

assert os.path.exists(data_path), f'❌ training_dataset.npz not found in {SCRIPT_DIR}!'

data = np.load(data_path)
states_raw = data['states'].astype(np.float32)
actions_raw = data['actions'].astype(np.float32)
N_SAMPLES, STATE_DIM = states_raw.shape
_, ACTION_DIM = actions_raw.shape

print(f'\n📦 Dataset: {data_path}')
print(f'   Samples: {N_SAMPLES:,}')
print(f'   State dim: {STATE_DIM} | Action dim: {ACTION_DIM}')

# ══════════════════════════════════════════════════════════════
# STEP 3: DATASET STATISTICS
# ══════════════════════════════════════════════════════════════
STATE_LABELS = ['Rel Pos X','Rel Pos Y','Rel Pos Z','Rel Vel X','Rel Vel Y','Rel Vel Z',
                'Msl Vel X','Msl Vel Y','Msl Vel Z','Tgt Acc X','Tgt Acc Y','Tgt Acc Z']
ACTION_LABELS = ['Cmd AX','Cmd AY','Cmd AZ']

print(f"\n{'Feature':<14} {'Mean':>10} {'Std':>10} {'Min':>10} {'Max':>10}")
print('-' * 56)
for i, label in enumerate(STATE_LABELS):
    col = states_raw[:, i]
    print(f'{label:<14} {col.mean():>10.1f} {col.std():>10.1f} {col.min():>10.1f} {col.max():>10.1f}')

# ══════════════════════════════════════════════════════════════
# STEP 4: PRE-TRAINING VISUALIZATIONS (VIZ 1-5)
# ══════════════════════════════════════════════════════════════
OUT_DIR = os.path.join(SCRIPT_DIR, 'training_output')
os.makedirs(OUT_DIR, exist_ok=True)

# VIZ 1: State distributions
fig, axes = plt.subplots(3, 4, figsize=(18, 10))
fig.suptitle('VIZ 1: State Feature Distributions', fontsize=16, color=CYAN, fontweight='bold')
for i, (ax, label) in enumerate(zip(axes.flat, STATE_LABELS)):
    ax.hist(states_raw[::10, i], bins=80, color=CYAN, alpha=0.7, edgecolor='none')
    ax.set_title(label, fontsize=9, color=AMBER)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(os.path.join(OUT_DIR, 'viz01_state_distributions.png'), bbox_inches='tight')
plt.close()
print('✅ VIZ 1 saved')

# VIZ 2: Action distributions
fig, axes = plt.subplots(1, 3, figsize=(16, 4))
fig.suptitle('VIZ 2: Guidance Command Distributions', fontsize=14, color=CYAN, fontweight='bold')
for i, (ax, label) in enumerate(zip(axes, ACTION_LABELS)):
    ax.hist(actions_raw[::10, i], bins=100, color=ax_colors[i], alpha=0.7, edgecolor='none')
    ax.set_title(label, fontsize=10, color=ax_colors[i])
    ax.axvline(0, color='white', linewidth=0.5, linestyle='--', alpha=0.5)
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(os.path.join(OUT_DIR, 'viz02_action_distributions.png'), bbox_inches='tight')
plt.close()
print('✅ VIZ 2 saved')

# VIZ 3: Correlation heatmap
fig, ax = plt.subplots(figsize=(14, 10))
combined = np.concatenate([states_raw[::50], actions_raw[::50]], axis=1)
all_labels = STATE_LABELS + ACTION_LABELS
corr = np.corrcoef(combined.T)
sns.heatmap(corr, ax=ax, xticklabels=all_labels, yticklabels=all_labels,
            cmap='coolwarm', center=0, vmin=-1, vmax=1, annot=True, fmt='.2f',
            annot_kws={'size': 7}, linewidths=0.5, linecolor='#21262d')
ax.set_title('VIZ 3: State-Action Correlation Heatmap', fontsize=14, color=CYAN, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'viz03_correlation_heatmap.png'), bbox_inches='tight')
plt.close()
print('✅ VIZ 3 saved')

# VIZ 4 & 5: Range & Command Intensity
ranges = np.linalg.norm(states_raw[:, :3], axis=1)
cmd_magnitude = np.linalg.norm(actions_raw, axis=1) / 9.81

fig, ax = plt.subplots(figsize=(10, 4))
ax.hist(ranges, bins=100, color=PURPLE, alpha=0.8, edgecolor='none')
ax.set_xlabel('Range (m)'); ax.set_ylabel('Count')
ax.set_title('VIZ 4: Range-to-Target Distribution', fontsize=14, color=CYAN, fontweight='bold')
ax.axvline(ranges.mean(), color=AMBER, linestyle='--', label=f'Mean: {ranges.mean():.0f}m')
ax.legend(); plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'viz04_range_distribution.png'), bbox_inches='tight')
plt.close()

fig, ax = plt.subplots(figsize=(10, 5))
sub = np.random.choice(len(ranges), min(50000, len(ranges)), replace=False)
sc = ax.scatter(ranges[sub]/1000, cmd_magnitude[sub], c=cmd_magnitude[sub], cmap='inferno', s=0.5, alpha=0.3)
ax.set_xlabel('Range (km)'); ax.set_ylabel('G-Load')
ax.set_title('VIZ 5: Guidance Intensity vs Range', fontsize=14, color=CYAN, fontweight='bold')
plt.colorbar(sc, ax=ax, label='G'); plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'viz05_cmd_vs_range.png'), bbox_inches='tight')
plt.close()
print('✅ VIZ 4 & 5 saved')

# ══════════════════════════════════════════════════════════════
# STEP 5: NORMALIZE & SPLIT
# ══════════════════════════════════════════════════════════════
state_mean, state_std = states_raw.mean(0), states_raw.std(0)
state_std[state_std < 1e-6] = 1.0
action_mean, action_std = actions_raw.mean(0), actions_raw.std(0)
action_std[action_std < 1e-6] = 1.0

states_norm = (states_raw - state_mean) / state_std
actions_norm = (actions_raw - action_mean) / action_std
norm_params = {'state_mean': state_mean, 'state_std': state_std,
               'action_mean': action_mean, 'action_std': action_std}

n = len(states_norm)
indices = np.random.permutation(n)
split = int(0.9 * n)
train_idx, val_idx = indices[:split], indices[split:]

X_train = torch.FloatTensor(states_norm[train_idx]).to(device)
y_train = torch.FloatTensor(actions_norm[train_idx]).to(device)
X_val = torch.FloatTensor(states_norm[val_idx]).to(device)
y_val = torch.FloatTensor(actions_norm[val_idx]).to(device)

print(f'\n✅ Train: {len(X_train):,} | Val: {len(X_val):,} | Device: {device}')

# ══════════════════════════════════════════════════════════════
# STEP 6: MODEL ARCHITECTURE (matches ai_law.py EXACTLY!)
# ══════════════════════════════════════════════════════════════
class MissileGuidanceNet(nn.Module):
    def __init__(self, input_dim=12, output_dim=3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256), nn.LayerNorm(256), nn.ReLU(), nn.Dropout(0.1),
            nn.Linear(256, 512), nn.LayerNorm(512), nn.ReLU(), nn.Dropout(0.1),
            nn.Linear(512, 512), nn.LayerNorm(512), nn.ReLU(), nn.Dropout(0.05),
            nn.Linear(512, 256), nn.LayerNorm(256), nn.ReLU(),
            nn.Linear(256, 128), nn.ReLU(),
            nn.Linear(128, output_dim),
        )
    def forward(self, x): return self.net(x)

model = MissileGuidanceNet(STATE_DIM, ACTION_DIM).to(device)
total_params = sum(p.numel() for p in model.parameters())
print(f'\n🧠 Model: 12→256→512→512→256→128→3')
print(f'   Parameters: {total_params:,}')

# ══════════════════════════════════════════════════════════════
# STEP 7: OPTUNA HYPERPARAMETER TUNING (30 trials)
# ══════════════════════════════════════════════════════════════
print('\n🔬 Optuna Hyperparameter Tuning (30 trials)...')

def optuna_objective(trial):
    m = MissileGuidanceNet(STATE_DIM, ACTION_DIM).to(device)
    lr = trial.suggest_float('lr', 5e-5, 3e-3, log=True)
    wd = trial.suggest_float('weight_decay', 1e-6, 1e-3, log=True)
    bs = trial.suggest_categorical('batch_size', [1024, 2048, 4096])
    opt = optim.AdamW(m.parameters(), lr=lr, weight_decay=wd)
    loader = DataLoader(TensorDataset(X_train, y_train), batch_size=bs, shuffle=True, drop_last=True)
    crit = nn.MSELoss()
    for _ in range(20):
        m.train()
        for xb, yb in loader:
            opt.zero_grad(); crit(m(xb), yb).backward(); opt.step()
    m.eval()
    with torch.no_grad(): return crit(m(X_val), y_val).item()

study = optuna.create_study(direction='minimize')
study.optimize(optuna_objective, n_trials=30, show_progress_bar=True)
bp = study.best_params

print(f'\n✅ Best Val Loss: {study.best_value:.6f}')
print(f'   LR: {bp["lr"]:.6f} | WD: {bp["weight_decay"]:.6f} | BS: {bp["batch_size"]}')

# VIZ 6 & 7: Optuna Charts
fig, ax = plt.subplots(figsize=(12, 5))
vals = [t.value for t in study.trials if t.value is not None]
nums = [t.number for t in study.trials if t.value is not None]
ax.scatter(nums, vals, c=CYAN, s=20, alpha=0.7)
best_so_far = [min(vals[:i+1]) for i in range(len(vals))]
ax.plot(nums, best_so_far, color=GREEN, linewidth=2, label='Best So Far')
ax.set_xlabel('Trial'); ax.set_ylabel('Val Loss')
ax.set_title('VIZ 6: Optuna Optimization History', fontsize=14, color=CYAN, fontweight='bold')
ax.legend(); plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'viz06_optuna_history.png'), bbox_inches='tight'); plt.close()

fig, ax = plt.subplots(figsize=(10, 5))
try:
    imp = optuna.importance.get_param_importances(study)
    ax.barh(list(imp.keys()), list(imp.values()), color=CYAN, alpha=0.8)
    ax.set_xlabel('Importance')
    ax.set_title('VIZ 7: Hyperparameter Importance', fontsize=14, color=CYAN, fontweight='bold')
except:
    ax.text(0.5, 0.5, 'Insufficient data', transform=ax.transAxes, ha='center', color=AMBER, fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'viz07_param_importance.png'), bbox_inches='tight'); plt.close()
print('✅ VIZ 6 & 7 saved')

# ══════════════════════════════════════════════════════════════
# STEP 8: 1000-EPOCH TRAINING
# ══════════════════════════════════════════════════════════════
print('\n🚀 Starting 1000-epoch training...\n')

model = MissileGuidanceNet(STATE_DIM, ACTION_DIM).to(device)
optimizer = optim.AdamW(model.parameters(), lr=bp['lr'], weight_decay=bp['weight_decay'])
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=1000, eta_min=1e-6)
criterion = nn.MSELoss()
train_loader = DataLoader(TensorDataset(X_train, y_train), batch_size=bp['batch_size'], shuffle=True, drop_last=True)

SAVE_PATH = os.path.join(SCRIPT_DIR, 'trained_missile_brain.pth')

history = {'train_loss':[], 'val_loss':[], 'lr':[], 'grad_norms':[]}
best_val_loss, best_epoch = float('inf'), 0
t0 = time.time()

for epoch in range(1, 1001):
    model.train()
    ep_loss, batches, gn_total = 0.0, 0, 0.0
    for xb, yb in train_loader:
        optimizer.zero_grad()
        loss = criterion(model(xb), yb)
        loss.backward()
        gn = sum(p.grad.data.norm(2).item()**2 for p in model.parameters() if p.grad is not None)**0.5
        gn_total += gn
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        ep_loss += loss.item(); batches += 1

    scheduler.step()
    avg_train = ep_loss / max(batches, 1)
    avg_gn = gn_total / max(batches, 1)
    model.eval()
    with torch.no_grad(): val_loss = criterion(model(X_val), y_val).item()
    lr_now = scheduler.get_last_lr()[0]

    history['train_loss'].append(avg_train)
    history['val_loss'].append(val_loss)
    history['lr'].append(lr_now)
    history['grad_norms'].append(avg_gn)

    if val_loss < best_val_loss:
        best_val_loss = val_loss; best_epoch = epoch
        torch.save({'model_state_dict': model.state_dict(),
                    'norm_params': {k: v.tolist() for k, v in norm_params.items()},
                    'input_dim': STATE_DIM, 'output_dim': ACTION_DIM,
                    'epoch': epoch, 'val_loss': val_loss}, SAVE_PATH)

    # Print EVERY epoch for live tracking
    elapsed = time.time() - t0
    eta = (elapsed / epoch) * (1000 - epoch)
    marker = " ★" if val_loss <= best_val_loss else ""
    print(f'Epoch {epoch:>4}/1000 | Train: {avg_train:.6f} | Val: {val_loss:.6f} | LR: {lr_now:.2e} | {elapsed:.0f}s (ETA: {eta:.0f}s){marker}')

total_time = time.time() - t0
print(f'\n{"="*60}')
print(f'  ✅ TRAINING COMPLETE!')
print(f'  Time: {total_time:.0f}s | Best Epoch: {best_epoch} | Val: {best_val_loss:.6f}')
print(f'  Model saved: {SAVE_PATH}')
print(f'{"="*60}')

# ══════════════════════════════════════════════════════════════
# STEP 9: LOAD BEST & GENERATE PREDICTIONS
# ══════════════════════════════════════════════════════════════
checkpoint = torch.load(SAVE_PATH, map_location=device, weights_only=False)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

with torch.no_grad():
    val_preds_norm = model(X_val).cpu().numpy()
    val_true_norm = y_val.cpu().numpy()

val_preds_real = val_preds_norm * action_std + action_mean
val_true_real = val_true_norm * action_std + action_mean
errors_real = val_preds_real - val_true_real
axis_names = ['AX (North)', 'AY (East)', 'AZ (Down)']
print('\n✅ Predictions generated on validation set')

# ══════════════════════════════════════════════════════════════
# STEP 10: POST-TRAINING VISUALIZATIONS (VIZ 8-20)
# ══════════════════════════════════════════════════════════════

# VIZ 8: Loss Curve
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(range(1,1001), history['train_loss'], color=CYAN, alpha=0.7, linewidth=1, label='Train')
ax.plot(range(1,1001), history['val_loss'], color=AMBER, alpha=0.9, linewidth=1.5, label='Val')
ax.axvline(best_epoch, color=GREEN, linestyle='--', alpha=0.5, label=f'Best: {best_epoch}')
ax.set_xlabel('Epoch'); ax.set_ylabel('MSE'); ax.set_yscale('log')
ax.set_title('VIZ 8: Training Loss Curve (1000 Epochs)', fontsize=14, color=CYAN, fontweight='bold')
ax.legend(); plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'viz08_loss_curve.png'), bbox_inches='tight'); plt.close()
print('✅ VIZ 8 saved')

# VIZ 9: LR Schedule
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(range(1,1001), history['lr'], color=PURPLE, linewidth=1.5)
ax.set_xlabel('Epoch'); ax.set_ylabel('LR'); ax.set_yscale('log')
ax.set_title('VIZ 9: Cosine Annealing LR', fontsize=14, color=CYAN, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'viz09_lr_schedule.png'), bbox_inches='tight'); plt.close()

# VIZ 10: Gradient Norms
fig, ax = plt.subplots(figsize=(14, 4))
ax.plot(range(1,1001), history['grad_norms'], color=RED, alpha=0.6, linewidth=0.8)
ax.axhline(1.0, color=GREEN, linestyle='--', alpha=0.3, label='Clip')
ax.set_xlabel('Epoch'); ax.set_ylabel('Grad Norm')
ax.set_title('VIZ 10: Gradient Norm Flow', fontsize=14, color=CYAN, fontweight='bold')
ax.legend(); plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'viz10_gradient_norms.png'), bbox_inches='tight'); plt.close()
print('✅ VIZ 9 & 10 saved')

# VIZ 11: Predicted vs True
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('VIZ 11: AI Predicted vs Ground Truth', fontsize=14, color=CYAN, fontweight='bold')
sub_v = np.random.choice(len(val_true_real), min(20000, len(val_true_real)), replace=False)
for i, (ax, name) in enumerate(zip(axes, axis_names)):
    tg = val_true_real[sub_v, i]/9.81; pg = val_preds_real[sub_v, i]/9.81
    ax.scatter(tg, pg, c=ax_colors[i], s=0.5, alpha=0.2)
    lims = [min(tg.min(), pg.min()), max(tg.max(), pg.max())]
    ax.plot(lims, lims, 'w--', linewidth=0.8, alpha=0.5)
    r2 = 1 - np.sum((tg-pg)**2) / (np.sum((tg-tg.mean())**2) + 1e-8)
    ax.set_title(f'{name}  R²={r2:.4f}', fontsize=10, color=ax_colors[i])
    ax.set_xlabel('True (G)'); ax.set_ylabel('Pred (G)')
plt.tight_layout(rect=[0,0,1,0.93])
plt.savefig(os.path.join(OUT_DIR, 'viz11_pred_vs_true.png'), bbox_inches='tight'); plt.close()
print('✅ VIZ 11 saved')

# VIZ 12: Error Distributions
fig, axes = plt.subplots(1, 3, figsize=(16, 4))
fig.suptitle('VIZ 12: Error Distributions', fontsize=14, color=CYAN, fontweight='bold')
for i, (ax, name) in enumerate(zip(axes, axis_names)):
    eg = errors_real[:, i]/9.81
    ax.hist(eg, bins=100, color=ax_colors[i], alpha=0.7, edgecolor='none')
    ax.axvline(0, color='white', linewidth=0.5, linestyle='--')
    ax.set_title(f'{name}  μ={eg.mean():.3f}G  σ={eg.std():.3f}G', fontsize=9, color=ax_colors[i])
plt.tight_layout(rect=[0,0,1,0.93])
plt.savefig(os.path.join(OUT_DIR, 'viz12_error_distributions.png'), bbox_inches='tight'); plt.close()

# VIZ 13: Error Correlation
fig, ax = plt.subplots(figsize=(8, 6))
ec = np.corrcoef(errors_real.T)
sns.heatmap(ec, ax=ax, xticklabels=axis_names, yticklabels=axis_names, cmap='RdBu_r', center=0, annot=True, fmt='.3f', vmin=-1, vmax=1)
ax.set_title('VIZ 13: Error Cross-Correlation', fontsize=14, color=CYAN, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'viz13_error_heatmap.png'), bbox_inches='tight'); plt.close()
print('✅ VIZ 12 & 13 saved')

# VIZ 14: Error vs Range
val_states_real = states_raw[val_idx]
val_ranges = np.linalg.norm(val_states_real[:, :3], axis=1)
error_mag_g = np.linalg.norm(errors_real, axis=1) / 9.81

fig, ax = plt.subplots(figsize=(12, 5))
sub_r = np.random.choice(len(val_ranges), min(30000, len(val_ranges)), replace=False)
ax.scatter(val_ranges[sub_r]/1000, error_mag_g[sub_r], c=error_mag_g[sub_r], cmap='hot', s=0.5, alpha=0.3)
ax.set_xlabel('Range (km)'); ax.set_ylabel('Error (G)')
ax.set_title('VIZ 14: AI Error vs Range', fontsize=14, color=CYAN, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'viz14_error_vs_range.png'), bbox_inches='tight'); plt.close()

# VIZ 15: Weight Distributions
fig, axes = plt.subplots(2, 3, figsize=(16, 8))
fig.suptitle('VIZ 15: Weight Distributions', fontsize=14, color=CYAN, fontweight='bold')
wl = [(n,p.data.cpu().numpy().flatten()) for n,p in model.named_parameters() if 'weight' in n and p.dim()>=2]
clrs = [CYAN,AMBER,GREEN,PURPLE,RED,CYAN]
for idx,(ax,(name,w)) in enumerate(zip(axes.flat, wl[:6])):
    ax.hist(w, bins=80, color=clrs[idx], alpha=0.7, edgecolor='none')
    ax.set_title(f'{name}\nμ={w.mean():.4f} σ={w.std():.4f}', fontsize=8)
for ax in axes.flat[len(wl):]: ax.set_visible(False)
plt.tight_layout(rect=[0,0,1,0.95])
plt.savefig(os.path.join(OUT_DIR, 'viz15_weight_histograms.png'), bbox_inches='tight'); plt.close()
print('✅ VIZ 14 & 15 saved')

# VIZ 16: G-Load comparison
true_mag_g = np.linalg.norm(val_true_real, axis=1)/9.81
pred_mag_g = np.linalg.norm(val_preds_real, axis=1)/9.81

fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(true_mag_g, bins=100, color=CYAN, alpha=0.5, label='Expert', edgecolor='none')
ax.hist(pred_mag_g, bins=100, color=AMBER, alpha=0.5, label='AI', edgecolor='none')
ax.set_title('VIZ 16: G-Load — AI vs Expert', fontsize=14, color=CYAN, fontweight='bold')
ax.legend(); plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'viz16_gload_comparison.png'), bbox_inches='tight'); plt.close()

# VIZ 17: Error vs Target Evasion
tgt_g = np.linalg.norm(val_states_real[:, 9:12], axis=1)/9.81
fig, ax = plt.subplots(figsize=(10, 5))
sub_t = np.random.choice(len(tgt_g), min(30000, len(tgt_g)), replace=False)
ax.scatter(tgt_g[sub_t], error_mag_g[sub_t], c=PURPLE, s=0.5, alpha=0.3)
ax.set_xlabel('Target G'); ax.set_ylabel('AI Error (G)')
ax.set_title('VIZ 17: Error vs Evasion', fontsize=14, color=CYAN, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'viz17_error_vs_evasion.png'), bbox_inches='tight'); plt.close()

# VIZ 18: QQ Plots
fig, axes = plt.subplots(1, 3, figsize=(16, 4))
fig.suptitle('VIZ 18: QQ Plots', fontsize=14, color=CYAN, fontweight='bold')
for i, (ax, name) in enumerate(zip(axes, axis_names)):
    eg = errors_real[::10, i]/9.81
    stats.probplot(eg, dist='norm', plot=ax)
    ax.set_title(name, fontsize=10, color=ax_colors[i])
    ax.get_lines()[0].set_color(ax_colors[i]); ax.get_lines()[0].set_markersize(1)
    ax.get_lines()[1].set_color('white')
plt.tight_layout(rect=[0,0,1,0.93])
plt.savefig(os.path.join(OUT_DIR, 'viz18_qq_plots.png'), bbox_inches='tight'); plt.close()

# VIZ 19: CDF
sorted_err = np.sort(error_mag_g)
cdf = np.arange(1, len(sorted_err)+1)/len(sorted_err)
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(sorted_err, cdf, color=CYAN, linewidth=2)
for pct,c in [(0.50,AMBER),(0.90,GREEN),(0.95,RED),(0.99,PURPLE)]:
    v = sorted_err[int(pct*len(sorted_err))]
    ax.axhline(pct, color=c, linestyle='--', alpha=0.5)
    ax.axvline(v, color=c, linestyle='--', alpha=0.5)
    ax.annotate(f'P{int(pct*100)}: {v:.2f}G', xy=(v,pct), fontsize=9, color=c, xytext=(10,5), textcoords='offset points')
ax.set_title('VIZ 19: Error CDF', fontsize=14, color=CYAN, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'viz19_error_cdf.png'), bbox_inches='tight'); plt.close()
print('✅ VIZ 16-19 saved')

# VIZ 20: Final Dashboard
fig = plt.figure(figsize=(18, 10))
fig.suptitle('VIZ 20: STRIKE-VECTOR AI — FINAL DASHBOARD', fontsize=16, color=CYAN, fontweight='bold', y=0.98)
gs = gridspec.GridSpec(2, 3, hspace=0.35, wspace=0.3)

ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(range(1,1001), history['train_loss'], color=CYAN, alpha=0.6, linewidth=0.8, label='Train')
ax1.plot(range(1,1001), history['val_loss'], color=AMBER, linewidth=1.2, label='Val')
ax1.set_yscale('log'); ax1.set_title('Loss', color=CYAN); ax1.legend(fontsize=8)

ax2 = fig.add_subplot(gs[0, 1])
s = np.random.choice(len(true_mag_g), min(10000, len(true_mag_g)), replace=False)
ax2.scatter(true_mag_g[s], pred_mag_g[s], c=GREEN, s=0.5, alpha=0.2)
ax2.plot([0, true_mag_g.max()], [0, true_mag_g.max()], 'w--', linewidth=0.5)
r2_t = 1 - np.sum((true_mag_g-pred_mag_g)**2)/(np.sum((true_mag_g-true_mag_g.mean())**2)+1e-8)
ax2.set_title(f'R²={r2_t:.4f}', color=GREEN)

ax3 = fig.add_subplot(gs[0, 2])
ax3.hist(error_mag_g, bins=100, color=RED, alpha=0.7, edgecolor='none')
ax3.axvline(np.median(error_mag_g), color=AMBER, linestyle='--', label=f'Med: {np.median(error_mag_g):.2f}G')
ax3.set_title('Errors', color=RED); ax3.legend(fontsize=8)

ax4 = fig.add_subplot(gs[1, 0])
s2 = np.random.choice(len(val_ranges), min(15000, len(val_ranges)), replace=False)
ax4.scatter(val_ranges[s2]/1000, error_mag_g[s2], c=PURPLE, s=0.3, alpha=0.2)
ax4.set_title('Err vs Range', color=PURPLE)

ax5 = fig.add_subplot(gs[1, 1])
ax5.plot(range(1,1001), history['grad_norms'], color=AMBER, alpha=0.5, linewidth=0.5)
ax5.set_title('Gradients', color=AMBER)

ax6 = fig.add_subplot(gs[1, 2]); ax6.axis('off')
dash = '\u2500'
txt = (f'MODEL SUMMARY\n{dash*28}\n'
       f'Arch: 12>256>512>512>256>128>3\n'
       f'Params: {total_params:,}\n'
       f'Best Epoch: {best_epoch}/1000\n'
       f'Val Loss: {best_val_loss:.6f}\n'
       f'Time: {total_time:.0f}s\n'
       f'R2: {r2_t:.4f}\n'
       f'Median Err: {np.median(error_mag_g):.3f} G\n'
       f'P95: {sorted_err[int(0.95*len(sorted_err))]:.3f} G\n'
       f'P99: {sorted_err[int(0.99*len(sorted_err))]:.3f} G')
ax6.text(0.1, 0.95, txt, transform=ax6.transAxes, fontsize=10, color=CYAN,
         fontfamily='monospace', verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='#0d1117', edgecolor=CYAN, alpha=0.8))
plt.savefig(os.path.join(OUT_DIR, 'viz20_final_dashboard.png'), bbox_inches='tight'); plt.close()
print('✅ VIZ 20 saved')

# ══════════════════════════════════════════════════════════════
# FINAL REPORT
# ══════════════════════════════════════════════════════════════
model_size = os.path.getsize(SAVE_PATH) / 1024
print('\n' + '=' * 60)
print(f'  STRIKE-VECTOR AI — TRAINING COMPLETE')
print(f'  {"="*56}')
print(f'  Model: {SAVE_PATH}')
print(f'  Size:  {model_size:.0f} KB')
print(f'  Best Epoch: {best_epoch} | Val Loss: {best_val_loss:.6f}')
print(f'  R² Score: {r2_t:.4f}')
print(f'  Median Error: {np.median(error_mag_g):.3f} G')
print(f'  P95 Error: {sorted_err[int(0.95*len(sorted_err))]:.3f} G')
print(f'  P99 Error: {sorted_err[int(0.99*len(sorted_err))]:.3f} G')
print(f'  Charts: {OUT_DIR}/')
print('=' * 60)
print('\n✅ trained_missile_brain.pth is READY!')
print('   → Select AI NEURAL NET in the simulator dashboard')
print('   → All 20 visualizations saved in training_output/ folder')
