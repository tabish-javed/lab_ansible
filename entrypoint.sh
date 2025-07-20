#!/usr/bin/bash

# Ensure /home/ansible/.ssh exists and has correct ownership (handle named volumes)
if [ -d "/home/ansible/.ssh" ]; then
  chown -R ansible:ansible /home/ansible/.ssh
  chmod 700 /home/ansible/.ssh
fi

exec "$@"
