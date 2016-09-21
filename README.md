# Delete User

Python script to delete a user in PagerDuty including removing them from all schedules, escalation policies, and teams that they are a part of. The affected resources are printed to the console.

## Usage

This script is meant to be used as a command line tool with the following arguments:

`./delete_user.py --access-token ENTER_PD_ACCESS_TOKEN --user-email user-to-delete@example.com`

**--access-token**: A valid PagerDuty v2 REST API access token from your account

**--user-email**: The PagerDuty email address for the user you want to delete from your account

## Author

Luke Epp <lucas@pagerduty.com>
