#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Django settings for floreal project.
"""

# Django project settings loader
import os
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

# You can key the configurations off of anything - I use project path.
# settings files go into ROOT_PATH/config/
# e.g. ROOT_PATH/config/roco.py, ROOT_PATH/config/prod.py

configs = {
    '/home/roco/caracole/caracole': 'roco',
    '/home/florealpavillons/circuit-court/caracole': 'prod',
}

# Import the configuration settings file
config_module = __import__('config.%s' % configs[ROOT_PATH], globals(), locals(), 'caracole')

# Load the config settings properties into the local scope.
for setting in dir(config_module):
    if setting == setting.upper():
        locals()[setting] = getattr(config_module, setting)
