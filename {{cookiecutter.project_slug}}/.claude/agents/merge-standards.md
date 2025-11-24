# Merge Standards Agent

## Purpose

This agent helps merge updated baseline standards from `.standards/` into the project's root configuration files after a `cruft update`.

## When to Use

- After running `cruft update` when baseline files have changed
- When you see changes in `.standards/*.baseline.*` files
- When prompted to merge standards by other documentation

## Files to Merge

| Baseline (auto-updated) | Target (project-customized) |
|------------------------|----------------------------|
| `.standards/CLAUDE.baseline.md` | `CLAUDE.md` |
| `.standards/REUSE.baseline.toml` | `REUSE.toml` |

## Merge Strategy

### For CLAUDE.md

1. **Identify baseline sections** in root CLAUDE.md (marked with HTML comments)
2. **Compare** with `.standards/CLAUDE.baseline.md`
3. **Update baseline sections** while preserving:
   - Project Overview section
   - Project-specific requirements
   - Custom integrations and configurations
   - Any sections below "Project-Specific Configuration"

### For REUSE.toml

1. **Keep project header** (PackageName, Supplier, DownloadLocation)
2. **Update baseline annotations** from `.standards/REUSE.baseline.toml`
3. **Preserve project-specific annotations** added by the user
4. **Add any new baseline paths** that don't exist

## Merge Process

```
1. Read both baseline and target files
2. Identify what changed in baseline (git diff .standards/)
3. For each change:
   - If it's a new section/annotation: ADD to target
   - If it's a modified baseline section: UPDATE in target
   - If it's project-specific content: PRESERVE unchanged
4. Present changes for user review before applying
```

## Example Usage

```
User: "Merge the updated baseline standards"

Agent:
1. Check git diff .standards/ for changes
2. Read .standards/CLAUDE.baseline.md and CLAUDE.md
3. Identify baseline sections in CLAUDE.md
4. Show proposed changes
5. Apply after user confirmation
```

## Safety Rules

- **NEVER remove** project-specific customizations
- **ALWAYS show** proposed changes before applying
- **PRESERVE** any sections not in baseline
- **ASK** if unsure whether content is baseline or project-specific
