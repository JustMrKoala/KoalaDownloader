# Koala YT Downloader

Minimalist Flask app to download YouTube videos and Shorts as MP4.
Zero storage -- files are base64-encoded and delivered straight to the browser, then deleted.

## Usage

```bash
docker compose up --build
```

Open http://localhost:5000, paste any YouTube or Shorts URL, hit Download.

## Notes

- Uses yt-dlp for best-quality MP4 (video + audio merged via ffmpeg)
- Shorts URLs are automatically normalized to regular watch links
- Temp files are cleaned up immediately after encoding
- No database, no storage, no logging
