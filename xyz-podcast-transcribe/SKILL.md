---
name: xyz-podcast-transcribe
description: Download and transcribe Xiaoyuzhou.fm podcast episodes to SRT subtitles and TXT transcripts. Use when a user provides a Xiaoyuzhoufm episode URL and wants full transcript text with timestamps, or needs to convert podcast audio into SRT/TXT files. Orchestrates downloading episodes using xyz-podcast-downloader, then transcribing using audio-transcribe. Supports custom output directories, multiple Whisper model sizes, language specification, and VAD filtering control.
---

# Xiaoyuzhou.fm Podcast Transcription

Download and transcribe Xiaoyuzhou.fm podcast episodes to SRT subtitles and TXT transcripts.

This skill orchestrates two other skills:
- **xyz-podcast-downloader** - Downloads podcast episodes
- **audio-transcribe** - Transcribes audio to text

## Quick Start

```bash
scripts/transcribe.py https://www.xiaoyuzhoufm.com/episode/123456
```

This will:
1. Download the audio using xyz-podcast-downloader
2. Transcribe with audio-transcribe (tiny model, auto-detect language)
3. Save `{title}.srt` and `{title}.txt` to `~/Downloads/music/xyz/{channel_name}/`

## Command-Line Options

### Positional Arguments

- `url` - Xiaoyuzhou.fm episode URL (required)

### Optional Arguments

- `--output-dir PATH` - Write outputs to specific directory (default: `~/Downloads/music/xyz/{channel_name}/`)
- `--model SIZE` - Whisper model size: `tiny` (default), `base`, `small`, `medium`, `large`, `large-v1`, `large-v2`, `large-v3`
- `--language CODE` - Force language code (e.g., `zh`, `en`) or allow auto-detect
- `--force-download` - Re-download audio even if it exists locally
- `--no-vad` - Disable VAD (Voice Activity Detection) filtering
- `--device {auto,cpu,cuda}` - Device for transcription (default: `auto`)

## Common Workflows

### Higher accuracy transcription

```bash
scripts/transcribe.py https://www.xiaoyuzhoufm.com/episode/123456 --model small
```

### Force Chinese language

```bash
scripts/transcribe.py https://www.xiaoyuzhoufm.com/episode/123456 --language zh
```

### Custom output directory

```bash
scripts/transcribe.py https://www.xiaoyuzhoufm.com/episode/123456 --output-dir ~/transcripts
```

### Re-download and re-transcribe

```bash
scripts/transcribe.py https://www.xiaoyuzhoufm.com/episode/123456 --force-download --model base
```

## Output Files

Generates two files:

1. **`{title}.srt`** - SubRip subtitle file
   - Format: `sequence_number`, `start_time --> end_time`, `subtitle_text`

2. **`{title}.txt`** - Plain text transcript with timestamps
   - Format: `[HH:MM:SS,mmm] transcript_text`

## Dependencies

Requires these skills to be installed:
- **xyz-podcast-downloader** - Downloads podcast episodes
- **audio-transcribe** - Transcribes audio to text

Note: For transcribing local audio files (not from Xiaoyuzhou.fm), use the audio-transcribe skill directly.

## How It Works

1. **Download**: Calls xyz-podcast-downloader to fetch episode audio and metadata
2. **Transcribe**: Calls audio-transcribe to generate SRT and TXT files
3. **Output**: Saves files to the specified directory

## Important Notes

- **Private episodes**: Episodes that are private or require login cannot be accessed
- **No native transcripts**: Xiaoyuzhou does not expose public transcripts; this uses speech-to-text
- **Model selection**: `tiny` is fastest but least accurate; `small` or `base` recommended for production
- **Local audio**: For transcribing local audio files, use audio-transcribe directly instead of this skill
