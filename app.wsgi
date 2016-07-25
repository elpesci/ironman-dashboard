#!/usr/bin/python

import sys
#sys.path.insert(0, '/home/ubuntu/dashboard')
#sys.path.insert(0, '/home/ubuntu/dashboard/utils')
sys.path.insert(0, '/home/jcsm/Dashboard Workspace')
sys.path.insert(0, '/home/jcsm/Dashboard Workspace/utils')
from app import app

app.run(host='0.0.0.0', port=80)


