<p align="center">
  <img src="https://img.shields.io/badge/Flutter-3.12+-02569B?style=flat-square&logo=flutter&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.141-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
</p>

<h1 align="center">ExpenseMate</h1>

<p align="center">
  <strong>A full-stack personal expense manager</strong><br/>
  FastAPI backend &middot; Flutter mobile app &middot; SQLite database
</p>

---

## Features

- **Transaction Management** — Track income and expenses with categories, currencies, and descriptions
- **Budget Tracking** — Set monthly budgets per category with automatic alerts when spending exceeds thresholds
- **Budget Enforcement** — Warns before adding an expense that exceeds its category budget
- **Visual Reports** — Pie charts (category-wise spending), bar charts (monthly income vs expense), and dashboard summaries
- **CSV Import/Export** — Analyze CSV structure before importing; export data for backup or external use
- **Multi-Currency** — Supports multiple currencies (PKR, SAR, AED, USD and more) with live exchange rates via open.er-api.com
- **Database Backup/Restore** — Full SQLite backup and restore from the app
- **Animated Splash Screen** — Custom personalized landing page
- **Material 3 Design** — Teal theme with dark mode support

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, FastAPI, Uvicorn, SQLite |
| **Frontend** | Flutter 3.12+, Dart, Riverpod 3.x, dio, fl_chart, go_router |
| **State Management** | Riverpod 3.x (Notifier pattern) |
| **Navigation** | go_router with StatefulShellRoute (bottom nav) |
| **Charts** | fl_chart (pie + bar charts) |
| **File Operations** | file_picker v12 (SAF Save As dialog) |

---

## Project Structure

```
ExpenseTracker/
├── Backend/
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # Database path, API settings
│   ├── requirements.txt         # Python dependencies
│   ├── controllers/             # Request handlers
│   ├── models/                  # Database models & queries
│   ├── routes/                  # API route definitions
│   ├── schemas/                 # Pydantic validation schemas
│   ├── services/                # Business logic (backup, currency API)
│   └── utils/                   # CSV handler, validators
├── Frontend/
│   ├── lib/
│   │   ├── main.dart            # App entry point + theme + routing
│   │   ├── config/              # API base URL configuration
│   │   ├── models/              # Dart data models
│   │   ├── providers/           # Riverpod state providers
│   │   ├── screens/             # Feature-based UI screens
│   │   ├── services/            # HTTP API clients
│   │   └── widgets/             # Reusable UI components
│   └── pubspec.yaml
└── .gitignore
```

---

## Prerequisites

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **Flutter 3.12+** — [Install Guide](https://docs.flutter.dev/get-started/install)
- **Android Emulator** or physical Android device (for running the app)

---

## How to Run

### 1. Start the Backend

Set `MONGO_URI` in `Backend\.env` to your MongoDB Atlas connection URI. The app
uses the `expensemate` database by default; set `MONGO_DATABASE` to override it.
Do not commit `.env` or include the URI in logs or screenshots. On startup, the
backend connects to MongoDB, initializes its indexes and any missing default
data, and then serves requests from MongoDB.

```powershell
cd Backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.  
Interactive docs at `http://127.0.0.1:8000/docs`.

> The migrated SQLite file is retained as the source/backup; the active backend
uses MongoDB after the repository migration.

### Migrate SQLite data to MongoDB

The migration utility copies the six SQLite tables into MongoDB collections,
preserving each SQLite primary key as MongoDB `_id` and retaining the original
columns (including the `id` field). The backend now uses MongoDB through its
repository layer; new app records are written to MongoDB, not SQLite.

1. Back up `Backend\expense.db` and install the backend requirements:

   ```powershell
   cd Backend
   pip install -r requirements.txt
   ```

2. Set `MONGO_URI` in `Backend\.env`. Optionally set `MONGO_DATABASE`; otherwise,
   the migration uses the `expensemate` database.
3. From the project root, run:

   ```powershell
   python Backend\scripts\migrate_sqlite_to_mongo.py
   ```

   To specify a different SQLite file or MongoDB database, use
   `--sqlite-path path\to\expense.db` and/or `--database database_name`.
4. Check the printed per-collection source-row and verification counts. The script
   verifies every copied record and exits with an error if a destination record
   with the same key contains different data.

The script creates missing collections, inserts missing documents, and is safe
to rerun when matching documents are already present. It does not delete target
documents, replace conflicting records, or modify the SQLite source. A failed
run may have copied some records; rerunning completes those missing records.
MongoDB access requires network access to the Atlas cluster and a database user
with permission to create collections and insert/read documents. Keep `.env`
private and never include the URI in logs or commits.

The application uses MongoDB repositories for transactions, categories,
budgets, settings, payment methods, and users. MongoDB does not enforce the
SQLite foreign keys; the service layer validates category references, and
integer IDs continue through a MongoDB sequence collection for API compatibility.
Database backups are exported as Extended JSON ZIP archives.

### Assignment 02 architecture and evidence

**Before:** HTTP routes called controller modules that mixed business rules
with model functions; model functions contained SQLite queries.

```text
Routes → Controllers (request handling + business rules) → SQLite models/SQL
```

**After:** routes are the HTTP/controller layer, services contain ExpenseMate
rules and calculations, repositories own MongoDB queries, and the database
module owns connection setup and initialization.

```text
Routes/Controllers → Services → Repositories → MongoDB
```

The request and response paths for transactions, budgets, categories, reports,
CSV operations, currencies, and backups now use services/repositories; there are
no SQLite queries in the active application path. SQLite access remains only in
the one-time migration utility and its tests.

**Measured maintainability indicators**

- **Database separation:** before the migration/refactor, six domain model
  modules contained SQLite query logic, in addition to SQLite setup/queries in
  `models/database.py`; after it, zero runtime application modules execute SQL.
  This was checked by searching backend Python files for `sqlite3` and SQL
  `execute` calls; the remaining matches are limited to the migration utility
  and migration tests.
- **Dependency separation:** the old path had route/controller/model layers,
  with business logic inside controllers; the new runtime path has four
  distinct responsibilities—HTTP controller, service, repository, and database.
  This was checked by following the imports from the route modules and verifying
  that services import repositories rather than database clients or SQL code.
- **Automated checks:** run
  `python -m unittest discover -s Backend\tests -p "test*.py" -v`. The current
  suite contains 17 tests: six migration tests, two MongoDB repository unit
  tests, and nine API integration tests. API integration tests use mocked
  repositories; live Atlas smoke checks also exercised the transaction,
  category, budget, report, and CSV read endpoints.

**Change log**

| Version/commit | Change | Reason |
|---|---|---|
| `9b12fb1` | Added SQLite-to-MongoDB copy utility and PyMongo dependency | Preserve Assignment 01 data in Atlas with repeatable, verified migration |
| Pending | Replaced SQLite models/controllers with MongoDB repositories and services; switched startup and backup/restore; added tests | Route backend reads/writes through the required layered architecture while preserving API behavior |

The pending row should be updated with the actual commit ID and version after the
Assignment 02 changes are committed; do not record a commit hash before then.

### 2. Run the Flutter App

**On Android Emulator:**

```powershell
cd Frontend
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

> `10.0.2.2` is the Android emulator's alias for your host machine's `localhost`.

**On a Physical Phone (same WiFi):**

First, find your laptop's local IP:

```powershell
ipconfig
```

Look for **IPv4 Address** under your WiFi adapter (e.g., `192.168.1.5`).

Then run the backend on all interfaces so the phone can reach it:

```powershell
cd Backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Build a Release APK

Replace `192.168.1.5` with your actual laptop IP:

```powershell
cd Frontend
flutter build apk --release --dart-define=API_BASE_URL=http://192.168.1.5:8000
```

The APK will be at:
```
Frontend\build\app\outputs\flutter-apk\app-release.apk
```

Transfer the APK to your phone and install it. Both the phone and laptop must be on the **same WiFi network**.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/transactions` | List all transactions (with filters) |
| POST | `/transactions` | Add a transaction |
| PUT | `/transactions/{id}` | Update a transaction |
| DELETE | `/transactions/{id}` | Void (soft-delete) a transaction |
| GET | `/categories` | List categories |
| POST | `/categories` | Add a category |
| GET | `/budget` | List budgets for a month |
| POST | `/budget` | Set a budget |
| GET | `/budget/alerts` | Get budget alerts |
| GET | `/reports/dashboard` | Monthly dashboard summary |
| GET | `/reports/category-wise` | Category-wise spending |
| GET | `/reports/income-vs-expense` | Monthly income vs expense |
| GET | `/reports/monthly-summary` | Monthly summary stats |
| GET | `/currencies` | List supported currencies |
| GET | `/currencies/rate` | Get exchange rate |
| POST | `/csv/analyze` | Analyze CSV structure (preview) |
| POST | `/csv/import` | Import transactions from CSV |
| GET | `/csv/export` | Export all transactions as CSV |
| GET | `/csv/guidelines` | CSV format guidelines |
| POST | `/backup` | Create database backup |
| POST | `/backup/restore` | Restore from backup |

---

## CSV Import Format

| Column | Required | Description |
|---|---|---|
| `type` | Yes | `income` or `expense` |
| `amount` | Yes | Positive number (e.g., `1500` or `99.50`) |
| `date` | Yes | Format: `YYYY-MM-DD` (e.g., `2025-01-15`) |
| `category` | No | Category name (matched case-insensitively) |
| `category_id` | No | Category numeric ID (fallback if name not found) |
| `currency` | No | Currency code (defaults to `PKR`) |
| `description` | No | Any text |

**Example:**
```csv
type,category,category_id,amount,currency,date,description
expense,Food,6,1500,PKR,2025-01-15,Lunch at cafe
income,Salary,1,50000,PKR,2025-01-01,Monthly salary
```

> **Tip:** Export your data first to get a pre-filled template with your existing categories.

---

## Default Data

On first run, the database is seeded with:

**Income Categories:** Salary, Freelance, Business, Gift, Other

**Expense Categories:** Food, Transport, Bills, Shopping, Entertainment, Healthcare, Education, Rent, Subscriptions, Other

**Payment Methods:** Cash, Bank, Credit Card, Debit Card, Digital Wallet, Other

---

## Screenshots

| Splash | Dashboard | Transactions | Reports |
|---|---|---|---|
| Animated landing page | Monthly summary | Transaction list | Pie & bar charts |

---

## Deployment

For production deployment, consider:

| Platform | Best For | SQLite Support |
|---|---|---|
| **Railway** | Easiest with persistent volumes | Yes (with volume) |
| **Render** | Free tier available | Yes (with persistent disk) |
| **Fly.io** | Global edge deployment | Yes (with volume) |
| **PythonAnywhere** | Python-focused hosting | Yes (persistent) |

Build the APK pointing to your deployed URL:

```powershell
flutter build apk --release --dart-define=API_BASE_URL=https://your-backend.com
```

---

## License

This project is open source and available under the [MIT License](LICENSE).
