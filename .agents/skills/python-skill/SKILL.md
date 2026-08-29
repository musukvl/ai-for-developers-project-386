---
name: python-skill
description: Use this skill when writing, reviewing, or refactoring Python code, creating or running a Python project, or managing dependencies, lockfiles, or environments. Enforces UV-first tooling, latest stable Python, PEP style, type hints (PEP 484), and loguru for logging.
---

# Python Skill

## When to Use This Skill

- Writing, reviewing, or refactoring Python code
- Creating or running a Python project
- Managing dependencies, lockfiles, or environments (`pyproject.toml`, `uv.lock`)
- Adding, updating, or removing packages with uv
- Choosing uv over pip, venv, or poetry-style workflows
- Applying project Python style: module layout, naming, docstrings, type hints (PEP 484), and PEP 8
- Testing, debugging, or running Python code

## Mandatory requirements

- Python code must be well structured and clear for the reader. Split into packages, modules, and functions; use paragraphs inside functions.
- Use the latest stable Python by default. Do not use legacy patterns.
- The component owns the actual Python version (`requires-python`, `AGENTS.md`, `pyproject.toml`). Use the latest guidelines and syntax allowed by that version. Never apply legacy guidance when a newer, still-allowed form exists.
- By default follow the PEP guidelines, except instructions in skills and AGENTS.md or user prompts.
- UV is mandatory by default for dependencies, environments, and running the project. Prefer `uv add`, `uv sync`, and `uv run` over `python`, `pip`, and `venv`.
- Use clear names for variables, avoid 2-letter variable names, and do not use 3-letter variable names except for loop counters. Ensure code is well-documented.
- Annotate public functions: every parameter and the return type (PEP 484).
- Use modern type syntax (`X | None`, `list[str]`, `dict[str, int]`). Use newer syntax when the component’s Python version allows it. Do not use `Optional`, `List`, `Dict`, or `Tuple` from `typing`.
- Use `-> None` when the function returns nothing. Use `-> NoReturn` (from `typing`) only when it cannot return (infinite loop, always raises, `sys.exit`).
- Avoid `Any` unless the value is truly unknown.
- Use data classes to represent structured data rather than dicts where appropriate.
- Use loguru instead of print statements for logging.
- Each function should have a clear input and output specification. Avoid side effects.

## Python tooling

- Use UV to manage Python dependencies and isolated environments.
- Use UV to run applications (`uv run`).
- Generate a `pyproject.toml` file to specify project dependencies and configurations using UV.

## Code writing guides

- Add a short module description at the beginning of the file (PEP 257: a module should start with a docstring).
- Document each method with inline comments.
- Add docstrings to all public methods and classes to explain their purpose and usage.
- Place entrypoint functions in the file first, private functions below.
- Place constants at the top of the file.
- Private methods should start with underscore `_`.
- Follow PEP 8: Public and Internal Interfaces.
- Use functions and procedures to organize code into logical sections.

### Method body guides

- Follow PEP 8 blank lines: use blank lines in functions, sparingly, to indicate logical sections. Separate logical blocks into paragraphs (for example, input validation from main logic).
- Method structure should always be obvious: input, processing, output.
- For a complex-logic paragraph, add a paragraph title comment.
- Do not extract a 2-3 line method used only once; keep it as a code paragraph.
