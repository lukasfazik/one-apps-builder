#!/usr/bin/env python3

import os
from one import One
import logging

if __name__ == "__main__":
    # Setup logging
    DEBUG = os.environ.get("DEBUG", "false")
    if DEBUG == "true":
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    # Init logging handler
    logger = logging.getLogger("main")
    logger.setLevel(log_level)
    # Create formatter
    log_formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s %(module)s %(funcName)s -> %(message)s', "%d-%m-%Y %H:%M:%S")
    # Create stream handler (console)
    log_stream_handler = logging.StreamHandler()
    log_stream_handler.setFormatter(log_formatter)
    # Add stream handler to logger
    logger.addHandler(log_stream_handler)    
    # Set up environment variables and determine image name
    ONE_XMLRPC = os.environ.get("ONE_XMLRPC", "http://localhost:2633/RPC2")
    logger.debug(f"ONE_XMLRPC: {ONE_XMLRPC}")
    ONE_AUTH = os.environ.get("ONE_AUTH", "~/.one/one_auth")
    logger.debug(f"ONE_AUTH: {ONE_AUTH}")
    CI_PIPELINE_ID = os.environ.get("CI_PIPELINE_ID", "")
    logger.debug(f"CI_PIPELINE_ID: {CI_PIPELINE_ID}")
    CI_COMMIT_SHA = os.environ.get("CI_COMMIT_SHA", "")
    logger.debug(f"CI_COMMIT_SHA: {CI_COMMIT_SHA}")
    # Read credentials from ONE_AUTH file
    try:
        logger.info(f"Reading Opennebula credentials from {ONE_AUTH}")
        with open(os.path.expanduser(ONE_AUTH), "r") as f:
            credentials = f.read().strip()
            if ":" not in credentials:
                logger.critical(f"Error: Invalid credentials format in {ONE_AUTH}. Expected 'username:password'")
                exit(1)
            username, password = credentials.split(":", 1)
            session = f"{username}:{password}"
    except FileNotFoundError:
        logger.critical(f"ONE_AUTH file not found at {ONE_AUTH}")
        exit(1)
    # Inicialize OpenNebula connection
    logger.info("Inicializing OpenNebula connection")
    one = One(url=ONE_XMLRPC, username=username, password=password)
    # Get all images with given CI_PIPELINE_ID
    all_resources_filter = -2
    logger.info(f"Getting all templates with CI_PIPELINE_ID: {CI_PIPELINE_ID} and CI_COMMIT_SHA: {CI_COMMIT_SHA}")
    template_ids: list = one.find_templates_by_attributes(
        filter=all_resources_filter,
        attributes={
            "CI_PIPELINE_ID": CI_PIPELINE_ID,
            "CI_COMMIT_SHA": CI_COMMIT_SHA
        }
    )
    logger.info(f"Found {len(template_ids)} matching templates")
    for template_id in template_ids:
        logger.info(f"Deleting template {template_id} with all images")
        one.delete_vm_template(template_id, delete_images=True)
