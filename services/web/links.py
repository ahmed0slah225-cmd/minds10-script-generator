from urllib.parse import urlparse

def normalize_urls(text):
    vals=[]
    for line in (text or '').splitlines():
        u=line.strip()
        if not u: continue
        if not u.startswith(('http://','https://')): u='https://'+u
        p=urlparse(u)
        if p.scheme in ('http','https') and p.netloc: vals.append(u)
    return list(dict.fromkeys(vals))
