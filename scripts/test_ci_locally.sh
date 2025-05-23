#!/bin/bash

# Test CI locally - simulates GitHub Actions workflow
set -e

echo "🔧 Setting up local CI test environment..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run from project root."
    exit 1
fi

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🧪 Running unit tests with coverage..."
python -m pytest tests/unit/ \
    --cov=scoring.scoring_v2 \
    --cov-report=term-missing \
    --cov-fail-under=80 \
    -v

echo "🔗 Running integration tests..."
python tests/test_runner.py

echo "🎯 Testing CLI with example data..."
python -m scoring.scoring_v2 tests/data/v2/basic_test.csv

echo "❓ Testing help and version flags..."
python -m scoring.scoring_v2 --help
python -m scoring.scoring_v2 --version

echo "📋 Verifying package imports..."
python -c "from scoring.scoring_v2 import main, compute_scores, load_matrix; print('✅ All imports successful')"

echo ""
echo "🎉 Local CI test completed successfully!"
echo "✅ All tests passed"
echo "✅ Coverage target met (80%+)"
echo "✅ CLI functionality verified"
echo "✅ Package imports working"
