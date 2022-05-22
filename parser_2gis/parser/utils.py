from __future__ import annotations


def blocked_requests(extended: bool = False) -> list[str]:
    """Get blocked request patterns list: metrics, logging,
    analytics, counters, ads, etc.

    During the parsing we don't need requests that could slow
    down the speed or increase memory consumption or
    send any logs of automatic bot activity.

    The lists are separated: basic and extended that includes
    images, styles, map tiles, fonts and other visual-related
    resources.

    Args:
        extended: Whether to return extended list or basic.

    Returns:
        List of blocking url patterns.
    """
    # Metrics, logging, analytics, counters, ads, etc.
    blocked_requests: list[str] = [
        'https://favorites.api.2gis.*/*',
        'https://2gis.*/_/log',
        'https://2gis.*/_/metrics',
        'https://google-analytics.com/*',
        'https://www.google-analytics.com/*',
        'https://counter.yadro.ru/*',
        'https://www.tns-counter.ru/*',
        'https://mc.yandex.ru/*',
        'https://catalog.api.2gis.ru/3.0/ads/*',
        'https://d-assets.2gis.*/privacyPolicyBanner*.js',
        'https://vk.com/*',
    ]

    # Styles, map tiles, images, etc.
    blocked_requests_extra: list[str] = [
        'https://d-assets.2gis.*/fonts/*',
        'https://mapgl.2gis.*/api/fonts/*',
        'https://tile*.maps.2gis.*',
        'https://s*.bss.2gis.*',
        'https://styles.api.2gis.*',
        'https://video-pr.api.2gis.*',
        'https://api.photo.2gis.*/*',
        'https://market-backend.api.2gis.*',
        'https://traffic*.edromaps.2gis.*',
        'https://disk.2gis.*/styles/*',
    ]

    ret_list = blocked_requests
    if extended:
        ret_list.extend(blocked_requests_extra)

    return ret_list
