#!/usr/bin/env python3
"""
Download Xiaoyuzhou podcast episode audio file.

This script extracts the audio URL from a Xiaoyuzhou episode page
and downloads it to ~/Downloads/music/xyz/[频道名]/ with the episode title.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Error: Required Python package is missing: {e}", file=sys.stderr)
    print("\nPlease install dependencies:", file=sys.stderr)
    print("  pip3 install --break-system-packages requests beautifulsoup4 lxml", file=sys.stderr)
    print("  OR create a virtual environment:", file=sys.stderr)
    print("  python3 -m venv ~/.venv/xyz-episode", file=sys.stderr)
    print("  source ~/.venv/xyz-episode/bin/activate", file=sys.stderr)
    print("  pip3 install requests beautifulsoup4 lxml", file=sys.stderr)
    sys.exit(1)


def extract_episode_info(url: str) -> tuple[str, str, str]:
    """
    Extract channel name, episode title and audio URL from Xiaoyuzhou page.

    Args:
        url: Xiaoyuzhou episode URL

    Returns:
        Tuple of (channel_name, episode_title, audio_url)

    Raises:
        ValueError: If audio URL or title cannot be found
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Try to find audio URL in <audio> tag
    audio_tag = soup.find('audio')
    if audio_tag and audio_tag.get('src'):
        audio_url = audio_tag.get('src')
    else:
        # Try to find in JSON data embedded in script tags
        scripts = soup.find_all('script', type='application/json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                # Navigate through the JSON structure to find audio URL
                if isinstance(data, dict):
                    # Common paths in Xiaoyuzhou data structure
                    audio_url = (
                        data.get('data', {}).get('episode', {}).get('audio', {}).get('src') or
                        data.get('episode', {}).get('audio', {}).get('src') or
                        data.get('audio', {}).get('src')
                    )
                    if audio_url:
                        break
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        else:
            # Search for .m4a URLs in the HTML source
            m4a_pattern = re.compile(r'https?://[^\s"\']+\.m4a[^\s"\']*', re.IGNORECASE)
            m4a_matches = m4a_pattern.findall(response.text)
            if m4a_matches:
                audio_url = m4a_matches[0]
            else:
                raise ValueError("Could not find audio URL in page")

    if not audio_url or not isinstance(audio_url, str):
        raise ValueError("Could not find audio URL in page")

    # Extract episode title
    title_tag = soup.find('meta', property='og:title') or soup.find('title')
    if title_tag:
        episode_title = title_tag.get('content') or title_tag.text
    else:
        # Try to find in JSON data
        scripts = soup.find_all('script', type='application/json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    episode_title = (
                        data.get('data', {}).get('episode', {}).get('title') or
                        data.get('episode', {}).get('title') or
                        data.get('title')
                    )
                    if episode_title:
                        break
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        else:
            episode_title = "xiaoyuzhou_episode"

    # Extract channel/podcast name
    channel_name = None

    # Try parsing from title tag: "{episode_title} - {channel_name} | 小宇宙 ..."
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.text.strip()
        # Pattern: "Episode - Channel | 小宇宙" or "Episode - Channel| 小宇宙"
        if ' | ' in title_text:
            parts = title_text.split(' | ')[0]
            if ' - ' in parts:
                channel_name = parts.split(' - ')[1].strip()
        elif '|' in title_text:
            parts = title_text.split('|')[0]
            if ' - ' in parts:
                channel_name = parts.split(' - ')[1].strip()

    # If not found in title, try meta tags
    if not channel_name:
        og_site_name = soup.find('meta', property='og:site_name')
        if og_site_name and og_site_name.get('content'):
            channel_name = og_site_name.get('content')

    # If still not found, try JSON data
    if not channel_name:
        scripts = soup.find_all('script', type='application/json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    channel_name = (
                        data.get('data', {}).get('episode', {}).get('podcast', {}).get('title') or
                        data.get('episode', {}).get('podcast', {}).get('title') or
                        data.get('data', {}).get('podcast', {}).get('title') or
                        data.get('podcast', {}).get('title')
                    )
                    if channel_name:
                        break
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue

    if not channel_name:
        channel_name = "Unknown_Channel"

    # Clean episode title for filename
    episode_title = episode_title.strip()
    # Remove or replace invalid filename characters
    episode_title = re.sub(r'[<>:"/\\|?*]', '', episode_title)
    episode_title = episode_title.replace('\n', ' ').replace('\r', ' ')
    # Limit length
    if len(episode_title) > 200:
        episode_title = episode_title[:200]

    # Clean channel name for filename
    channel_name = channel_name.strip()
    # Remove or replace invalid filename characters
    channel_name = re.sub(r'[<>:"/\\|?*]', '', channel_name)
    channel_name = channel_name.replace('\n', ' ').replace('\r', ' ')

    return channel_name, episode_title, audio_url


def download_audio(audio_url: str, output_path: Path) -> None:
    """
    Download audio file to specified path.

    Args:
        audio_url: URL of the audio file
        output_path: Where to save the file
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    response = requests.get(audio_url, headers=headers, stream=True, timeout=30)
    response.raise_for_status()

    # Get file extension from URL
    ext = os.path.splitext(audio_url)[1] or '.m4a'

    # Add extension if not already present (only check for audio extensions)
    audio_extensions = {'.m4a', '.mp3', '.mp4', '.aac', '.wav', '.flac', '.ogg', '.opus'}
    if output_path.suffix.lower() not in audio_extensions:
        # Use string concatenation instead of with_suffix to avoid truncating filenames with dots
        output_path = Path(str(output_path) + ext)

    total_size = int(response.headers.get('content-length', 0))

    print(f"Downloading to: {output_path}")
    print(f"File size: {total_size / 1024 / 1024:.2f} MB")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'wb') as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    progress = (downloaded / total_size) * 100
                    print(f"\rProgress: {progress:.1f}%", end='', flush=True)

    print()  # New line after progress
    print(f"✅ Downloaded: {output_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description='Download Xiaoyuzhou podcast episode audio'
    )
    parser.add_argument('url', help='Xiaoyuzhou episode URL')
    parser.add_argument(
        '-o', '--output-dir',
        default=None,
        help='Custom output directory (default: ~/Downloads/music/xyz/{频道名}/)'
    )
    parser.add_argument(
        '-f', '--filename',
        help='Custom filename (without extension)'
    )

    args = parser.parse_args()

    try:
        print(f"Parsing episode: {args.url}")
        channel_name, episode_title, audio_url = extract_episode_info(args.url)
        print(f"Channel: {channel_name}")
        print(f"Episode: {episode_title}")
        print(f"Audio URL: {audio_url}")

        # Determine output path
        # If --output-dir is specified, use it; otherwise use ~/Downloads/music/xyz/{频道名}/
        if args.output_dir:
            output_dir = Path(args.output_dir).expanduser()
        else:
            output_dir = Path('~/Downloads/music/xyz').expanduser() / channel_name

        # Generate filename: {单集标题名} (if using default channel directory)
        # or {频道名} - {单集标题名} (if using custom output directory)
        if args.filename:
            filename = args.filename
        elif args.output_dir:
            # Custom directory: include channel name in filename
            filename = f"{channel_name} - {episode_title}"
        else:
            # Default channel directory: only episode title in filename
            filename = episode_title

        output_path = output_dir / filename

        print()
        download_audio(audio_url, output_path)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
