---
name: xyz-podcast-downloader
description: Download Xiaoyuzhou (小宇宙) podcast episode audio files. Use when the user provides a Xiaoyuzhou podcast URL and asks to download the episode, extract audio, save the podcast, or mentions "小宇宙播客下载", "下载播客音频", or similar requests to save podcast episodes from xiaoyuzhou.fm URLs.
---

# Xyz Podcast Downloader

Download audio files from Xiaoyuzhou (小宇宙) podcast episodes with automatic title extraction and organized file saving.

## When to Use

Use this skill when:
- User provides a Xiaoyuzhou.fm URL and asks to download the episode
- User wants to save podcast audio from a Xiaoyuzhou episode page
- User mentions downloading podcasts, extracting audio, or saving episodes from 小宇宙
- User provides any URL from xiaoyuzhou.fm with download/save intent

## Quick Start

### Basic Usage

Download an episode to the default location (`~/Downloads/music/xyz/{频道名}/`):

```bash
python3 scripts/download_episode.py "https://www.xiaoyuzhou.fm/episode/..."
```

The script will:
1. Parse the webpage and extract the channel name and episode title
2. Find the .m4a audio file URL
3. Download the file with the episode title as the filename
4. Save to `~/Downloads/music/xyz/{频道名}/` (channel-specific directory)

**Example**: For "知行小酒馆" channel's episode "E160 牛市（少）亏钱指南", the file will be saved to:
- Path: `~/Downloads/music/xyz/知行小酒馆/E160 牛市（少）亏钱指南.m4a`

### Custom Output Directory

Use `--output-dir` to specify a custom directory:

```bash
python3 scripts/download_episode.py "https://www.xiaoyuzhou.fm/episode/..." \
  --output-dir ~/Podcasts/
```

When using a custom output directory, the filename format changes to `{频道名} - {单集标题名}.m4a` to include the channel name.

### Custom Filename

```bash
python3 scripts/download_episode.py "https://www.xiaoyuzhou.fm/episode/..." \
  --filename "my_episode"
```

## How It Works

The script uses a multi-strategy approach to extract episode information:

1. **HTML parsing**: Searches for `<audio>` tags with direct audio URLs
2. **JSON data extraction**: Looks for episode data in embedded JSON-LD or script tags
3. **Pattern matching**: Falls back to regex search for .m4a URLs in page source

Title extraction follows a similar strategy:
1. Checks `<meta property="og:title">` tags
2. Falls back to `<title>` tag
3. Searches embedded JSON for episode title

## Dependencies

The script requires Python packages:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast XML/HTML parser

### Installation

**Option 1: System-wide (macOS with externally-managed Python)**
```bash
pip3 install --break-system-packages requests beautifulsoup4 lxml
```

**Option 2: Virtual environment (recommended)**
```bash
python3 -m venv ~/.venv/xyz-episode
source ~/.venv/xyz-episode/bin/activate
pip3 install -r scripts/requirements.txt
```

**Option 3: User-specific**
```bash
pip3 install --user requests beautifulsoup4 lxml
```

## Output

The script provides real-time feedback:
- Episode title and audio URL (after parsing)
- File size information
- Download progress percentage
- Confirmation message when complete

Filenames are sanitized by:
- Removing invalid characters (`<>:"/\|?*`)
- Replacing newlines with spaces
- Limiting length to 200 characters

## Error Handling

The script will exit with error codes and messages for:
- Missing Python dependencies (with installation instructions)
- Network errors or timeouts
- Unable to find audio URL in the page
- File system errors (permissions, disk space)

## Examples

**Example 1: Download single episode**
```bash
python3 scripts/download_episode.py "https://www.xiaoyuzhou.fm/episode/12345678"
```
Output:
```
Parsing episode: https://www.xiaoyuzhou.fm/episode/12345678
Channel: 科技早知道
Episode: 技术漫谈第42期
Audio URL: https://audio.xiaoyuzhou.fm/episode_12345678.m4a

Downloading to: /Users/user/Downloads/music/xyz/科技早知道/技术漫谈第42期.m4a
File size: 45.67 MB
Progress: 100.0%
✅ Downloaded: 技术漫谈第42期.m4a
```

**Example 2: Download to custom location**
```bash
python3 scripts/download_episode.py "https://www.xiaoyuzhou.fm/episode/87654321" \
  --output-dir ~/Music/Podcasts/
```

**Example 3: Custom filename**
```bash
python3 scripts/download_episode.py "https://www.xiaoyuzhou.fm/episode/11112222" \
  -f "episode_111"
```

## Script Location

- **Main script**: `scripts/download_episode.py`
- **Requirements**: `scripts/requirements.txt`
