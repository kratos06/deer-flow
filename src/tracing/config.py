# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

# Default configuration path
DEFAULT_CONFIG_PATH = "conf.yaml"

def get_tracing_config():
    """Get tracing configuration from conf.yaml.
    
    Returns:
        dict: The tracing configuration, or a default configuration if not found.
    """
    config_path = os.environ.get("DEERFLOW_CONFIG", DEFAULT_CONFIG_PATH)
    
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            
        # Get tracing configuration
        tracing_config = config.get("TRACING", {})
        if not tracing_config:
            logger.warning(
                "No TRACING section found in configuration. "
                "Using default configuration with tracing disabled."
            )
            return {"enabled": False}
            
        return tracing_config
    except FileNotFoundError:
        logger.warning(
            f"Configuration file {config_path} not found. "
            "Using default configuration with tracing disabled."
        )
        return {"enabled": False}
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return {"enabled": False}


def update_config_with_tracing():
    """Add TRACING section to configuration if it doesn't exist.
    
    This function adds a default TRACING section to the configuration
    file if it doesn't already exist.
    """
    config_path = os.environ.get("DEERFLOW_CONFIG", DEFAULT_CONFIG_PATH)
    
    if not Path(config_path).exists():
        logger.warning(f"Configuration file {config_path} not found.")
        return
        
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f) or {}
            
        # Add TRACING section if it doesn't exist
        if "TRACING" not in config:
            config["TRACING"] = {
                "enabled": False,
                "service_name": "deerflow",
                "endpoint": "http://localhost:4317",
                "sampling_rate": 1.0
            }
            
            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False)
                
            logger.info(f"Added TRACING section to {config_path}")
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")

