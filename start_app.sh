#!/bin/bash
gunicorn app:server -b 0.0.0.0:8050 -w 4
