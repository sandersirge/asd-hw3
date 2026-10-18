Feature: End-of-trip receipt

  As a driver
  I want to see a receipt when I complete a ride
  So that I can show the rider what they paid and why

  Background:
    Given a driver named "Mari"
    And a pending ride from "Raekoja plats" to "Tartu Airport" of 5.0 km

  Scenario: Driver views the receipt for a ride they completed
    Given Mari has started the ride
    When  Mari completes the ride
    Then  Mari sees the receipt for the ride
    And   the receipt shows the distance as "5.00 km"
    And   the receipt shows the total as "8.50 €"
    And   the receipt shows the surge as "None"

  Scenario: Receipt reflects the active surge multiplier
    Given a 1.5× surge is active
    And   Mari has started the ride
    When  Mari completes the ride
    Then  Mari sees the receipt for the ride
    And   the receipt shows the surge as "×1.50"
    And   the receipt shows the base fare as "8.50 €"
    And   the receipt shows the surge amount as "4.25 €"
    And   the receipt shows the total as "12.75 €"