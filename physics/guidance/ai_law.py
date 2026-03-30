"""AI Neural Network Guidance Law — Real-time PyTorch Inference.

Loads the trained MissileGuidanceNet and performs real-time inference
during RK4 integration to steer the missile.
"""

import os
import numpy as np

# Try to import torch; if not available, provide a clear error
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from physics.constants import MAX_ACCEL_MS2
from physics.utils.vector_math import clip_vector, magnitude


class MissileGuidanceNet(nn.Module):
    """Mirror of the training architecture — must match exactly."""
    
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


class AIGuidance:
    """AI Neural Network guidance law for real-time missile steering.
    
    Loads the trained .pth model and runs inference each timestep.
    Falls back to basic proportional navigation if model is unavailable.
    """
    
    def __init__(self):
        self.model = None
        self.norm_params = None
        self.device = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained model weights."""
        if not TORCH_AVAILABLE:
            print("⚠️  PyTorch not installed. AI guidance will use fallback PNG.")
            return
        
        # Look for the model file
        model_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'ai_training', 'trained_missile_brain.pth'
        )
        model_path = os.path.abspath(model_path)
        
        if not os.path.exists(model_path):
            print(f"⚠️  No trained model found at {model_path}. AI guidance will use fallback PNG.")
            return
        
        try:
            self.device = torch.device('cpu')  # Always CPU for real-time inference
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
            
            input_dim = checkpoint.get('input_dim', 12)
            output_dim = checkpoint.get('output_dim', 3)
            
            self.model = MissileGuidanceNet(input_dim=input_dim, output_dim=output_dim)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()
            self.model.to(self.device)
            
            # Load normalization parameters
            self.norm_params = {
                k: np.array(v, dtype=np.float32)
                for k, v in checkpoint['norm_params'].items()
            }
            
            epoch = checkpoint.get('epoch', '?')
            val_loss = checkpoint.get('val_loss', '?')
            print(f"🧠 AI Guidance loaded: epoch {epoch}, val_loss={val_loss:.6f}" if isinstance(val_loss, float) else f"🧠 AI Guidance loaded")
            
        except Exception as e:
            print(f"⚠️  Failed to load AI model: {e}. Using fallback PNG.")
            self.model = None
    
    def compute(self, missile_state: np.ndarray,
                target_state: np.ndarray,
                target_accel: np.ndarray = None) -> np.ndarray:
        """Compute AI-guided acceleration command.
        
        Args:
            missile_state: [x, y, z, vx, vy, vz]
            target_state: [x, y, z, vx, vy, vz]
            target_accel: [ax, ay, az] estimated target acceleration
        
        Returns:
            [ax, ay, az] acceleration command in m/s²
        """
        if target_accel is None:
            target_accel = np.zeros(3)
        
        # If model not loaded, return basic PNG fallback
        if self.model is None:
            return self._fallback_png(missile_state, target_state)
        
        # Build 12D state vector (same format as training)
        rel_pos = target_state[:3] - missile_state[:3]
        rel_vel = target_state[3:6] - missile_state[3:6]
        missile_vel = missile_state[3:6]
        
        state_vec = np.concatenate([rel_pos, rel_vel, missile_vel, target_accel]).astype(np.float32)
        
        # Normalize using training statistics
        state_norm = (state_vec - self.norm_params['state_mean']) / self.norm_params['state_std']
        
        # Run inference
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state_norm).unsqueeze(0).to(self.device)
            action_norm = self.model(state_tensor).squeeze(0).cpu().numpy()
        
        # Denormalize output
        a_cmd = action_norm * self.norm_params['action_std'] + self.norm_params['action_mean']
        
        # Clip to physical limits
        a_cmd = clip_vector(a_cmd, MAX_ACCEL_MS2)
        
        return a_cmd
    
    def _fallback_png(self, missile_state, target_state):
        """Simple proportional navigation fallback if model fails."""
        from physics.guidance.png_law import ProportionalNavigation
        png = ProportionalNavigation(N=4.0)
        return png.compute(missile_state, target_state)
