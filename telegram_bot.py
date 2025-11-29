#!/usr/bin/env python3
"""
Telegram bot interface for TRUTHBOT.
Replies to user messages with fact-check summaries.
"""

import asyncio
import logging
import os
from typing import List, Dict, Any, Set

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    _updater,
)

from truthbot import TruthBot


logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("truthbot.telegram")

# Temporary compatibility patch for python-telegram-bot on Python 3.13
if "_Updater__polling_cleanup_cb" not in _updater.Updater.__slots__:
    _updater.Updater.__slots__ = _updater.Updater.__slots__ + (
        "_Updater__polling_cleanup_cb",
    )
    _updater.Updater._Updater__polling_cleanup_cb = None


def get_allowed_user_ids() -> Set[int]:
    """Read allowed Telegram user IDs from environment variable."""
    raw = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "")
    ids: Set[int] = set()
    for token in raw.split(","):
        token = token.strip()
        if token.isdigit():
            ids.add(int(token))
    return ids


class TelegramTruthBot:
    """Wraps Telegram bot handlers around the TruthBot pipeline."""

    def __init__(self) -> None:
        token = os.getenv("8448867587:AAFOnzgYZdHSjLYB06BCRkFalLaBv2wcBGE")
        if not token:
            raise RuntimeError(
                "Missing TELEGRAM_BOT_TOKEN environment variable. "
                "Create a bot via @BotFather and export the token."
            )

        self.application = (
            ApplicationBuilder().token(token).build()
        )
        self.truthbot = TruthBot()
        self.allowed_ids = get_allowed_user_ids()

        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        self.application.add_error_handler(self.on_error)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        if not self._is_allowed(user.id):
            await update.message.reply_text(
                "Sorry, you are not authorized to use this bot."
            )
            return

        await update.message.reply_text(
            "👋 Welcome to TRUTHBOT on Telegram!\n"
            "Send me any claim, headline, or paragraph and I will extract factual "
            "statements, verify them, and reply with verdicts plus confidence scores.\n\n"
            "Type /help for details."
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        if not self._is_allowed(update.effective_user.id):
            await update.message.reply_text(
                "Sorry, you are not authorized to use this bot."
            )
            return

        await update.message.reply_text(
            "Usage:\n"
            "• Send any text containing factual claims.\n"
            "• TRUTHBOT extracts claims, retrieves evidence, and returns a verdict.\n"
            "• Outputs include confidence score, explanation, and top sources.\n"
            "• Results are conservative—\"Unverified\" when evidence is insufficient."
        )

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Run TRUTHBOT on any incoming text."""
        if not self._is_allowed(update.effective_user.id):
            await update.message.reply_text(
                "Sorry, you are not authorized to use this bot."
            )
            return

        text = (update.message.text or "").strip()
        if not text:
            await update.message.reply_text("Please send a non-empty claim.")
            return

        await update.message.chat_action(action="typing")

        try:
            result = self.truthbot.process_input(text, "text")
            response_text = self._format_response(result)
            await update.message.reply_text(
                response_text, parse_mode=ParseMode.MARKDOWN
            )
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Error processing message: %s", exc)
            await update.message.reply_text(
                "Sorry, something went wrong while verifying that claim."
            )

    async def on_error(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Generic error handler for Telegram webhook/polling errors."""
        logger.error("Telegram error: %s", context.error)

    def _is_allowed(self, user_id: int) -> bool:
        """Check if the Telegram user is allowed to interact with the bot."""
        if not self.allowed_ids:
            return True
        return user_id in self.allowed_ids

    def _format_response(self, response: Dict[str, Any]) -> str:
        """Convert TRUTHBOT result into Telegram-friendly Markdown."""
        results = response.get("results", [])
        if not results:
            return "Unverified — No claims detected. Try rephrasing your input."

        lines: List[str] = []
        for idx, result in enumerate(results, start=1):
            lines.append(f"*Claim {idx}*")
            lines.append(result.get("verdict_line", "Verdict unavailable"))
            explanation = result.get("explanation", "")
            if explanation:
                lines.append(explanation)

            evidence_lines = []
            for evidence in result.get("evidence", [])[:3]:
                source = evidence.get("source", "Source unavailable")
                finding = evidence.get("finding", "")
                evidence_lines.append(f"• {source} — {finding}")

            if evidence_lines:
                lines.append("_Evidence:_")
                lines.extend(evidence_lines)

            lines.append(result.get("recommendation", ""))
            lines.append("")  # blank line between claims

        text = "\n".join(line for line in lines if line)
        # Telegram has 4096 char limit—truncate if necessary
        if len(text) > 3800:
            text = text[:3800] + "\n...\n(Truncated)"
        return text

    async def run(self):
        """Start polling updates."""
        logger.info("Starting Telegram polling ...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        await self.application.updater.idle()


async def main():
    """Entry point for running the Telegram bot."""
    bot = TelegramTruthBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())

