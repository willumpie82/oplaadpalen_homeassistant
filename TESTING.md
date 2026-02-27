# Testing Guide

## Testing Layers

### Layer 1: Local Unit Tests (Always Run)
- **Library unit tests** (`oplaadpalen_py`) - 14 tests, mocked HTTP
- **Code quality** - linting, type checking, formatting
- **Mocked integration tests** - HA objects mocked (if dependencies installed)

### Layer 2: Runtime Integration Tests (Docker)
- **Real Home Assistant instance** running in Docker
- **Real API calls** to oplaadpalen.nl
- **UI testing** - create integration in HA dashboard

---

## Quick Start

### 1. Run Local Tests Only

```bash
./run_all_tests.sh
```

This runs (fast, ~10 seconds):
- ✅ Library unit tests (oplaadpalen_py) - 14 tests
- ✅ Code linting (flake8)
- ✅ Type checking (mypy)
- ✅ Code formatting (black)
- ✅ Mocked integration tests (if HA dependencies available)

### 2. Run Local Tests + Deploy to Docker

```bash
./run_all_tests.sh --docker
```

This runs all local tests, then:
- ✅ Copies integration to Docker container
- ✅ Restarts Home Assistant
- ✅ Ready for manual testing at http://localhost:8123

### 3. Set Up Pre-Commit Hooks (Automatic Testing)

Pre-commit hooks run tests **automatically before each git commit**, preventing bad code from being pushed.

**Install pre-commit:**
```bash
pip install pre-commit
```

**Set up hooks:**
```bash
cd "/Users/willemoldemans/Documents/PROJECTEN/homeassistant hacs"
pre-commit install
```

**Run hooks manually:**
```bash
pre-commit run --all-files
```

**Skip hooks (if needed):**
```bash
git commit --no-verify
```

---

## Docker Runtime Testing

### Prerequisites
Docker container `ha-test` must be running:
```bash
docker start ha-test  # Start if stopped
```

### Option 1: Automated Deployment
```bash
./run_all_tests.sh --docker
```

This:
1. Runs all local tests
2. Copies integration to Docker
3. Restarts Home Assistant
4. You can then test at http://localhost:8123

### Option 2: Manual Deployment
```bash
# Copy integration
docker cp ./custom_components/oplaadpalen ha-test:/config/custom_components/

# Restart Home Assistant
docker restart ha-test && sleep 20
```

### Manual Testing in HA UI
1. Visit http://localhost:8123
2. Settings → Devices & Services → Create Integration
3. Search for "Oplaadpalen"
4. Enter:
   - **Address**: Your address (e.g., "Dam 1, Amsterdam")
   - **Radius**: 5 km
   - **Update Interval**: 30 minutes
5. Check logs for errors: Settings → System → Logs
6. View sensors: Settings → Devices & Services → Devices (filter by "Oplaadpalen")

---

## Individual Test Commands

### Library Tests Only
```bash
cd oplaadpalen_py
python3 -m pytest test_client.py -v --tb=short
cd ..
```

### Library Tests with Coverage
```bash
cd oplaadpalen_py
python3 -m pytest test_client.py -v --cov=oplaadpalen_py --cov-report=html
cd ..
# Open htmlcov/index.html to see coverage report
```

### Code Linting
```bash
python3 -m flake8 oplaadpalen_py/ custom_components/ --max-line-length=100
```

### Code Formatting (Auto-fix)
```bash
python3 -m black oplaadpalen_py/ custom_components/ --line-length=100
```

### Type Checking
```bash
python3 -m mypy oplaadpalen_py/ custom_components/ --ignore-missing-imports
```

### Mocked Integration Tests (requires Home Assistant dependencies)
```bash
# Tests HA integration logic with mocked HA objects
cd tests
python3 -m pytest -v --tb=short
cd ..
```

⚠️ **Note:** These don't test actual HA runtime. Use Docker tests for that.

---

## Development Workflow

1. **Make code changes**
2. **Run tests locally:**
   ```bash
   ./run_all_tests.sh
   ```
3. **Auto-format code:**
   ```bash
   python3 -m black oplaadpalen_py/ custom_components/
   ```
4. **Commit (will run pre-commit hooks automatically):**
   ```bash
   git add .
   git commit -m "Your message"
   ```
5. **Push to GitHub:**
   ```bash
   git push
   ```

---

## Advanced Testing

### Generate Coverage Report
```bash
cd oplaadpalen_py
python3 -m pytest test_client.py --cov=oplaadpalen_py --cov-report=html
open htmlcov/index.html
cd ..
```

### Install All Testing Tools
```bash
pip install pytest pytest-asyncio pytest-cov flake8 mypy black pre-commit
```

---

## Troubleshooting

**Local tests pass but integration doesn't load in Docker?**
- Check Docker logs: `docker logs ha-test | tail -100`
- Look for import errors in "Oplaadpalen" integration startup
- Verify oplaadpalen-py is installed: `docker exec ha-test pip list | grep oplaadpalen`

**Pre-commit hooks won't run?**
```bash
pre-commit install --install-hooks
pre-commit run --all-files
```

**Docker container not running?**
```bash
# Start container
docker start ha-test

# Or check if it exists
docker ps -a | grep ha-test
```

**Tests failing but want to commit anyway?**
```bash
git commit --no-verify
```

**Black reformatted files?**
- Just `git add` the reformatted files and commit again

**Want to disable a specific pre-commit check?**
- Edit `.pre-commit-config.yaml` and comment out or remove the hook
- Re-install: `pre-commit install`

---

## Test Results Summary

### What Each Layer Tests

| Test Layer | What It Tests | Time | Dependencies |
|---|---|---|---|
| **Library Unit Tests** | oplaadpalen_py API client with mocked HTTP | ~2s | pytest, pytest-asyncio |
| **Code Quality** | Linting, type checking, formatting | ~3s | flake8, mypy, black |
| **Mocked Integration Tests** | HA integration logic with mocked HA objects | ~3s | pytest, Home Assistant package (optional) |
| **Docker Runtime Tests** | Real HA instance, real API calls, UI testing | ~30s | Docker, running container |

### Recommended Workflow

1. **During development:** Run `./run_all_tests.sh` frequently (10 seconds)
2. **Before committing:** Pre-commit hooks run automatically (5 seconds)
3. **Before deploying:** Run `./run_all_tests.sh --docker` for full integration test (35 seconds)
4. **Final validation:** Manual test in HA UI at http://localhost:8123
