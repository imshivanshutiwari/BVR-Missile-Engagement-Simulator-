"""AI Guidance Model — PyTorch Neural Network Training Script.

Trains a deep MLP to learn optimal missile guidance commands from
APNG expert demonstrations. 1000 epochs of supervised learning.
"""

import sys
import os
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader


class MissileGuidanceNet(nn.Module):
    """Deep MLP for missile guidance command prediction.
    
    Input:  12D state vector (rel_pos, rel_vel, missile_vel, target_accel)
    Output: 3D acceleration command (ax, ay, az)
    """
    
    def __init__(self, input_dim=12, output_dim=3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.LayerNorm(256),
            nn.ReLU(),
            nn.Dropout(0.1),
            
            nn.Linear(256, 512),
            nn.LayerNorm(512),
            nn.ReLU(),
            nn.Dropout(0.1),
            
            nn.Linear(512, 512),
            nn.LayerNorm(512),
            nn.ReLU(),
            nn.Dropout(0.05),
            
            nn.Linear(512, 256),
            nn.LayerNorm(256),
            nn.ReLU(),
            
            nn.Linear(256, 128),
            nn.ReLU(),
            
            nn.Linear(128, output_dim),
        )
    
    def forward(self, x):
        return self.net(x)


def normalize_data(states, actions):
    """Normalize inputs and outputs for stable training."""
    # State normalization: zero mean, unit variance
    state_mean = states.mean(axis=0)
    state_std = states.std(axis=0)
    state_std[state_std < 1e-6] = 1.0  # prevent division by zero
    
    # Action normalization
    action_mean = actions.mean(axis=0)
    action_std = actions.std(axis=0)
    action_std[action_std < 1e-6] = 1.0
    
    states_norm = (states - state_mean) / state_std
    actions_norm = (actions - action_mean) / action_std
    
    return states_norm, actions_norm, {
        'state_mean': state_mean,
        'state_std': state_std,
        'action_mean': action_mean,
        'action_std': action_std,
    }


def train(epochs=1000, batch_size=2048, lr=1e-3):
    """Train the guidance neural network for the specified epochs."""
    
    # Load dataset
    data_path = os.path.join(os.path.dirname(__file__), 'training_dataset.npz')
    if not os.path.exists(data_path):
        print("❌ No training dataset found. Run data_generator.py first!")
        return
    
    data = np.load(data_path)
    states_raw = data['states']
    actions_raw = data['actions']
    
    print(f"📦 Loaded dataset: {states_raw.shape[0]} samples")
    print(f"   State dim: {states_raw.shape[1]}, Action dim: {actions_raw.shape[1]}")
    
    # Normalize
    states_norm, actions_norm, norm_params = normalize_data(states_raw, actions_raw)
    
    # Train/val split (90/10)
    n = len(states_norm)
    indices = np.random.permutation(n)
    split = int(0.9 * n)
    train_idx, val_idx = indices[:split], indices[split:]
    
    X_train = torch.FloatTensor(states_norm[train_idx])
    y_train = torch.FloatTensor(actions_norm[train_idx])
    X_val = torch.FloatTensor(states_norm[val_idx])
    y_val = torch.FloatTensor(actions_norm[val_idx])
    
    train_ds = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, drop_last=True)
    
    # Model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = MissileGuidanceNet(input_dim=states_raw.shape[1], output_dim=actions_raw.shape[1]).to(device)
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"🧠 Model: {total_params:,} parameters | Device: {device}")
    
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)
    criterion = nn.MSELoss()
    
    X_val_dev = X_val.to(device)
    y_val_dev = y_val.to(device)
    
    best_val_loss = float('inf')
    
    print(f"\n🚀 Training for {epochs} epochs...")
    print(f"{'Epoch':>6} | {'Train Loss':>12} | {'Val Loss':>12} | {'LR':>10} | {'Time':>6}")
    print("-" * 60)
    
    start_time = time.time()
    
    for epoch in range(1, epochs + 1):
        model.train()
        epoch_loss = 0.0
        batches = 0
        
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            
            optimizer.zero_grad()
            pred = model(X_batch)
            loss = criterion(pred, y_batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            
            epoch_loss += loss.item()
            batches += 1
        
        scheduler.step()
        avg_train_loss = epoch_loss / max(batches, 1)
        
        # Validation
        model.eval()
        with torch.no_grad():
            val_pred = model(X_val_dev)
            val_loss = criterion(val_pred, y_val_dev).item()
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            # Save best checkpoint
            save_path = os.path.join(os.path.dirname(__file__), 'trained_missile_brain.pth')
            torch.save({
                'model_state_dict': model.state_dict(),
                'norm_params': {k: v.tolist() for k, v in norm_params.items()},
                'input_dim': states_raw.shape[1],
                'output_dim': actions_raw.shape[1],
                'epoch': epoch,
                'val_loss': val_loss,
            }, save_path)
        
        # Print every 50 epochs or last epoch
        if epoch % 50 == 0 or epoch == 1 or epoch == epochs:
            lr_now = scheduler.get_last_lr()[0]
            elapsed = time.time() - start_time
            print(f"{epoch:>6} | {avg_train_loss:>12.6f} | {val_loss:>12.6f} | {lr_now:>10.2e} | {elapsed:>5.0f}s")
    
    total_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"✅ TRAINING COMPLETE!")
    print(f"   Total time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"   Best val loss: {best_val_loss:.6f}")
    print(f"   Model saved: ai_training/trained_missile_brain.pth")
    print(f"{'='*60}")


if __name__ == "__main__":
    train(epochs=1000, batch_size=2048, lr=1e-3)
