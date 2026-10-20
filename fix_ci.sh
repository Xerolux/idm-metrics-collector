#!/bin/bash
ruff format tests && ruff check --fix tests
