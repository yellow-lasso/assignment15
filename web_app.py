import requests

import os
from dotenv import load_dotenv
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask import jsonify
from models import db, User, Trade

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///project.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

db.init_app(app)

with app.app_context():
    db.create_all()


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped_view


def get_current_user():
    user_id = session.get("user_id")
    if user_id:
        return User.query.get(user_id)
    return None

def normalize_fmp_trade(item):
    """Convert an FMP API record into fields used by our Trade model."""

    first_name = item.get("firstName", "").strip()
    last_name = item.get("lastName", "").strip()
    full_name = f"{first_name} {last_name}".strip()

    representative = (
        full_name
        or item.get("office")
        or "Unknown Representative"
    )

    trade_date = (
        item.get("transactionDate")
        or item.get("transaction_date")
        or item.get("tradeDate")
        or item.get("date")
        or ""
    )

    disclosure_date = (
        item.get("disclosureDate")
        or item.get("disclosure_date")
        or item.get("filingDate")
        or ""
    )

    ticker = (
        item.get("symbol")
        or item.get("ticker")
        or item.get("assetTicker")
        or "N/A"
    )

    asset_type = (
        item.get("assetType")
        or item.get("asset_type")
        or item.get("assetDescription")
        or "Unknown"
    )

    transaction_type = (
        item.get("type")
        or item.get("transactionType")
        or item.get("transaction_type")
        or "Unknown"
    )

    amount = (
        item.get("amount")
        or item.get("transactionAmount")
        or ""
    )

    source_link = (
        item.get("link")
        or item.get("source")
        or "Financial Modeling Prep"
    )

    return {
        "representative": str(representative),
        "trade_date": str(trade_date),
        "disclosure_date": str(disclosure_date),
        "ticker": str(ticker).upper(),
        "asset_type": str(asset_type),
        "transaction_type": str(transaction_type),
        "amount_min": str(amount),
        "amount_max": str(amount),
        "source": str(source_link),
    }


def trade_exists(user_id, trade_data):
    """Prevent obvious duplicate imports for the same user."""
    return Trade.query.filter_by(
        user_id=user_id,
        representative=trade_data["representative"],
        trade_date=trade_data["trade_date"],
        disclosure_date=trade_data["disclosure_date"],
        ticker=trade_data["ticker"],
        transaction_type=trade_data["transaction_type"],
        amount_min=trade_data["amount_min"],
        amount_max=trade_data["amount_max"],
    ).first() is not None


@app.route("/")
@login_required
def home():
    user = get_current_user()
    trades = Trade.query.filter_by(user_id=user.id).all()
    return render_template("index.html", trades=trades, user=user)

@app.route("/sync")
@login_required
def sync_real_data():
    user = get_current_user()
    api_key = os.getenv("FMP_API_KEY")

    if not api_key:
        flash("Missing FMP_API_KEY environment variable.")
        return redirect(url_for("home"))

    url = "https://financialmodelingprep.com/stable/house-latest"

    params = {
        "page": 0,
        "limit": 100,
        "apikey": api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        records = response.json()
    except requests.RequestException as error:
        flash(f"Unable to sync real data: {error}")
        return redirect(url_for("home"))

    if not isinstance(records, list):
        flash("Unexpected API response format.")
        return redirect(url_for("home"))

    imported_count = 0
    skipped_count = 0

    for item in records:
        trade_data = normalize_fmp_trade(item)

        if trade_exists(user.id, trade_data):
            skipped_count += 1
            continue

        trade = Trade(
            representative=trade_data["representative"],
            trade_date=trade_data["trade_date"],
            disclosure_date=trade_data["disclosure_date"],
            ticker=trade_data["ticker"],
            asset_type=trade_data["asset_type"],
            transaction_type=trade_data["transaction_type"],
            amount_min=trade_data["amount_min"],
            amount_max=trade_data["amount_max"],
            source=trade_data["source"],
            user_id=user.id,
        )

        db.session.add(trade)
        imported_count += 1

    db.session.commit()

    flash(f"Sync complete. Imported {imported_count} new records. Skipped {skipped_count} duplicates.")
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.")
            return redirect(url_for("register"))

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            return redirect(url_for("home"))

        flash("Invalid username or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



@app.route("/add", methods=["GET", "POST"])
@login_required
def add_trade():
    user = get_current_user()

    if request.method == "POST":
        trade = Trade(
            representative=request.form.get("representative", "").strip(),
            trade_date=request.form.get("trade_date", "").strip(),
            disclosure_date=request.form.get("disclosure_date", "").strip(),
            ticker=request.form.get("ticker", "").strip(),
            asset_type=request.form.get("asset_type", "").strip(),
            transaction_type=request.form.get("transaction_type", "").strip(),
            amount_min=request.form.get("amount_min", "").strip(),
            amount_max=request.form.get("amount_max", "").strip(),
            source=request.form.get("source", "").strip(),
            user_id=user.id,
        )

        db.session.add(trade)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("add_trade.html")

@app.route("/representative/<path:representative_name>")
@login_required
def representative_profile(representative_name):
    user = get_current_user()

    trades = Trade.query.filter_by(
        user_id=user.id,
        representative=representative_name
    ).all()

    ticker_counts = {}
    transaction_counts = {}

    for trade in trades:
        ticker = trade.ticker or "Unknown"
        transaction_type = trade.transaction_type or "Unknown"

        ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
        transaction_counts[transaction_type] = transaction_counts.get(transaction_type, 0) + 1

    most_traded_ticker = "N/A"
    if ticker_counts:
        most_traded_ticker = max(ticker_counts, key=ticker_counts.get)

    most_common_transaction = "N/A"
    if transaction_counts:
        most_common_transaction = max(transaction_counts, key=transaction_counts.get)

    return render_template(
        "representative.html",
        representative_name=representative_name,
        trades=trades,
        user=user,
        ticker_counts=ticker_counts,
        transaction_counts=transaction_counts,
        most_traded_ticker=most_traded_ticker,
        most_common_transaction=most_common_transaction
    )

@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_trade(item_id):
    user = get_current_user()
    trade = Trade.query.filter_by(id=item_id, user_id=user.id).first_or_404()

    if request.method == "POST":
        trade.representative = request.form.get("representative", "").strip()
        trade.trade_date = request.form.get("trade_date", "").strip()
        trade.disclosure_date = request.form.get("disclosure_date", "").strip()
        trade.ticker = request.form.get("ticker", "").strip()
        trade.asset_type = request.form.get("asset_type", "").strip()
        trade.transaction_type = request.form.get("transaction_type", "").strip()
        trade.amount_min = request.form.get("amount_min", "").strip()
        trade.amount_max = request.form.get("amount_max", "").strip()
        trade.source = request.form.get("source", "").strip()

        db.session.commit()

        return redirect(url_for("home"))

    return render_template("edit_trade.html", trade=trade)


@app.route("/delete/<int:item_id>")
@login_required
def delete_trade(item_id):
    user = get_current_user()
    trade = Trade.query.filter_by(id=item_id, user_id=user.id).first_or_404()

    db.session.delete(trade)
    db.session.commit()

    return redirect(url_for("home"))

@app.route("/api/v1/trades")
@login_required
def api_get_trades():
    user = get_current_user()
    trades = Trade.query.filter_by(user_id=user.id).all()

    results = []
    for trade in trades:
        results.append({
            "id": trade.id,
            "representative": trade.representative,
            "trade_date": trade.trade_date,
            "disclosure_date": trade.disclosure_date,
            "ticker": trade.ticker,
            "asset_type": trade.asset_type,
            "transaction_type": trade.transaction_type,
            "amount_min": trade.amount_min,
            "amount_max": trade.amount_max,
            "source": trade.source
        })

    return jsonify(results)

@app.route("/api/v1/trades/<int:item_id>")
@login_required
def api_get_trade(item_id):
    user = get_current_user()

    trade = Trade.query.filter_by(id=item_id, user_id=user.id).first()

    if not trade:
        return jsonify({"error": "Trade not found"}), 404

    result = {
        "id": trade.id,
        "representative": trade.representative,
        "trade_date": trade.trade_date,
        "disclosure_date": trade.disclosure_date,
        "ticker": trade.ticker,
        "asset_type": trade.asset_type,
        "transaction_type": trade.transaction_type,
        "amount_min": trade.amount_min,
        "amount_max": trade.amount_max,
        "source": trade.source
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)