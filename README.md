Nagios Plugin for Docker
========================

## Purpose

* Perform different checks against a Docker Host and its containers over the Docker API
* Check things like Docker Host responsiveness (ping) or if specific Docker containers are running

## Requirements

### Python

* Python 2.7
* See the [Requirements file](requests.txt)

## Run

### Deployment

* Login to your Nagios Server
* Download the latest release version of this plugin and extract (adjust the version as needed):
```
curl -SL https://github.com/polster/nagios-docker-plugin/archive/v1.0.0.tar.gz | tar xJv
```
* cd into the extracted project folder
```
cd nagios-docker-plugin-1.0.0
```
* Copy the check file into your Nagios Plugin folder:
```
cp check_docker.py /usr/local/nagios/libexec/check_docker.py
```
* Ensure the file can be executed:
```
chmod u+x /usr/local/nagios/libexec/check_docker
```
* Ensure the required Python dependencies are present:
```
pip install -r requirements.txt
```

### Test

* First of all, test the plugin by printing the available command options:
```
/usr/local/nagios/libexec/check_docker -h
```
* Try to ping one or more Docker Hosts (adjust sample params as needed):
```
python check_docker.py -H "http://192.168.9.70:4243" -c "ping"
```

## Usage

### Check Docker Containers are running

* Add the following command definition to your commands.cfg file:
```
define command {
    command_name   check_docker_container_status
    command_line   $USER1$/check_docker.py -H $ARG1$ -c container_status -d $ARG2$
}
```
* Add the following service definition to your services.cfg file (assuming we want to check container mysql-db and web-app):
```
define service{
    host_name                       srv-docker-node01
    service_description             Running containers
    check_command                   check_docker_container_status!http://192.168.9.70:4243!mysql-db web-app
    check_interval                  1
    use                             generic-service
}
```

### Check Docker Host responsiveness

* Add the following command definition to your commands.cfg file:
```
define command {
    command_name   check_docker_host_ping
    command_line   $USER1$/check_docker.py -H $ARG1$ -c ping
}
```
* Add the following service definition to your services.cfg file (assuming we want to check container mysql-db and web-app):
```
define service{
    host_name                       srv-docker-node01
    service_description             Docker Host responsiveness
    check_command                   check_docker_host_ping!http://192.168.9.70:4243
    check_interval                  1
    use                             generic-service
}
```

## Dev

### Requirements

* [Direnv](https://direnv.net/)

### Setup

* Checkout this project and cd into the same
* After being prompted by direnv, run:
```
direnv allow
```
* The required Python dependencies should be installed automatically
