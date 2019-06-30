#!/usr/bin/python3

import jenkins
import time

import xml.etree.ElementTree as ET

server = jenkins.Jenkins('http://localhost:8080', username='admin', password='admin')
job_name = 'test_pipeline_job'

with open('Jenkinsfile') as f:
    script = f.read()

job_info = server.get_job_info(job_name)
last_build_number = job_info['lastCompletedBuild']['number']

xml_config = server.get_job_config(job_name)
xml_tree_root = ET.fromstring(xml_config)
xml_tree_root.find('definition').find('script').text = script
new_xml_config = ET.tostring(xml_tree_root, encoding='unicode', method='xml')

server.reconfig_job(job_name, new_xml_config)
server.build_job(job_name)

last_build_number += 1

while True:
    time.sleep(0.5)
    try:
        build_info = server.get_build_info(job_name, last_build_number)
        if build_info['building']:
            continue
        log = server.get_build_console_output(job_name, last_build_number)
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
