#!/bin/bash
set -e

export PYTHONPATH=/app

if [ "$#" -eq "0" ]; then
  echo "Start command not found. Starting shell"
  exec sh
else
  echo "Executing start command '$@'"
  exec sh -c "$@"
  echo "Executed. Sleep"
  sleep 120
fi
