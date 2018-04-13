#!/usr/bin/env python
from __future__ import print_function
import argparse
import hashlib
import os
import requests
import sys
from psutil import virtual_memory

BASE_ETC_PATH = '/etc/default/%'
BASE_ES_PATH = '/etc/elasticsearch/%s'


def aws_instance_id():
    return requests.get('http://169.254.169.254/latest/meta-data/placement/instance-id').text


def aws_region():
    return requests.get('http://169.254.169.254/latest/meta-data/placement/availability-zone').text[0:-1]


def file_hash(filename):
    hash = None
    try:
        hash = hashlib.md5(open(filename,'rb').read()).hexdigest()
    except IOError:
        pass
    return hash


def config_elasticsearch(cluster):
    params =  {
        'cluster': cluster,
        'region': aws_region(),
        'memory': min([max([2.56e+8, virtual_memory().total/2]), 3.2e+10])
    }

    before_hash_etc = file_hash(BASE_ETC_PATH % 'elasticsearch')
    with open(BASE_ES_PATH % 'default/elasticsearch.tmpl', 'r') as template:
        with open(BASE_ETC_PATH % 'default/elasticsearch', 'w') as config:
            config.write(template.read() % params)
    after_hash_etc = file_hash(BASE_ETC_PATH % 'elasticsearch')

    before_hash = file_hash(BASE_ES_PATH % 'elasticsearch.yml')
    with open(BASE_ES_PATH % 'elasticsearch.tmpl.yml', 'r') as template:
        with open(BASE_ES_PATH % 'elasticsearch.yml', 'w') as config:
            config.write(template.read() % params)
    after_hash = file_hash(BASE_ES_PATH % 'elasticsearch.yml')
    
    if before_hash_etc != after_hash_etc or before_hash != after_hash:
        os.system('/etc/init.d/elasticsearch restart')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Configure Elasticsearch server.')
    parser.add_argument('cluster', type=str, help='Cluster Name')
    args = parser.parse_args()
    config_elasticsearch(args.cluster)
