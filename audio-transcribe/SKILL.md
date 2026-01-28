---
name: audio-transcribe
description: Transcribe local audio files to SRT subtitles and TXT transcripts with timestamps using faster-whisper. Use when Claude needs to convert local audio files (MP3, M4A, WAV, etc.) into text transcripts with or without timestamps, generate subtitle files from audio, or perform speech-to-text transcription. Supports multiple Whisper model sizes for accuracy/speed tradeoffs, language specification, VAD filtering, and custom output directories.
---

# Local Audio Transcription

Transcribe local audio files to SRT subtitles and TXT transcripts using faster-whisper speech-to-text.

## Quick Start

Transcribe an audio file:

```bash
scripts/transcribe_audio.py /path/to/audio.mp3
```

This generates `audio.srt` and `audio.txt` in the same directory as the audio file.

**Note**: If you get an onnxruntime error or are using Python 3.14+, use:

```bash
scripts/transcribe_audio.py /path/to/audio.mp3 --no-vad
```

## Command-Line Options

### Positional Arguments

- `audio_path` - Path to local audio file

### Optional Arguments

- `--output-dir PATH` - Output directory (default: same as audio file)
- `--model SIZE` - Whisper model size: `tiny` (default), `base`, `small`, `medium`, `large`, `large-v1`, `large-v2`, `large-v3`
- `--language CODE` - Force language code (e.g., `zh`, `en`) or allow auto-detect
- `--no-vad` - Disable VAD (Voice Activity Detection) filtering
- `--device {auto,cpu,cuda}` - Device for transcription (default: `auto`)

## Common Workflows

### Higher accuracy transcription

```bash
scripts/transcribe_audio.py episode.m4a --model small
```

### Force Chinese language

```bash
scripts/transcribe_audio.py interview.mp3 --language zh
```

### Custom output directory

```bash
scripts/transcribe_audio.py recording.wav --output-dir ~/Documents/transcripts
```

### Disable VAD for quiet audio

```bash
scripts/transcribe_audio.py quiet_podcast.mp3 --no-vad
```

### Use GPU for faster processing

```bash
scripts/transcribe_audio.py long_audio.mp3 --device cuda --model base
```

## Output Files

Generates two files:

1. **`{basename}.srt`** - SubRip subtitle file
   - Format: `sequence_number`, `start_time --> end_time`, `subtitle_text`
   - Compatible with video players and subtitle editors

2. **`{basename}.txt`** - Plain text transcript with timestamps
   - Format: `[HH:MM:SS,mmm] transcript_text`
   - Human-readable with embedded timestamps

## Model Selection

Trade off between speed and accuracy:

| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| tiny | ⚡️ Fastest | ✗ Lowest | Quick drafts, testing |
| base | 🚀 Fast | ✓ Good | Everyday use |
| small | ⏱️ Medium | ✓✓ Better | Production quality |
| medium | 🐢 Slow | ✓✓✓ High | Important content |
| large | 🐌 Slowest | ✓✓✓✗ Best | Critical accuracy needed |

## Dependencies

Requires:
- `faster-whisper` - Whisper speech-to-text implementation
- `torch` - For device detection (optional, for GPU/CUDA)
- `onnxruntime` - For VAD filtering (optional, Python 3.13 and earlier only)

### Setup

**Option 1: Virtual environment (recommended)**

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install faster-whisper torch

# For VAD support (Python 3.13 and earlier only)
pip install 'onnxruntime<2,>=1.14'
```

**Option 2: System-wide installation**

```bash
pip install --user faster-whisper torch
pip install --user 'onnxruntime<2,>=1.14'  # Python 3.13 and earlier only
```

**For detailed setup instructions and troubleshooting**, see [setup.md](references/setup.md).

### Important: Python Version Compatibility

- **Python 3.14+**: VAD filtering is not yet supported (onnxruntime incompatible). Use `--no-vad` flag.
- **Python 3.13 and earlier**: Full VAD support available after installing onnxruntime.

## How It Works

1. Load Whisper model with specified size and device
2. Transcribe audio with language detection and VAD filtering
3. Generate SRT file with subtitle timestamps
4. Generate TXT file with readable transcript

## Important Notes

- **Audio formats**: Supports all formats accepted by ffmpeg (MP3, M4A, WAV, FLAC, etc.)
- **Language detection**: Auto-detection works well in most cases; use `--language` for better accuracy
- **VAD filtering**: Removes silence segments by default when onnxruntime is installed
  - Automatically disabled if onnxruntime is not available
  - Use `--no-vad` to explicitly disable (recommended for Python 3.14+)
- **GPU support**: Automatically uses CUDA if available; install PyTorch with CUDA support for GPU acceleration
- **Python 3.14+ compatibility**: VAD filtering not supported; use `--no-vad` flag or downgrade to Python 3.13 for VAD support
