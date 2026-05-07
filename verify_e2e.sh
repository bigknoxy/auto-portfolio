#!/bin/bash
set -e

echo "=== E2E Verification ==="

cd /Users/Joshua.Knox/projects/auto-portfolio
source .venv/bin/activate

echo ""
echo "1. Running unit tests..."
python -m pytest tests/unit/ -q

echo ""
echo "2. Running integration tests..."
python -m pytest tests/integration/ -q

echo ""
echo "3. Testing from-github command..."
rm -rf test-portfolio
python -m auto_portfolio_cli.auto_portfolio from-github \
  --url https://github.com/example \
  --output-dir test-portfolio \
  --no-git

echo ""
echo "4. Verifying generated files..."
test -f test-portfolio/src/data/profile.json || { echo "ERROR: profile.json missing"; exit 1; }
test -f test-portfolio/src/data/projects.json || { echo "ERROR: projects.json missing"; exit 1; }

echo ""
echo "5. Verifying profile content..."
python -c "
import json
with open('test-portfolio/src/data/profile.json') as f:
    p = json.load(f)
    assert 'name' in p, 'name missing'
    assert 'bio' in p, 'bio missing'
print('Profile OK:', p['name'])
"

echo ""
echo "6. Verifying project count > 0..."
python -c "
import json
with open('test-portfolio/src/data/projects.json') as f:
    data = json.load(f)
    projects = data.get('projects', [])
    assert len(projects) > 0, 'No projects generated'
print(f'Projects: {len(projects)}')
"

echo ""
echo "7. Running ruff check..."
ruff check .

echo ""
echo "8. Cleanup..."
rm -rf test-portfolio

echo ""
echo "=== All E2E tests passed ==="