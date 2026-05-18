# @router.post("/testing-ip")
async def get_info(request: Request):
    import requests
    import socket
    import user_agents
    import re

    def get_real_client_ip(request):
        headers_to_check = [
            'X-Forwarded-For', 'X-Real-IP', 'CF-Connecting-IP', 
            'X-Client-IP', 'X-Forwarded', 'Forwarded-For', 'Forwarded'
        ]
        
        for header in headers_to_check:
            ip = request.headers.get(header)
            if ip:
                return ip.split(',')[0].strip()
        return request.client.host

    def parse_org_info(org_string):
        """Parse ASN depuis l'org string"""
        if not org_string or org_string == "Unknown":
            return "Unknown", "Unknown", "Unknown"
        
        asn_match = re.match(r'(AS\d+)\s+(.+)', org_string)
        if asn_match:
            asn = asn_match.group(1)
            as_name = asn_match.group(2)
            return asn, as_name, "Unknown"
        return "Unknown", org_string, "Unknown"

    def get_continent_info(country_code):
        """Mapping simple des codes pays vers continents"""
        continent_mapping = {
            # Afrique
            "SN": {"code": "AF", "name": "Africa"}, "MA": {"code": "AF", "name": "Africa"},
            "NG": {"code": "AF", "name": "Africa"}, "ZA": {"code": "AF", "name": "Africa"},
            # Europe
            "FR": {"code": "EU", "name": "Europe"}, "DE": {"code": "EU", "name": "Europe"},
            "GB": {"code": "EU", "name": "Europe"}, "IT": {"code": "EU", "name": "Europe"},
            # Amérique du Nord
            "US": {"code": "NA", "name": "North America"}, 
            "CA": {"code": "NA", "name": "North America"},
            # Asie
            "CN": {"code": "AS", "name": "Asia"}, "JP": {"code": "AS", "name": "Asia"},
            "IN": {"code": "AS", "name": "Asia"},
            # Amérique du Sud
            "BR": {"code": "SA", "name": "South America"}, 
            "AR": {"code": "SA", "name": "South America"},
            # Océanie
            "AU": {"code": "OC", "name": "Oceania"}, "NZ": {"code": "OC", "name": "Oceania"}
        }
        return continent_mapping.get(country_code, {"code": "Unknown", "name": "Unknown"})

    # IP du client
    client_ip = get_real_client_ip(request)
    
    # ✅ Une seule vérification IP privée avec ipify si nécessaire
    if client_ip.startswith(('10.', '172.', '192.168.', '127.')):
        try:
            public_ip_resp = requests.get('https://api.ipify.org?format=json', timeout=5)
            client_ip = public_ip_resp.json().get('ip', client_ip)
        except Exception:
            pass

    # User-Agent
    ua_string = request.headers.get("user-agent")
    ua = user_agents.parse(ua_string) if ua_string else None
    
    os = f"{ua.os.family} {ua.os.version_string}" if ua else "Unknown"
    browser = f"{ua.browser.family} {ua.browser.version_string}" if ua else "Unknown"
    device_type = "Mobile" if ua.is_mobile else "Tablet" if ua.is_tablet else "PC" if ua.is_pc else "Bot" if ua.is_bot else "Unknown"

    # Reverse DNS
    try:
        hostname = socket.gethostbyaddr(client_ip)[0]
    except Exception:
        hostname = "Unknown"

    # ✅ UNIQUEMENT ipinfo.io (suffisant pour la plupart des cas)
    try:
        resp = requests.get(f"https://ipinfo.io/{client_ip}?token={IPINFO_TOKEN}", timeout=10).json()
        
        country = resp.get("country", "Unknown")
        region = resp.get("region", "Unknown") 
        city = resp.get("city", "Unknown")
        timezone = resp.get("timezone", "Unknown")
        org = resp.get("org", "Unknown")
        postal = resp.get("postal", "Unknown")
        loc = resp.get("loc", "Unknown")
        
        # Parser l'ASN depuis l'org
        asn, as_name, as_domain = parse_org_info(org)
        
        # Continent depuis mapping local
        continent_info = get_continent_info(country)
        continent_code = continent_info["code"]
        continent = continent_info["name"]
        
    except Exception as e:
        print(f"Erreur API ipinfo: {e}")
        country = region = city = timezone = org = "Unknown"
        asn = as_name = as_domain = postal = loc = "Unknown"
        continent_code = continent = "Unknown"
        resp = {}

    return {
        "ip": client_ip,
        "os": os,
        "browser": browser,
        "device": device_type,
        "hostname": hostname,
        "country": country,
        "region": region,
        "city": city,
        "timezone": timezone,
        "isp_org": org,
        "asn": asn,
        "as_name": as_name,
        "as_domain": as_domain,
        "country_code": country,  # ipinfo.io donne le code pays dans "country"
        "continent_code": continent_code,
        "continent": continent,
        "postal": postal,
        "coordinates": loc
    }