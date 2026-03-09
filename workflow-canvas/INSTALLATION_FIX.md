# Installation Fix for Python 3.14

## Problem

The original `requirements.txt` used `pydantic==2.5.0` which includes `pydantic-core==2.14.1`. This version doesn't support Python 3.14 and fails to build with the error:

```
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
```

## Solution

Updated `requirements.txt` to use newer versions that support Python 3.14:

- `fastapi>=0.115.0` (was 0.104.1)
- `uvicorn[standard]>=0.32.0` (was 0.24.0)
- `pydantic>=2.10.0` (was 2.5.0) - This brings `pydantic-core>=2.41.5` which supports Python 3.14
- `aiohttp>=3.11.0` (was 3.9.1)
- `python-multipart>=0.0.12` (was 0.0.6)

## Installation

```bash
cd workflow-canvas
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r requirements.txt
```

## Verification

All packages installed successfully:
- ✅ fastapi 0.128.0
- ✅ uvicorn 0.40.0
- ✅ pydantic 2.12.5 (with pydantic-core 2.41.5)
- ✅ aiohttp 3.13.3
- ✅ python-multipart 0.0.21

The system is now ready to run!
