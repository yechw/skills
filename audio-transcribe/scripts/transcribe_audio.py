#!/usr/bin/env python3
"""
Transcribe local audio files to SRT and TXT using faster-whisper.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List


def parse_args():
    parser = argparse.ArgumentParser(
        description="Transcribe local audio files to SRT and TXT"
    )
    parser.add_argument(
        "audio_path",
        type=str,
        help="Path to local audio file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory (default: same as audio file)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="tiny",
        choices=["tiny", "base", "small", "medium", "large", "large-v1", "large-v2", "large-v3"],
        help="Whisper model size (default: tiny; use base or small for higher accuracy)"
    )
    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="Force language code (e.g., 'zh', 'en') or allow auto-detect"
    )
    parser.add_argument(
        "--no-vad",
        action="store_true",
        help="Disable VAD filtering if segments are too aggressive"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="Device to use for transcription (default: auto)"
    )

    return parser.parse_args()


def format_timestamp(seconds: float) -> str:
    """Format timestamp as SRT timecode (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def check_onnxruntime():
    """Check if onnxruntime is available for VAD."""
    try:
        import onnxruntime
        return True
    except ImportError:
        return False


def transcribe_audio(
    audio_path: str,
    model_size: str = "tiny",
    language: Optional[str] = None,
    use_vad: bool = True,
    device: str = "auto"
):
    """Transcribe audio using faster-whisper."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("❌ Error: faster-whisper not installed")
        print("   Install with: pip install faster-whisper")
        sys.exit(1)

    # Check VAD availability
    if use_vad and not check_onnxruntime():
        print("⚠️  Warning: onnxruntime not installed. VAD filtering will be disabled.")
        print("   To enable VAD, install onnxruntime:")
        print("   - For Python 3.13 and earlier: pip install 'onnxruntime<2,>=1.14'")
        print("   - For Python 3.14+: VAD not yet supported, use --no-vad flag")
        use_vad = False

    # Determine device
    if device == "auto":
        try:
            import torch
            device_type = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device_type = "cpu"
    else:
        device_type = device

    compute_type = "float16" if device_type == "cuda" else "int8"

    print(f"🎙️  Loading Whisper model '{model_size}' on {device_type}...")

    model = WhisperModel(
        model_size,
        device=device_type,
        compute_type=compute_type
    )

    print(f"📝 Transcribing {audio_path}...")

    segments, info = model.transcribe(
        audio_path,
        language=language,
        vad_filter=use_vad,
        word_timestamps=True
    )

    print(f"✅ Detected language: {info.language} (probability: {info.language_probability:.2f})")

    return list(segments), info


def write_srt(segments, output_path: Path):
    """Write segments to SRT file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, 1):
            start_time = format_timestamp(segment.start)
            end_time = format_timestamp(segment.end)

            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{segment.text.strip()}\n\n")

    print(f"✅ SRT saved to: {output_path}")


def write_txt(segments, output_path: Path):
    """Write segments to TXT file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for segment in segments:
            timestamp = format_timestamp(segment.start)
            f.write(f"[{timestamp}] {segment.text.strip()}\n")

    print(f"✅ TXT saved to: {output_path}")


def main():
    args = parse_args()

    # Validate audio path
    audio_path = Path(args.audio_path)
    if not audio_path.exists():
        print(f"❌ Error: Audio file not found: {args.audio_path}")
        sys.exit(1)

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = audio_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)

    # Output filenames
    base_name = audio_path.stem
    srt_path = output_dir / f"{base_name}.srt"
    txt_path = output_dir / f"{base_name}.txt"

    # Transcribe
    segments, info = transcribe_audio(
        str(audio_path),
        model_size=args.model,
        language=args.language,
        use_vad=not args.no_vad,
        device=args.device
    )

    # Write outputs
    write_srt(segments, srt_path)
    write_txt(segments, txt_path)

    print(f"\n🎉 Transcription complete!")
    print(f"   Output directory: {output_dir}")
    print(f"   Segments: {len(segments)}")


if __name__ == "__main__":
    main()
