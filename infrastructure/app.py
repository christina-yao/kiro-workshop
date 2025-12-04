#!/usr/bin/env python3
import os
import sys

# Add the venv to the path
venv_path = os.path.join(os.path.dirname(__file__), 'venv', 'lib', 'python3.11', 'site-packages')
if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)

import aws_cdk as cdk
from infrastructure.infrastructure_stack import InfrastructureStack

app = cdk.App()
InfrastructureStack(app, "InfrastructureStack")

app.synth()
