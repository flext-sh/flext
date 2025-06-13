#!/bin/bash
# FLX CLI Runner Script
# Automatically activates the virtual environment and runs flx commands

source .venv/bin/activate
flx "$@"