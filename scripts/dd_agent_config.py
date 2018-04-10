#!/usr/bin/env python
from __future__ import print_function
import argparse
import hashlib
import os
import sys

BASE_PATH = '/etc/datadog-agent/%s'


def file_hash(filename):
    hash = None
    try:
        hash = hashlib.md5(open(filename,'rb').read()).hexdigest()
    except IOError:
        pass
    return hash


def config_dd_agent(environment, api_key):
    params =  {
        'environment': environment,
        'api_key': api_key
    }

    before_hash = file_hash(BASE_PATH % 'datadog.yaml')
    with open(BASE_PATH % 'datadog.tmpl.yaml', 'r') as template:
        with open(BASE_PATH % 'datadog.yaml', 'w') as config:
            config.write(template.read() % params)
    after_hash = file_hash(BASE_PATH % 'datadog.yaml')
    
    if before_hash != after_hash:
        os.system('/bin/systemctl restart datadog-agent.service')  


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Configure Datadog Agent.')
    parser.add_argument('environment', type=str, help='production|staging|homolog')
    parser.add_argument('api_key', type=str, help='datadog api agent', nargs='?', default=None)
    args = parser.parse_args()
    if args.environment not in ['production', 'staging', 'homolog', 'dev']:
        print('Invalid environment %s' % args.environment)
        sys.exit(1)
    elif not args.api_key:
        print('No API-KEY, DD-Agent will remain stopped.')
        sys.exit(0)
    elif len(args.api_key) != 32:
        print('Invalid API-KEY. DD-Agent will remain stopped.')
        sys.exit(1)
    config_dd_agent(args.environment, args.api_key)
