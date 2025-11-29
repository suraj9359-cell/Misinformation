"""
Claim Extraction Module
Extracts discrete factual claims from user input
"""

import re
from typing import List, Dict, Any
import json


class ClaimExtractor:
    """Extracts and parses factual claims from user input"""
    
    def __init__(self):
        self.inferred_marker = "[INFERRED]"
    
    def extract_claims(self, user_input: str, input_type: str = "text") -> List[Dict[str, Any]]:
        """
        Extract discrete factual claims from input
        
        Args:
            user_input: User's input text, image path, or URL
            input_type: Type of input ('text', 'image', 'url')
        
        Returns:
            List of claim dictionaries with 'text', 'inferred', and 'queries' fields
        """
        if input_type == "image":
            # For images, we'd need OCR - placeholder for now
            # In production, use libraries like pytesseract or cloud OCR APIs
            return self._extract_from_text("Image content analysis not yet implemented. Please provide text description.")
        elif input_type == "url":
            # For URLs, we'd fetch and parse content - placeholder
            return self._extract_from_text(f"URL content: {user_input}")
        else:
            return self._extract_from_text(user_input)
    
    def _extract_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract claims from text input"""
        claims = []
        
        # Clean and normalize text
        text = text.strip()
        if not text:
            return claims
        
        # Strategy 1: Look for explicit statements (sentences ending with periods)
        sentences = self._split_into_sentences(text)
        
        # Strategy 2: Look for numbered lists or bullet points
        numbered_claims = self._extract_numbered_claims(text)
        if numbered_claims:
            claims.extend(numbered_claims)
            return claims
        
        # Strategy 3: Extract declarative sentences that look like factual claims
        for sentence in sentences:
            claim = self._parse_sentence_as_claim(sentence)
            if claim:
                claims.append(claim)
        
        # If no claims found, treat entire input as one claim (inferred)
        if not claims:
            inferred_claim = {
                'text': text,
                'inferred': True,
                'queries': self._generate_search_queries(text)
            }
            claims.append(inferred_claim)
        
        return claims
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (can be enhanced with NLP libraries)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _extract_numbered_claims(self, text: str) -> List[Dict[str, Any]]:
        """Extract claims from numbered or bulleted lists"""
        claims = []
        
        # Pattern for numbered lists: "1. Claim", "2. Claim", etc.
        numbered_pattern = r'^\d+[\.\)]\s*(.+?)(?=\n\d+[\.\)]|\n\n|$)'
        matches = re.finditer(numbered_pattern, text, re.MULTILINE)
        
        for match in matches:
            claim_text = match.group(1).strip()
            if self._looks_like_factual_claim(claim_text):
                claims.append({
                    'text': claim_text,
                    'inferred': False,
                    'queries': self._generate_search_queries(claim_text)
                })
        
        return claims
    
    def _parse_sentence_as_claim(self, sentence: str) -> Dict[str, Any]:
        """Parse a sentence to determine if it's a factual claim"""
        sentence = sentence.strip()
        
        if not self._looks_like_factual_claim(sentence):
            return None
        
        # Determine if claim is inferred (questions, ambiguous statements)
        is_inferred = self._is_inferred_claim(sentence)
        
        return {
            'text': sentence,
            'inferred': is_inferred,
            'queries': self._generate_search_queries(sentence)
        }
    
    def _looks_like_factual_claim(self, text: str) -> bool:
        """Heuristic to determine if text looks like a factual claim"""
        text_lower = text.lower()
        
        # Skip very short text
        if len(text.split()) < 3:
            return False
        
        # Skip questions (unless they contain assertions)
        if text.strip().endswith('?') and not any(word in text_lower for word in ['claim', 'say', 'report', 'fact']):
            return False
        
        # Look for factual claim indicators
        factual_indicators = [
            'is', 'are', 'was', 'were', 'has', 'have', 'had',
            'causes', 'caused', 'leads to', 'results in',
            'according to', 'study shows', 'research indicates',
            'fact', 'truth', 'proven', 'evidence'
        ]
        
        return any(indicator in text_lower for indicator in factual_indicators)
    
    def _is_inferred_claim(self, text: str) -> bool:
        """Determine if a claim is inferred rather than explicit"""
        text_lower = text.lower()
        
        # Questions are inferred
        if text.strip().endswith('?'):
            return True
        
        # Ambiguous statements
        ambiguous_phrases = ['might', 'could', 'possibly', 'perhaps', 'maybe', 'seems']
        if any(phrase in text_lower for phrase in ambiguous_phrases):
            return True
        
        return False
    
    def _generate_search_queries(self, claim_text: str) -> List[str]:
        """Generate search queries for fact-checking a claim"""
        queries = []
        
        # Query 1: Direct claim
        queries.append(claim_text)
        
        # Query 2: Claim with "fact check" or "verify"
        queries.append(f'"{claim_text}" fact check')
        queries.append(f'"{claim_text}" verify')
        
        # Query 3: Extract key terms for targeted search
        key_terms = self._extract_key_terms(claim_text)
        if key_terms:
            queries.append(' '.join(key_terms[:3]) + ' fact check')
        
        return queries[:3]  # Limit to top 3 queries
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from claim for search"""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them'
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        key_terms = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Return unique terms, preserving order
        seen = set()
        unique_terms = []
        for term in key_terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        return unique_terms[:5]  # Top 5 key terms

