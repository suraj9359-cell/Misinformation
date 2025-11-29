# TRUTHBOT - Fact-Checking Assistant

TRUTHBOT is an agentic fact-checking assistant that extracts factual claims from user inputs, verifies them against reliable sources, and provides evidence-backed confidence scores with clear verdicts.

## Features

- **Claim Extraction**: Automatically parses user input into discrete factual claims
- **Evidence Retrieval**: Searches trusted sources (WHO, CDC, fact-checkers, news orgs)
- **Verification & Scoring**: Computes confidence scores (0-100%) based on evidence quality
- **Clear Verdicts**: Provides Supported/Partially true/Unverified/Contradicted labels
- **User-Friendly Output**: Plain-language explanations with source citations
- **Multilingual Support**: Detects and responds in user's language (when configured)

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up API keys for web search:
```bash
export GOOGLE_SEARCH_API_KEY="your_key"
export GOOGLE_CSE_ID="your_cse_id"
# OR
export SERPAPI_KEY="your_serpapi_key"
```

## Usage

### Web App (responsive UI + authentication)

Run the Flask server and open the app in your browser (desktop or mobile):

```bash
python web_app.py
```

Visit `http://localhost:8000` to access the interface. Create an account (data is stored securely in a local SQLite database), sign in, and enter a claim. TRUTHBOT will show verdicts, confidence scores, and evidence cards optimized for any screen size.

#### API endpoint
The same server exposes `POST /api/fact-check` which accepts:

```json
{
  "input": "Your claim here",
  "type": "text"
}
```

and returns the structured JSON response used by the UI.

### Telegram Bot (chat interface)

Bring TRUTHBOT into Telegram for quick fact-checks on the go:

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. Export environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN="123456:ABC..."
   # Optional: Restrict usage to specific Telegram user IDs
   export TELEGRAM_ALLOWED_USER_IDS="123456789,987654321"
   ```
3. Start the bot:
   ```bash
   python telegram_bot.py
   ```

Send any claim/headline to your bot and it will respond with verdicts, confidence scores, and citations just like the CLI or web UI. Responses are truncated automatically if they near Telegram’s 4096-character limit.

### Authentication & database

- User profiles are stored in `truthbot.db` (created automatically).
- Passwords are hashed with Werkzeug; set `TRUTHBOT_SECRET_KEY` for production.
- Routes `/register`, `/login`, and `/logout` manage sessions.
- The `/api/fact-check` endpoint returns `401` when called without authentication.

### Command Line

**Basic usage:**
```bash
python truthbot.py "Your claim to fact-check here"
```

**From file:**
```bash
python truthbot.py -f input.txt
```

**Specify input type:**
```bash
python truthbot.py -t url "https://example.com/article"
python truthbot.py -t image "path/to/image.png"
```

**JSON output:**
```bash
python truthbot.py --json "Your claim" > results.json
```

**Save to file:**
```bash
python truthbot.py -o output.txt "Your claim"
```

### Python API

```python
from truthbot import TruthBot

bot = TruthBot()
response = bot.process_input("Your claim to verify")

# Access results
for result in response['results']:
    print(result['verdict_line'])
    print(result['explanation'])
    print(result['recommendation'])
```

## Output Format

TRUTHBOT provides structured responses with:

1. **Verdict Line**: `Verdict: Supported — Confidence: 85%`
2. **Explanation**: 2-4 sentence plain-language explanation
3. **Evidence**: Top 3 sources with findings and dates
4. **Recommendation**: Actionable guidance (share/verify/consult/ignore)
5. **Social Summary**: One-sentence shareable summary

## Example

**Input:**
```bash
python truthbot.py "COVID-19 vaccines cause infertility"
```

**Output:**
```
============================================================
TRUTHBOT - Fact-Checking Results
============================================================

Claim #1
------------------------------------------------------------
Verdict: Contradicted — Confidence: 92%

Explanation:
This claim is contradicted by available evidence (confidence: 92%).
Key evidence: Multiple studies have found no evidence that COVID-19 
vaccines cause infertility. Assessment based on: 3 supporting source(s), 
3 authoritative source(s), 2 recent source(s) (high confidence from 
multiple authoritative sources).

Evidence:
  • Fact Check: COVID-19 Vaccines and Infertility — snopes.com
    Multiple medical studies have found no link between COVID-19 
    vaccines and infertility in men or women.
    Date: 2023-08-15

  • CDC: COVID-19 Vaccines and Fertility — cdc.gov
    No evidence suggests that COVID-19 vaccines cause fertility 
    problems in women or men.
    Date: 2023-09-01

Recommendation: This claim is contradicted by evidence. Do not share. 
Consult authoritative sources for accurate information.
============================================================
```

## Architecture

- **truthbot.py**: Main application entry point
- **claim_extractor.py**: Extracts discrete claims from input
- **evidence_retriever.py**: Retrieves evidence from web/search APIs
- **verifier.py**: Verifies claims and computes confidence scores
- **formatter.py**: Formats results for user display
- **web_app.py**: Flask server powering the responsive web UI
- **telegram_bot.py**: Telegram interface for chat-based fact-checks
- **config.py**: Configuration and settings

## Configuration

Edit `config.py` to:
- Add/remove trusted source domains
- Adjust search settings
- Modify verification thresholds
- Configure output formatting

## API Integration

To enable actual web search (currently uses placeholder), integrate one of:

1. **Google Custom Search API**: Set `GOOGLE_SEARCH_API_KEY` and `GOOGLE_CSE_ID`
2. **SerpAPI**: Set `SERPAPI_KEY`
3. **Bing Search API**: Set `BING_SEARCH_API_KEY`

Then update `evidence_retriever.py` to use the actual API calls.

## Safety & Ethics

- Never invents sources or fabricates quotes
- Defaults to "Unverified" when evidence is weak
- Provides transparent source citations
- Conservative verification approach
- Respects privacy and avoids political persuasion

## Limitations

- Requires internet connection and API keys for full functionality
- Evidence retrieval currently uses placeholder (integrate search APIs)
- Image OCR not yet implemented (requires additional libraries)
- URL content fetching not yet implemented

## Development

To extend TRUTHBOT:

1. **Add new fact-checking sources**: Update `TRUSTED_DOMAINS` in `config.py`
2. **Improve claim extraction**: Enhance `claim_extractor.py` with NLP libraries
3. **Add search APIs**: Implement actual API calls in `evidence_retriever.py`
4. **Customize scoring**: Adjust confidence calculation in `verifier.py`
5. **Enhance formatting**: Modify output templates in `formatter.py`

## License

This project is provided as-is for educational and research purposes.

## Disclaimer

TRUTHBOT is a tool to assist with fact-checking but should not be the sole source of verification for critical information. Always consult authoritative sources and experts for important decisions.

