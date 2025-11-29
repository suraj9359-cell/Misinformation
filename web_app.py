#!/usr/bin/env python3
"""
TRUTHBOT Web Application
Responsive web UI with authentication for mobile and desktop
"""

import os
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
    flash,
)
from werkzeug.security import generate_password_hash, check_password_hash

from truthbot import TruthBot
from database import init_db, create_user, get_user_by_email

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = os.getenv(
    "TRUTHBOT_SECRET_KEY", "change-me-truthbot-secret"
)

bot = TruthBot()
init_db()


def current_user():
    """Return current logged-in user dict."""
    return session.get("user")


def login_required(view):
    """Decorator to require authentication."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
@login_required
def index():
    """Serve landing page"""
    return render_template("index.html", user=current_user())


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if current_user():
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = get_user_by_email(email)

        if not user or not check_password_hash(user["password_hash"], password):
            error = "Invalid email or password."
        else:
            session["user"] = {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
            }
            next_url = request.args.get("next") or url_for("index")
            flash("Welcome back!", "success")
            return redirect(next_url)

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handle new user registration."""
    if current_user():
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm_password") or ""

        if len(name) < 2:
            error = "Name must be at least 2 characters."
        elif "@" not in email:
            error = "Please enter a valid email."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != confirm:
            error = "Passwords do not match."
        elif get_user_by_email(email):
            error = "An account with this email already exists."
        else:
            password_hash = generate_password_hash(password)
            user_id = create_user(name, email, password_hash)
            session["user"] = {"id": user_id, "name": name, "email": email}
            flash("Account created successfully.", "success")
            return redirect(url_for("index"))

    return render_template("register.html", error=error)


@app.get("/logout")
def logout():
    """Log the user out."""
    session.pop("user", None)
    flash("Signed out successfully.", "info")
    return redirect(url_for("login"))


@app.post("/api/fact-check")
def fact_check():
    """API endpoint for fact-checking claims"""
    if not current_user():
        return (
            jsonify(
                {
                    "error": True,
                    "message": "Authentication required.",
                }
            ),
            401,
        )

    data = request.get_json(silent=True) or {}
    user_input = (data.get("input") or data.get("text") or "").strip()
    input_type = data.get("type", "text")

    if not user_input:
        return (
            jsonify(
                {
                    "error": True,
                    "message": "Please provide a claim or text to fact-check.",
                }
            ),
            400,
        )

    try:
        result = bot.process_input(user_input, input_type)
        return jsonify(result)
    except Exception as exc:
        return (
            jsonify(
                {
                    "error": True,
                    "message": "An error occurred while processing the request.",
                    "details": str(exc),
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

