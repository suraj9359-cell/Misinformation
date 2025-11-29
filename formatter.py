"""
Response Formatter Module
Formats verification results into user-friendly responses
"""

from typing import List, Dict, Any
from datetime import datetime
import json


class ResponseFormatter:
    """Formats verification results for user display"""
    
    def __init__(self):
        self.max_quote_length = 25
    
    def format_response(self, verified_claims: List[Dict[str, Any]], original_input: str) -> Dict[str, Any]:
        """
        Format complete response with all verified claims
        
        Args:
            verified_claims: List of verification results
            original_input: Original user input
        
        Returns:
            Formatted response dictionary
        """
        response = {
            'timestamp': datetime.now().isoformat(),
            'input': original_input,
            'claims_verified': len(verified_claims),
            'results': []
        }
        
        for i, claim_result in enumerate(verified_claims, 1):
            claim_response = self._format_single_claim(claim_result, claim_number=i)
            response['results'].append(claim_response)
        
        # Add overall summary if multiple claims
        if len(verified_claims) > 1:
            response['summary'] = self._generate_summary(verified_claims)
        
        return response
    
    def _format_single_claim(self, claim_result: Dict[str, Any], claim_number: int = 1) -> Dict[str, Any]:
        """Format a single claim's verification result"""
        verdict = claim_result.get('verdict', 'Unverified')
        confidence = claim_result.get('confidence_score', 0)
        rationale = claim_result.get('rationale', '')
        evidence = claim_result.get('evidence_summary', [])
        
        # Build explanation
        explanation = self._build_explanation(verdict, confidence, evidence, rationale)
        
        # Build evidence list
        evidence_list = self._format_evidence_list(evidence)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(verdict, confidence)
        
        # Generate social-shareable one-liner
        social_summary = self._generate_social_summary(verdict, confidence)
        
        return {
            'claim_number': claim_number,
            'verdict_line': f"Verdict: {verdict} — Confidence: {confidence}%",
            'explanation': explanation,
            'evidence': evidence_list,
            'recommendation': recommendation,
            'social_summary': social_summary,
            'timestamp': datetime.now().isoformat(),
            'detailed': {
                'verdict': verdict,
                'confidence': confidence,
                'rationale': rationale,
                'evidence_count': len(evidence)
            }
        }
    
    def _build_explanation(
        self, verdict: str, confidence: int, evidence: List[Dict], rationale: str
    ) -> str:
        """Build 2-4 sentence explanation"""
        sentences = []
        
        # Opening sentence
        if verdict == 'Supported':
            sentences.append(f"This claim appears to be supported by evidence (confidence: {confidence}%).")
        elif verdict == 'Partially true':
            sentences.append(f"This claim is partially true but may be misleading (confidence: {confidence}%).")
        elif verdict == 'Contradicted':
            sentences.append(f"This claim is contradicted by available evidence (confidence: {confidence}%).")
        else:
            sentences.append(f"Insufficient evidence to verify this claim (confidence: {confidence}%).")
        
        # Evidence summary
        if evidence:
            top_evidence = evidence[0]
            finding = top_evidence.get('finding', '')
            if finding:
                # Truncate if too long
                if len(finding) > 150:
                    finding = finding[:147] + '...'
                sentences.append(f"Key evidence: {finding}")
        
        # Rationale
        if rationale and rationale != 'No reliable evidence found':
            sentences.append(f"Assessment based on: {rationale}.")
        
        # Note about common misinterpretations if applicable
        if verdict in ['Partially true', 'Contradicted'] and confidence > 50:
            sentences.append("This claim may be commonly misunderstood or taken out of context.")
        
        return ' '.join(sentences)
    
    def _format_evidence_list(self, evidence: List[Dict]) -> List[Dict[str, str]]:
        """Format evidence into bullet-point list"""
        formatted = []
        
        for ev in evidence[:3]:  # Top 3 sources
            formatted.append({
                'source': f"{ev.get('title', 'Unknown')} — {ev.get('domain', 'Unknown')}",
                'finding': ev.get('finding', 'No summary available'),
                'date': ev.get('date', 'Unknown')
            })
        
        return formatted
    
    def _generate_recommendation(self, verdict: str, confidence: int) -> str:
        """Generate recommendation based on verdict and confidence"""
        if verdict == 'Supported' and confidence >= 70:
            return "This claim appears reliable. You can share this information, but consider checking for updates if the topic is time-sensitive."
        elif verdict == 'Supported' and confidence < 70:
            return "This claim has some support but confidence is moderate. Verify with additional sources before sharing."
        elif verdict == 'Partially true':
            return "This claim needs context. Do not share without additional verification and full context."
        elif verdict == 'Contradicted':
            return "This claim is contradicted by evidence. Do not share. Consult authoritative sources for accurate information."
        else:
            return "Insufficient evidence to verify. Do not share. Check for updates from authoritative sources or consult experts."
    
    def _generate_social_summary(self, verdict: str, confidence: int) -> str:
        """Generate one-sentence summary for social sharing"""
        if verdict == 'Supported':
            return f"Fact-check: {verdict.lower()} ({confidence}% confidence)."
        elif verdict == 'Contradicted':
            return f"Fact-check: {verdict.lower()} ({confidence}% confidence)."
        else:
            return f"Fact-check: {verdict.lower()} ({confidence}% confidence). Verify with additional sources."
    
    def _generate_summary(self, verified_claims: List[Dict[str, Any]]) -> str:
        """Generate overall summary for multiple claims"""
        total = len(verified_claims)
        supported = sum(1 for c in verified_claims if c.get('verdict') == 'Supported')
        contradicted = sum(1 for c in verified_claims if c.get('verdict') == 'Contradicted')
        unverified = sum(1 for c in verified_claims if c.get('verdict') == 'Unverified / Insufficient evidence')
        
        parts = [f"Verified {total} claim(s):"]
        if supported > 0:
            parts.append(f"{supported} supported")
        if contradicted > 0:
            parts.append(f"{contradicted} contradicted")
        if unverified > 0:
            parts.append(f"{unverified} unverified")
        
        return ', '.join(parts)
    
    def format_human_readable(self, response: Dict[str, Any]) -> str:
        """Format response as human-readable text"""
        lines = []
        
        lines.append("=" * 60)
        lines.append("TRUTHBOT - Fact-Checking Results")
        lines.append("=" * 60)
        lines.append("")
        
        if response.get('claims_verified', 0) > 1:
            lines.append(f"Summary: {response.get('summary', '')}")
            lines.append("")
        
        for result in response.get('results', []):
            lines.append(f"\nClaim #{result.get('claim_number', 1)}")
            lines.append("-" * 60)
            lines.append(f"{result.get('verdict_line', '')}")
            lines.append("")
            lines.append("Explanation:")
            lines.append(f"  {result.get('explanation', '')}")
            lines.append("")
            
            evidence = result.get('evidence', [])
            if evidence:
                lines.append("Evidence:")
                for ev in evidence:
                    lines.append(f"  • {ev.get('source', 'Unknown')}")
                    lines.append(f"    {ev.get('finding', '')}")
                    if ev.get('date') and ev.get('date') != 'Unknown':
                        lines.append(f"    Date: {ev.get('date')}")
                    lines.append("")
            
            lines.append(f"Recommendation: {result.get('recommendation', '')}")
            lines.append("")
        
        lines.append("=" * 60)
        lines.append("Note: Always verify critical information with authoritative sources.")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def format_error(self, error_message: str) -> Dict[str, Any]:
        """Format error response"""
        return {
            'timestamp': datetime.now().isoformat(),
            'error': True,
            'message': error_message,
            'recommendation': 'Please rephrase your input or provide more specific claims to verify.'
        }

