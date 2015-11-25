[![Build Status](https://travis-ci.org/boxuk/ansible-boxuk-modules-passwordstate.svg)](https://travis-ci.org/boxuk/ansible-boxuk-modules-passwordstate)

# Ansible PasswordState Modules

This repository contains two ansible modules for
setting and getting passwordstate passwords.

## passwordstate_password

```
- name: push password to passwordstate
  sudo: False
  local_action:
    module: 'passwordstate_password'
    url: 'http://passwordstate.internal.corp.net'
    api_key: 'xxxxxxxxx'
    password_list_id: 'xxxx'
    match_field: 'GenericField1'
    match_field_id: 'xx'
    title: 'My password title'
    username: 'username'
    password: 'my secure password'
```

## passwordstate_password_fact

Fetch by custom match field/id:

```
- name: get password from passwordstate
  sudo: False
  local_action:
    module: 'passwordstate_password'
    url: 'http://passwordstate.internal.corp.net'
    api_key: 'xxxxxxxxx'
    password_list_id: 'xxxx'
    match_field: 'GenericField1'
    match_field_id: 'xx'
    fact_name: 'myaccount'

- debug: var=myaccount_password
```


Fetch by password id:

```
- name: get password from passwordstate
  sudo: False
  local_action:
    module: 'passwordstate_password'
    url: 'http://passwordstate.internal.corp.net'
    api_key: 'xxxxxxxxx'
    password_list_id: 'xxxx'
    password_id: 'xx'
    fact_name: 'myaccount'

- debug: var=myaccount_password
```
