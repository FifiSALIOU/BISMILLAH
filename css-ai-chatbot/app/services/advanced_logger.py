#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service de logging avancé avec collecte d'informations IP
Intègre la surveillance des activités utilisateurs pour les endpoints ask
"""

import os
import json
import csv
import requests
import socket
import user_agents
import re
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from fastapi import Request

from app.core.config import settings
from app.utils.logging import logger

class AdvancedLogger:
    """Service de logging avancé avec collecte d'informations IP"""
    
    def __init__(self):
        self.log_directory = Path("app/for-analysis/request-logs")
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Token ipinfo.io depuis les settings ou variable d'environnement
        self.ipinfo_token = getattr(settings, 'IPINFO_TOKEN', os.getenv('IPINFO_TOKEN', ''))
        
        if not self.ipinfo_token:
            logger.warning("Token ipinfo.io non configuré. Les informations géographiques seront limitées.")
    
    def get_real_client_ip(self, request: Request) -> str:
        """Récupère l'adresse IP réelle du client"""
        headers_to_check = [
            'X-Forwarded-For', 'X-Real-IP', 'CF-Connecting-IP', 
            'X-Client-IP', 'X-Forwarded', 'Forwarded-For', 'Forwarded'
        ]
        
        for header in headers_to_check:
            ip = request.headers.get(header)
            if ip:
                return ip.split(',')[0].strip()
        return request.client.host
    
    def parse_org_info(self, org_string: str) -> tuple:
        """Parse ASN depuis l'org string"""
        if not org_string or org_string == "Unknown":
            return "Unknown", "Unknown", "Unknown"
        
        asn_match = re.match(r'(AS\d+)\s+(.+)', org_string)
        if asn_match:
            asn = asn_match.group(1)
            as_name = asn_match.group(2)
            return asn, as_name, "Unknown"
        return "Unknown", org_string, "Unknown"
    
    def get_continent_info(self, country_code: str) -> Dict[str, str]:
        """Mapping simple des codes pays vers continents"""
        continent_mapping = {
            # Afrique
            "SN": {"code": "AF", "name": "Africa"}, "MA": {"code": "AF", "name": "Africa"},
            "NG": {"code": "AF", "name": "Africa"}, "ZA": {"code": "AF", "name": "Africa"},
            "DZ": {"code": "AF", "name": "Africa"}, "EG": {"code": "AF", "name": "Africa"},
            "KE": {"code": "AF", "name": "Africa"}, "GH": {"code": "AF", "name": "Africa"},
            # Europe
            "FR": {"code": "EU", "name": "Europe"}, "DE": {"code": "EU", "name": "Europe"},
            "GB": {"code": "EU", "name": "Europe"}, "IT": {"code": "EU", "name": "Europe"},
            "ES": {"code": "EU", "name": "Europe"}, "NL": {"code": "EU", "name": "Europe"},
            # Amérique du Nord
            "US": {"code": "NA", "name": "North America"}, 
            "CA": {"code": "NA", "name": "North America"},
            "MX": {"code": "NA", "name": "North America"},
            # Asie
            "CN": {"code": "AS", "name": "Asia"}, "JP": {"code": "AS", "name": "Asia"},
            "IN": {"code": "AS", "name": "Asia"}, "KR": {"code": "AS", "name": "Asia"},
            # Amérique du Sud
            "BR": {"code": "SA", "name": "South America"}, 
            "AR": {"code": "SA", "name": "South America"},
            "CL": {"code": "SA", "name": "South America"},
            # Océanie
            "AU": {"code": "OC", "name": "Oceania"}, "NZ": {"code": "OC", "name": "Oceania"}
        }
        return continent_mapping.get(country_code, {"code": "Unknown", "name": "Unknown"})
    
    def collect_ip_info(self, request: Request) -> Dict[str, Any]:
        """Collecte toutes les informations liées à l'adresse IP"""
        # IP du client
        client_ip = self.get_real_client_ip(request)
        
        # Vérification IP privée avec ipify si nécessaire
        if client_ip.startswith(('10.', '172.', '192.168.', '127.')):
            try:
                public_ip_resp = requests.get('https://api.ipify.org?format=json', timeout=5)
                client_ip = public_ip_resp.json().get('ip', client_ip)
            except Exception:
                pass
        
        # User-Agent
        ua_string = request.headers.get("user-agent")
        ua = user_agents.parse(ua_string) if ua_string else None
        
        os_info = f"{ua.os.family} {ua.os.version_string}" if ua else "Unknown"
        browser = f"{ua.browser.family} {ua.browser.version_string}" if ua else "Unknown"
        device_type = "Mobile" if ua.is_mobile else "Tablet" if ua.is_tablet else "PC" if ua.is_pc else "Bot" if ua.is_bot else "Unknown"
        
        # Reverse DNS
        try:
            hostname = socket.gethostbyaddr(client_ip)[0]
        except Exception:
            hostname = "Unknown"
        
        # Informations géographiques via ipinfo.io
        geo_info = self._get_geo_info(client_ip)
        
        return {
            "ip": client_ip,
            "os": os_info,
            "browser": browser,
            "device": device_type,
            "hostname": hostname,
            "user_agent": ua_string or "Unknown",
            **geo_info
        }
    
    def _get_geo_info(self, ip: str) -> Dict[str, Any]:
        """Récupère les informations géographiques via ipinfo.io"""
        if not self.ipinfo_token:
            return {
                "country": "Unknown",
                "region": "Unknown",
                "city": "Unknown",
                "timezone": "Unknown",
                "isp_org": "Unknown",
                "asn": "Unknown",
                "as_name": "Unknown",
                "as_domain": "Unknown",
                "country_code": "Unknown",
                "continent_code": "Unknown",
                "continent": "Unknown",
                "postal": "Unknown",
                "coordinates": "Unknown"
            }
        
        try:
            resp = requests.get(
                f"https://ipinfo.io/{ip}?token={self.ipinfo_token}", 
                timeout=10
            ).json()
            
            country = resp.get("country", "Unknown")
            region = resp.get("region", "Unknown")
            city = resp.get("city", "Unknown")
            timezone = resp.get("timezone", "Unknown")
            org = resp.get("org", "Unknown")
            postal = resp.get("postal", "Unknown")
            loc = resp.get("loc", "Unknown")
            
            # Parser l'ASN depuis l'org
            asn, as_name, as_domain = self.parse_org_info(org)
            
            # Continent depuis mapping local
            continent_info = self.get_continent_info(country)
            continent_code = continent_info["code"]
            continent = continent_info["name"]
            
            return {
                "country": country,
                "region": region,
                "city": city,
                "timezone": timezone,
                "isp_org": org,
                "asn": asn,
                "as_name": as_name,
                "as_domain": as_domain,
                "country_code": country,
                "continent_code": continent_code,
                "continent": continent,
                "postal": postal,
                "coordinates": loc
            }
            
        except Exception as e:
            logger.error(f"Erreur API ipinfo: {e}")
            return {
                "country": "Unknown",
                "region": "Unknown",
                "city": "Unknown",
                "timezone": "Unknown",
                "isp_org": "Unknown",
                "asn": "Unknown",
                "as_name": "Unknown",
                "as_domain": "Unknown",
                "country_code": "Unknown",
                "continent_code": "Unknown",
                "continent": "Unknown",
                "postal": "Unknown",
                "coordinates": "Unknown"
            }
    
    def log_ask_request(self, 
                       request: Request,
                       endpoint: str,
                       response_id: str,
                       question: str,
                       response: str,
                       processing_time_ms: float,
                       additional_data: Optional[Dict[str, Any]] = None) -> None:
        """Enregistre une requête ask avec toutes les informations"""
        
        try:
            # Collecte des informations IP
            ip_info = self.collect_ip_info(request)
            
            # Données de base
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "endpoint": endpoint,
                "response_id": response_id,
                "question": question,
                "response": response,
                "processing_time_ms": processing_time_ms,
                **ip_info
            }
            
            # Ajout des données supplémentaires si fournies
            if additional_data:
                log_entry.update(additional_data)
            
            # Écriture dans le fichier CSV
            self._write_to_csv(endpoint, log_entry)
            
            # Écriture dans le fichier JSON pour analyse avancée
            self._write_to_json(endpoint, log_entry)
            
            logger.info(f"Log enregistré pour {endpoint}: {response_id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du log: {e}")
    
    def _write_to_csv(self, endpoint: str, log_entry: Dict[str, Any]) -> None:
        """Écrit l'entrée de log dans un fichier CSV"""
        csv_file = self.log_directory / f"{endpoint.replace('/', '_').replace('-', '_')}_requests.csv"
        
        # Définir les colonnes dans l'ordre souhaité
        fieldnames = [
            'timestamp', 'endpoint', 'response_id', 'question', 'response', 
            'processing_time_ms', 'ip', 'country', 'region', 'city', 'timezone',
            'isp_org', 'asn', 'as_name', 'continent', 'coordinates', 'postal',
            'os', 'browser', 'device', 'hostname', 'user_agent'
        ]
        
        # Ajouter les champs supplémentaires s'ils existent
        for key in log_entry.keys():
            if key not in fieldnames:
                fieldnames.append(key)
        
        file_exists = csv_file.exists()
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            # S'assurer que toutes les valeurs sont des chaînes
            clean_entry = {k: str(v) if v is not None else "" for k, v in log_entry.items()}
            writer.writerow(clean_entry)
    
    def _write_to_json(self, endpoint: str, log_entry: Dict[str, Any]) -> None:
        """Écrit l'entrée de log dans un fichier JSON pour analyse avancée"""
        json_file = self.log_directory / f"{endpoint.replace('/', '_').replace('-', '_')}_requests.jsonl"
        
        with open(json_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def get_log_statistics(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Récupère les statistiques des logs"""
        stats = {
            "total_requests": 0,
            "endpoints": {},
            "countries": {},
            "devices": {},
            "browsers": {},
            "last_24h": 0
        }
        
        try:
            # Parcourir tous les fichiers CSV de logs
            pattern = "*_requests.csv" if not endpoint else f"{endpoint.replace('/', '_').replace('-', '_')}_requests.csv"
            
            for csv_file in self.log_directory.glob(pattern):
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        stats["total_requests"] += 1
                        
                        # Statistiques par endpoint
                        ep = row.get('endpoint', 'unknown')
                        stats["endpoints"][ep] = stats["endpoints"].get(ep, 0) + 1
                        
                        # Statistiques par pays
                        country = row.get('country', 'Unknown')
                        stats["countries"][country] = stats["countries"].get(country, 0) + 1
                        
                        # Statistiques par device
                        device = row.get('device', 'Unknown')
                        stats["devices"][device] = stats["devices"].get(device, 0) + 1
                        
                        # Statistiques par browser
                        browser = row.get('browser', 'Unknown')
                        stats["browsers"][browser] = stats["browsers"].get(browser, 0) + 1
                        
                        # Requêtes des dernières 24h
                        try:
                            timestamp = datetime.fromisoformat(row.get('timestamp', ''))
                            if (datetime.now() - timestamp).total_seconds() < 86400:  # 24h
                                stats["last_24h"] += 1
                        except:
                            pass
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques: {e}")
        
        return stats

# Instance globale du logger avancé
advanced_logger = AdvancedLogger()