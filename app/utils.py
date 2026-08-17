import re
from urllib.parse import parse_qs, urlparse


def normalize_whatsapp_number(value):
    """Return a WhatsApp-compatible Turkish number without a leading plus sign."""
    digits = re.sub(r"\D", "", str(value or ""))

    if digits.startswith("00"):
        digits = digits[2:]

    if len(digits) == 12 and digits.startswith("90"):
        return digits
    if len(digits) == 11 and digits.startswith("0"):
        return f"90{digits[1:]}"
    if len(digits) == 10:
        return f"90{digits}"

    return digits


def youtube_embed_url(value):
    """Return a privacy-enhanced YouTube embed URL for supported share URLs."""
    raw_url = str(value or '').strip()
    if not raw_url:
        return ''

    try:
        parsed = urlparse(raw_url if '://' in raw_url else f'https://{raw_url}')
        host = parsed.netloc.lower().split(':')[0]
        video_id = ''

        if host in {'youtu.be', 'www.youtu.be'}:
            video_id = parsed.path.strip('/').split('/')[0]
        elif host in {'youtube.com', 'www.youtube.com', 'm.youtube.com'}:
            if parsed.path == '/watch':
                video_id = parse_qs(parsed.query).get('v', [''])[0]
            elif parsed.path.startswith(('/embed/', '/shorts/', '/live/')):
                video_id = parsed.path.strip('/').split('/')[1]

        if re.fullmatch(r'[A-Za-z0-9_-]{11}', video_id):
            return f'https://www.youtube-nocookie.com/embed/{video_id}?autoplay=1&rel=0'
    except (TypeError, ValueError, IndexError):
        pass

    return ''
