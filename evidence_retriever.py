"""
Evidence Retrieval Module
Retrieves evidence from multiple sources for fact-checking
"""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class EvidenceRetriever:
    """Retrieves evidence from web search and trusted sources"""
    
    def __init__(self):
        self.trusted_domains = [
            'who.int', 'cdc.gov', 'un.org', 'snopes.com', 'politifact.com',
            'factcheck.org', 'reuters.com', 'ap.org', 'bbc.com', 'npr.org',
            'science.org', 'nature.com', 'pubmed.ncbi.nlm.nih.gov',
            'gov.uk', 'europa.eu', 'nih.gov', 'fda.gov'
        ]
        self.max_sources_per_claim = 5
    
    def retrieve_evidence(self, claim_text: str, demo_mode: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve evidence for a claim from multiple sources
        
        Args:
            claim_text: The claim to verify
            demo_mode: If True, use mock evidence when no API results found
        
        Returns:
            List of evidence dictionaries with 'title', 'url', 'domain', 'snippet', 'date'
        """
        evidence = []
        
        # Strategy 1: Search trusted fact-checking sites
        fact_check_evidence = self._search_fact_checkers(claim_text)
        evidence.extend(fact_check_evidence)
        
        # Strategy 2: Search trusted news and official sources
        if len(evidence) < self.max_sources_per_claim:
            news_evidence = self._search_trusted_sources(claim_text)
            evidence.extend(news_evidence)
        
        # Strategy 3: General web search (if needed)
        if len(evidence) < self.max_sources_per_claim:
            web_evidence = self._web_search(claim_text)
            evidence.extend(web_evidence)
        
        # If no evidence found and demo mode, use mock evidence
        if not evidence and demo_mode:
            evidence = self._generate_demo_evidence(claim_text)
        
        # Deduplicate and rank by reliability
        evidence = self._deduplicate_and_rank(evidence)
        
        return evidence[:self.max_sources_per_claim]
    
    def _search_fact_checkers(self, claim_text: str) -> List[Dict[str, Any]]:
        """Search dedicated fact-checking websites"""
        evidence = []
        
        fact_check_sites = [
            ('snopes.com', f'site:snopes.com "{claim_text}"'),
            ('politifact.com', f'site:politifact.com "{claim_text}"'),
            ('factcheck.org', f'site:factcheck.org "{claim_text}"')
        ]
        
        for domain, query in fact_check_sites:
            results = self._perform_search(query, domain)
            evidence.extend(results)
        
        return evidence
    
    def _search_trusted_sources(self, claim_text: str) -> List[Dict[str, Any]]:
        """Search trusted official and news sources"""
        evidence = []
        
        # Search official health/science sources
        official_sources = [
            ('who.int', f'site:who.int "{claim_text}"'),
            ('cdc.gov', f'site:cdc.gov "{claim_text}"'),
            ('nih.gov', f'site:nih.gov "{claim_text}"')
        ]
        
        for domain, query in official_sources:
            results = self._perform_search(query, domain)
            evidence.extend(results)
        
        # Search trusted news sources
        news_sources = [
            ('reuters.com', f'site:reuters.com "{claim_text}"'),
            ('ap.org', f'site:ap.org "{claim_text}"'),
            ('bbc.com', f'site:bbc.com "{claim_text}"')
        ]
        
        for domain, query in news_sources:
            results = self._perform_search(query, domain)
            evidence.extend(results)
        
        return evidence
    
    def _web_search(self, claim_text: str) -> List[Dict[str, Any]]:
        """Perform general web search"""
        query = f'"{claim_text}" fact check verify'
        return self._perform_search(query)
    
    def _perform_search(self, query: str, domain_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Perform a web search (placeholder - in production, use search API)
        
        Note: This is a placeholder implementation. In production, you would:
        - Use Google Custom Search API, Bing Search API, or similar
        - Use SerpAPI, ScraperAPI, or other search services
        - Implement proper rate limiting and error handling
        """
        # Placeholder: Return mock results for demonstration
        # In production, replace with actual API calls
        
        results = []
        
        # Example: If using a search API, it would look like:
        # try:
        #     response = requests.get(
        #         'https://api.example.com/search',
        #         params={'q': query, 'key': API_KEY},
        #         timeout=10
        #     )
        #     data = response.json()
        #     for item in data.get('results', [])[:3]:
        #         results.append({
        #             'title': item.get('title', ''),
        #             'url': item.get('url', ''),
        #             'domain': self._extract_domain(item.get('url', '')),
        #             'snippet': item.get('snippet', ''),
        #             'date': item.get('date', datetime.now().strftime('%Y-%m-%d'))
        #         })
        # except Exception as e:
        #     print(f"Search error: {e}", file=sys.stderr)
        
        # For now, return empty list (will be populated by actual API integration)
        return results
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return ''
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ''
    
    def _deduplicate_and_rank(self, evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates and rank by source reliability"""
        # Remove duplicates by URL
        seen_urls = set()
        unique_evidence = []
        for item in evidence:
            url = item.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_evidence.append(item)
        
        # Rank by domain trustworthiness
        def reliability_score(item: Dict[str, Any]) -> int:
            domain = item.get('domain', '').lower()
            score = 0
            
            # Fact-checkers get highest priority
            if any(fc in domain for fc in ['snopes', 'politifact', 'factcheck']):
                score += 100
            # Official sources
            elif any(official in domain for official in ['who.int', 'cdc.gov', 'nih.gov', 'fda.gov', 'un.org']):
                score += 80
            # Trusted news
            elif any(news in domain for news in ['reuters', 'ap.org', 'bbc', 'npr']):
                score += 60
            # Other trusted domains
            elif domain in self.trusted_domains:
                score += 40
            
            return score
        
        unique_evidence.sort(key=reliability_score, reverse=True)
        
        return unique_evidence
    
    def _generate_demo_evidence(self, claim_text: str) -> List[Dict[str, Any]]:
        """
        Generate demo evidence for testing/demonstration purposes
        In production, this would be replaced by actual API calls
        """
        claim_lower = claim_text.lower()
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Context-aware demo evidence based on claim keywords
        evidence = []
        
        # Health/medical claims
        if any(term in claim_lower for term in ['vaccine', 'covid', 'health', 'medical', 'disease']):
            evidence.extend([
                {
                    'title': f'Fact Check: {claim_text[:60]}',
                    'url': 'https://www.cdc.gov/factcheck/example',
                    'domain': 'cdc.gov',
                    'snippet': 'Multiple peer-reviewed studies and clinical trials have examined this claim. The evidence from authoritative health organizations supports this statement.',
                    'date': '2024-01-15'
                },
                {
                    'title': f'Verification: {claim_text[:60]}',
                    'url': 'https://www.snopes.com/factcheck/example',
                    'domain': 'snopes.com',
                    'snippet': 'This claim has been verified by multiple independent sources. Fact-checkers have reviewed the available evidence and found it to be accurate.',
                    'date': '2024-02-01'
                },
                {
                    'title': f'WHO Statement: {claim_text[:50]}',
                    'url': 'https://www.who.int/news/example',
                    'domain': 'who.int',
                    'snippet': 'The World Health Organization has published guidance on this topic. Scientific evidence from multiple countries supports this conclusion.',
                    'date': '2023-12-10'
                }
            ])
        # Science/technology claims
        elif any(term in claim_lower for term in ['earth', 'climate', 'science', 'study', 'research']):
            evidence.extend([
                {
                    'title': f'Scientific Review: {claim_text[:60]}',
                    'url': 'https://www.nature.com/articles/example',
                    'domain': 'nature.com',
                    'snippet': 'Published research in peer-reviewed journals has extensively studied this topic. The scientific consensus supports this claim.',
                    'date': '2024-01-20'
                },
                {
                    'title': f'Fact Check: {claim_text[:60]}',
                    'url': 'https://www.politifact.com/factcheck/example',
                    'domain': 'politifact.com',
                    'snippet': 'This claim has been fact-checked by multiple independent organizations. The evidence is clear and well-documented.',
                    'date': '2024-02-05'
                }
            ])
        # General claims
        else:
            evidence.extend([
                {
                    'title': f'Fact Check: {claim_text[:60]}',
                    'url': 'https://www.snopes.com/factcheck/example',
                    'domain': 'snopes.com',
                    'snippet': 'This claim has been investigated by fact-checkers. Multiple sources have verified the accuracy of this statement.',
                    'date': current_date
                },
                {
                    'title': f'Verification Report: {claim_text[:55]}',
                    'url': 'https://www.factcheck.org/article/example',
                    'domain': 'factcheck.org',
                    'snippet': 'Independent verification confirms this claim. Evidence from reliable sources supports this conclusion.',
                    'date': '2024-01-10'
                },
                {
                    'title': f'Reuters Fact Check: {claim_text[:55]}',
                    'url': 'https://www.reuters.com/factcheck/example',
                    'domain': 'reuters.com',
                    'snippet': 'Reuters has fact-checked this claim and found it to be accurate based on available evidence from authoritative sources.',
                    'date': '2024-01-25'
                }
            ])
        
        return evidence[:self.max_sources_per_claim]

