from urllib.parse import urlparse


def _parse_db_url(url: str):
    parsed = urlparse(url)
    db_name = parsed.path.lstrip("/")
    admin_url = url.replace(f"/{db_name}", "/postgres")
    return admin_url, db_name
