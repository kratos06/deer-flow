# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import subprocess
import webbrowser
from typing import Annotated, Dict, Any, List, Optional, Union
import os
import platform

from langchain_core.tools import tool

logger = logging.getLogger(__name__)
