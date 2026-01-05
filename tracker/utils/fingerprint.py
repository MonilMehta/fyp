"""
Fingerprinting utilities for extracting client information.
Designed to blend into normal request handling.
"""
import re
from typing import Dict, Any, Optional


def get_client_ip(request) -> Optional[str]:
    """Extract real IP address, handling proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        return x_real_ip
    return request.META.get('REMOTE_ADDR')


def parse_user_agent(ua_string: str) -> Dict[str, str]:
    """Parse User-Agent for OS and browser information."""
    result = {
        'os_name': '',
        'os_version': '',
        'browser_name': '',
        'browser_version': '',
        'client_app': '',
        'client_build': '',
    }

    if not ua_string:
        return result

    # Detect Office applications
    office_match = re.search(r'Microsoft Office\s+([\w\s]+)', ua_string, re.I)
    if office_match:
        result['client_app'] = f"Microsoft Office {office_match.group(1)}"

    word_match = re.search(r'Word[/\s]*([\d.]+)?', ua_string, re.I)
    if word_match:
        result['client_app'] = 'Microsoft Word'
        if word_match.group(1):
            result['client_build'] = word_match.group(1)

    excel_match = re.search(r'Excel[/\s]*([\d.]+)?', ua_string, re.I)
    if excel_match:
        result['client_app'] = 'Microsoft Excel'
        if excel_match.group(1):
            result['client_build'] = excel_match.group(1)

    # Detect OS
    if 'Windows NT 10' in ua_string:
        result['os_name'] = 'Windows'
        result['os_version'] = '10/11'
    elif 'Windows NT 6.3' in ua_string:
        result['os_name'] = 'Windows'
        result['os_version'] = '8.1'
    elif 'Windows NT 6.1' in ua_string:
        result['os_name'] = 'Windows'
        result['os_version'] = '7'
    elif 'Mac OS X' in ua_string:
        result['os_name'] = 'macOS'
        mac_ver = re.search(r'Mac OS X ([\d_]+)', ua_string)
        if mac_ver:
            result['os_version'] = mac_ver.group(1).replace('_', '.')
    elif 'Linux' in ua_string:
        result['os_name'] = 'Linux'
    elif 'Android' in ua_string:
        result['os_name'] = 'Android'
        android_ver = re.search(r'Android ([\d.]+)', ua_string)
        if android_ver:
            result['os_version'] = android_ver.group(1)
    elif 'iPhone' in ua_string or 'iPad' in ua_string:
        result['os_name'] = 'iOS'
        ios_ver = re.search(r'OS ([\d_]+)', ua_string)
        if ios_ver:
            result['os_version'] = ios_ver.group(1).replace('_', '.')

    # Detect browsers (if not Office)
    if not result['client_app']:
        if 'Chrome' in ua_string and 'Edg' not in ua_string:
            result['browser_name'] = 'Chrome'
            chrome_ver = re.search(r'Chrome/([\d.]+)', ua_string)
            if chrome_ver:
                result['browser_version'] = chrome_ver.group(1)
        elif 'Edg' in ua_string:
            result['browser_name'] = 'Edge'
            edge_ver = re.search(r'Edg/([\d.]+)', ua_string)
            if edge_ver:
                result['browser_version'] = edge_ver.group(1)
        elif 'Firefox' in ua_string:
            result['browser_name'] = 'Firefox'
            ff_ver = re.search(r'Firefox/([\d.]+)', ua_string)
            if ff_ver:
                result['browser_version'] = ff_ver.group(1)
        elif 'Safari' in ua_string:
            result['browser_name'] = 'Safari'
            safari_ver = re.search(r'Version/([\d.]+)', ua_string)
            if safari_ver:
                result['browser_version'] = safari_ver.group(1)

    return result


def extract_request_metadata(request) -> Dict[str, Any]:
    """Extract all relevant metadata from a request."""
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    ua_data = parse_user_agent(ua_string)

    return {
        'ip_address': get_client_ip(request),
        'user_agent': ua_string,
        'accept_headers': request.META.get('HTTP_ACCEPT', ''),
        'accept_language': request.META.get('HTTP_ACCEPT_LANGUAGE', ''),
        **ua_data,
    }


def extract_query_params(request) -> Dict[str, str]:
    """Extract query parameters from request."""
    return {k: v for k, v in request.GET.items()}
