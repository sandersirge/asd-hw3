# Tasko — Lab Starter Project

A minimal Django driver-facing dashboard for **Tasko**, a small ride-hailing
service. You will extend this project during the lab session by following
**TDD** (Test-Driven Development) and **BDD** (Behaviour-Driven Development)
practices.

---

## 1. Requirements

* Python 3.10 or newer
* `pip` and a virtual environment tool (`venv`)

## 2. First-Time Setup

```bash
# 1. Unpack this archive and enter the directory
cd tasko_starter

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate           # macOS / Linux
# .venv\Scripts\activate            # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations and seed two demo drivers + a few pending rides
python manage.py migrate
python manage.py seed_demo

# 5. Run the development server
python manage.py runserver
# Open http://127.0.0.1:8000/ and log in as one of the demo drivers
```

Two demo drivers are created by `seed_demo`:

| Username | Password   |
|----------|------------|
| `mari`   | `tasko123` |
| `anna`   | `tasko123` |

## 3. Running the Tests

```bash
# Unit tests (PyTest)
pytest

# Acceptance tests (Behave via behave-django)
python manage.py behave
```

A small set of tests for the existing fare calculator is already passing.
Behave reports **0 features / 0 scenarios** at this point — you will add
scenarios during the lab.

## 4. Project Layout

```
tasko_starter/
├── manage.py
├── pytest.ini
├── requirements.txt
├── tasko/                          # Django project package
├── rides/                          # Django app — the dispatcher
│   ├── models.py                   # Ride model (you extend in Task 1)
│   ├── fares.py                    # Existing fare calculator — DO NOT change
│   ├── views.py                    # Dashboard + lifecycle action endpoints
│   ├── urls.py
│   ├── templates/rides/            # HTML templates with state-aware buttons
│   └── management/commands/
│       └── seed_demo.py
├── tests/                          # PyTest unit tests
│   ├── test_fares.py               # Existing — already passing
│   └── test_models.py              # EMPTY — Task 1
└── features/                       # Behave BDD tests
    ├── environment.py
    ├── driver_dispatching.feature  # EMPTY — Task 2
    └── steps/
        └── dispatching_steps.py    # EMPTY — Task 2
```

## 5. Where You Will Write Code

| Task | File(s) you edit                                                                |
|------|---------------------------------------------------------------------------------|
| 1    | `tests/test_models.py`, then `rides/models.py`                                  |
| 2    | `features/driver_dispatching.feature`, `features/steps/dispatching_steps.py`    |

After the lab, the same code base will be the basis of a graded homework assignment.
