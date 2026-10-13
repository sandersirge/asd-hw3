# Task 2 — Behaviour-Driven Development with Behave
#
# Write one Gherkin scenario that describes a driver accepting a pending ride
# from the dashboard. Use a Background section to share fixture data across
# additional scenarios later on.
#
# A scenario is made of three kinds of steps:
#     Given  …  preconditions / fixture data
#     When   …  the user action
#     Then   …  the observable outcome
#
# Use the structure below as a starting point and finish writing the steps.

 Feature: Driver dispatching

   As a driver
   I want to manage rides from request through completion
   So that riders get from A to B and I get paid

   Background:
     Given a driver named "Mari"
     And a pending ride from "Raekoja plats" to "Tartu Airport" of 5.0 km

   Scenario: Driver accepts a pending ride from the dashboard
     When  Mari accepts the ride from her dashboard
     Then  the ride is "accepted"
     And   the ride is assigned to "Mari"
