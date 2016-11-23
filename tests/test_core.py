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

import unittest
import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
import delete_user  # NOQA

expected_filename = os.path.join(
    os.path.dirname(__file__),
    './expected/core.json'
)
input_filename = os.path.join(
    os.path.dirname(__file__),
    './input/core.json'
)
config_filname = os.path.join(os.path.dirname(__file__), './config.json')

with open(expected_filename) as expected_file:
    expected = json.load(expected_file)

with open(input_filename) as input_file:
    input = json.load(input_file)

with open(config_filname) as config_file:
    config = json.load(config_file)

core = delete_user.DeleteUser(config['access_token'])


class CoreLogicTests(unittest.TestCase):

    def get_user_id(self):
        expected_result = expected['get_user_id'][0]
        actual_result = core.get_user_id(input['get_user_id'][0])
        self.assertEqual(expected_result, actual_result)
        expected_result = expected['get_user_id'][1]
        actual_result = core.get_user_id(input['get_user_id'][1])
        self.assertEqual(expected_result, actual_result)

    def list_users_on_team(self):
        expected_result = expected['list_users_on_team'][0]
        actual_result = core.list_users_on_team(input['list_users_on_team'][0])
        self.assertEqual(expected_result, actual_result)
        expected_result = expected['list_users_on_team'][1]
        actual_result = core.list_users_on_team(input['list_users_on_team'][1])
        self.assertEqual(expected_result, actual_result)

    def list_user_escalation_policies(self):
        expected_result = expected['list_user_escalation_policies'][0]
        actual_result = core.list_user_escalation_policies(
            input['list_user_escalation_policies'][0]
        )
        self.assertEqual(expected_result, actual_result)

    def get_schedule(self):
        expected_result = expected['get_schedule'][0]
        actual_result = core.get_schedule(input['get_schedule'][0])
        self.assertEqual(expected_result, actual_result)

    def get_escalation_policy(self):
        expected_result = expected['get_escalation_policy'][0]
        actual_result = core.get_escalation_policy(
            input['get_escalation_policy'][0]
        )
        self.assertEqual(expected_result, actual_result)

    def check_schedule_for_user(self):
        expected_result = expected['check_schedule_for_user'][0]
        actual_result = core.check_schedule_for_user(
            input['check_schedule_for_user'][0]['user_id'],
            input['check_schedule_for_user'][0]['schedule']
        )
        self.assertEqual(expected_result, actual_result)
        expected_result = expected['check_schedule_for_user'][1]
        actual_result = core.check_schedule_for_user(
            input['check_schedule_for_user'][1]['user_id'],
            input['check_schedule_for_user'][1]['schedule']
        )
        self.assertEqual(expected_result, actual_result)

    def check_team_for_user(self):
        expected_result = expected['check_team_for_user'][0]
        actual_result = core.check_team_for_user(
            input['check_team_for_user'][0]['user_id'],
            input['check_team_for_user'][0]['team_users']
        )
        self.assertEqual(expected_result, actual_result)
        expected_result = expected['check_team_for_user'][1]
        actual_result = core.check_team_for_user(
            input['check_team_for_user'][1]['user_id'],
            input['check_team_for_user'][1]['team_users']
        )
        self.assertEqual(expected_result, actual_result)

    def get_user_layer_index(self):
        expected_result = expected['get_user_layer_index'][0]
        actual_result = core.get_user_layer_index(
            input['get_user_layer_index'][0]['user_id'],
            input['get_user_layer_index'][0]['schedule_layer']
        )
        self.assertEqual(expected_result, actual_result)
        expected_result = expected['get_user_layer_index'][1]
        actual_result = core.get_user_layer_index(
            input['get_user_layer_index'][1]['user_id'],
            input['get_user_layer_index'][1]['schedule_layer']
        )
        self.assertEqual(expected_result, actual_result)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(CoreLogicTests('get_user_id'))
    suite.addTest(CoreLogicTests('list_users_on_team'))
    suite.addTest(CoreLogicTests('list_user_escalation_policies'))
    suite.addTest(CoreLogicTests('get_schedule'))
    suite.addTest(CoreLogicTests('get_escalation_policy'))
    suite.addTest(CoreLogicTests('check_schedule_for_user'))
    suite.addTest(CoreLogicTests('check_team_for_user'))
    suite.addTest(CoreLogicTests('get_user_layer_index'))
    return suite
