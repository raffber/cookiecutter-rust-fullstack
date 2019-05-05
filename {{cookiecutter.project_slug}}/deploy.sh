#!/bin/bash

set -xe
cd "$(dirname "$0")"

DEPLOY_DIR="{{cookiecutter.deploy_directory}}"

./wasp release
sudo rm -r $DEPLOY_DIR
sudo mkdir -p $DEPLOY_DIR
sudo cp build/prod.zip $DEPLOY_DIR
sudo unzip -o $DEPLOY_DIR/prod.zip -d $DEPLOY_DIR/
sudo chown www-srv -R /home/www-srv/
sudo cp deploy/{{cookiecutter.project_slug}}.service /etc/systemd/system/
sudo cp deploy/{{cookiecutter.project_slug}}.conf /etc/nginx/sites-enabled/
sudo systemctl daemon-reload
sudo systemctl restart {{cookiecutter.project_slug}}.service
sudo systemctl restart nginx.service
