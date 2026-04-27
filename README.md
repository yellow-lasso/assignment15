# Congressional Trade Tracker

## 📌 Overview

The **Congressional Trade Tracker** is a full-stack web application that allows users to track, manage, and analyze congressional stock trading activity. The application integrates real-world financial disclosure data via an external API and presents it through an interactive dashboard with analytics and visualizations.

This project demonstrates end-to-end development including backend logic, database management, frontend design, API integration, and deployment.

---

## 🚀 Features

### 🔐 Authentication

* User registration and login system
* Session-based authentication

### 📊 Trade Management (CRUD)

* Create, view, update, and delete trade records
* Data stored using a relational database (SQLite via SQLAlchemy)

### 🌐 Real Data Integration

* Sync real congressional trading data using the Financial Modeling Prep API
* Automatic normalization and storage of API data
* Duplicate prevention during sync

### 📈 Dashboard & Analytics

* Interactive dashboard displaying all trades
* Search and filter functionality
* Sorting by multiple fields (date, ticker, representative, etc.)

### 📉 Data Visualization

* Charts powered by Chart.js
* Trade distribution by ticker (bar chart)
* Transaction type breakdown (doughnut chart)

### 🧑‍💼 Representative Profiles

* Dynamic pages for each representative
* Automatically generated analytics:

  * Total trades
  * Most traded ticker
  * Most common transaction type
* Individual charts and insights per representative

### 🎨 UI/UX Enhancements

* Responsive layout
* Modern card-based design
* Navigation bar and dashboard layout
* Delete confirmation for safety

---

## 🛠️ Tech Stack

**Backend**

* Python
* Flask
* SQLAlchemy

**Frontend**

* HTML5
* CSS3
* JavaScript (Vanilla)

**Data Visualization**

* Chart.js

**API**

* Financial Modeling Prep (Congressional Trading Data)

**Deployment**

* Render

---

## ⚙️ Installation (Local Setup)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate environment

**Windows (PowerShell)**

```powershell
.\venv\Scripts\activate
```

**Git Bash**

```bash
source venv/Scripts/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create `.env` file

```text
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///project.db
FMP_API_KEY=your_api_key
```

### 6. Run the app

```bash
python web_app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

## 🌍 Deployment (Render)

### Start Command

```bash
gunicorn web_app:app
```

### Required Environment Variables

* `SECRET_KEY`
* `DATABASE_URL`
* `FMP_API_KEY`

---

## 🔄 API Integration

The application uses the Financial Modeling Prep API to retrieve congressional trade disclosures.

### Key Data Handling

* Extracts representative names using `firstName` and `lastName`
* Normalizes trade fields for database compatibility
* Prevents duplicate entries during sync

---

## 📂 Project Structure

```text
project-folder/
│
├── web_app.py
├── models.py
├── requirements.txt
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
└── templates/
    ├── base.html
    ├── index.html
    ├── add_trade.html
    ├── edit_trade.html
    ├── login.html
    ├── register.html
    └── representative.html
```

---

## 📊 Future Improvements

* PostgreSQL database for persistent storage in production
* Scheduled automatic data syncing
* Enhanced analytics (time-series trends, sector breakdowns)
* Dark mode UI
* Improved data cleaning and validation

---

## 🏁 Conclusion

This project demonstrates the ability to build a complete, production-ready web application that integrates real-world data, provides meaningful analytics, and delivers a polished user experience.

---

## 👨‍💻 Author

Developed as a final project for a Python web development course.
