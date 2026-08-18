---
name: vule-skill
description: Provides Vue.js development guidance. Use for all interaction with Vue.js frontend code, including reading, writing, modifying, reviewing, refactoring, testing, debugging, and running Vue applications.
---

# Vue.js Best Practices Skill

This skill provides guidance for building and maintaining Vue.js frontends.

## When To Use

Use this skill for all interaction with Vue.js frontend code, including reading, writing, modifying, reviewing, refactoring, testing, debugging, and running Vue applications.

## Vue.js code generation instructions

- Prefer Vue 3 and the Composition API with `<script setup>`.
- Use clear component, prop, emit, composable, and state names.
- Define props, emitted events, and composable return values with TypeScript types.
- Keep components focused; extract reusable logic into composables.
- Use `computed` for derived state and avoid mutating props.
- Handle loading, empty, and error states in asynchronous UI.
- Add component tests for user-visible behavior and composable tests for reusable logic.
