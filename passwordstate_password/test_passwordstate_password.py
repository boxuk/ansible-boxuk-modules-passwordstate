""" PasswordState Test """

import unittest2 as unittest

from passwordstate_password import Password
from passwordstate_password import PasswordState
from passwordstate_password import PasswordIdException
from ddt import ddt, data, unpack
import mock

class PasswordTest(unittest.TestCase):
    """ PasswordTest """

    def test_init_passwordid_1(self):
        """ test constructor with password id """
        api = mock.Mock()
        list_id = 123
        matcher = {'id': 987, 'field': None, 'field_id': None}
        password = Password(api, list_id, matcher)

        self.assertEqual(password.api, api)
        self.assertEqual(password.password_list_id, list_id)
        self.assertEqual(password.password_id, matcher['id'])
        self.assertFalse(hasattr(password, 'field'))
        self.assertFalse(hasattr(password, 'field_id'))

    def test_init_passwordid_2(self):
        """ test constructor with password id and field values """
        api = mock.Mock()
        list_id = 123
        matcher = {'id': 987, 'field': 'GenericField1', 'field_id': 'abc'}
        password = Password(api, list_id, matcher)

        self.assertEqual(password.api, api)
        self.assertEqual(password.password_list_id, list_id)
        self.assertEqual(password.password_id, matcher['id'])
        self.assertFalse(hasattr(password, 'field'))
        self.assertFalse(hasattr(password, 'field_id'))

    def test_init_field(self):
        """ test constructor """
        api = mock.Mock()
        list_id = 123
        matcher = {'id': None, 'field': 'GenericField1', 'field_id': 'abc'}
        password = Password(api, list_id, matcher)

        self.assertEqual(password.api, api)
        self.assertEqual(password.password_list_id, list_id)
        self.assertEqual(password.match_field, matcher['field'])
        self.assertEqual(password.match_field_id, matcher['field_id'])
        self.assertFalse(hasattr(password, 'password_id'))

    def test_init_exception(self):
        """ test constructor """
        api = mock.Mock()
        list_id = 123

        matcher = {'id': None, 'field': None, 'field_id': None}
        with self.assertRaises(PasswordIdException):
            password = Password(api, list_id, matcher)

        matcher = {}
        with self.assertRaises(PasswordIdException):
            password = Password(api, list_id, matcher)

    @mock.patch('passwordstate_password.Password.__init__',
                mock.Mock(return_value=None))
    def test_type_passwordid_1(self):
        """ test logic of password id type """
        password = Password()
        password.password_id = 987
        self.assertEqual('password_id', password.type)

    @mock.patch('passwordstate_password.Password.__init__', mock.Mock(return_value=None))
    def test_type_passwordid_2(self):
        """ test logic of password id type """
        password = Password()
        password.password_id = 987
        self.assertEqual('password_id', password.type)

    @mock.patch('passwordstate_password.Password.__init__', mock.Mock(return_value=None))
    def test_type_field(self):
        """ test logic of password id type """
        password = Password()
        password.match_field = 'GenericField1'
        password.match_field_id = 'abc'
        self.assertEqual('match_field', password.type)

    @mock.patch('passwordstate_password.Password.__init__', mock.Mock(return_value=None))
    def test_type_field(self):
        """ test logic of password id type """
        password = Password()
        with self.assertRaises(PasswordIdException):
            password.type

    @mock.patch('passwordstate_password.Password.__init__', mock.Mock(return_value=None))
    def test_password(self):
        """ test password getter """
        api = mock.Mock()
        api.get_password_fields = mock.Mock()
        api.get_password_fields.return_value = {"Password": "securepassword"}

        password = Password()
        password.api = api

        self.assertEqual("securepassword", password.password)

    @mock.patch('passwordstate_password.Password.__init__', mock.Mock(return_value=None))
    def test_password(self):
        """ test password getter """
        api = mock.Mock()
        api.update = mock.Mock()
        password = Password()
        password.api = api
        fields = {"password": "newpassword"}
        password.update(fields)
        password.api.update.assert_called_once_with(password, fields)

@ddt
class PasswordStateTest(unittest.TestCase):
    """ PasswordStateTest """

    def test_init(self):
        """ test constructor """
        module = mock.Mock()
        url = "http://passwordstate"
        api_key = "abc123xyz"
        passwordstate = PasswordState(module, url, api_key)

        self.assertEqual(passwordstate.module, module)
        self.assertEqual(passwordstate.url, url)
        self.assertEqual(passwordstate.api_key, api_key)

    def test_filter_passwords(self):
        """ test filter passwords """
        passwords = [{'GenericField1': 'alpha', 'GenericField2': 'beta'},
                     {'GenericField1': 'charlie', 'GenericField2': 'delta'},
                     {'GenericField1': 'echo', 'GenericField2': 'alpha'}]
        filtered = PasswordState._filter_passwords(passwords, 'GenericField1', 'alpha')
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['GenericField1'], 'alpha')

    def test_merge_dicts_1(self):
        """ test merge dicts """
        dict1 = {'Foo': 'bar', 'Bar': 'foo'}
        dict2 = {'Foobar': 'Baz'}
        actual = PasswordState._merge_dicts(dict1, dict2)
        expected = {'Foo': 'bar', 'Bar': 'foo', 'Foobar': 'Baz'}

        self.assertEqual(actual, expected)
    def test_merge_dicts_2(self):
        """ test merge dicts """
        dict1 = {'Foo': 'bar', 'Bar': 'foo'}
        dict2 = {'Foo': 'foobar', 'Foobar': 'Baz'}
        actual = PasswordState._merge_dicts(dict1, dict2)
        expected = {'Foo': 'foobar', 'Bar': 'foo', 'Foobar': 'Baz'}

        self.assertEqual(actual, expected)

    @mock.patch('urllib2.urlopen', autospec=True)
    def test_update_passwordmatch_match_id(self, mock_urlopen):
        """ password that doesnt need updating """
        value = '[{"Password": "foo", "Title": "bar", ' \
                '"UserName": "foobar", "GenericField1": "123", ' \
                '"PasswordID": 999}]'

        mock_urlopen.return_value.read.return_value = value

        module = mock.Mock()
        module.exit_json = mock.MagicMock()
        url = "http://passwordstate"
        api_key = "abc123xyz"

        api = PasswordState(module, url, api_key)
        password = Password(api, '123',
                            {'id': '999', 'field': None, 'field_id': None})

        fields = {"password": "foo"}
        password.update(fields)

        module.exit_json.assert_called_with(changed=False)

    @mock.patch('urllib2.urlopen', autospec=True)
    def test_update_passwordmatch_match_field(self, mock_urlopen):
        """ password that doesnt need updating """
        value = '[{"Password": "foo", "Title": "bar", ' \
                '"UserName": "foobar", "GenericField1": "123", ' \
                '"PasswordID": 999}]'
        mock_urlopen.return_value.read.return_value = value

        module = mock.Mock()
        module.exit_json = mock.MagicMock()
        url = "http://passwordstate"
        api_key = "abc123xyz"

        api = PasswordState(module, url, api_key)
        password = Password(api, '123',
                            {'id': None, 'field': 'GenericField1', 'field_id': '123'})

        fields = {"password": "foo"}
        password.update(fields)

        module.exit_json.assert_called_with(changed=False)

    @mock.patch('urllib2.urlopen', autospec=True)
    @data({'password': 'newpassword'},
          {'Title': 'newtitle'},
          {'UserName': 'newuser'},
          {'password': 'foo', 'Title': 'newtitle'},
          {'Title': 'bar', 'UserName': 'newuser'})
    def test_update_passwordmatch_nomatch_id(self, fields, mock_urlopen):
        """ password that doesnt need updating """
        value = '[{"Password": "foo", "Title": "bar", ' \
                '"UserName": "foobar", "GenericField1": "123", ' \
                '"PasswordID": 999}]'
        mock_urlopen.return_value.read.return_value = value

        module = mock.Mock()
        module.exit_json = mock.MagicMock()
        url = "http://passwordstate"
        api_key = "abc123xyz"

        api = PasswordState(module, url, api_key)
        password = Password(api, '123',
                            {'id': '999', 'field': None, 'field_id': None})

        password.update(fields)

        module.exit_json.assert_called_with(changed=True)

    @mock.patch('urllib2.urlopen', autospec=True)
    @data({'password': 'newpassword'},
          {'Title': 'newtitle'},
          {'UserName': 'newuser'},
          {'password': 'foo', 'Title': 'newtitle'},
          {'Title': 'bar', 'UserName': 'newuser'})
    def test_update_passwordmatch_nomatch_field(self, fields, mock_urlopen):
        """ password that doesnt need updating """
        value = '[{"Password": "foo", "Title": "bar", ' \
                '"UserName": "foobar", "GenericField1": "123", ' \
                '"PasswordID": 999}]'
        mock_urlopen.return_value.read.return_value = value

        module = mock.Mock()
        module.exit_json = mock.MagicMock()
        url = "http://passwordstate"
        api_key = "abc123xyz"

        api = PasswordState(module, url, api_key)
        password = Password(api, '123',
                            {'id': None, 'field': 'GenericField1', 'field_id': '123'})

        password.update(fields)

        module.exit_json.assert_called_with(changed=True)

    @mock.patch('urllib2.urlopen', autospec=True)
    def test_update_newpassword_notitle(self, mock_urlopen):
        """ password that doesnt need updating """
        mock_urlopen.return_value.read.return_value = '[]'

        module = mock.Mock()
        module.fail_json = mock.MagicMock()
        url = "http://passwordstate"
        api_key = "abc123xyz"

        api = PasswordState(module, url, api_key)
        password = Password(api, '123',
                            {'id': None, 'field': 'GenericField1', 'field_id': '123'})

        fields = {'password': 'foo'}
        password.update(fields)

        module.fail_json.assert_called_with(msg='Title is required when creating passwords')

    @mock.patch('urllib2.urlopen', autospec=True)
    def test_update_newpassword_withtitle(self, mock_urlopen):
        """ password that doesnt need updating """
        mock_urlopen.return_value.read.return_value = '[]'

        module = mock.Mock()
        module.exit_json = mock.MagicMock()
        url = "http://passwordstate"
        api_key = "abc123xyz"

        api = PasswordState(module, url, api_key)
        password = Password(api, '123',
                            {'id': None, 'field': 'GenericField1', 'field_id': '123'})

        fields = {'password': 'foo', 'Title': 'mytitle'}
        password.update(fields)

        module.exit_json.assert_called_with(changed=True)
