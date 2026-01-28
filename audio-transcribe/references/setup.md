# Audio Transcribe Setup Guide

Detailed setup instructions for audio-transcribe dependencies.

## Python Version Compatibility

| Python Version | VAD Support | Notes |
|----------------|-------------|-------|
| 3.14+ | ❌ No | onnxruntime not yet compatible; use `--no-vad` flag |
| 3.13 and earlier | ✅ Yes | Full VAD support after installing onnxruntime |

## Installation Methods

### Method 1: Virtual Environment (Recommended)

Best for isolation and avoiding system package conflicts.

```bash
# Create virtual environment in the skill directory
cd /path/to/audio-transcribe
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install core dependencies
pip install faster-whisper torch

# Install VAD support (Python 3.13 and earlier only)
pip install 'onnxruntime<2,>=1.14'
```

### Method 2: User Directory Installation

Install without virtual environment (may conflict with system packages).

```bash
# Install core dependencies
pip install --user faster-whisper torch

# Install VAD support (Python 3.13 and earlier only)
pip install --user 'onnxruntime<2,>=1.14'
```

### Method 3: System-Wide Installation

Not recommended on macOS with externally-managed Python.

```bash
# May require --break-system-packages flag (use with caution)
pip install --break-system-packages faster-whisper torch
pip install --break-system-packages 'onnxruntime<2,>=1.14'
```

## Dependency Versions

Tested with:
- `faster-whisper>=1.0.0`
- `torch>=2.0.0`
- `onnxruntime>=1.14,<2` (VAD only, Python 3.13 and earlier)

## Troubleshooting

### Error: "externally-managed-environment"

**Cause**: Python 3.11+ on some systems prevents system-wide pip installs.

**Solution**: Use a virtual environment (Method 1) or `--user` flag (Method 2).

### Error: "onnxruntime not installed"

**Cause**: VAD filtering requires onnxruntime package.

**Solutions**:
1. Install onnxruntime (Python 3.13 and earlier): `pip install 'onnxruntime<2,>=1.14'`
2. Disable VAD: Add `--no-vad` flag to transcription command
3. Downgrade to Python 3.13 if VAD is critical

### Error: "no module named 'faster-whisper'"

**Cause**: faster-whisper not installed or wrong Python environment.

**Solutions**:
1. Activate virtual environment: `source .venv/bin/activate`
2. Install faster-whisper: `pip install faster-whisper`
3. Check which Python is being used: `which python`

### VAD cuts off speech segments

**Cause**: Aggressive VAD filtering removes quiet speech.

**Solutions**:
1. Disable VAD: Add `--no-vad` flag
2. Use larger model for better detection: `--model small` or `--model base`

## GPU Acceleration (Optional)

For faster transcription on NVIDIA GPUs:

```bash
# Install PyTorch with CUDA support
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Transcription will automatically use GPU when available
scripts/transcribe_audio.py audio.mp3 --device cuda
```

## Verifying Installation

Test your setup:

```bash
# Check if dependencies are installed
python -c "import faster_whisper; print('faster-whisper:', faster_whisper.__version__)"
python -c "import torch; print('torch:', torch.__version__)"

# Check VAD support (Python 3.13 and earlier)
python -c "import onnxruntime; print('onnxruntime:', onnxruntime.__version__)"

# Run a test transcription
scripts/transcribe_audio.py /path/to/short_audio.mp3 --no-vad
```
