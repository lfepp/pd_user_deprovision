#!/usr/bin/env python

import unittest
import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
import user_deprovision  # NOQA

input_filename = os.path.join(os.path.dirname(__file__), './input/live.json')
config_filname = os.path.join(os.path.dirname(__file__), './config.json')

with open(input_filename) as input_file:
    _in = json.load(input_file)

with open(config_filname) as config_file:
    config = json.load(config_file)


class LiveTestInAccount(unittest.TestCase):

    def setUp(self):
        self.objects = {}
        self.pdr = user_deprovision.PagerDutyREST(config['access_token'])
        pdr = self.pdr
        api_err_msg = ("Failed to create {type} input data in the account for "\
            "testing purposes. Response from the server was ({code}): {body}")
        # Create user and add to all the things:
        user = pdr.post(
            '/users', 
            _in['users'][0],
            config['from_header']
        )['user']
        self.objects['users'] = [user]

        _in['schedules'][0]['schedule_layers'][0]['users'] = [{
            'type': 'user_reference',
            'id': user[u'id']
        }]
        schedule = pdr.post(
            '/schedules', 
            {'schedule':_in['schedules'][0]}
        )['schedule']
        self.objects['schedules'] = [schedule]

        _in['escalation_policies'][0]['escalation_rules'][0]['targets'] = [{
            'type': 'user_reference',
            'id': user['id']
        }]
        _in['escalation_policies'][0]['escalation_rules'][1]['targets'] = [{
            'type': 'schedule_reference',
            'id': schedule['id']
        }]
        
        ep = pdr.post(
            '/escalation_policies', 
            {'escalation_policy': _in['escalation_policies'][0]}
        )['escalation_policy']
        self.objects['escalation_policies'] = [ep]
        self.input_yn = user_deprovision.input_yn

    def tearDown(self):
        for obj_type in ['escalation_policies', 'schedules', 'users']:
            if obj_type in self.objects:
                for obj in self.objects[obj_type]:
                    try:
                        self.pdr.delete('/%s/%s'%(obj_type, obj['id']))
                    except Exception as e:
                        pass
        user_deprovision.input_yn = self.input_yn

    def test_live_delete_none(self):
        # Say no to all deletion: escalation policy and schedule should still be
        # there:
        user_deprovision.input_yn = lambda s: False

        ep = self.objects['escalation_policies'][0]
        schedule = self.objects['schedules'][0]

        user_deprovision.main(
            config['access_token'], 
            self.objects['users'][0]['email'],
            config['from_header'], 
            prompt_del=config['prompt_del']
        )

        try:
            self.pdr.delete('/escalation_policies/'+ep['id'])
            self.pdr.delete('/schedules/'+schedule['id'])
        except Exception as e:
            self.fail("An object should have been deleted but probably "
                "was not. Exception message: "+str(e))
        
    def test_live_delete_all(self):
        # Say no to all deletion: escalation policy and schedule should still be
        # there:
        user_deprovision.input_yn = lambda s: True

        ep = self.objects['escalation_policies'][0]
        schedule = self.objects['schedules'][0]

        user_deprovision.main(
            config['access_token'], 
            self.objects['users'][0]['email'],
            config['from_header'], 
            prompt_del=config['prompt_del']
        )

        # Should not have been deleted at this point:
        with self.assertRaises(Exception):
            pdr.delete('/escalation_policies/'+ep['id'])
        with self.assertRaises(Exception):
            pdr.delete('/schedules/'+schedule['id'])

def suite():
    suite = unittest.TestSuite()
    suite.addTest(LiveTestInAccount('live_test'))

if __name__ == '__main__':
    unittest.main()
