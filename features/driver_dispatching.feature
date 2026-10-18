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
