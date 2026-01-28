#!/usr/bin/env python3
"""
Orchestrates downloading Xiaoyuzhou.fm podcasts and transcribing them.
Uses xyz-podcast-downloader and audio-transcribe skills.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download and transcribe Xiaoyuzhou.fm podcast episodes"
    )
    parser.add_argument(
        "url",
        help="Xiaoyuzhou.fm episode URL"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Write outputs to a specific directory (default: ~/Downloads/music/xyz/{channel_name})"
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
        help="Force a language code (e.g., 'zh', 'en') or allow auto-detect"
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Re-download the audio even if it exists"
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


def find_skill_script(skill_name: str, script_name: str) -> Optional[Path]:
    """Find a script from another skill."""
    possible_paths = [
        Path.home() / ".claude" / "skills" / skill_name / "scripts" / script_name,
        Path(f"/Users/changweiye/.claude/skills/{skill_name}/scripts/{script_name}"),
    ]

    for path in possible_paths:
        if path.exists():
            return path

    return None


def download_episode(url: str, force_download: bool = False) -> dict:
    """Download episode using xyz-podcast-downloader."""
    downloader_path = find_skill_script("xyz-podcast-downloader", "download_episode.py")

    if not downloader_path:
        print("❌ Error: xyz-podcast-downloader skill not found")
        print("Please ensure xyz-podcast-downloader is installed in your skills directory")
        sys.exit(1)

    # Import the download module directly to get episode info
    import importlib.util
    spec = importlib.util.spec_from_file_location("download_episode", str(downloader_path))
    download_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(download_module)

    # Extract episode info first
    try:
        channel_name, episode_title, audio_url = download_module.extract_episode_info(url)
    except Exception as e:
        print(f"❌ Error extracting episode info: {e}")
        sys.exit(1)

    # Determine output path
    default_output_dir = Path.home() / "Downloads" / "music" / "xyz" / channel_name
    default_output_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize filename
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', episode_title)
    audio_path = default_output_dir / f"{safe_title}.m4a"

    # Check if already exists
    if audio_path.exists() and not force_download:
        print(f"✅ Audio already exists: {audio_path}")
    else:
        # Build download command
        cmd = [
            sys.executable,
            str(downloader_path),
            url,
            "-o", str(default_output_dir),
            "-f", safe_title
        ]

        print(f"📥 Downloading episode from {url}...")
        print(f"   Title: {episode_title}")
        print(f"   Channel: {channel_name}")

        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Downloaded to: {audio_path}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error downloading episode")
            sys.exit(1)

    return {
        "audio_path": str(audio_path),
        "title": safe_title,
        "channel_name": channel_name,
        "original_title": episode_title
    }


def transcribe_audio(
    audio_path: str,
    output_dir: Path,
    model_size: str = "tiny",
    language: Optional[str] = None,
    use_vad: bool = True,
    device: str = "auto"
):
    """Transcribe audio using audio-transcribe skill."""
    transcriber_path = find_skill_script("audio-transcribe", "transcribe_audio.py")

    if not transcriber_path:
        print("❌ Error: audio-transcribe skill not found")
        print("Please ensure audio-transcribe is installed in your skills directory")
        sys.exit(1)

    # Check if virtual environment exists and activate it
    audio_transcribe_dir = transcriber_path.parent.parent
    venv_python = audio_transcribe_dir / ".venv" / "bin" / "python"

    if venv_python.exists():
        python_exe = str(venv_python)
    else:
        python_exe = sys.executable

    # Build command
    cmd = [
        python_exe,
        str(transcriber_path),
        audio_path,
        "--output-dir", str(output_dir),
        "--model", model_size,
        "--device", device
    ]

    # Add --no-vad if Python 3.14+ (onnxruntime not supported)
    if use_vad and venv_python.exists():
        import sys
        # Check Python version
        result = subprocess.run(
            [str(venv_python), "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            major, minor = map(int, version.split('.')[:2])
            if major >= 3 and minor >= 14:
                print(f"⚠️  Python {version} detected: VAD not supported, using --no-vad")
                use_vad = False

    if language:
        cmd.extend(["--language", language])

    if not use_vad:
        cmd.append("--no-vad")

    print(f"\n🎙️  Transcribing audio...")
    print(f"   Using Python: {python_exe}")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error transcribing audio:")
        sys.exit(1)


def main():
    args = parse_args()

    # Download episode
    episode_info = download_episode(args.url, args.force_download)
    audio_path = Path(episode_info["audio_path"])

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path.home() / "Downloads" / "music" / "xyz" / episode_info["channel_name"]

    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if already transcribed
    base_name = episode_info["title"]
    srt_path = output_dir / f"{base_name}.srt"
    txt_path = output_dir / f"{base_name}.txt"

    if srt_path.exists() and txt_path.exists() and not args.force_download:
        print(f"\n⚠️  Transcript files already exist:")
        print(f"   {srt_path}")
        print(f"   {txt_path}")
        print("   Use --force-download to overwrite")
        return

    # Transcribe
    transcribe_audio(
        str(audio_path),
        output_dir,
        model_size=args.model,
        language=args.language,
        use_vad=not args.no_vad,
        device=args.device
    )

    print(f"\n🎉 Complete! Output directory: {output_dir}")


if __name__ == "__main__":
    main()
