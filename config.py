"""
Configuration file for TRUTHBOT
"""

import os
from typing import Dict, Any

# API Keys (set via environment variables in production)
API_KEYS = {
    'google_search': os.getenv('GOOGLE_SEARCH_API_KEY', ''),
    'google_cse_id': os.getenv('GOOGLE_CSE_ID', ''),
    'serpapi': os.getenv('SERPAPI_KEY', ''),
    'bing_search': os.getenv('BING_SEARCH_API_KEY', '')
}

# Trusted source domains
TRUSTED_DOMAINS = [
    # Fact-checkers
    'snopes.com',
    'politifact.com',
    'factcheck.org',
    'fullfact.org',
    'checkyourfact.com',
    
    # Official health/science
    'who.int',
    'cdc.gov',
    'nih.gov',
    'fda.gov',
    'epa.gov',
    'nasa.gov',
    
    # International organizations
    'un.org',
    'europa.eu',
    'gov.uk',
    
    # Trusted news
    'reuters.com',
    'ap.org',
    'bbc.com',
    'npr.org',
    'pbs.org',
    
    # Scientific journals
    'science.org',
    'nature.com',
    'pubmed.ncbi.nlm.nih.gov',
    'scholar.google.com'
]

# Search settings
SEARCH_SETTINGS = {
    'max_results_per_query': 10,
    'max_sources_per_claim': 5,
    'timeout_seconds': 10,
    'retry_attempts': 2
}

# Verification settings
VERIFICATION_SETTINGS = {
    'min_confidence_for_supported': 60,
    'recent_years_threshold': 2,
    'max_evidence_sources': 5
}

# Output settings
OUTPUT_SETTINGS = {
    'max_quote_length': 25,
    'max_explanation_sentences': 4,
    'max_evidence_sources_displayed': 3
}

