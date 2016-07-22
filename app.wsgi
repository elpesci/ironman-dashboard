#!/usr/bin/python

import sys
sys.path.insert(0, '/home/ubuntu/dashboard')
sys.path.insert(0, '/home/ubuntu/dashboard/utils')
from app import app

app.run(host='0.0.0.0', port=80)


