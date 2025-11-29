#!/usr/bin/env python3
"""
TRUTHBOT - An agentic fact-checking assistant
Main application entry point
"""

import sys
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
from claim_extractor import ClaimExtractor
from evidence_retriever import EvidenceRetriever
from verifier import Verifier
from formatter import ResponseFormatter


class TruthBot:
    """Main TRUTHBOT application class"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize TRUTHBOT with configuration"""
        self.claim_extractor = ClaimExtractor()
        self.evidence_retriever = EvidenceRetriever()
        self.verifier = Verifier()
        self.formatter = ResponseFormatter()
        self.logs = []
    
    def process_input(self, user_input: str, input_type: str = "text") -> Dict[str, Any]:
        """
        Main workflow: Extract claims → Retrieve evidence → Verify → Format response
        
        Args:
            user_input: User's input (text, image path, or URL)
            input_type: Type of input ('text', 'image', 'url')
        
        Returns:
            Formatted response dictionary
        """
        # Step 1: Claim Extraction
        claims = self.claim_extractor.extract_claims(user_input, input_type)
        
        if not claims:
            return self.formatter.format_error("No factual claims could be extracted from the input.")
        
        # Step 2-3: For each claim, retrieve evidence and verify
        verified_claims = []
        for claim in claims:
            # Retrieve evidence (demo_mode=True for demonstration when no API keys)
            evidence = self.evidence_retriever.retrieve_evidence(claim['text'], demo_mode=True)
            
            # Verify and score
            verification = self.verifier.verify_claim(claim, evidence)
            verified_claims.append(verification)
            
            # Log internally
            self._log_verification(claim, evidence, verification)
        
        # Step 4: Format response
        response = self.formatter.format_response(verified_claims, user_input)
        
        return response
    
    def _log_verification(self, claim: Dict, evidence: List[Dict], verification: Dict):
        """Internal logging for verification process"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'claim': claim['text'],
            'retrieval_queries': claim.get('queries', []),
            'top_sources': [s['title'] for s in evidence[:3]],
            'confidence_score': verification['confidence_score'],
            'verdict': verification['verdict']
        }
        self.logs.append(log_entry)
    
    def get_verification_logs(self) -> List[Dict]:
        """Get internal verification logs (for debugging/admin)"""
        return self.logs


def main():
    """Command-line interface for TRUTHBOT"""
    parser = argparse.ArgumentParser(
        description="TRUTHBOT - An agentic fact-checking assistant"
    )
    parser.add_argument(
        'input',
        nargs='?',
        help='Input text, image path, or URL to fact-check'
    )
    parser.add_argument(
        '-t', '--type',
        choices=['text', 'image', 'url'],
        default='text',
        help='Type of input (default: text)'
    )
    parser.add_argument(
        '-f', '--file',
        help='Read input from file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: stdout)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    
    args = parser.parse_args()
    
    # Get input
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            user_input = f.read()
    elif args.input:
        user_input = args.input
    else:
        # Interactive mode
        print("TRUTHBOT - Fact-checking Assistant")
        print("Enter your claim (or 'quit' to exit):")
        user_input = input().strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            return
    
    if not user_input:
        print("Error: No input provided")
        return
    
    # Process
    bot = TruthBot()
    try:
        response = bot.process_input(user_input, args.type)
        
        # Output
        if args.json:
            output_text = json.dumps(response, indent=2, ensure_ascii=False)
        else:
            output_text = bot.formatter.format_human_readable(response)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_text)
        else:
            print(output_text)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

