#!/usr/bin/env python

import sys
import logging as log
import docker

nagios_status_list = { 'OK' : 0 , 'WARNING' : 1, 'CRITICAL' : 2 , 'UNKNOWN' : 3}
message = ''
exit_status = 'OK'

def check_container_status(container_check_list,url):

    global message, exit_status

    try:
        container_status_list = []
        container_status_nok = False

        client = docker.DockerClient(base_url=url, timeout=20)
        container_list = client.containers.list(all=True)

        for container in container_list:
            container_status_list.append("container:[%s] status:[%s]" % (container.name, container.status))

            # We are only interested in verifying if the specified container by name is running or not
            if container.name in container_check_list and container.status != "running":
                exit_status = 'CRITICAL'

        message = ', '.join(container_status_list)

    except Exception, e:
        message = "FAIL! %s" % e
        exit_status = 'CRITICAL'

def nagios_out(exit_status, message=''):

    log.debug('Exiting with rc [{0}] and message [{1}]'.format(exit_status, message))
    if message:
        print message
    exit(nagios_status_list[exit_status])

def main():

    container_check_list = ['nagios']
    url = 'http://192.168.9.70:4243'

    check_container_status(container_check_list, url)
    nagios_out(exit_status, message)

if __name__ == '__main__':

    ## Initialize logging before hitting main, in case we need extra debuggability
    log.basicConfig(level=log.DEBUG, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    main()
