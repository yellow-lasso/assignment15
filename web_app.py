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


@app.route("/")
@login_required
def home():
    user = get_current_user()
    trades = Trade.query.filter_by(user_id=user.id).all()
    return render_template("index.html", trades=trades, user=user)


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