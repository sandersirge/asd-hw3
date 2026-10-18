# Tasko — Homework Starter Project

This is the starting point for the **TDD and BDD with the Django framework**
homework assignment. It is a snapshot of the Tasko code base after a
correctly-completed lab session: the fare calculator, the four lifecycle
methods on `Ride`, and the BDD acceptance test for "Accept a ride from the
dashboard" are all in place.

If you completed the lab successfully, you may use **your own code** instead
of this archive — they are functionally equivalent. Use this archive if you
got behind in the lab or want a clean baseline.

---

## 1. Setup

> **Python version:** use **Python 3.10 – 3.12** (developed and tested on
> 3.11). `requirements.txt` pins Django below 5.1, and Django 5.0 does not
> support Python 3.13+. On Python 3.14 the view tests and Behave scenarios
> crash whenever a template is rendered (`AttributeError: 'super' object has
> no attribute 'dicts'` in `django/template/context.py`). The code itself is
> fine; only the interpreter is unsupported.
>
> On Windows, if several Pythons are installed, create the venv explicitly:
>
> ```bash
> py -3.11 -m venv .venv
> ```

```bash
python -m venv .venv
source .venv/bin/activate           # macOS / Linux
# .venv\Scripts\activate            # Windows PowerShell

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo          # 2 demo drivers + 4 pending rides
python manage.py runserver
```

Demo accounts: **mari / tasko123** and **anna / tasko123**.

## 2. Confirm the baseline tests pass

```bash
pytest                              # 28 tests pass
python manage.py behave             # 1 scenario, 5 steps pass
```

If anything fails, fix it before starting the homework.

## 3. What you will build

The homework consists of three tasks:

1. **Surge pricing** (TDD) — extend the fare calculator to honour an active
   `SurgeRule` on top of the base formula.
2. **Cancellation flow** (TDD + view tests) — let drivers cancel an accepted
   ride from the dashboard with a reason, verified by view-layer tests.
3. **End-of-trip receipt** (BDD) — show a completed-ride receipt page with
   the surge-aware fare breakdown, verified by acceptance scenarios.

See the **homework instructions document** for full details and expected deliverables
