"""
Behave hooks for the BDD test suite.

`behave_django` configures Django and creates a test database when you run
`python manage.py behave`. This file exposes a fresh Django test client on
the context object so step definitions remain short.
"""
from django.test import Client


def before_scenario(context, scenario):
    """Run before EVERY scenario — gives each scenario a fresh client."""
    context.client = Client()
