#!/usr/bin/env python3
"""
Example usage of TRUTHBOT
"""

from truthbot import TruthBot

def main():
    """Example fact-checking session"""
    bot = TruthBot()
    
    # Example claims to verify
    test_claims = [
        "COVID-19 vaccines cause infertility",
        "The Earth is flat",
        "Drinking 8 glasses of water per day is necessary for health"
    ]
    
    print("TRUTHBOT - Example Fact-Checking Session\n")
    print("=" * 60)
    
    for i, claim in enumerate(test_claims, 1):
        print(f"\nExample {i}: Verifying claim...")
        print(f"Claim: {claim}\n")
        
        try:
            response = bot.process_input(claim)
            
            # Display formatted output
            formatted = bot.formatter.format_human_readable(response)
            print(formatted)
            
        except Exception as e:
            print(f"Error processing claim: {e}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

