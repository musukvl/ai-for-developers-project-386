# Instructions

## Orientation

Read `README.md` first. It is the default map of project layout, stack, how to run, and how to test. Do not assume the tree from memory.

## Spec is the source of truth

Implement and change behaviour against `spec/`, not against neighbouring code:

- `spec/requirements.md` — functional requirements
- `spec/api.tsp` — HTTP API contract (`spec/api.md` is the prose companion; keep it in sync)
- `spec/ui.md` — routes, screens, and presentation
- `spec/implementation.md` — architecture and module layout
- `spec/use_cases/` — user scenarios

If the code, README, or another spec file contradicts `spec/`, stop and report the contradiction before implementing a workaround. Prefer aligning the implementation to the spec unless the user explicitly asks to change the spec.

Keep README.md up to date.

## Workspace

- Place reports in the `__reports` directory
- Place temporary scripts in the `__scripts` directory
