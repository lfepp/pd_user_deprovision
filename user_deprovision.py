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

import requests
import json
import argparse
from datetime import datetime
import logging
import os


class PagerDutyREST():
    """Class to handle all calls to the PagerDuty API"""

    def __init__(self, access_token):
        self.base_url = 'https://api.pagerduty.com'
        self.headers = {
            'Accept': 'application/vnd.pagerduty+json;version=2',
            'Content-type': 'application/json',
            'Authorization': 'Token token={token}'.format(token=access_token)
        }

    def get(self, endpoint, payload={}, resource=None):
        """Handle all GET requests"""

        url = '{base_url}{endpoint}'.format(
            base_url=self.base_url,
            endpoint=endpoint
        )
        payload['limit'] = 100
        r = requests.get(url, params=payload, headers=self.headers)
        if r.status_code == 200:
            r = r.json()
            # Handle pagination if over 100 resources returned
            # Try/except for cases where getting a single resource
            try:
                if r['more']:
                    # FIXME: Remove when teams can have total in params
                    if not resource:
                        resource = endpoint[1:]
                    payload['offset'] = 100
                    output = r
                    while r['more']:
                        r = requests.get(
                            url,
                            params=payload,
                            headers=self.headers
                        ).json()
                        for i in r[resource]:
                            output[resource].append(i)
                        payload['offset'] += 100
                    r = output
                return r
            except:
                return r
        else:
            raise Exception(
                'There was an issue with your GET request:\nStatus code: {code}\
                \nError: {error}'.format(code=r.status_code, error=r.text)
            )

    def put(self, endpoint, payload=None):
        """Handle all PUT requests"""

        url = '{base_url}{endpoint}'.format(
            base_url=self.base_url,
            endpoint=endpoint
        )
        if payload:
            r = requests.put(
                url,
                data=json.dumps(payload),
                headers=self.headers
            )
        else:
            r = requests.put(url, headers=self.headers)
        if r.status_code == 200 or r.status_code == 204:
            return r.status_code
        else:
            raise Exception(
                'There was an issue with your PUT request:\nStatus code: {code}\
                \nError: {error}'.format(code=r.status_code, error=r.text)
            )

    def delete(self, endpoint):
        """Handle all DELETE requests"""

        url = '{base_url}{endpoint}'.format(
            base_url=self.base_url,
            endpoint=endpoint
        )
        r = requests.delete(url, headers=self.headers)
        if r.status_code == 204:
            return r.status_code
        else:
            raise Exception(
                'There was an issue with your DELETE request:\nStatus code: {code}\
                \nError: {error}'.format(code=r.status_code, error=r.text)
            )

    def post(self, endpoint, payload, from_header=None):
        """Handle all POST requests"""

        url = '{base_url}{endpoint}'.format(
            base_url=self.base_url,
            endpoint=endpoint
        )
        headers = self.headers
        if from_header:
            headers['From'] = from_header
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 201:
            return r.json()
        else:
            raise Exception(
                'There was an issue with your POST request:\nStatus code: {code}\
                \nError: {error}'.format(code=r.status_code, error=r.text)
            )


class DeleteUser():
    """Class to handle all user deletion logic"""

    def __init__(self, access_token):
        self.pd_rest = PagerDutyREST(access_token)

    def get_user_id(self, email):
        """Get PagerDuty user ID from user email"""

        r = self.pd_rest.get('/users', {'query': email})
        for user in r['users']:
            if user['email'] == email:
                return user['id']
        raise ValueError(
            'Could not find user with email {email}'.format(email=email)
        )

    def list_open_incidents(self, user_id):
        """Get any open incidents assigned to the user"""

        r = self.pd_rest.get('/incidents', {
            'total': True,
            'statuses[]': ['triggered', 'acknowledged'],
            'user_ids[]': user_id
        })
        return r

    def list_schedules(self):
        """Outputs list of all schedules"""

        r = self.pd_rest.get('/schedules')
        return r['schedules']

    def list_teams(self):
        """Outputs list of all teams"""

        r = self.pd_rest.get('/teams')
        return r['teams']

    def list_users_on_team(self, team_id):
        """List all users on a particular team"""

        r = self.pd_rest.get('/users', {'team_ids[]': team_id})
        return r['users']

    def list_user_escalation_policies(self, user_id):
        """List all escalation policies user is on"""

        r = self.pd_rest.get('/escalation_policies', {'user_ids[]': user_id})
        return r['escalation_policies']

    def get_schedule(self, schedule_id):
        """Get a single schedule"""

        r = self.pd_rest.get('/schedules/{id}'.format(id=schedule_id))
        return r['schedule']

    def get_escalation_policy(self, escalation_policy_id):
        """Get a single escalation policy"""

        r = self.pd_rest.get(
            '/escalation_policies/{id}'.format(id=escalation_policy_id)
        )
        return r['escalation_policy']

    def check_schedule_for_user(self, user_id, schedule):
        """Check if a schedule contains a particular user"""

        for user in schedule['users']:
            if user['id'] == user_id:
                return True
        return False

    def check_team_for_user(self, user_id, team_users):
        """Check the users on a team for the deletion user"""

        for user in team_users:
            if user['id'] == user_id:
                return True
        return False

    def get_user_layer_index(self, user_id, schedule_layer):
        """Get the index of a user on a schedule layer"""

        for i, user in enumerate(schedule_layer['users']):
            # TODO: Fix once endpoint is fixed
            if user['user']['id'] == user_id:
                return i
        return None

    def get_target_indices(self, id, escalation_rules):
        """Get the escalation rule indices and target indices for the user or
        schedule
        """

        output = []
        for i, rule in enumerate(escalation_rules):
            for j, target in enumerate(rule['targets']):
                if target['id'] == id:
                    output.append({'rule': i, 'target': j})
        return output

    def remove_user_from_layer(self, index, schedule_layer):
        """Remove a user from a schedule layer"""

        del schedule_layer['users'][index]
        return schedule_layer

    def remove_from_escalation_policy(self, indices, escalation_rules):
        """Remove a user or schedule from an escalation policy"""

        for index in indices:
            del escalation_rules[index['rule']]['targets'][index['target']]
        return escalation_rules

    def remove_user_from_team(self, team_id, user_id):
        """Remove a user from a team"""

        r = self.pd_rest.delete(
            '/teams/{team_id}/users/{user_id}'.format(
                team_id=team_id,
                user_id=user_id
            )
        )
        return r

    def update_schedule(self, schedule_id, schedule):
        """Updates the schedule"""

        payload = {
            'schedule': schedule
        }
        r = self.pd_rest.put(
            '/schedules/{id}'.format(id=schedule_id),
            payload
        )
        return r

    def delete_schedule(self, schedule_id):
        """Deletes the schedule"""

        r = self.pd_rest.delete(
            '/schedules/{id}'.format(id=schedule_id)
        )
        return r

    def create_schedule(self, schedule):
        """Creates the schedule"""

        r = self.pd_rest.post(
            '/schedules',
            schedule
        )
        return r

    def update_escalation_policy(self, escalation_policy_id, ep):
        """Updates the escalation policy"""

        # Delete description in case it is null
        del ep['description']
        payload = {
            'escalation_policy': ep
        }
        r = self.pd_rest.put(
            '/escalation_policies/{id}'.format(id=escalation_policy_id),
            payload
        )
        return r

    def delete_escalation_policy(self, escalation_policy_id):
        """Deletes the escalation policy"""

        r = self.pd_rest.delete(
            '/escalation_policies/{id}'.format(id=escalation_policy_id)
        )
        return r

    def create_escalation_policy(self, escalation_policy):
        """Creates the escalation policy"""

        payload = {
            'escalation_policy': escalation_policy
        }
        r = self.pd_rest.post(
            '/escalation_policies',
            payload
        )
        return r

    def cache_schedule(self, schedule, cache):
        """Adds current schedule to the cache of affected schedules"""

        cache.append({
            'id': schedule['id'],
            'name': schedule['name']
        })
        return cache

    def cache_team(self, team, cache):
        """Adds current team to the cache of affected teams"""

        cache.append({
            'id': team['id'],
            'name': team['name']
        })
        return cache

    def cache_escalation_policy(self, escalation_policy, cache):
        """Adds current escalation policy to the cache of affected EPs"""

        cache.append({
            'id': escalation_policy['id'],
            'name': escalation_policy['name']
        })
        return cache

    def delete_user(self, user_id):
        """Delete user from PagerDuty"""

        r = self.pd_rest.delete('/users/{id}'.format(id=user_id))
        return r


def main(access_token, user_email):
    """Handle command-line logic to delete user"""

    # Initialize logging
    if not os.path.isdir(os.path.join(os.getcwd(), './logs')):
        os.mkdir(os.path.join(os.getcwd(), './logs'))
    logging.basicConfig(filename='./logs/{timestamp}.log'.format(
        timestamp=datetime.now().isoformat()
    ), level=logging.WARNING)
    logging.info('Start of main logic')
    # Declare cache variables
    schedule_cache = []
    escalation_policy_cache = []
    team_cache = []
    # Declare an instance of the DeleteUser class
    delete_user = DeleteUser(access_token)
    # Get the user ID of the user to be deleted
    user_id = delete_user.get_user_id(user_email)
    logging.info('User ID: {id}'.format(id=user_id))
    # Check for open incidents user is currently in use for
    incidents = delete_user.list_open_incidents(user_id)
    if incidents['total'] > 0:
        incident_output = ""
        for incident in incidents['incidents']:
            incident_output = "{current}\n[#{number}]: {description}".format(
                current=incident_output,
                number=incident['incident_number'],
                description=incident['description']
            )
        logging.critical(
            ('There are currently {total} open incidents that this user is '
             'in use for. Please resolve the following incidents and '
             'try again:{incidents}'.format(
                total=incidents['total'],
                incidents=incident_output
                )
             )
        )
        raise Exception(
            ('There are currently {total} open incidents that this user is '
             'in use for. Please resolve the following incidents and '
             'try again:{incidents}'.format(
                total=incidents['total'],
                incidents=incident_output
                )
             )
        )
    # Get a list of all esclation policies
    escalation_policies = delete_user.list_user_escalation_policies(user_id)
    logging.info('GOT escalation policies')
    logging.debug('EPs: \n{eps}'.format(eps=json.dumps(escalation_policies)))
    for i, ep in enumerate(escalation_policies):
        # Cache escalation policy
        escalation_policy_cache = delete_user.cache_escalation_policy(
            ep,
            escalation_policy_cache
        )
        ep_indices = delete_user.get_target_indices(
            user_id,
            ep['escalation_rules']
        )
        escalation_policies[i]['escalation_rules'] = (
            delete_user.remove_from_escalation_policy(
                ep_indices,
                ep['escalation_rules']
            )
        )
        # Remove rules with no more targets
        escalation_policies[i]['escalation_rules'] = [
            x for j, x in enumerate(escalation_policies[i]['escalation_rules'])
            if not len(x['targets']) == 0
        ]
        # Update the escalation policy if there are rules or delete the escalation policy  # NOQA
        if len(escalation_policies[i]['escalation_rules']) != 0:
            delete_user.update_escalation_policy(
                escalation_policies[i]['id'],
                escalation_policies[i]
            )
        else:
            try:
                delete_user.delete_escalation_policy(
                    ep['id']
                )
            except Exception:
                logging.warning('The escalation policy {name} no longer has any \
                on-call engineers or schedules but is still attached to \
                services in your account.'.format(
                    name=escalation_policies[i]['name']
                ))
    logging.info('Finished removing from escalation policies')
    logging.debug('EP cache: \n{cache}'.format(cache=json.dumps(
        escalation_policy_cache
    )))
    # Get a list of all schedules
    schedules = delete_user.list_schedules()
    logging.info('GOT schedules')
    logging.debug('Schedules: \n{schedules}'.format(schedules=json.dumps(
        schedules
    )))
    for sched in schedules:
        # Get the specific schedule
        schedule = delete_user.get_schedule(sched['id'])
        # Check if user is in schedule
        if delete_user.check_schedule_for_user(user_id, schedule):
            # Cache schedule
            schedule_cache = delete_user.cache_schedule(
                schedule,
                schedule_cache
            )
            for i, layer in enumerate(schedule['schedule_layers']):
                # Get index of user in layer
                layer_index = delete_user.get_user_layer_index(user_id, layer)
                # If this is the only user on the layer, end the layer now
                if layer_index == 0 and len(layer['users']) == 1:
                    schedule['schedule_layers'][i]['end'] = (
                        datetime.now().isoformat()
                    )
                elif layer_index is not None:
                    schedule['schedule_layers'][i] = (
                        delete_user.remove_user_from_layer(
                            layer_index,
                            layer
                        )
                    )
            schedule['schedule_layers'] = [
                x for i, x in enumerate(schedule['schedule_layers'])
                if not len(schedule['schedule_layers'][i]['users']) == 0
            ]
            # Reverse the schdule layers
            schedule['schedule_layers'] = schedule['schedule_layers'][::-1]
            del schedule['users']
            if len(schedule['schedule_layers']) > 0:
                delete_user.update_schedule(schedule['id'], schedule)
            # If deleting, remove the schedule from any escalation policies
            elif len(schedule['escalation_policies']) > 0:
                for ep in schedule['escalation_policies']:
                    escalation_policy = delete_user.get_escalation_policy(
                        ep['id']
                    )
                    ep_indices = delete_user.get_target_indices(
                        schedule['id'],
                        escalation_policy['escalation_rules']
                    )
                    escalation_policy['escalation_rules'] = (
                        delete_user.remove_from_escalation_policy(
                            ep_indices,
                            escalation_policy['escalation_rules']
                        )
                    )
                    # Remove rules with no targets
                    for i, rule in enumerate(
                        escalation_policy['escalation_rules']
                    ):
                        if len(rule['targets']) == 0:
                            del escalation_policy['escalation_rules'][i]
                    # Update the escalation policy if there are rules or delete the escalation policy  # NOQA
                    if len(escalation_policy['escalation_rules']) > 0:
                        delete_user.update_escalation_policy(
                            escalation_policy['id'],
                            escalation_policy
                        )
                    else:
                        try:
                            delete_user.delete_escalation_policy(
                                escalation_policy['id']
                            )
                        except Exception:
                            logging.warning('The escalation policy {name} no \
                            longer has any on-call engineers or schedules but \
                            is still attached to services in your account.\
                            '.format(name=escalation_policy['name']))
            else:
                # If no layers and no escalation policies, remove schedule
                delete_user.delete_schedule(schedule['id'])
    logging.info('Finished removing from schedules')
    logging.debug('Schedule cache: {cache}'.format(cache=json.dumps(
        schedule_cache
    )))
    # Get a list of all teams
    teams = delete_user.list_teams()
    logging.info('GOT teams')
    logging.debug('Teams: \n{teams}'.format(teams=json.dumps(teams)))
    for team in teams:
        team_users = delete_user.list_users_on_team(team['id'])
        if delete_user.check_team_for_user(user_id, team_users):
            # Cache team
            team_cache = delete_user.cache_team(team, team_cache)
            delete_user.remove_user_from_team(team['id'], user_id)
    logging.info('Finished removing from teams')
    logging.debug('Team cache: {cache}'.format(cache=json.dumps(team_cache)))
    # Delete user
    delete_user.delete_user(user_id)
    print 'Schedules affected:\n{cache}'.format(cache=json.dumps(
        schedule_cache
    ))
    logging.info('Schedules affected:\n{cache}'.format(cache=json.dumps(
        schedule_cache
    )))
    print 'Escalation policies affected:\n{cache}'.format(cache=json.dumps(
        escalation_policy_cache
    ))
    logging.info('Escalation policies affected:\n{cache}'.format(
        cache=json.dumps(escalation_policy_cache)
    ))
    print 'Teams affected:\n{cache}'.format(cache=json.dumps(team_cache))
    logging.info('Teams affected:\n{cache}'.format(cache=json.dumps(
        team_cache
    )))
    print 'User {email} has been Successfully removed!'.format(
        email=user_email
    )
    logging.info('End of main logic')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Delete a PagerDuty user')
    parser.add_argument(
        '--access-token', '-a',
        help='PagerDuty v2 access token',
        dest='access_token',
        required=True
    )
    parser.add_argument(
        '--user-email', '-u',
        help='Email address of user to be deleted',
        dest='user_email',
        required=True
    )
    args = parser.parse_args()
    main(args.access_token, args.user_email)
