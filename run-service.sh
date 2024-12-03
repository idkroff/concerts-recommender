#!/bin/bash

sudo ln -s "$(pwd)/recommender.service" /etc/systemd/system/recommender.service

sudo systemctl daemon-reload

sudo systemctl restart recommender.service

systemctl status recommender.service
