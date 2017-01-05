#!/usr/bin/env python
#
# Copyright (c) 2016, PagerDuty, Inc. <info@pagerduty.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of PagerDuty Inc nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL PAGERDUTY INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
import sys
import os
import random
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
import user_deprovision  # NOQA

config_filname = os.path.join(os.path.dirname(__file__), '../config.json')
with open(config_filname) as config_file:
    config = json.load(config_file)

pd_rest = user_deprovision.PagerDutyREST(config['access_token'])


def select_random(data, resource):
    """Select random resources from the passed data"""

    total = data['total']
    count = int(random.random() * total)
    if count == 0:
        count = 1
    output = []
    for i in xrange(count):
        resource_index = int(random.random() * total)
        output.append(data[resource][resource_index])
        del data[resource][resource_index]
        total -= 1
    return output


def main():
    """Creates a user based on the information in tests/config.json attached to
    random esclation policies, schedules, and teams in the account
    """

    # Get all escalation policies
    r = pd_rest.get('/escalation_policies', {'total': True})
    # Select random EPs
    escalation_policies = select_random(r, 'escalation_policies')
    # Get all schedules
    r = pd_rest.get('/schedules', {'total': True})
    # Select random schedules
    schedules = select_random(r, 'schedules')
    # Get all teams
    # TODO: Figure out why param isn't working
    r = pd_rest.get('/teams?total=true')
    # Select random teams
    teams = select_random(r, 'teams')
    # Add user
    # TODO: Fix once schema is fixed to remove extra user level
    user = {
        'user': {
            'type': 'user',
            'name': config['utils']['add_test_user']['name'],
            'email': config['utils']['add_test_user']['email']
        }
    }
    # TODO: Fix once schema is fixed to remove extra user level
    r = pd_rest.post(
        '/users',
        user,
        config['utils']['add_test_user']['from_header']
    )['user']
    print "Added user successfully"
    # Add to EPs
    for ep in escalation_policies:
        if not ep['description']:
            ep['description'] = ep['summary']
        ep['escalation_rules'][0]['targets'].append({
            'id': r['id'],
            'type': 'user'
        })
        pd_rest.put(
            '/escalation_policies/{id}'.format(id=ep['id']),
            {'escalation_policy': ep}
        )
    print "Added user to escalation policies"
    # Add to schedules
    for sched in schedules:
        schedule = pd_rest.get('/schedules/{id}'.format(
            id=sched['id']
        ))['schedule']
        schedule['schedule_layers'][0]['users'].append({
            'user': {
                'id': r['id'],
                'type': 'user'
            }
        })
        pd_rest.put(
            '/schedules/{id}'.format(id=schedule['id']),
            {'schedule': schedule}
        )
    print "Added user to schedules"
    # Add to teams
    for team in teams:
        pd_rest.put('/teams/{team_id}/users/{user_id}'.format(
            team_id=team['id'],
            user_id=r['id']
        ))
    print "Added user to teams"

if __name__ == '__main__':
    main()
