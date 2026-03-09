"""
Similarity analysis for solution diversity enforcement.

Uses AST-based code similarity (no ML required, fast and deterministic).
"""
import ast
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class SimilarityAnalyzer:
    """
    Analyzes code similarity using AST comparison.
    
    Methods:
    1. AST structure similarity (tree edit distance)
    2. File structure similarity (directory tree)
    3. Hash-based exact matching
    """
    
    def __init__(self):
        self._ast_cache: Dict[str, ast.AST] = {}
        self._hash_cache: Dict[str, str] = {}
    
    def calculate_similarity(
        self,
        solution1_path: Path,
        solution2_path: Path,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate overall similarity between two solutions.
        
        Args:
            solution1_path: Path to first solution directory
            solution2_path: Path to second solution directory
            weights: Weights for different similarity metrics
                     Default: {"ast": 0.6, "structure": 0.3, "hash": 0.1}
        
        Returns:
            Similarity score [0.0, 1.0] where 1.0 is identical
        """
        if weights is None:
            weights = {"ast": 0.6, "structure": 0.3, "hash": 0.1}
        
        # AST similarity (code structure)
        ast_sim = self._ast_similarity(solution1_path, solution2_path)
        
        # File structure similarity
        struct_sim = self._structure_similarity(solution1_path, solution2_path)
        
        # Hash-based similarity (exact matches)
        hash_sim = self._hash_similarity(solution1_path, solution2_path)
        
        # Weighted combination
        overall = (
            weights["ast"] * ast_sim +
            weights["structure"] * struct_sim +
            weights["hash"] * hash_sim
        )
        
        return overall
    
    def _ast_similarity(self, path1: Path, path2: Path) -> float:
        """Calculate AST-based similarity."""
        asts1 = self._extract_asts(path1)
        asts2 = self._extract_asts(path2)
        
        if not asts1 or not asts2:
            return 0.0
        
        # Compare ASTs using tree edit distance approximation
        similarities = []
        for ast1 in asts1:
            best_match = 0.0
            for ast2 in asts2:
                sim = self._ast_compare(ast1, ast2)
                best_match = max(best_match, sim)
            similarities.append(best_match)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _extract_asts(self, solution_path: Path) -> List[ast.AST]:
        """Extract ASTs from all Python files in solution."""
        asts = []
        
        for py_file in solution_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                asts.append(tree)
            except SyntaxError:
                logger.warning(f"Failed to parse {py_file}")
                continue
            except Exception as e:
                logger.error(f"Error extracting AST from {py_file}: {e}")
                continue
        
        return asts
    
    def _ast_compare(self, ast1: ast.AST, ast2: ast.AST) -> float:
        """
        Compare two ASTs using structure similarity.
        
        Simple approach: Compare node types and structure depth.
        More sophisticated: Tree edit distance (Levenshtein on tree).
        """
        # Extract node signatures (type + depth)
        sig1 = self._ast_signature(ast1)
        sig2 = self._ast_signature(ast2)
        
        # Jaccard similarity on node signatures
        set1 = set(sig1)
        set2 = set(sig2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _ast_signature(self, node: ast.AST, depth: int = 0, max_depth: int = 10) -> List[str]:
        """Extract signature from AST (node types at each depth)."""
        if depth > max_depth:
            return []
        
        sig = [f"{type(node).__name__}:{depth}"]
        
        for child in ast.iter_child_nodes(node):
            sig.extend(self._ast_signature(child, depth + 1, max_depth))
        
        return sig
    
    def _structure_similarity(self, path1: Path, path2: Path) -> float:
        """Calculate file/directory structure similarity."""
        files1 = self._get_file_tree(path1)
        files2 = self._get_file_tree(path2)
        
        # Jaccard similarity on file paths (relative to solution root)
        set1 = set(files1)
        set2 = set(files2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _get_file_tree(self, solution_path: Path) -> Set[str]:
        """Get set of relative file paths in solution."""
        files = set()
        for file_path in solution_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(solution_path)
                files.add(str(rel_path))
        return files
    
    def _hash_similarity(self, path1: Path, path2: Path) -> float:
        """Calculate hash-based similarity (exact file matches)."""
        hashes1 = self._get_file_hashes(path1)
        hashes2 = self._get_file_hashes(path2)
        
        # Count matching hashes
        matches = len(hashes1 & hashes2)
        total = len(hashes1 | hashes2)
        
        return matches / total if total > 0 else 0.0
    
    def _get_file_hashes(self, solution_path: Path) -> Set[str]:
        """Get SHA256 hashes of all files."""
        hashes = set()
        
        for file_path in solution_path.rglob("*"):
            if file_path.is_file():
                file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
                hashes.add(file_hash)
        
        return hashes
    
    def find_most_similar(
        self,
        solution_path: Path,
        existing_solutions: List[Tuple[str, Path]],
        threshold: float = 0.85
    ) -> List[Tuple[str, float]]:
        """
        Find most similar existing solutions.
        
        Args:
            solution_path: Path to new solution
            existing_solutions: List of (solution_id, path) tuples
            threshold: Minimum similarity to report
        
        Returns:
            List of (solution_id, similarity_score) tuples, sorted by similarity
        """
        similarities = []
        
        for solution_id, existing_path in existing_solutions:
            sim = self.calculate_similarity(solution_path, existing_path)
            if sim >= threshold:
                similarities.append((solution_id, sim))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities
