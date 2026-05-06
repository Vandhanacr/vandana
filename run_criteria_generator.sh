#!/bin/bash

# ADO Acceptance Criteria Generator - Setup & Run Script
# This script sets up the environment and runs the criteria generator

set -e

echo "🚀 Azure DevOps Acceptance Criteria Generator"
echo "=============================================="

# Check if work item ID is provided
if [ -z "$1" ]; then
    echo "❌ Usage: bash run_criteria_generator.sh <WORK_ITEM_ID>"
    echo "   Example: bash run_criteria_generator.sh 2516289"
    exit 1
fi

WORK_ITEM_ID=$1

# Check required environment variables
echo "📋 Checking environment variables..."

required_vars=("ADO_ORGANIZATION" "ADO_PROJECT" "ADO_PAT" "COPILOT_API_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "📚 Setup Instructions:"
    echo "   export ADO_ORGANIZATION=kantarware"
    echo "   export ADO_PROJECT=KM-Ecosystem"
    echo "   export ADO_PAT=<your_azure_devops_pat>"
    echo "   export COPILOT_API_KEY=<your_api_key>"
    exit 1
fi

echo "✓ All required variables set"

# Check Python installation
echo "🐍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q anthropic azure-devops azure-identity 2>/dev/null || {
    echo "   Attempting alternate installation method..."
    pip install anthropic azure-devops azure-identity
}
echo "✓ Dependencies installed"

# Create scripts directory if it doesn't exist
mkdir -p scripts

# Run the generator
echo ""
echo "🤖 Running acceptance criteria generator..."
echo "   Work Item ID: $WORK_ITEM_ID"
echo "   Organization: $ADO_ORGANIZATION"
echo "   Project: $ADO_PROJECT"
echo ""

python3 scripts/generate_acceptance_criteria.py "$WORK_ITEM_ID"

exit $?
