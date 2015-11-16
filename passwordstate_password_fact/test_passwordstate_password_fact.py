""" PasswordState Test """

import unittest2 as unittest

from passwordstate_password_fact import Password
from passwordstate_password_fact import PasswordState
from ddt import ddt, data, unpack
import mock

class PasswordTest(unittest.TestCase):
    """ PasswordTest """

    @mock.patch('urllib2.urlopen', autospec=True)
    def test_gather_facts_id(self, mock_urlopen):
        """ gather facts by id """
        value = '[{"Password": "foo", "Title": "bar", ' \
                '"UserName": "foobar", "GenericField1": "123", ' \
                '"PasswordID": 999}]'
        mock_urlopen.return_value.read.return_value = value

        module = mock.Mock()
        url = "http://passwordstate"
        api_key = "abc123xyz"

        api = PasswordState(module, url, api_key)
        password = Password(api, '123',
                            {'id': '999', 'field': None, 'field_id': None})

        facts = password.gather_facts('fact_name_prefix')
        expected = {'fact_name_prefix_password': 'foo'}
        self.assertEquals(expected, facts)

    @mock.patch('urllib2.urlopen', autospec=True)
    def test_gather_facts_field(self, mock_urlopen):
        """ gather facts by custom field """
        value = '[{"Password": "foo", "Title": "bar", ' \
                '"UserName": "foobar", "GenericField1": "123", ' \
                '"PasswordID": 999}]'
        mock_urlopen.return_value.read.return_value = value

        module = mock.Mock()
        url = "http://passwordstate"
        api_key = "abc123xyz"

        api = PasswordState(module, url, api_key)
        password = Password(api, '123',
                            {'id': None, 'field': 'GenericField1', 'field_id': '123'})

        facts = password.gather_facts('fact_name_prefix')
        expected = {'fact_name_prefix_password': 'foo'}
        self.assertEquals(expected, facts)
