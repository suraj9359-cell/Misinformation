"""
Verification and Scoring Module
Verifies claims against evidence and computes confidence scores
"""

from typing import List, Dict, Any
from datetime import datetime
import re


class Verifier:
    """Verifies claims against evidence and computes confidence scores"""
    
    def __init__(self):
        self.verdict_labels = {
            'supported': 'Supported',
            'partially_true': 'Partially true',
            'unverified': 'Unverified / Insufficient evidence',
            'contradicted': 'Contradicted'
        }
    
    def verify_claim(self, claim: Dict[str, Any], evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify a claim against evidence and compute confidence score
        
        Args:
            claim: Claim dictionary with 'text', 'inferred', 'queries'
            evidence: List of evidence dictionaries
        
        Returns:
            Verification dictionary with 'verdict', 'confidence_score', 'rationale', 'evidence_summary'
        """
        if not evidence:
            return self._create_verification_result(
                verdict='unverified',
                confidence=0,
                rationale='No evidence found',
                evidence_summary=[]
            )
        
        # Analyze evidence
        support_count = 0
        contradict_count = 0
        partial_count = 0
        authoritative_count = 0
        recent_count = 0
        
        evidence_summary = []
        current_date = datetime.now()
        
        for ev in evidence:
            # Check if evidence supports, contradicts, or is partial
            relevance = self._analyze_relevance(claim['text'], ev)
            
            if relevance == 'supports':
                support_count += 1
            elif relevance == 'contradicts':
                contradict_count += 1
            elif relevance == 'partial':
                partial_count += 1
            
            # Check source authority
            if self._is_authoritative_source(ev.get('domain', '')):
                authoritative_count += 1
            
            # Check recency (within last 2 years)
            ev_date = ev.get('date', '')
            if ev_date and self._is_recent(ev_date, current_date, years=2):
                recent_count += 1
            
            # Create evidence summary entry
            evidence_summary.append({
                'title': ev.get('title', 'Unknown'),
                'domain': ev.get('domain', 'Unknown'),
                'date': ev_date or 'Unknown',
                'finding': self._extract_finding(ev, relevance),
                'relevance': relevance
            })
        
        # Determine verdict
        verdict = self._determine_verdict(
            support_count, contradict_count, partial_count, len(evidence)
        )
        
        # Compute confidence score
        confidence = self._compute_confidence(
            support_count, contradict_count, partial_count,
            authoritative_count, recent_count, len(evidence),
            claim.get('inferred', False)
        )
        
        # Generate rationale
        rationale = self._generate_rationale(
            verdict, confidence, support_count, contradict_count,
            authoritative_count, recent_count
        )
        
        return self._create_verification_result(
            verdict=verdict,
            confidence=confidence,
            rationale=rationale,
            evidence_summary=evidence_summary
        )
    
    def _analyze_relevance(self, claim_text: str, evidence: Dict[str, Any]) -> str:
        """
        Analyze if evidence supports, contradicts, or partially addresses the claim
        
        Returns: 'supports', 'contradicts', 'partial', or 'unclear'
        """
        snippet = evidence.get('snippet', '').lower()
        title = evidence.get('title', '').lower()
        combined_text = (snippet + ' ' + title).lower()
        claim_lower = claim_text.lower()
        
        # Keywords indicating support
        support_keywords = [
            'true', 'correct', 'accurate', 'confirmed', 'verified',
            'fact', 'evidence shows', 'study confirms', 'proven'
        ]
        
        # Keywords indicating contradiction
        contradict_keywords = [
            'false', 'incorrect', 'misleading', 'debunked', 'untrue',
            'hoax', 'myth', 'not true', 'no evidence', 'disproven'
        ]
        
        # Keywords indicating partial/mixed
        partial_keywords = [
            'partially', 'somewhat', 'mostly', 'but', 'however',
            'misleading', 'context needed', 'depends'
        ]
        
        support_score = sum(1 for kw in support_keywords if kw in combined_text)
        contradict_score = sum(1 for kw in contradict_keywords if kw in combined_text)
        partial_score = sum(1 for kw in partial_keywords if kw in combined_text)
        
        # Check if claim keywords appear in evidence (direct relevance)
        claim_keywords = set(re.findall(r'\b\w{4,}\b', claim_lower))
        evidence_keywords = set(re.findall(r'\b\w{4,}\b', combined_text))
        overlap = len(claim_keywords & evidence_keywords)
        relevance_threshold = max(2, len(claim_keywords) * 0.3)
        
        if contradict_score > support_score and contradict_score > 0:
            return 'contradicts'
        elif support_score > contradict_score and support_score > 0:
            return 'supports'
        elif partial_score > 0 or (overlap >= relevance_threshold and support_score == contradict_score):
            return 'partial'
        elif overlap >= relevance_threshold:
            return 'supports'  # Default to supports if keywords match
        else:
            return 'unclear'
    
    def _is_authoritative_source(self, domain: str) -> bool:
        """Check if source is authoritative"""
        domain_lower = domain.lower()
        authoritative_domains = [
            'who.int', 'cdc.gov', 'nih.gov', 'fda.gov', 'un.org',
            'snopes.com', 'politifact.com', 'factcheck.org',
            'reuters.com', 'ap.org', 'bbc.com', 'npr.org',
            'science.org', 'nature.com', 'pubmed'
        ]
        return any(auth in domain_lower for auth in authoritative_domains)
    
    def _is_recent(self, date_str: str, current_date: datetime, years: int = 2) -> bool:
        """Check if date is within specified years"""
        try:
            # Try various date formats
            date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%B %d, %Y', '%b %d, %Y']
            ev_date = None
            
            for fmt in date_formats:
                try:
                    ev_date = datetime.strptime(date_str, fmt)
                    break
                except:
                    continue
            
            if not ev_date:
                return False
            
            years_diff = (current_date - ev_date).days / 365.25
            return years_diff <= years
        except:
            return False
    
    def _extract_finding(self, evidence: Dict[str, Any], relevance: str) -> str:
        """Extract one-line finding from evidence"""
        snippet = evidence.get('snippet', '')
        if snippet:
            # Take first sentence or first 100 chars
            sentences = snippet.split('.')
            if sentences:
                finding = sentences[0].strip()
                if len(finding) > 100:
                    finding = finding[:97] + '...'
                return finding
        
        # Fallback to title
        title = evidence.get('title', '')
        if title:
            return title[:100]
        
        return f"Evidence from {evidence.get('domain', 'source')} ({relevance})"
    
    def _determine_verdict(self, support: int, contradict: int, partial: int, total: int) -> str:
        """Determine verdict based on evidence analysis"""
        if total == 0:
            return 'unverified'
        
        if contradict > support and contradict > 0:
            return 'contradicted'
        elif support > contradict and support >= 2:
            return 'supported'
        elif partial > 0 or (support == 1 and contradict == 0):
            return 'partially_true'
        elif support == 1:
            return 'partially_true'
        else:
            return 'unverified'
    
    def _compute_confidence(
        self, support: int, contradict: int, partial: int,
        authoritative: int, recent: int, total: int, inferred: bool
    ) -> int:
        """
        Compute confidence score (0-100)
        
        Factors:
        - Number of supporting sources
        - Source authority
        - Recency
        - Directness (inferred claims get lower confidence)
        """
        if total == 0:
            return 0
        
        # Base score from support
        base_score = min(70, support * 20)
        
        # Authority bonus
        authority_bonus = min(20, authoritative * 5)
        
        # Recency bonus
        recency_bonus = min(10, recent * 2)
        
        # Penalty for contradictions
        contradiction_penalty = contradict * 15
        
        # Penalty for inferred claims
        inferred_penalty = 10 if inferred else 0
        
        # Penalty for partial evidence
        partial_penalty = partial * 5
        
        confidence = base_score + authority_bonus + recency_bonus
        confidence -= contradiction_penalty + inferred_penalty + partial_penalty
        
        # Normalize to 0-100
        confidence = max(0, min(100, confidence))
        
        return int(confidence)
    
    def _generate_rationale(
        self, verdict: str, confidence: int, support: int, contradict: int,
        authoritative: int, recent: int
    ) -> str:
        """Generate one-line rationale for confidence score"""
        parts = []
        
        if support > 0:
            parts.append(f"{support} supporting source(s)")
        if authoritative > 0:
            parts.append(f"{authoritative} authoritative source(s)")
        if recent > 0:
            parts.append(f"{recent} recent source(s)")
        if contradict > 0:
            parts.append(f"{contradict} contradicting source(s)")
        
        if not parts:
            return "No reliable evidence found"
        
        rationale = ", ".join(parts)
        if confidence < 50:
            rationale += " (low confidence due to limited or mixed evidence)"
        elif confidence > 80:
            rationale += " (high confidence from multiple authoritative sources)"
        
        return rationale
    
    def _create_verification_result(
        self, verdict: str, confidence: int, rationale: str, evidence_summary: List[Dict]
    ) -> Dict[str, Any]:
        """Create standardized verification result"""
        return {
            'verdict': self.verdict_labels.get(verdict, verdict),
            'confidence_score': confidence,
            'rationale': rationale,
            'evidence_summary': evidence_summary,
            'verdict_key': verdict
        }

