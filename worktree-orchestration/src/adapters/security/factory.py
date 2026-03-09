"""
Factory for creating security adapters with graceful fallback.
"""
from typing import Optional
from .semgrep_adapter import SemgrepAdapter
from .snyk_adapter import SnykAdapter
from .fallback_adapter import FallbackSecurityAdapter
from ..base import SecurityAdapter


class SecurityAdapterFactory:
    """
    Factory that creates security adapters with graceful fallback.
    
    Tries adapters in order of preference:
    1. Semgrep (if available)
    2. Snyk (if available)
    3. Fallback (always available)
    """
    
    @staticmethod
    def create(preferred_adapters: Optional[list] = None) -> SecurityAdapter:
        """
        Create a security adapter, trying preferred adapters first.
        
        Args:
            preferred_adapters: List of adapter names to try in order.
                               Default: ["semgrep", "snyk"]
        
        Returns:
            Available security adapter instance
        """
        if preferred_adapters is None:
            preferred_adapters = ["semgrep", "snyk"]
        
        # Try preferred adapters in order
        for adapter_name in preferred_adapters:
            adapter_name_lower = adapter_name.lower()
            
            if adapter_name_lower == "semgrep":
                adapter = SemgrepAdapter()
                if adapter.is_available():
                    return adapter
            
            elif adapter_name_lower == "snyk":
                adapter = SnykAdapter()
                if adapter.is_available():
                    return adapter
        
        # Fallback to neutral adapter
        return FallbackSecurityAdapter()
    
    @staticmethod
    def create_all_available() -> list[SecurityAdapter]:
        """
        Create all available security adapters.
        
        Returns:
            List of available adapter instances
        """
        adapters = []
        
        semgrep = SemgrepAdapter()
        if semgrep.is_available():
            adapters.append(semgrep)
        
        snyk = SnykAdapter()
        if snyk.is_available():
            adapters.append(snyk)
        
        # Always include fallback
        adapters.append(FallbackSecurityAdapter())
        
        return adapters
