"""
Module untuk fuzzy string matching
"""

from typing import List, Tuple, Optional
from thefuzz import fuzz, process

from .config import FUZZY


class FuzzyMatcher:
    """Kelas untuk fuzzy matching nama pelanggan"""
    
    def __init__(self, choices: Optional[List[str]] = None):
        self.choices = choices or []
    
    def set_choices(self, choices: List[str]) -> 'FuzzyMatcher':
        """Set daftar pilihan yang akan dicocokkan"""
        self.choices = choices
        return self
    
    def search(
        self, 
        query: str, 
        limit: int = None, 
        threshold: int = None
    ) -> List[Tuple[str, int]]:
        """
        Cari match fuzzy untuk query
        
        Returns:
            List of tuples (matched_string, score)
        """
        if not self.choices:
            return []
        
        if limit is None:
            limit = FUZZY.MAX_RESULTS
        
        if threshold is None:
            threshold = FUZZY.SCORE_THRESHOLD
        
        results = process.extract(
            query, 
            self.choices, 
            scorer=fuzz.partial_ratio, 
            limit=limit
        )
        
        # Filter berdasarkan threshold
        return [(name, score) for name, score in results if score >= threshold]
    
    def find_best_match(self, query: str) -> Optional[Tuple[str, int]]:
        """Cari match terbaik"""
        results = self.search(query, limit=1)
        return results[0] if results else None
    
    def is_good_match(self, score: int) -> bool:
        """Cek apakah score termasuk good match"""
        return score >= 80


# Helper functions untuk backward compatibility
def fuzzy_search(
    query: str, 
    choices: List[str], 
    limit: int = 10
) -> List[Tuple[str, int]]:
    """Fuzzy search helper function"""
    matcher = FuzzyMatcher(choices)
    return matcher.search(query, limit=limit)


def find_best_match(query: str, choices: List[str]) -> Optional[Tuple[str, int]]:
    """Find best match helper function"""
    matcher = FuzzyMatcher(choices)
    return matcher.find_best_match(query)
