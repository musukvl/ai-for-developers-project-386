---
name: python-skill
description: Use this skill when writing, reviewing, or refactoring Python code to ensure adherence to BIP coding standards and industry best practices.
metadata:
  version: 1.1.0
---
# Python Best Practices Skill

This skill provides comprehensive guidance on Python coding practices.

# Python scripts instructions

- Use descriptive variable and function names. Don't use 3-letter variable names except for loop counters.
- Use functions and procedures to organize code into logical sections.
- Use UV to manage Python dependencies.
- Use UV capabilities to create isolated environments for different projects.
- Use UV capabilities to run applications.
- Generate a `pyproject.toml` file to specify project dependencies and configurations using UV.
- Python scripts should have all configuration variables at the top of the script. For example, host, port, username, password, topic names, etc.
- Use data classes to represent structured data prior Dicts where appropriate.
- Use logger package functionality instead of print statements for logging.
- Use loguru for logging in Python.
- Each function should have a clear input and output specification. Avoid side effects.
- Each Python module script should have an entrypoint function first. Next private methods.
- Private methods should start with an underscore (_).
- Use type hints for function signatures to improve code readability and maintainability.
- Add docstrings to all public methods and classes to explain their purpose and usage.
