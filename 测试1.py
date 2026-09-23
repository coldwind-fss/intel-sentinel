
from __future__ import annotation

import concurrent.futures
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
import requests


SESSION_DIR = Path("/opt/customer-dashboard/runtime/sessions")
TARGETS = (
    ("飞比特官方旗舰店", "pdd_main__official"),
    ("FlipBelt运动旗舰店", "pdd_main__flipbelt_sports"),
)


def probe(target: tuple[str, str]) -> dict[str, object]:
    store_name, session_key = target
    state = json.loads(
        (SESSION_DIR / f"{session_key}.storage-state.json").read_text(encoding="utf-8")
    )
    summary = json.loads(
        (SESSION_DIR / f"{session_key}.summary.json").read_text(encoding="utf-8")
    )
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
    )
    for item in state.get("cookies", []):
        session.cookies.set(
            item["name"],
            item["value"],
            domain=item.get("domain") or None,
            path=item.get("path") or "/",
        )
    response = session.get(
        "https://mms.pinduoduo.com/mms-chat/overview/merchant",
        timeout=25,
        allow_redirects=False,
    )
    body = response.text
    return {
        "store": store_name,
        "sessionKey": session_key,
        "savedAt": summary.get("saved_at"),
        "matchingCookieCount": summary.get("matching_cookie_count"),
        "statusCode": response.status_code,
        "host": urlparse(response.url).netloc,
        "locationHost": urlparse(response.headers.get("Location", "")).netloc or None,
        "responseBytes": len(response.content),
        "responseFingerprint": hashlib.sha256(body.encode("utf-8", errors="replace")).hexdigest()[:16],
        "expectedNameInResponse": store_name in body,
        "authSuspected": response.status_code in {301, 302, 303, 307, 308, 401, 403},
    }


with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    results = list(executor.map(probe, TARGETS))
print(json.dumps(results, ensure_ascii=False, indent=2))
print(
    json.dumps(
        {
            "allSuccessful": all(item["statusCode"] == 200 for item in results),
            "uniqueResponseFingerprints": len({item["responseFingerprint"] for item in results}),
        },
        ensure_ascii=False,
    )
)
