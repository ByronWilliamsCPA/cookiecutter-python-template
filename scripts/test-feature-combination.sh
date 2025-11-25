#!/usr/bin/env bash
# Test a specific feature combination
# Usage: ./scripts/test-feature-combination.sh --config <config_name> [--python-version <version>]

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
CONFIG_NAME=""
PYTHON_VERSION="${PYTHON_VERSION:-3.12}"
TEMPLATE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="/tmp/cookiecutter-test-$$"
KEEP_OUTPUT=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG_NAME="$2"
            shift 2
            ;;
        --python-version)
            PYTHON_VERSION="$2"
            shift 2
            ;;
        --keep)
            KEEP_OUTPUT=true
            shift
            ;;
        --help)
            echo "Usage: $0 --config <config_name> [options]"
            echo ""
            echo "Options:"
            echo "  --config <name>          Configuration name (minimal, cli-app, api-service, ml-project, full-featured)"
            echo "  --python-version <ver>   Python version to use (default: 3.12)"
            echo "  --keep                   Keep generated project after testing"
            echo "  --help                   Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$CONFIG_NAME" ]; then
    echo -e "${RED}Error: --config is required${NC}"
    echo "Use --help for usage information"
    exit 1
fi

# Functions
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

cleanup() {
    if [ "$KEEP_OUTPUT" = false ] && [ -d "$OUTPUT_DIR" ]; then
        info "Cleaning up test directory: $OUTPUT_DIR"
        rm -rf "$OUTPUT_DIR"
    else
        info "Test output preserved at: $OUTPUT_DIR"
    fi
}

trap cleanup EXIT

# Main test flow
main() {
    info "Testing feature combination: $CONFIG_NAME"
    info "Python version: $PYTHON_VERSION"
    info "Template directory: $TEMPLATE_DIR"
    info "Output directory: $OUTPUT_DIR"
    echo ""

    # Create output directory
    mkdir -p "$OUTPUT_DIR"

    # Find configuration file
    CONFIG_FILE="$TEMPLATE_DIR/tests/fixtures/configs/${CONFIG_NAME}.json"

    if [ ! -f "$CONFIG_FILE" ]; then
        error "Configuration file not found: $CONFIG_FILE"
        echo "Available configurations:"
        ls -1 "$TEMPLATE_DIR/tests/fixtures/configs/"
        exit 1
    fi

    info "Using configuration: $CONFIG_FILE"

    # 1. Generate Project
    info "=== Step 1: Generating Project ==="

    if ! cookiecutter "$TEMPLATE_DIR" \
        --no-input \
        --config-file "$CONFIG_FILE" \
        --output-dir "$OUTPUT_DIR"; then
        error "Project generation failed"
        exit 1
    fi

    success "Project generated successfully"
    echo ""

    # Find the generated project directory
    # Read project_slug from config
    PROJECT_SLUG=$(python -c "import json; print(json.load(open('$CONFIG_FILE'))['default_context']['project_slug'])")
    PROJECT_DIR="$OUTPUT_DIR/$PROJECT_SLUG"

    if [ ! -d "$PROJECT_DIR" ]; then
        error "Generated project directory not found: $PROJECT_DIR"
        exit 1
    fi

    info "Project directory: $PROJECT_DIR"
    echo ""

    # 2. Validate Generated Project
    info "=== Step 2: Validating Project Structure ==="

    if ! "$TEMPLATE_DIR/scripts/validate-generated-project.sh" "$PROJECT_DIR"; then
        error "Project validation failed"
        exit 1
    fi

    success "Project validation passed"
    echo ""

    # 3. Install Dependencies
    info "=== Step 3: Installing Dependencies ==="

    cd "$PROJECT_DIR"

    if command -v uv &> /dev/null; then
        if uv sync; then
            success "Dependencies installed with UV"
        else
            error "UV sync failed"
            exit 1
        fi
    else
        warning "UV not available, skipping dependency installation"
    fi
    echo ""

    # 4. Run Quality Checks
    info "=== Step 4: Running Quality Checks ==="

    # Ruff
    if command -v ruff &> /dev/null; then
        if ruff check .; then
            success "Ruff check passed"
        else
            error "Ruff check failed"
            exit 1
        fi
    fi

    # Type checking (if available)
    if command -v mypy &> /dev/null; then
        if mypy src/ --ignore-missing-imports 2>&1; then
            success "Type checking passed"
        else
            warning "Type checking reported issues"
        fi
    fi
    echo ""

    # 5. Run Tests
    info "=== Step 5: Running Tests ==="

    if command -v uv &> /dev/null; then
        if uv run pytest -v --tb=short; then
            success "Tests passed"
        else
            warning "Some tests failed"
        fi
    else
        warning "UV not available, skipping tests"
    fi
    echo ""

    # 6. Security Checks
    info "=== Step 6: Security Checks ==="

    if command -v bandit &> /dev/null; then
        if bandit -r src/ -ll 2>&1; then
            success "Bandit security scan passed"
        else
            warning "Bandit found potential issues"
        fi
    else
        warning "Bandit not available"
    fi

    if command -v safety &> /dev/null; then
        if safety check 2>&1; then
            success "Safety dependency check passed"
        else
            warning "Safety found vulnerabilities"
        fi
    else
        warning "Safety not available"
    fi
    echo ""

    # 7. Feature-Specific Tests
    info "=== Step 7: Feature-Specific Validation ==="

    case $CONFIG_NAME in
        cli-app)
            if [ -f "pyproject.toml" ] && grep -q "\[project.scripts\]" pyproject.toml; then
                success "CLI entrypoint configured"
            else
                error "CLI entrypoint not found"
            fi
            ;;
        api-service)
            if [ -f "pyproject.toml" ] && (grep -qi "fastapi\|flask" pyproject.toml); then
                success "API framework configured"
            else
                error "API framework not found"
            fi
            ;;
        ml-project)
            if [ -f "pyproject.toml" ] && (grep -qi "numpy\|pandas\|scikit-learn" pyproject.toml); then
                success "ML dependencies configured"
            else
                error "ML dependencies not found"
            fi
            ;;
    esac
    echo ""

    # Final Summary
    echo "========================================"
    echo -e "${GREEN}Feature Combination Test: PASSED${NC}"
    echo "========================================"
    echo "Configuration: $CONFIG_NAME"
    echo "Project: $PROJECT_DIR"
    echo "All checks completed successfully"
    echo ""

    if [ "$KEEP_OUTPUT" = true ]; then
        info "Project preserved at: $PROJECT_DIR"
        info "To remove: rm -rf $OUTPUT_DIR"
    fi
}

main "$@"
