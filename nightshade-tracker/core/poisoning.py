"""
Adversarial image poisoning module (Nightshade-style).
Generates perturbations that cause AI models to misclassify images.
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Optional, Tuple
import cv2


class AdversarialPoisoner:
    """
    Generates adversarial perturbations to poison AI model training.
    Shifts images in latent space to cause misclassification.
    """
    
    def __init__(self, strength: float = 0.1, epsilon: float = 0.03,
                 target_class: Optional[str] = None):
        """
        Initialize poisoner.
        
        Args:
            strength: Poisoning strength (0.0 to 1.0)
            epsilon: Maximum perturbation per pixel (0.0 to 1.0)
            target_class: Target class for poisoning (None = auto-detect)
        """
        self.strength = strength
        self.epsilon = epsilon
        self.target_class = target_class
        
        # Simple feature extractor (in practice, use a pre-trained model)
        # For demonstration, we'll use a simple CNN
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._create_simple_model()
    
    def _create_simple_model(self) -> nn.Module:
        """
        Create a simple feature extractor model.
        In production, this would be a pre-trained CLIP or similar model.
        """
        class SimpleFeatureExtractor(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = nn.Conv2d(3, 64, 3, padding=1)
                self.conv2 = nn.Conv2d(64, 128, 3, padding=1)
                self.pool = nn.AdaptiveAvgPool2d(1)
                self.fc = nn.Linear(128, 1000)  # 1000 ImageNet classes
            
            def forward(self, x):
                x = torch.relu(self.conv1(x))
                x = torch.relu(self.conv2(x))
                x = self.pool(x).flatten(1)
                x = self.fc(x)
                return x
        
        model = SimpleFeatureExtractor().to(self.device)
        model.eval()
        return model
    
    def generate_perturbation(self, image: np.ndarray,
                            target_label: Optional[int] = None,
                            iterations: int = 10) -> np.ndarray:
        """
        Generate adversarial perturbation using PGD (Projected Gradient Descent).
        
        Args:
            image: Input image array (H, W, C) in RGB, values [0, 255]
            target_label: Target class label for poisoning (None = untargeted)
            iterations: Number of optimization iterations
            
        Returns:
            Perturbation array (same shape as image)
        """
        # Normalize image to [0, 1]
        image_norm = image.astype(np.float32) / 255.0
        
        # Convert to tensor
        image_tensor = torch.from_numpy(image_norm).permute(2, 0, 1).unsqueeze(0)
        image_tensor = image_tensor.to(self.device)
        image_tensor.requires_grad = True
        
        # Initialize perturbation
        perturbation = torch.zeros_like(image_tensor)
        perturbation.requires_grad = True
        
        # If no target label, use untargeted attack (maximize loss)
        if target_label is None:
            # Get current prediction
            with torch.no_grad():
                output = self.model(image_tensor)
                current_label = output.argmax(dim=1).item()
                target_label = (current_label + 1) % 1000  # Shift to different class
        
        target_tensor = torch.tensor([target_label], device=self.device)
        
        # Optimize perturbation
        optimizer = torch.optim.Adam([perturbation], lr=0.01)
        
        for _ in range(iterations):
            optimizer.zero_grad()
            
            # Apply perturbation
            perturbed = image_tensor + perturbation * self.strength
            
            # Clip to valid range
            perturbed = torch.clamp(perturbed, 0, 1)
            
            # Get model output
            output = self.model(perturbed)
            
            # Loss: maximize probability of target class (or minimize current class)
            loss = -torch.nn.functional.cross_entropy(output, target_tensor)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Project perturbation to epsilon ball
            with torch.no_grad():
                perturbation.data = torch.clamp(perturbation.data, 
                                               -self.epsilon, self.epsilon)
        
        # Convert back to numpy
        perturbation_np = perturbation.squeeze(0).permute(1, 2, 0).cpu().detach().numpy()
        
        # Scale to [0, 255] range
        perturbation_np = (perturbation_np * 255.0).astype(np.float32)
        
        return perturbation_np
    
    def apply_poison(self, image: np.ndarray, 
                    perturbation: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Apply poisoning perturbation to image.
        
        Args:
            image: Input image array (H, W, C) in RGB
            perturbation: Pre-computed perturbation (if None, generates new)
            
        Returns:
            Poisoned image array
        """
        if perturbation is None:
            perturbation = self.generate_perturbation(image)
        
        # Apply perturbation
        poisoned = image.astype(np.float32) + perturbation * self.strength
        
        # Clip to valid range
        poisoned = np.clip(poisoned, 0, 255).astype(np.uint8)
        
        return poisoned
    
    def compute_poison_loss(self, original: np.ndarray, 
                          perturbed: np.ndarray) -> float:
        """
        Compute poisoning loss (how effective the poison is).
        
        Args:
            original: Original image
            perturbed: Perturbed image
            
        Returns:
            Loss value (higher = more effective poison)
        """
        # Normalize images
        orig_norm = original.astype(np.float32) / 255.0
        pert_norm = perturbed.astype(np.float32) / 255.0
        
        # Convert to tensors
        orig_tensor = torch.from_numpy(orig_norm).permute(2, 0, 1).unsqueeze(0).to(self.device)
        pert_tensor = torch.from_numpy(pert_norm).permute(2, 0, 1).unsqueeze(0).to(self.device)
        
        # Get predictions
        with torch.no_grad():
            orig_output = self.model(orig_tensor)
            pert_output = self.model(pert_tensor)
            
            orig_pred = orig_output.argmax(dim=1)
            pert_pred = pert_output.argmax(dim=1)
            
            # Loss = 1 if prediction changed, 0 otherwise
            loss = float((orig_pred != pert_pred).item())
            
            # Also consider confidence change
            orig_conf = torch.softmax(orig_output, dim=1).max().item()
            pert_conf = torch.softmax(pert_output, dim=1).max().item()
            conf_loss = abs(orig_conf - pert_conf)
            
            return loss + conf_loss
