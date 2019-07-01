#!/usr/bin/python3

import os, sys
import time
import xml.etree.ElementTree as ET

import yaml
import jenkins

CONFIG_FILE = 'push_job.yml'

def main():
    if not os.path.isfile(CONFIG_FILE):
        raise FileNotFoundError("The '{}' config file not found!".format(CONFIG_FILE))

    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f)['config']

    with open(config['jenkinsfile']) as f:
        script = f.read()

    server = jenkins.Jenkins(config['url'],
        username=config['username'],
        password=config['password'])

    job_info = server.get_job_info(config['job'])
    last_build_number = job_info['lastCompletedBuild']['number']

    xml_config = server.get_job_config(config['job'])
    xml_tree_root = ET.fromstring(xml_config)
    xml_tree_root.find('definition').find('script').text = script
    new_xml_config = ET.tostring(xml_tree_root, encoding='unicode', method='xml')

    server.reconfig_job(config['job'], new_xml_config)
    server.build_job(config['job'])

    last_build_number += 1

    while True:
        time.sleep(0.5)
        try:
            build_info = server.get_build_info(config['job'], last_build_number)
            if build_info['building']:
                continue
            log = server.get_build_console_output(config['job'], last_build_number)
            break
        except jenkins.JenkinsException as ex:
            if ('number' in str(ex) and
                'does not exist' in str(ex)):
                continue
            else:
                raise ex

    print(log)
    print(f"Job URL:        {job_info['url']}")
    print(f"Build number:   {last_build_number}")

if __name__ == "__main__":
    main()