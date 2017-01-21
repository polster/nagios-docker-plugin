#!/usr/bin/env python

import sys
import logging as log
import argparse
import docker

# The plugin version
version = "1.0.0"
# The plugin description
plugin_description = '''Nagios plugin for Docker'''
# The check help
check_help = '''Docker monitoring check:
    container_status:   Checks if one or more containers specified by name are running.
    ping:               Checks if the Docker host is responsive.
'''
# The Nagios supported status codes
nagios_status_list = { 'OK' : 0 , 'WARNING' : 1, 'CRITICAL' : 2 , 'UNKNOWN' : 3}
# The message to be returned to Nagios
message = ''
# The exit code to be returned to Nagios
exit_status = 'OK'

def check_container_status(container_check_list, docker_client):

    global message, exit_status

    log.debug('Checking Docker container status')

    container_status_list = []
    container_list = docker_client.containers.list(all=True)
    exit_status = 'OK'

    for container in container_list:

        # We are only interested in verifying if container X specified by name is running or not
        if container.name in container_check_list:
            if container.status != "running":
                container_status_list.append("container: [%s] status: [%s]" % (container.name, container.status))
                exit_status = 'CRITICAL'
            else:
                container_status_list.append("container: %s status: %s" % (container.name, container.status))

    message = ', '.join(container_status_list)

def check_ping(docker_client):

    global message, exit_status

    log.debug('Checking Docker host is responsive')

    response = docker_client.ping()
    if response == True:
        exit_status = 'OK'
        message = 'Docker host is responsive'

def instantiate_docker_client(url,connection_timeout_in_seconds):

    log.debug('Instantiating docker client with url [%s] and connection timeout [%s] seconds' % (url, connection_timeout_in_seconds))
    docker_client = docker.DockerClient(base_url=url, timeout=connection_timeout_in_seconds)
    return docker_client

def nagios_out(exit_status, message=''):

    log.debug('Exiting with rc [{0}] and message [{1}]'.format(exit_status, message))
    if message:
        print message
    exit(nagios_status_list[exit_status])

def main():

    global exit_status, message

    try:

        # command args config
        parser = argparse.ArgumentParser(description=plugin_description, formatter_class=argparse.RawTextHelpFormatter)
        parser.version = parser.prog+" 1.0"
        parser.add_argument('-v','--version', action='version', help="Show plugin version", version='%(prog)s '+version)
        connection_parameters = parser.add_argument_group('Connection parameters', 'parameters for the connection to the Docker Host')
        connection_parameters.add_argument('-H','--host', default = "unix:///var/run/docker.sock", help='''Docker host url, "unix:///var/run/docker.sock" by default''')
        connection_parameters.add_argument('-t','--timeout', default = 20, help='''Connection timeout in seconds, "20" by default''', type=int)
        parameters = parser.add_argument_group('Check parameters', 'Parameters for Docker check')
        parameters.add_argument('-c','--check', choices=['container_status', 'ping'], help=check_help, required=True)
        parameters.add_argument('-d','--docker_names', nargs='+', help='List containing one or more names of the containers to be checked', required=False)

        # in case we have no user provided arguments
        if sys.argv[1:] == []:
            parser.print_usage()
            parser.exit(nagios_status_list['UNKNOWN'], "ERROR: No arguments, use '" + parser.prog + " -h' for help\n")

        # parse arguments
        args = parser.parse_args()

        # instantiate the docker client
        docker_client = instantiate_docker_client(args.host, args.timeout)

        if args.check == 'container_status':
            if args.docker_names is None:
                parser.error('ERROR: For container status checking, -d/--docker-names has to be specified')
            check_container_status(args.docker_names, docker_client)

    except Exception, e:
        message = "FAIL! %s" % e
        exit_status = 'UNKNOWN'

    nagios_out(exit_status, message)

if __name__ == '__main__':

    ## Initialize logging before hitting main, in case we need extra debuggability
    log.basicConfig(level=log.DEBUG, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    main()
