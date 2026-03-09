"""
Text adversarial poisoning module.
Generates adversarial text perturbations that cause AI models to misclassify or produce faulty outputs.
"""

import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
from typing import Optional, List, Dict
import numpy as np


class TextPoisoner:
    """
    Generates adversarial text perturbations to poison AI model training.
    Shifts text in embedding space to cause misclassification or faulty outputs.
    """
    
    def __init__(self, strength: float = 0.1, model_name: str = "bert-base-uncased",
                 target_class: Optional[str] = None):
        """
        Initialize text poisoner.
        
        Args:
            strength: Poisoning strength (0.0 to 1.0)
            model_name: Base model for embeddings (bert-base-uncased, roberta-base, etc.)
            target_class: Target class for poisoning (None = untargeted)
        """
        self.strength = strength
        self.model_name = model_name
        self.target_class = target_class
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
    
    def generate_perturbation(self, text: str, target_label: Optional[int] = None,
                            iterations: int = 10) -> torch.Tensor:
        """
        Generate adversarial perturbation for text using embedding space attacks.
        
        Args:
            text: Input text string
            target_label: Target label for poisoning (None = untargeted)
            iterations: Number of optimization iterations
            
        Returns:
            Perturbation tensor in embedding space
        """
        # Tokenize text
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, 
                               truncation=True, max_length=512).to(self.device)
        
        # Get original embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            original_embeddings = outputs.last_hidden_state
        
        # Initialize perturbation
        perturbation = torch.zeros_like(original_embeddings)
        perturbation.requires_grad = True
        
        # If no target label, use untargeted attack
        if target_label is None:
            # Get current prediction (simplified - would use actual classifier)
            target_label = 0  # Placeholder
        
        # Optimize perturbation
        optimizer = torch.optim.Adam([perturbation], lr=0.01)
        
        for _ in range(iterations):
            optimizer.zero_grad()
            
            # Apply perturbation
            perturbed_embeddings = original_embeddings + perturbation * self.strength
            
            # Clip perturbation
            perturbation.data = torch.clamp(perturbation.data, -self.strength, self.strength)
            
            # Loss: maximize distance from original or target specific class
            # Simplified loss function
            loss = -torch.nn.functional.mse_loss(
                perturbed_embeddings, original_embeddings
            )
            
            loss.backward()
            optimizer.step()
        
        return perturbation.detach()
    
    def poison_text(self, text: str, perturbation: Optional[torch.Tensor] = None) -> str:
        """
        Apply poisoning to text by modifying embeddings.
        
        Note: This is a simplified version. In practice, you'd need to:
        1. Modify embeddings
        2. Find nearest tokens in embedding space
        3. Replace original tokens with adversarial tokens
        
        Args:
            text: Input text
            perturbation: Pre-computed perturbation (if None, generates new)
            
        Returns:
            Poisoned text (with adversarial modifications)
        """
        if perturbation is None:
            perturbation = self.generate_perturbation(text)
        
        # Tokenize
        inputs = self.tokenizer(text, return_tensors="pt", padding=True,
                               truncation=True, max_length=512).to(self.device)
        
        # Get embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state
        
        # Apply perturbation
        poisoned_embeddings = embeddings + perturbation * self.strength
        
        # In practice, you'd decode back to text tokens
        # For now, return modified text with subtle changes
        # This is a placeholder - real implementation would use embedding-to-token mapping
        
        # Simple approach: Add invisible unicode characters or modify spacing
        poisoned_text = self._apply_text_modifications(text)
        
        return poisoned_text
    
    def _apply_text_modifications(self, text: str) -> str:
        """
        Apply subtle text modifications that are adversarial but preserve readability.
        Uses invisible unicode, zero-width spaces, or character substitutions.
        """
        # Add zero-width spaces (invisible but affect embeddings)
        # Use Unicode zero-width characters
        zero_width_space = '\u200B'  # Zero-width space
        zero_width_non_joiner = '\u200C'  # Zero-width non-joiner
        
        # Insert at strategic positions (every N characters)
        modified = []
        for i, char in enumerate(text):
            modified.append(char)
            # Insert invisible characters periodically
            if i > 0 and i % 10 == 0:
                if i % 20 == 0:
                    modified.append(zero_width_space)
                else:
                    modified.append(zero_width_non_joiner)
        
        return ''.join(modified)
    
    def compute_poison_loss(self, original_text: str, 
                           poisoned_text: str) -> float:
        """
        Compute poisoning loss (how effective the poison is).
        
        Args:
            original_text: Original text
            poisoned_text: Poisoned text
            
        Returns:
            Loss value (higher = more effective poison)
        """
        # Get embeddings for both
        orig_inputs = self.tokenizer(original_text, return_tensors="pt",
                                    padding=True, truncation=True,
                                    max_length=512).to(self.device)
        pois_inputs = self.tokenizer(poisoned_text, return_tensors="pt",
                                    padding=True, truncation=True,
                                    max_length=512).to(self.device)
        
        with torch.no_grad():
            orig_outputs = self.model(**orig_inputs)
            pois_outputs = self.model(**pois_inputs)
            
            orig_emb = orig_outputs.last_hidden_state.mean(dim=1)
            pois_emb = pois_outputs.last_hidden_state.mean(dim=1)
            
            # Loss = distance in embedding space
            loss = torch.nn.functional.mse_loss(orig_emb, pois_emb).item()
            
            return loss
