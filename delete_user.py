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


class PagerDutyREST():
    """Class to handle all calls to the PagerDuty API"""

    def __init__(self, access_token):
        self.base_url = 'https://api.pagerduty.com'
        self.headers = {
            'Accept': 'application/vnd.pagerduty+json;version=2',
            'Content-type': 'application/json',
            'Authorization': 'Token token={token}'.format(token=access_token)
        }

    def get(self, endpoint, payload=None):
        """Handle all GET requests"""

        url = '{base_url}{endpoint}'.format(
            base_url=self.base_url,
            endpoint=endpoint
        )
        r = requests.get(url, params=payload, headers=self.headers)
        if r.status_code == 200:
            return r.json()
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
        r = requests.put(url, data=json.dumps(payload), headers=self.headers)
        if r.status_code == 200:
            return r.json()
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


class DeleteUser():
    """Class to handle all user deletion logic"""

    def __init__(self, user, access_token):
        self.user = user
        self.pd_rest = PagerDutyREST(access_token)

    def get_user_id(self, email):
        """Get PagerDuty user ID from user email"""

        payload = {
            'query': email
        }
        r = self.pd_rest.get('/users?limit=100', payload)
        # Handle pagination if over 100 users
        if r['more']:
            offset = 100
            output = r['users']
            while r['more']:
                r = self.pd_rest.get(
                    '/users?limit=100&offset={offset}'.format(offset=offset),
                    payload
                )
                output.append(r['users'])
                offset += 100
            r = {
                'users': output
            }
        for user in r['users']:
            if user['email'] == email:
                return user['id']
        raise ValueError(
            'Could not find user with email {email}'.format(email=email)
        )

    def list_schedules(self):
        """Outputs list of all schedules"""

        r = self.pd_rest.get('/schedules?limit=100')
        # Handle pagination if over 100 schedules
        if r['more']:
            offset = 100
            output = r['schedules']
            while r['more']:
                r = self.pd_rest.get(
                    '/schedules?limit=100&offset={offset}'.format(
                        offset=offset
                    )
                )
                output.append(r['schedules'])
                offset += 100
            r = {
                'schedules': output
            }
        return r['schedules']

    def get_schedule(self, schedule_id):
        """Get a single schedule"""

        r = self.pd_rest.get('/schedules/{id}'.format(id=schedule_id))
        return r

    def check_schedule_for_user(self, user_id, schedule):
        """Check if a schedule contains a particular user"""

        for user in schedule['users']:
            if user['id'] == user_id:
                return True
        return False

    def get_user_index(self, user_id, schedule_layer):
        """Get the index of a user on a schedule layer"""

        for i, user in enumerate(schedule_layer['users']):
            if user['id'] == user_id:
                return i
        return None

    def remove_user_from_layer(self, index, schedule_layer):
        """Remove a user from a schedule layer"""

        del schedule_layer['users'][index]
        return schedule_layer

    def cache_schedule(self, schedule, cache):
        """Adds current schedule to the cache of affected schedules"""

        cache.append({
            'id': schedule['id'],
            'name': schedule['name']
        })
        return cache

    def delete_user(self, user_id):
        """Delete user from PagerDuty"""

        r = self.pd_rest.delete('/users/{id}'.format(id=user_id))
        return r


def main(access_token, user_email):
    """Handle command-line logic to delete user"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Delete a user')
    parser.add_argument(
        '--access-token',
        help='PagerDuty v2 access token',
        dest='access_token',
        required=True
    )
    parser.add_argument(
        '--user-email',
        help='Email address of user to be deleted',
        dest='user_email',
        required=True
    )
