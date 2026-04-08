#!/usr/bin/env python3
"""
GhostRoute Pro v2.0.0 - Endpoint Resurrection Scanner
Find hidden API endpoints that developers thought they deleted.

Author: P.H.O.E.N.I.X
License: MIT
Version: 2.0.0

Usage:
    python ghostroute.py
    python ghostroute.py --target https://example.com --quick
    python ghostroute.py --target https://example.com --deep --output report.html
"""

import os
import re
import sys
import json
import time
import argparse
import threading
from urllib.parse import urlparse, urljoin
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional, Tuple

try:
    import requests
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    print("[!] Missing dependencies. Run: pip install requests colorama")
    sys.exit(1)

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================================================
# CONFIGURATION & DATA CLASSES
# ============================================================================

@dataclass
class GhostFinding:
    """Represents a discovered ghost endpoint."""
    url: str
    status_code: int
    source: str
    evidence: str
    risk: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class Colors:
    """Terminal colors for output."""
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT

# Patterns for finding commented routes
COMMENTED_PATTERNS = {
    'express_get': r'(?://|/\*).*?app\.get\s*\(\s*["\']([^"\']+)["\']',
    'express_post': r'(?://|/\*).*?app\.post\s*\(\s*["\']([^"\']+)["\']',
    'express_router': r'(?://|/\*).*?router\.(?:get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
    'react_route': r'(?://|/\*).*?(?:path|to)\s*:\s*["\']([^"\']+)["\']',
    'html_href': r'<!--.*?(?:href|src|action)\s*=\s*["\']([^"\']+)["\']',
    'python_route': r'#.*?@app\.(?:route|get|post)\s*\(\s*["\']([^"\']+)["\']',
    'php_route': r'//.*?Route::(?:get|post|put|delete)\s*\(\s*["\']([^"\']+)["\']',
    'generic_path': r'(?://|#|/\*).*?(/[a-zA-Z0-9_\-/]+)(?:\s|$)',
}

# Browser headers to avoid blocking
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
}

# ============================================================================
# BANNER FUNCTIONS
# ============================================================================

def print_banner():
    """Display the GhostRoute Pro banner."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                                  ║
║  {Colors.MAGENTA} ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗██████╗  ██████╗ ██╗   ██╗████████╗███████╗{Colors.CYAN}  ║
║  {Colors.MAGENTA}██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗██║   ██║╚══██╔══╝██╔════╝{Colors.CYAN}  ║
║  {Colors.MAGENTA}██║  ███╗███████║██║   ██║███████╗   ██║   ██████╔╝██║   ██║██║   ██║   ██║   █████╗  {Colors.CYAN}  ║
║  {Colors.MAGENTA}██║   ██║██╔══██║██║   ██║╚════██║   ██║   ██╔══██╗██║   ██║██║   ██║   ██║   ██╔══╝  {Colors.CYAN}  ║
║  {Colors.MAGENTA}╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   ██║  ██║╚██████╔╝╚██████╔╝   ██║   ███████╗{Colors.CYAN}  ║
║  {Colors.MAGENTA} ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝{Colors.CYAN}  ║
║                                                                                  ║
║{Colors.YELLOW}                             Pro Edition v2.0.0 {Colors.CYAN}                                            ║
║{Colors.GREEN}                  \"Find what they thought was deleted\"{Colors.CYAN}                                     ║
║                                                                                  ║
║{Colors.BLUE}                         🛠️  Crafted by: P.H.O.E.N.I.X {Colors.CYAN}                                     ║
║                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)

def print_scan_header(target: str, mode: str, threads: int):
    """Display scan header."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'═'*80}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}🎯 TARGET:{Colors.RESET} {Colors.WHITE}{target}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}⚙️  MODE:{Colors.RESET} {Colors.YELLOW}{mode}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}🧵 THREADS:{Colors.RESET} {Colors.YELLOW}{threads}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}🕐 STARTED:{Colors.RESET} {Colors.WHITE}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'═'*80}{Colors.RESET}\n")

def print_scan_footer(findings_count: int, high: int, medium: int, low: int, elapsed: float):
    """Display scan footer with results."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'═'*80}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}✅ SCAN COMPLETE{Colors.RESET}")
    print(f"{Colors.CYAN}{'─'*80}{Colors.RESET}")
    print(f"{Colors.GREEN}⏱️  Time Elapsed:{Colors.RESET} {Colors.WHITE}{elapsed:.2f} seconds{Colors.RESET}")
    print(f"{Colors.GREEN}📊 Total Ghosts Found:{Colors.RESET} {Colors.BOLD}{findings_count}{Colors.RESET}")
    print(f"{Colors.CYAN}{'─'*80}{Colors.RESET}")
    print(f"{Colors.RED}🔥 HIGH:{Colors.RESET} {Colors.BOLD}{high}{Colors.RESET}    {Colors.YELLOW}⚠️  MEDIUM:{Colors.RESET} {Colors.BOLD}{medium}{Colors.RESET}    {Colors.BLUE}ℹ️  LOW:{Colors.RESET} {Colors.BOLD}{low}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'═'*80}{Colors.RESET}\n")

def print_credit():
    """Display credit footer."""
    credit = f"""
{Colors.MAGENTA}{Colors.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                                  ║
║                         {Colors.YELLOW} GHOSTROUTE PRO v2.0.0{Colors.MAGENTA}                                    ║
║                    {Colors.CYAN}🔮 \"Find what they thought was deleted\"{Colors.MAGENTA}                              ║
║                                                                                  ║
║                         {Colors.GREEN}🛠️  Crafted by{Colors.MAGENTA}                                         ║
║                                                                                  ║
║   {Colors.RED}██████╗ {Colors.YELLOW}██╗  ██╗ {Colors.GREEN}██████╗ {Colors.CYAN}███████╗ {Colors.BLUE}███╗   ██╗ {Colors.MAGENTA}██╗██╗  ██╗{Colors.MAGENTA}                             ║
║   {Colors.RED}██╔══██╗{Colors.YELLOW}██║  ██║{Colors.GREEN}██╔═══██╗{Colors.CYAN}██╔════╝{Colors.BLUE}████╗  ██║{Colors.MAGENTA}██║╚██╗██╔╝{Colors.MAGENTA}                             ║
║   {Colors.RED}██████╔╝{Colors.YELLOW}███████║{Colors.GREEN}██║   ██║{Colors.CYAN}█████╗  {Colors.BLUE}██╔██╗ ██║{Colors.MAGENTA}██║ ╚███╔╝ {Colors.MAGENTA}                             ║
║   {Colors.RED}██╔═══╝ {Colors.YELLOW}██╔══██║{Colors.GREEN}██║   ██║{Colors.CYAN}██╔══╝  {Colors.BLUE}██║╚██╗██║{Colors.MAGENTA}██║ ██╔██╗ {Colors.MAGENTA}                             ║
║   {Colors.RED}██║     {Colors.YELLOW}██║  ██║{Colors.GREEN}╚██████╔╝{Colors.CYAN}███████╗{Colors.BLUE}██║ ╚████║{Colors.MAGENTA}██║██╔╝ ██╗{Colors.MAGENTA}                             ║
║   {Colors.RED}╚═╝     {Colors.YELLOW}╚═╝  ╚═╝{Colors.GREEN} ╚═════╝ {Colors.CYAN}╚══════╝{Colors.BLUE}╚═╝  ╚═══╝{Colors.MAGENTA}╚═╝╚═╝  ╚═╝{Colors.MAGENTA}                             ║
║                                                                                  ║
║                         {Colors.WHITE}🐦  @phoenix_security  |                   ║
║                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(credit)

# ============================================================================
# CORE SCANNER CLASS
# ============================================================================

class GhostRouteScanner:
    """Main scanner class for finding ghost endpoints."""
    
    def __init__(self, target: str, threads: int = 10, timeout: int = 5, 
                 deep: bool = False, verbose: bool = False):
        self.target = target.rstrip('/')
        self.base_domain = urlparse(target).netloc
        self.threads = threads
        self.timeout = timeout
        self.deep = deep
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.session.verify = False
        
        self.js_files: Set[str] = set()
        self.potential_endpoints: Set[Tuple[str, str]] = set()
        self.findings: List[GhostFinding] = []
        
        self.lock = threading.Lock()
        
    def log(self, message: str, level: str = "INFO"):
        """Pretty logging with colors."""
        if level == "SUCCESS":
            print(f"{Colors.GREEN}[+] {message}{Colors.RESET}")
        elif level == "WARNING":
            print(f"{Colors.YELLOW}[!] {message}{Colors.RESET}")
        elif level == "ERROR":
            print(f"{Colors.RED}[-] {message}{Colors.RESET}")
        elif level == "GHOST":
            print(f"{Colors.MAGENTA}[👻] {message}{Colors.RESET}")
        elif level == "INFO" and self.verbose:
            print(f"{Colors.BLUE}[*] {message}{Colors.RESET}")
    
    def fetch_url(self, url: str) -> Optional[str]:
        """Fetch URL content safely."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            if self.verbose:
                self.log(f"Failed to fetch {url}: {e}", "ERROR")
        return None
    
    # ========================================================================
    # PHASE 1: JAVASCRIPT DISCOVERY
    # ========================================================================
    
    def discover_js_files(self):
        """Find all JavaScript files on target."""
        self.log(f"Discovering JavaScript files on {self.target}...", "INFO")
        
        html = self.fetch_url(self.target)
        if not html:
            self.log("Failed to fetch main page", "ERROR")
            return
        
        # Extract script tags
        patterns = [
            r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']',
            r'<script[^>]+src=["\']([^"\']+\.jsx[^"\']*)["\']',
            r'<script[^>]+src=["\']([^"\']+\.ts[^"\']*)["\']',
            r'<link[^>]+href=["\']([^"\']+\.js[^"\']*)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                full_url = urljoin(self.target, match)
                if self.base_domain in full_url:
                    self.js_files.add(full_url)
        
        # Check for source maps
        for js_file in list(self.js_files):
            map_url = js_file + '.map'
            try:
                response = self.session.head(map_url, timeout=self.timeout)
                if response.status_code == 200:
                    self.js_files.add(map_url)
                    self.log(f"Found source map: {map_url}", "SUCCESS")
            except:
                pass
        
        self.log(f"Discovered {len(self.js_files)} JavaScript files", "SUCCESS")
    
    # ========================================================================
    # PHASE 2: COMMENT EXTRACTION
    # ========================================================================
    
    def extract_from_js(self, js_url: str):
        """Extract commented endpoints from a JS file."""
        content = self.fetch_url(js_url)
        if not content:
            return
        
        found_count = 0
        for pattern_name, pattern in COMMENTED_PATTERNS.items():
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                endpoint = match if isinstance(match, str) else match[0]
                if endpoint and len(endpoint) > 1:
                    if endpoint.startswith('/') or endpoint.startswith('http'):
                        with self.lock:
                            self.potential_endpoints.add((endpoint, f"Commented in {js_url}"))
                        found_count += 1
        
        if found_count > 0 and self.verbose:
            self.log(f"Found {found_count} ghosts in {js_url}", "GHOST")
    
    def scan_all_js_files(self):
        """Scan all discovered JS files."""
        self.log("Scanning JavaScript files for commented routes...", "INFO")
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.extract_from_js, url): url 
                      for url in self.js_files}
            
            for i, future in enumerate(as_completed(futures), 1):
                if i % 10 == 0:
                    self.log(f"Progress: {i}/{len(self.js_files)} files", "INFO")
        
        self.log(f"Extracted {len(self.potential_endpoints)} potential endpoints", "SUCCESS")
    
    # ========================================================================
    # PHASE 3: WAYBACK MACHINE (Deep Scan Only)
    # ========================================================================
    
    def query_wayback(self):
        """Fetch historical URLs from Wayback Machine."""
        if not self.deep:
            return
        
        self.log("Querying Wayback Machine for historical endpoints...", "INFO")
        
        cdx_url = "http://web.archive.org/cdx/search/cdx"
        params = {
            'url': f"{self.target}/*",
            'output': 'json',
            'fl': 'original',
            'filter': 'statuscode:200',
            'collapse': 'urlkey',
            'limit': 1000
        }
        
        try:
            response = self.session.get(cdx_url, params=params, timeout=30)
            data = response.json()
            
            for entry in data[1:]:
                url = entry[0]
                parsed = urlparse(url)
                path = parsed.path
                
                interesting = ['/api/', '/admin/', '/internal/', '/v1/', '/v2/', 
                              '/backup/', '/debug/', '/export/', '/download/']
                if any(p in path for p in interesting):
                    with self.lock:
                        self.potential_endpoints.add((path, "Wayback Machine (historical)"))
            
            self.log(f"Found historical endpoints from Wayback", "SUCCESS")
        except Exception as e:
            self.log(f"Wayback query failed: {e}", "WARNING")
    
    # ========================================================================
    # PHASE 4: VALIDATION
    # ========================================================================
    
    def assess_risk(self, endpoint: str, status_code: int) -> str:
        """Determine risk level of endpoint."""
        endpoint_lower = endpoint.lower()
        
        high_risk = ['/admin/', '/backup/', '/export/', '/download/', 
                    '/debug/', '/internal/', '/migrate', '/dump']
        medium_risk = ['/api/', '/v1/', '/v2/', '/graphql', '/user/', '/account/']
        
        if any(p in endpoint_lower for p in high_risk):
            return "HIGH"
        elif any(p in endpoint_lower for p in medium_risk):
            return "MEDIUM"
        elif status_code in [200, 500]:
            return "MEDIUM"
        else:
            return "LOW"
    
    def validate_endpoint(self, endpoint: str, source: str) -> Optional[GhostFinding]:
        """Test if endpoint actually exists."""
        test_url = urljoin(self.target, endpoint)
        
        try:
            response = self.session.head(test_url, timeout=self.timeout, 
                                        allow_redirects=True)
            
            interesting_codes = [200, 201, 202, 204, 401, 403, 405, 500]
            
            if response.status_code in interesting_codes:
                risk = self.assess_risk(endpoint, response.status_code)
                return GhostFinding(
                    url=test_url,
                    status_code=response.status_code,
                    source=source,
                    evidence=f"Responds with {response.status_code}",
                    risk=risk
                )
                
            elif response.status_code == 405:
                get_response = self.session.get(test_url, timeout=self.timeout)
                if get_response.status_code in interesting_codes:
                    risk = self.assess_risk(endpoint, get_response.status_code)
                    return GhostFinding(
                        url=test_url,
                        status_code=get_response.status_code,
                        source=source,
                        evidence=f"GET responds with {get_response.status_code}",
                        risk=risk
                    )
        except:
            pass
        
        return None
    
    def validate_all(self):
        """Validate all discovered endpoints."""
        self.log(f"Validating {len(self.potential_endpoints)} potential endpoints...", "INFO")
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {}
            for endpoint, source in self.potential_endpoints:
                futures[executor.submit(self.validate_endpoint, endpoint, source)] = endpoint
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if completed % 20 == 0:
                    self.log(f"Validation: {completed}/{len(futures)}", "INFO")
                
                finding = future.result()
                if finding:
                    self.findings.append(finding)
                    if finding.risk == "HIGH":
                        self.log(f"🔥 CRITICAL: {finding.url}", "GHOST")
                    elif finding.risk == "MEDIUM":
                        self.log(f"⚠️  Found: {finding.url}", "GHOST")
    
    # ========================================================================
    # MAIN SCAN
    # ========================================================================
    
    def scan(self) -> List[GhostFinding]:
        """Run complete scan."""
        # Phase 1
        self.discover_js_files()
        
        # Phase 2
        if self.js_files:
            self.scan_all_js_files()
        
        # Phase 3
        if self.deep:
            self.query_wayback()
        
        # Phase 4
        if self.potential_endpoints:
            self.validate_all()
        
        return self.findings
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def generate_report(self, output_file: str):
        """Generate detailed report."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("👻 GHOSTROUTE PRO SCAN REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Target: {self.target}\n")
            f.write(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Mode: {'Deep' if self.deep else 'Quick'}\n")
            f.write(f"Total Ghosts: {len(self.findings)}\n")
            f.write(f"Crafted by: P.H.O.E.N.I.X\n\n")
            
            for risk_level in ["HIGH", "MEDIUM", "LOW"]:
                findings = [f for f in self.findings if f.risk == risk_level]
                if findings:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"{risk_level} RISK FINDINGS ({len(findings)})\n")
                    f.write(f"{'='*80}\n\n")
                    
                    for finding in findings:
                        f.write(f"URL: {finding.url}\n")
                        f.write(f"Status: {finding.status_code}\n")
                        f.write(f"Source: {finding.source}\n")
                        f.write(f"Evidence: {finding.evidence}\n")
                        f.write("-"*40 + "\n")
        
        self.log(f"Report saved to {output_file}", "SUCCESS")
    
    def export_json(self, output_file: str):
        """Export findings as JSON."""
        data = {
            "target": self.target,
            "scan_time": datetime.now().isoformat(),
            "mode": "deep" if self.deep else "quick",
            "total_findings": len(self.findings),
            "crafted_by": "P.H.O.E.N.I.X",
            "findings": [
                {
                    "url": f.url,
                    "status_code": f.status_code,
                    "source": f.source,
                    "evidence": f.evidence,
                    "risk": f.risk,
                    "timestamp": f.timestamp
                }
                for f in self.findings
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        self.log(f"JSON export saved to {output_file}", "SUCCESS")

# ============================================================================
# INTERACTIVE MENU
# ============================================================================

def interactive_menu():
    """Display interactive menu for no-argument mode."""
    print_banner()
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}🎯 ENTER TARGET URL:{Colors.RESET}")
    print(f"{Colors.CYAN}   (Example: https://example.com){Colors.RESET}")
    target = input(f"{Colors.YELLOW}   → {Colors.RESET}").strip()
    
    if not target:
        print(f"\n{Colors.RED}❌ No target provided. Exiting...{Colors.RESET}")
        sys.exit(1)
    
    if not target.startswith(('http://', 'https://')):
        target = 'https://' + target
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}🔍 SELECT SCAN MODE:{Colors.RESET}")
    print(f"   {Colors.CYAN}1.{Colors.RESET} {Colors.GREEN}Quick Scan{Colors.RESET} - Fast (2-3 min) - Recommended for initial recon")
    print(f"   {Colors.CYAN}2.{Colors.RESET} {Colors.BLUE}Deep Scan{Colors.RESET} - Comprehensive (5-10 min) - Includes Wayback Machine")
    
    mode = input(f"\n{Colors.YELLOW}   → Enter choice (1/2) [default: 1]: {Colors.RESET}").strip()
    deep = (mode == '2')
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}💾 SAVE REPORT?{Colors.RESET}")
    print(f"   {Colors.CYAN}1.{Colors.RESET} No (just display results)")
    print(f"   {Colors.CYAN}2.{Colors.RESET} Text report (.txt)")
    print(f"   {Colors.CYAN}3.{Colors.RESET} JSON export (.json)")
    print(f"   {Colors.CYAN}4.{Colors.RESET} Both formats")
    
    report_choice = input(f"\n{Colors.YELLOW}   → Enter choice (1-4) [default: 1]: {Colors.RESET}").strip()
    
    return target, deep, report_choice

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="👻 GhostRoute Pro - Find hidden endpoints in commented code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║                              📖 EXAMPLES                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}

  {Colors.GREEN}# Interactive mode (no arguments){Colors.RESET}
  python ghostroute.py

  {Colors.GREEN}# Quick scan{Colors.RESET}
  python ghostroute.py --target https://example.com --quick

  {Colors.GREEN}# Deep scan with all modules{Colors.RESET}
  python ghostroute.py --target https://example.com --deep

  {Colors.GREEN}# Save reports{Colors.RESET}
  python ghostroute.py -t https://example.com -q -o report.txt
  python ghostroute.py -t https://example.com -d --json findings.json
  python ghostroute.py -t https://example.com -d -o report.txt --json data.json

  {Colors.GREEN}# Advanced options{Colors.RESET}
  python ghostroute.py -t https://example.com --threads 20 --timeout 10 -v

{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║                    🛠️  CRAFTED BY: P.H.O.E.N.I.X                               ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
        """
    )
    
    parser.add_argument('--target', '-t', help='Target URL to scan')
    parser.add_argument('--quick', '-q', action='store_true', help='Quick scan mode')
    parser.add_argument('--deep', '-d', action='store_true', help='Deep scan mode (includes Wayback)')
    parser.add_argument('--threads', type=int, default=10, help='Number of threads (default: 10)')
    parser.add_argument('--timeout', type=int, default=5, help='Request timeout in seconds (default: 5)')
    parser.add_argument('--output', '-o', help='Save text report to file')
    parser.add_argument('--json', '-j', help='Export findings as JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--version', action='version', version='GhostRoute Pro v2.0.0 - Crafted by P.H.O.E.N.I.X')
    
    args = parser.parse_args()
    
    # Interactive mode if no target provided
    if not args.target:
        target, deep, report_choice = interactive_menu()
        threads = 10
        timeout = 5
        verbose = False
        output_file = None
        json_file = None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if report_choice == '2':
            output_file = f"ghostroute_report_{timestamp}.txt"
        elif report_choice == '3':
            json_file = f"ghostroute_findings_{timestamp}.json"
        elif report_choice == '4':
            output_file = f"ghostroute_report_{timestamp}.txt"
            json_file = f"ghostroute_findings_{timestamp}.json"
    else:
        target = args.target
        deep = args.deep
        threads = args.threads
        timeout = args.timeout
        verbose = args.verbose
        output_file = args.output
        json_file = args.json
    
    # Print banner for command-line mode
    if args.target:
        print_banner()
    
    mode_str = "Deep" if deep else "Quick"
    print_scan_header(target, mode_str, threads)
    
    # Create scanner
    scanner = GhostRouteScanner(
        target=target,
        threads=threads,
        timeout=timeout,
        deep=deep,
        verbose=verbose
    )
    
    # Run scan
    start_time = time.time()
    findings = scanner.scan()
    elapsed = time.time() - start_time
    
    # Count by risk
    high = len([f for f in findings if f.risk == "HIGH"])
    medium = len([f for f in findings if f.risk == "MEDIUM"])
    low = len([f for f in findings if f.risk == "LOW"])
    
    # Print footer
    print_scan_footer(len(findings), high, medium, low, elapsed)
    
    # Display results
    if findings:
        print(f"{Colors.CYAN}{Colors.BOLD}📋 TOP FINDINGS:{Colors.RESET}\n")
        for i, finding in enumerate(findings[:10], 1):
            if finding.risk == "HIGH":
                risk_display = f"{Colors.RED}[HIGH]{Colors.RESET}"
            elif finding.risk == "MEDIUM":
                risk_display = f"{Colors.YELLOW}[MEDIUM]{Colors.RESET}"
            else:
                risk_display = f"{Colors.BLUE}[LOW]{Colors.RESET}"
            
            print(f"  {Colors.WHITE}{i}.{Colors.RESET} {risk_display} {Colors.CYAN}{finding.url}{Colors.RESET}")
            source_short = finding.source[:60] + "..." if len(finding.source) > 60 else finding.source
            print(f"     {Colors.GREEN}└──{Colors.RESET} Status: {finding.status_code} | Source: {source_short}")
        print()
    
    # Generate reports
    if output_file:
        scanner.generate_report(output_file)
    
    if json_file:
        scanner.export_json(json_file)
    
    # Print credit
    print_credit()
    
    # Return code
    return 1 if high > 0 else 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Scan interrupted by user{Colors.RESET}")
        print_credit()
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Fatal error: {e}{Colors.RESET}")
        print_credit()
        sys.exit(1)