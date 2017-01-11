# PagerDuty User De-Provision

Python script to de-provision a user in PagerDuty including removing them from all schedules, escalation policies, and teams that they are a part of. The affected resources are logged and printed to the console.

## Usage

This script is meant to be used as a command line tool with the following arguments:

`./user_deprovision.py --access-token ENTER_PD_ACCESS_TOKEN --user-email user-to-delete@example.com`

**-a**, **--access-token**: A valid PagerDuty v2 REST API access token from your account

**-u**, **--user-email**: The PagerDuty email address for the user you want to delete from your account

## Author

Luke Epp <lucas@pagerduty.com>

## Maintainer

Luke Epp <lucas@pagerduty.com>
