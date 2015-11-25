#!/usr/bin/python

""" PasswordState Ansible Module """

from ansible.module_utils.basic import *

import urllib
import urllib2
import json

class PasswordIdException(Exception):
    msg = 'Either the password id or the match ' \
          'field id and value must be configured'

class Password(object):
    """ Password """
    def __init__(self, api, password_list_id, matcher):
        self.api = api
        self.password_list_id = password_list_id
        if 'id' in matcher and matcher['id'] != None:
            self.password_id = matcher['id']
        elif 'field' in matcher and 'field_id' in matcher \
             and matcher['field'] != None and matcher['field_id'] != None:
            self.match_field = matcher['field']
            self.match_field_id = matcher['field_id']
        else:
            raise PasswordIdException()

    @property
    def password(self):
        """ fetch the password from the api """
        return self.api.get_password_fields(self)['Password']

    @property
    def type(self):
        """ the method to uniquely identify the password """
        if hasattr(self, 'password_id'):
            return 'password_id'
        elif hasattr(self, 'match_field') and hasattr(self, 'match_field_id'):
            return 'match_field'
        raise PasswordIdException()

    def update(self, fields):
        """ Update the password """
        self.api.update(self, fields)

class PasswordState(object):
    """ PasswordState """
    def __init__(self, module, url, api_key):
        self.module = module
        self.url = url
        self.api_key = api_key

    def update(self, password, fields):
        """ update the password in PasswordState """
        if self._password_match(password, fields):
            self.module.exit_json(changed=False)
            return None

        if password.type == 'password_id':
            params = {
                'PasswordID': password.password_id,
                'PasswordListID': password.password_list_id
            }
            params = PasswordState._merge_dicts(fields, params)

            self._raw_request('passwords', 'PUT', params)
        elif password.type == 'match_field':
            if self._has_password(password):
                pid = self._get_password_id(password)

                params = {
                    'PasswordID': pid,
                    'PasswordListID': password.password_list_id
                }
                params = PasswordState._merge_dicts(fields, params)

                self._raw_request('passwords', 'PUT', params)
            else:
                if not 'Title' in fields:
                    self.module.fail_json(msg='Title is required when creating passwords')
                    return None

                params = {
                    'PasswordListID': password.password_list_id,
                    password.match_field: password.match_field_id
                }
                params = PasswordState._merge_dicts(fields, params)

                self._raw_request('passwords', 'POST', params)

        self.module.exit_json(changed=True)
        return None

    def get_password_fields(self, password):
        """ get the password fields """
        if password.type == 'password_id':
            return self._get_password_by_id(password.password_id)
        elif password.type == 'match_field':
            return self._get_password_by_field(password)

    def _get_password_by_id(self, password_id):
        """ get the password by the password id """
        passwords = self._request('passwords/' + str(password_id), 'GET')
        if len(passwords) == 0:
            self.module.fail_json(msg='Password not found')
            return None
        if len(passwords) > 1:
            self.module.fail_json(msg='Multiple matching passwords found')
            return None
        return passwords[0]

    def _get_password_by_field(self, password):
        """ get the password by a specific field """
        return self._get_password_by_id(self._get_password_id(password))

    def _get_password_id(self, password):
        """ get the password id by using a specific field """
        uri = 'passwords/' + password.password_list_id + '?QueryAll&ExcludePassword=true'
        passwords = self._request(uri, 'GET')
        passwords = PasswordState._filter_passwords(
            passwords,
            password.match_field,
            password.match_field_id
        )
        if len(passwords) == 0:
            self.module.fail_json(msg='Password not found')
            return None
        elif len(passwords) > 1:
            self.module.fail_json(msg='Multiple matching passwords found')
            return None

        return passwords[0]['PasswordID']

    def _has_password(self, password):
        """ checks if the password exists """
        if password.type == 'password_id':
            uri = 'passwords/' + password.password_id
            passwords = self._request(uri, 'GET')
            if len(passwords) == 0:
                return False
            return True
        elif password.type == 'match_field':
            plid = password.password_list_id
            uri = 'passwords/' + plid + '?QueryAll&ExcludePassword=true'
            passwords = self._request(uri, 'GET')
            passwords = PasswordState._filter_passwords(
                passwords,
                password.match_field,
                password.match_field_id
            )

            if len(passwords) == 1:
                return True
            elif len(passwords) > 1:
                self.module.fail_json(msg='Multiple matching passwords found')
                return None
            return False

    def _password_match(self, password, fields):
        """ checks if the password entity is up to date """
        match = True
        if self._has_password(password):
            current_password = self.get_password_fields(password)
            if 'password' in fields and current_password['Password'] != fields['password']:
                match = False
            if 'Title' in fields and current_password['Title'] != fields['Title']:
                match = False
            if 'UserName' in fields and current_password['UserName'] != fields['UserName']:
                match = False
        else:
            match = False
        return match

    def _request(self, uri, method, params=None):
        """ send a request to the api and return as json """
        response = self._raw_request(uri, method, params)
        if response == False:
            return []
        return json.loads(response)

    def _raw_request(self, uri, method, params=None):
        """ send a request to the api and return the raw response """
        request = self._create_request(uri, method)
        try:
            if params:
                response = urllib2.urlopen(request, urllib.urlencode(params)).read()
            else:
                response = urllib2.urlopen(request).read()
        except urllib2.URLError as inst:
            msg = str(inst)
            if "No Passwords found in the Password Lists for PasswordListID of" in msg:
                return False

            else:
                self.module.fail_json(msg="Failed: %s" % str(inst))
                return None

        return response

    def _create_request(self, uri, method):
        """ creates a request object """
        request = urllib2.Request(self.url + '/api/' +uri)
        request.add_header('APIKey', self.api_key)
        request.get_method = lambda: method
        return request

    @staticmethod
    def _filter_passwords(passwords, field, value):
        """ filter out passwords which does not match the specific field value """
        return [obj for i, obj in enumerate(passwords) if obj[field] == value]

    @staticmethod
    def _merge_dicts(xray, yankee):
        """ merge two dicts """
        zulu = xray.copy()
        zulu.update(yankee)
        return zulu

def main():
    """ main """
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present']),
            url=dict(required=True),
            api_key=dict(required=True),
            password_list_id=dict(required=False),
            match_field=dict(required=False),
            match_field_id=dict(required=False),
            password_id=dict(required=False),
            username=dict(required=False),
            password=dict(required=False),
            title=dict(required=False)
        ),
        supports_check_mode=False,
    )

    state = module.params['state']
    url = module.params['url']
    api_key = module.params['api_key']
    password_list_id = module.params['password_list_id']
    match_field = module.params['match_field']
    match_field_id = module.params['match_field_id']
    password_id = module.params['password_id']
    username = module.params['username']
    new_password = module.params['password']
    title = module.params['title']

    api = PasswordState(module, url, api_key)
    password = Password(api, password_list_id,
                        {"id": password_id, "field": match_field, "field_id": match_field_id})

    fields = {}
    if title != None:
        fields['Title'] = title
    if username != None:
        fields['UserName'] = username
    if password != None:
        fields['password'] = new_password

    if state == "present":
        password.update(fields)

if __name__ == '__main__':
    main()
