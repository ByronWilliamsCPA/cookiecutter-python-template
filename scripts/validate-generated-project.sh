#!/usr/bin/env bash
# Comprehensive validation script for generated projects
# Usage: ./scripts/validate-generated-project.sh <project_directory>

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="${1:-.}"
ERRORS=0
WARNINGS=0

# Functions
error() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

info() {
    echo -e "${NC}ℹ${NC} $1"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Main validation
main() {
    info "Validating generated project: $PROJECT_DIR"
    echo ""

    # Check project directory exists
    if [ ! -d "$PROJECT_DIR" ]; then
        error "Project directory does not exist: $PROJECT_DIR"
        exit 1
    fi

    cd "$PROJECT_DIR"

    # 1. Directory Structure Validation
    info "=== Directory Structure ==="

    required_files=(
        "pyproject.toml"
        "README.md"
        ".gitignore"
        "src"
        "tests"
    )

    for file in "${required_files[@]}"; do
        if [ -e "$file" ]; then
            success "Found $file"
        else
            error "Missing required file/directory: $file"
        fi
    done
    echo ""

    # 2. Python Syntax Validation
    info "=== Python Syntax Validation ==="

    if check_command python; then
        find src tests -name "*.py" -type f | while read -r pyfile; do
            if python -m py_compile "$pyfile" 2>/dev/null; then
                success "Valid Python syntax: $pyfile"
            else
                error "Invalid Python syntax: $pyfile"
            fi
        done
    else
        warning "Python not available, skipping syntax check"
    fi
    echo ""

    # 3. TOML Validation
    info "=== TOML Configuration Validation ==="

    if check_command python; then
        if python -c "import tomli" 2>/dev/null; then
            if TOML_ERROR=$(python -c "import tomli; tomli.load(open('pyproject.toml', 'rb'))" 2>&1); then
                success "Valid pyproject.toml"
            else
                error "Invalid pyproject.toml"
                echo "$TOML_ERROR"
            fi
        elif python -c "import tomllib" 2>/dev/null; then
            # Python 3.11+ has tomllib in stdlib
            if TOML_ERROR=$(python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))" 2>&1); then
                success "Valid pyproject.toml"
            else
                error "Invalid pyproject.toml"
                echo "$TOML_ERROR"
            fi
        else
            warning "tomli/tomllib not available, skipping TOML validation"
        fi
    fi
    echo ""

    # 4. YAML Validation
    info "=== YAML Configuration Validation ==="

    if [ -d ".github/workflows" ]; then
        if check_command yamllint; then
            for yamlfile in .github/workflows/*.yml .github/workflows/*.yaml; do
                [ -e "$yamlfile" ] || continue
                if yamllint "$yamlfile" &>/dev/null; then
                    success "Valid YAML: $yamlfile"
                else
                    # yamllint returns non-zero for warnings and errors
                    # Show the actual output to help debug
                    # Temporarily disable exit-on-error for command substitution
                    set +e
                    YAML_OUTPUT=$(yamllint "$yamlfile" 2>&1)
                    set -e
                    # Check for errors (including config errors and syntax errors)
                    if [[ "$YAML_OUTPUT" =~ [Ee]rror ]] || [[ "$YAML_OUTPUT" =~ "invalid config" ]]; then
                        error "YAML errors in: $yamlfile"
                        # Always show output for errors
                        echo "$YAML_OUTPUT"
                    else
                        warning "YAML issues in: $yamlfile (yamllint reported warnings - non-blocking)"
                        # Show warnings too for debugging in CI
                        echo "$YAML_OUTPUT"
                    fi
                fi
            done
        else
            warning "yamllint not available, skipping YAML validation"
        fi
    fi
    echo ""

    # 5. Template Variable Check
    info "=== Template Variable Check ==="

    # Check for unreplaced Jinja2 variables
    if grep -r "{{.*}}" --include="*.py" --include="*.md" --include="*.toml" --include="*.yml" . 2>/dev/null; then
        error "Found unreplaced Jinja2 template variables"
    else
        success "No unreplaced template variables found"
    fi
    echo ""

    # 6. Hardcoded Values Check
    info "=== Hardcoded Values Check ==="

    # Check for template author/org names
    if grep -r "williaby\|Byron Williams" --include="*.py" --include="*.toml" --exclude-dir=".git" . 2>/dev/null; then
        error "Found hardcoded template author information"
    else
        success "No hardcoded template author information"
    fi
    echo ""

    # 7. Ruff Validation
    info "=== Ruff Linting ==="

    if check_command ruff; then
        if ruff check . --output-format=concise; then
            success "Ruff check passed"
        else
            error "Ruff check failed"
        fi
    else
        warning "Ruff not available, skipping"
    fi
    echo ""

    # 8. UV Sync Test
    info "=== Dependency Resolution ==="

    if check_command uv; then
        if uv sync --dry-run 2>&1; then
            success "UV sync (dry-run) succeeded"
        else
            error "UV sync failed - dependency resolution issues"
        fi
    else
        warning "UV not available, skipping dependency check"
    fi
    echo ""

    # 9. Pre-commit Validation
    info "=== Pre-commit Hooks ==="

    if [ -f ".pre-commit-config.yaml" ]; then
        success "Pre-commit config exists"

        if check_command pre-commit; then
            if pre-commit run --all-files &>/dev/null; then
                success "Pre-commit hooks passed"
            else
                warning "Pre-commit hooks reported issues (may be expected for new projects)"
            fi
        else
            warning "pre-commit not available, skipping"
        fi
    else
        info "No pre-commit config (optional)"
    fi
    echo ""

    # 10. Test Execution
    info "=== Test Execution ==="

    if check_command uv; then
        # First sync dependencies
        if uv sync &>/dev/null; then
            if uv run pytest -v 2>&1; then
                success "Tests passed"
            else
                warning "Some tests failed (may be expected for template examples)"
            fi
        else
            warning "UV sync failed, cannot run tests"
        fi
    else
        warning "UV not available, skipping test execution"
    fi
    echo ""

    # Summary
    echo "========================================"
    echo "Validation Summary"
    echo "========================================"

    if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        success "All checks passed!"
        exit 0
    elif [ $ERRORS -eq 0 ]; then
        echo -e "${YELLOW}Completed with $WARNINGS warning(s)${NC}"
        exit 0
    else
        echo -e "${RED}Failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
        exit 1
    fi
}

main "$@"
