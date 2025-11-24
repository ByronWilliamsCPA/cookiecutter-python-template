# Standards Baseline Directory

This directory contains **baseline versions** of files that require project-specific customization.

## How It Works

1. **Cruft updates this folder** - When you run `cruft update`, files in `.standards/` are updated automatically
2. **You customize root files** - The actual config files at root level contain your project customizations
3. **Merge when needed** - When baselines change, use the merge agent to integrate updates

## Files in This Directory

| Baseline File | Root File | Purpose |
|---------------|-----------|---------|
| `CLAUDE.baseline.md` | `CLAUDE.md` | Development standards and guidelines |
| `REUSE.baseline.toml` | `REUSE.toml` | SPDX licensing annotations |

## Merging Updates

After running `cruft update`, check if baselines changed:

```bash
# Check for changes in .standards/
git diff .standards/

# If changes exist, merge them:
# Option 1: Ask Claude
"Merge the updated baseline standards into my project files"

# Option 2: Use the merge command
/merge-standards
```

## Workflow

```
┌─────────────────┐     cruft update     ┌──────────────────┐
│   Template      │ ──────────────────► │  .standards/     │
│   Repository    │                      │  (baselines)     │
└─────────────────┘                      └────────┬─────────┘
                                                  │
                                                  │ merge (manual/agent)
                                                  ▼
                                         ┌──────────────────┐
                                         │  Root files      │
                                         │  (customized)    │
                                         └──────────────────┘
```

## Important Notes

- **Never edit files in `.standards/`** - They will be overwritten by cruft
- **Root files are yours** - Customize them freely, cruft won't touch them
- **Review baseline changes** - Before merging, review what changed in the template
- **Keep customizations** - The merge agent preserves your project-specific content

---

*Last updated: {% now 'utc', '%Y-%m-%d' %}*
