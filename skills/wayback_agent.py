"""
wayback_agent.py  --  Query the Internet Archive CDX API for web snapshot history.

Used as optional enrichment for pharmacy records that have a known website.
Free, no API key required.

CDX API: https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server

Returns three fields per record:
    Wayback_Earliest_Year  -- first year a snapshot was captured (None if no history)
    Wayback_Latest_Year    -- most recent snapshot year (None if no history)
    Wayback_Snapshot_Count -- distinct years with at least one snapshot

Snapshot_Count semantics:
    -1  : known major pharmacy chain domain (CVS, Walgreens, etc.); CDX not queried
           to avoid timeout; web presence considered confirmed by chain status.
     0  : CDX returned no records, or query failed / timed out.
    >0  : number of distinct years with at least one archived snapshot.

Design rationale:
    Chain pharmacies operate under massive corporate domains (cvs.com, walgreens.com)
    whose CDX queries time out even with small limits. They are identified via a
    known-chain domain list and skipped. Independent pharmacies with their own small
    domains are queried with matchType=prefix on the http://www.{domain}/ prefix,
    which is fast and reliable for sites with modest web histories. The chain vs
    independent asymmetry in Snapshot_Count is analytically useful:
    independent pharmacies without web presence show Snapshot_Count=0.
"""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen

CDX_API = "https://web.archive.org/cdx/search/cdx"

_EMPTY = {
    "Wayback_Earliest_Year":  None,
    "Wayback_Latest_Year":    None,
    "Wayback_Snapshot_Count": 0,
}

_CHAIN_SENTINEL = {
    "Wayback_Earliest_Year":  None,
    "Wayback_Latest_Year":    None,
    "Wayback_Snapshot_Count": -1,
}

# Major pharmacy chain domains that would cause CDX query timeouts.
# Presence on any of these implies confirmed web history.
_CHAIN_DOMAINS = frozenset({
    "walgreens.com", "cvs.com", "riteaid.com", "walmart.com",
    "target.com", "costco.com", "kroger.com", "albertsons.com",
    "safeway.com", "publix.com", "meijer.com", "hy-vee.com",
    "hyvee.com", "duanereade.com", "thriftywhite.com",
})


def _root_domain(netloc: str) -> str:
    """Return two-part root domain, e.g. 'www.cvs.com' -> 'cvs.com'."""
    parts = netloc.lower().split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else netloc.lower()


def _bare_domain(netloc: str) -> str:
    """Return domain without www. prefix."""
    d = netloc.lower()
    return d[4:] if d.startswith("www.") else d


def get_snapshot_info(url: str, timeout: int = 8) -> dict:
    """
    Query CDX API for snapshot history of a business website.

    Parameters
    ----------
    url     : Business website URL from Google Maps (Business_Website field).
    timeout : Request timeout in seconds. Default 8 is pipeline-safe; independent
              pharmacy sites respond well within this window.

    Returns
    -------
    dict with Wayback_Earliest_Year, Wayback_Latest_Year, Wayback_Snapshot_Count.
    Never raises -- all exceptions are silently caught.
    """
    if not url:
        return dict(_EMPTY)

    try:
        parsed = urlparse(url if "://" in url else "https://" + url)
        netloc = parsed.netloc or parsed.path.split("/")[0]
    except Exception:
        return dict(_EMPTY)

    if not netloc:
        return dict(_EMPTY)

    # Short-circuit known chain domains to avoid CDX timeouts
    if _root_domain(netloc) in _CHAIN_DOMAINS:
        return dict(_CHAIN_SENTINEL)

    # For independent pharmacies, query using http://www.{domain}/ as the prefix.
    # matchType=prefix captures the homepage and direct subpages; fast on small sites.
    domain = _bare_domain(netloc)
    prefix_url = f"http://www.{domain}/"
    params = {
        "url":       prefix_url,
        "output":    "json",
        "fl":        "timestamp",
        "collapse":  "timestamp:4",
        "limit":     "20",
        "matchType": "prefix",
    }

    try:
        with urlopen(CDX_API + "?" + urlencode(params), timeout=timeout) as resp:
            raw = json.loads(resp.read())
    except (URLError, HTTPError, json.JSONDecodeError, Exception):
        return dict(_EMPTY)

    if not raw or len(raw) < 2:
        return dict(_EMPTY)

    years = []
    for row in raw[1:]:
        if row:
            ts = str(row[0])   # CDX returns int timestamps
            if len(ts) >= 4:
                try:
                    years.append(int(ts[:4]))
                except ValueError:
                    pass

    if not years:
        return dict(_EMPTY)

    return {
        "Wayback_Earliest_Year":  min(years),
        "Wayback_Latest_Year":    max(years),
        "Wayback_Snapshot_Count": len(years),
    }
