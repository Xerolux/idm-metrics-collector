#!/bin/bash
ruff check --fix idm_logger/
ruff check --fix ml_service/
ruff format idm_logger/
ruff format ml_service/
