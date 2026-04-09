#!/usr/bin/env python3
"""
GHOSTROUTE PRO v6.0 - PROFESSIONAL EDITION
The Most Advanced Endpoint Discovery Tool Ever Built
Crafted by P.H.O.E.N.I.X
"""

import os
import re
import sys
import json
import time
import hashlib
import argparse
import threading
from urllib.parse import urlparse, urljoin, parse_qs, quote
from datetime import datetime
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

def install_deps():
    for pkg in ['requests', 'colorama']:
        try: __import__(pkg)
        except: os.system(f"{sys.executable} -m pip install {pkg} -q")

install_deps()

import requests
from colorama import init, Fore, Style
init(autoreset=True)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================================================
# COLORS
# ============================================================================
class C:
    R = Fore.RED
    G = Fore.GREEN
    Y = Fore.YELLOW
    B = Fore.BLUE
    M = Fore.MAGENTA
    C = Fore.CYAN
    W = Fore.WHITE
    X = Style.RESET_ALL
    BD = Style.BRIGHT

# ============================================================================
# BANNERS
# ============================================================================
BANNER = f"""
{C.M}{C.BD}╔══════════════════════════════════════════════════════════════════════════════════════╗
║  {C.C}██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗██████╗  ██████╗ ██╗   ██╗████████╗███████╗{C.M}  ║
║  {C.C}██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗██║   ██║╚══██╔══╝██╔════╝{C.M}  ║
║  {C.C}██║  ███╗███████║██║   ██║███████╗   ██║   ██████╔╝██║   ██║██║   ██║   ██║   █████╗  {C.M}  ║
║  {C.C}██║   ██║██╔══██║██║   ██║╚════██║   ██║   ██╔══██╗██║   ██║██║   ██║   ██║   ██╔══╝  {C.M}  ║
║  {C.C}╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   ██║  ██║╚██████╔╝╚██████╔╝   ██║   ███████╗{C.M}  ║
║  {C.C} ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝{C.M}  ║
╠══════════════════════════════════════════════════════════════════════════════════════════╣
║  {C.Y} PROFESSIONAL v6.0.0         │  {C.G}GOBUSTER+FFUF+HARVESTER+WAYBACK+GHOST+VULN+WAF{C.M}     ║
║  {C.B}  CRAFTED BY: P.H.O.E.N.I.X  │  {C.W}github.com/debjit604/ghostroute{C.M}                    ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝{C.X}
"""

COMMANDS = f"""
{C.C}{C.BD}╔══════════════════════════════════════════════════════════════════════════════════════╗
║                              {C.W}📖 COMMAND REFERENCE{C.C}                                         ║
╠══════════════════════════════════════════════════════════════════════════════════════════╣
║  {C.G}QUICK START:{C.X}                                                                              ║
║    {C.C}python ghostroute.py{C.X}                              → Interactive mode                    ║
║    {C.C}python ghostroute.py -t https://target.com{C.X}         → Full scan                          ║
║    {C.C}python ghostroute.py -t https://target.com --deep{C.X}  → Deep scan + vulns                  ║
║                                                                                                      ║
║  {C.G}SCAN MODES (-m):{C.X}                                                                          ║
║    {C.C}all{C.X} (default)  → Everything         {C.C}subdomain{C.X}  → Subdomains only              ║
║    {C.C}gobuster{C.X}       → Directories        {C.C}wayback{C.X}    → Wayback only                 ║
║    {C.C}ffuf{C.X}           → Files/backups      {C.C}ghost{C.X}      → Ghost detection              ║
║                                                                                                      ║
║  {C.G}OPTIONS:{C.X}                                                                                  ║
║    {C.C}--deep{C.X}              → Test for SQLi, XSS, LFI                                           ║
║    {C.C}--threads 50{C.X}        → Threads (default:30)                                              ║
║    {C.C}--timeout 10{C.X}        → Timeout (default:8)                                               ║
║    {C.C}--cookie \"session=abc\"{C.X} → Authentication cookies                                       ║
║    {C.C}--proxy http://127.0.0.1:8080{C.X} → Route through Burp                                      ║
║    {C.C}-v, --verbose{C.X}       → Verbose output                                                    ║
║    {C.C}-s, --silent{C.X}        → Minimal output                                                    ║
║                                                                                                      ║
║  {C.G}EXPORT:{C.X}                                                                                   ║
║    {C.C}--json report.json{C.X}  → JSON export                                                       ║
║    {C.C}--txt report.txt{C.X}    → TXT report                                                        ║
║                                                                                                      ║
║  {C.G}EXAMPLES:{C.X}                                                                                 ║
║    {C.W}python ghostroute.py -t admin.target.com --cookie \"sess=xxx\" --deep{C.X}                   ║
║    {C.W}python ghostroute.py -t target.com -m ghost --json ghosts.json{C.X}                          ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝{C.X}
"""

CREDIT = f"""
{C.M}╔══════════════════════════════════════════════════════════════════════════════════════════╗
║  {C.Y}👻 GHOSTROUTE PRO v6.0.0 FINAL  │  {C.C}GOBUSTER+FFUF+HARVESTER+WAYBACK+GHOST+VULN+WAF{C.M}      ║
║  {C.G}🛠️  CRAFTED WITH 💀 BY P.H.O.E.N.I.X  │  {C.W}⭐ github.com/debjit604/ghostroute{C.M}           ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝{C.X}
"""

# ============================================================================
# WORDLISTS
# ============================================================================
DIRS = ["admin", "api", "backup", "backups", "beta", "config", "css", "dashboard", "db", "debug",
        "dev", "development", "docs", "download", "files", "graphql", "images", "img", "includes",
        "internal", "js", "json", "lib", "login", "logs", "media", "metrics", "old", "panel",
        "phpmyadmin", "private", "scripts", "secret", "secure", "sql", "staff", "staging", "static",
        "stats", "status", "storage", "swagger", "temp", "test", "testing", "tmp", "upload",
        "uploads", "user", "v1", "v2", "v3", "vendor"]

FILES = ["index", "home", "main", "config", "setup", "install", "readme", "changelog", "license",
         "wp-config", "web.config", ".htaccess", "robots", "sitemap", "phpinfo", "info", "test", "backup"]

EXTS = ["", ".php", ".asp", ".aspx", ".jsp", ".html", ".json", ".xml", ".txt", ".log", ".bak",
        ".backup", ".old", ".sql", ".zip", ".tar", ".gz"]

SUBDOMAINS = ["www", "mail", "blog", "api", "dev", "develop", "development", "test", "testing",
              "staging", "stage", "beta", "demo", "portal", "admin", "adm", "internal", "private",
              "app", "apps", "mobile", "support", "help", "docs", "status", "monitor", "metrics",
              "logs", "cdn", "static", "assets", "media"]

GHOST_PATTERNS = [
    (r'(?://|/\*).*?app\.get\s*\(\s*["\']([^"\']+)["\']', 'GET'),
    (r'(?://|/\*).*?app\.post\s*\(\s*["\']([^"\']+)["\']', 'POST'),
    (r'(?://|/\*).*?router\.(?:get|post|put|delete)\s*\(\s*["\']([^"\']+)["\']', 'GET'),
    (r'(?://|/\*).*?app\.use\s*\(\s*["\']([^"\']+)["\']', 'GET'),
    (r'(?://|/\*).*?path\s*:\s*["\']([^"\']+)["\']', 'GET'),
    (r'#.*?@app\.route\s*\(\s*["\']([^"\']+)["\']', 'GET'),
    (r'//.*?Route::(?:get|post|put|delete)\s*\(\s*["\']([^"\']+)["\']', 'GET'),
    (r'//.*?@(?:Get|Post|Put|Delete)Mapping\s*\(\s*["\']([^"\']+)["\']', 'GET'),
    (r'(?://|#|/\*).*?(/api/[a-zA-Z0-9_\-/]+)', 'GET'),
    (r'(?://|#|/\*).*?(/admin[a-zA-Z0-9_\-/]*)', 'GET'),
    (r'(?://|#|/\*).*?(/backup[a-zA-Z0-9_\-/]*)', 'GET'),
    (r'(?://|#|/\*).*?(/debug[a-zA-Z0-9_\-/]*)', 'GET'),
    (r'(?://|#|/\*).*?(/internal[a-zA-Z0-9_\-/]*)', 'GET'),
    (r'(?://|#|/\*).*?(/v[0-9]+/[a-zA-Z0-9_\-/]+)', 'GET'),
    (r'(?://|#|/\*).*?(/graphql[a-zA-Z0-9_\-/]*)', 'POST'),
]

WAF_SIGS = {
    'Cloudflare': ['cf-ray', '__cfduid', 'cloudflare'],
    'AWS WAF': ['x-amzn-requestid', 'x-amz-cf-id'],
    'Akamai': ['x-akamai-transformed', 'akamai'],
    'Imperva': ['x-iinfo', 'incapsula', 'imperva'],
    'Sucuri': ['x-sucuri-id', 'sucuri'],
    'ModSecurity': ['mod_security', 'modsecurity'],
}

SQLI = [("' OR '1'='1", "Boolean"), ("' AND SLEEP(3)--", "Time")]
XSS = ["<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>"]
LFI = ["../../../etc/passwd", "php://filter/convert.base64-encode/resource=index"]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# ============================================================================
# SCANNER CLASS
# ============================================================================
class GhostRoute:
    
    def __init__(self, target, mode="all", threads=30, timeout=8, verbose=False, silent=False,
                 deep=False, cookies=None, headers=None, proxy=None):
        
        self.target = target.rstrip('/')
        self.base = urlparse(target).netloc
        self.mode = mode
        self.threads = min(threads, 100)
        self.timeout = timeout
        self.verbose = verbose
        self.silent = silent
        self.deep = deep
        
        self.sess = requests.Session()
        self.sess.headers.update(HEADERS)
        if headers: self.sess.headers.update(headers)
        if cookies: self.sess.cookies.update(cookies)
        if proxy: self.sess.proxies = {'http': proxy, 'https': proxy}
        self.sess.verify = False
        
        self.js_files = set()
        self.endpoints = set()
        self.results = []
        self.vulns = []
        self.subdomains = []
        self.waf_info = None
        
        self.lock = threading.Lock()
        self.total = 0
        self.done = 0
        self.scan_id = hashlib.md5(f"{target}{time.time()}".encode()).hexdigest()[:8]
    
    def log(self, msg, level="INFO"):
        if self.silent: return
        if level == "OK": print(f"{C.G}[+]{C.X} {msg}")
        elif level == "VULN": print(f"{C.R}[🔥]{C.X} {msg}")
        elif level == "GHOST": print(f"{C.M}[👻]{C.X} {msg}")
        elif level == "FOUND": print(f"{C.Y}[🔍]{C.X} {msg}")
        elif level == "WAF": print(f"{C.M}[🛡️]{C.X} {msg}")
        elif level == "INFO" and self.verbose: print(f"{C.B}[*]{C.X} {msg}")
    
    def fetch(self, url, method="GET"):
        try: return self.sess.request(method, url, timeout=self.timeout, allow_redirects=True)
        except: return None
    
    def assess_risk(self, url, status):
        ul = url.lower()
        critical = ['admin', 'backup', 'export', 'debug', 'internal', 'sql', 'exec']
        high = ['api/admin', 'graphql', 'dashboard']
        
        if status == 200:
            if any(p in ul for p in critical): return "CRITICAL"
            if any(p in ul for p in high): return "HIGH"
            if '/api/' in ul or '/v1/' in ul: return "MEDIUM"
            return "LOW"
        elif status in [401, 403]: return "MEDIUM"
        elif status >= 500: return "MEDIUM"
        return "LOW"
    
    def test_url(self, url, method, source, ttype):
        r = self.fetch(url, method)
        if not r: return None
        
        status = r.status_code
        risk = self.assess_risk(url, status)
        
        result = {'url': url, 'method': method, 'status': status, 'size': len(r.content),
                  'source': source, 'type': ttype, 'risk': risk}
        
        if self.deep and status == 200:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if params:
                param = list(params.keys())[0]
                for payload, ptype in SQLI:
                    test_url = url.replace(f"{param}=", f"{param}={quote(payload)}")
                    try:
                        start = time.time()
                        resp = self.sess.get(test_url, timeout=self.timeout)
                        if time.time() - start > 2.5:
                            self.vulns.append({'type': 'SQLi', 'url': test_url, 'payload': payload})
                            self.log(f"SQLi: {test_url}", "VULN")
                            break
                    except: pass
        
        return result
    
    def _run(self, tests):
        self.total += len(tests)
        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            fs = [ex.submit(self.test_url, *t) for t in tests]
            for f in as_completed(fs):
                with self.lock: self.done += 1
                if self.done % 30 == 0 and not self.silent:
                    pct = int(self.done / self.total * 100) if self.total else 0
                    print(f"\r{C.B}[*] Progress: {self.done}/{self.total} ({pct}%){C.X}", end="", flush=True)
                r = f.result()
                if r:
                    self.results.append(r)
                    if r['status'] == 200:
                        self.log(f"200 OK: {r['url']} [{r['risk']}]", "OK")
                    elif r['status'] in [403, 401]:
                        self.log(f"{r['status']} Protected: {r['url']}", "FOUND")
                    elif r['status'] >= 500:
                        self.log(f"{r['status']} Error: {r['url']}", "FOUND")
        if not self.silent: print()
    
    def gobuster(self):
        self.log("Directory brute force...", "INFO")
        tests = [(f"{self.target}/{d}", "GET", "Gobuster", "directory") for d in DIRS[:25]]
        self._run(tests)
    
    def ffuf(self):
        self.log("File fuzzing...", "INFO")
        tests = []
        for f in FILES[:10]:
            for e in ["", ".php", ".html", ".bak"]:
                tests.append((f"{self.target}/{f}{e}", "GET", "FFUF", "file"))
        for bp in ['backup', 'back']:
            for e in ['.zip', '.sql', '.tar']:
                tests.append((f"{self.target}/{bp}{e}", "GET", "FFUF", "backup"))
        self._run(tests)
    
    def subdomain(self):
        self.log("Subdomain enumeration...", "INFO")
        parts = self.base.split('.')
        base = '.'.join(parts[-2:]) if len(parts) > 2 else self.base
        for sub in SUBDOMAINS[:20]:
            sd = f"{sub}.{base}"
            r = self.fetch(f"https://{sd}")
            if r:
                self.subdomains.append({'domain': sd, 'status': r.status_code})
                self.log(f"Subdomain: {sd} ({r.status_code})", "FOUND")
    
    def wayback(self):
        self.log("Wayback Machine...", "INFO")
        try:
            r = self.sess.get("http://web.archive.org/cdx/search/cdx",
                              params={'url': f"{self.target}/*", 'output': 'json', 'limit': 300}, timeout=15)
            for e in r.json()[1:]:
                p = urlparse(e[0]).path
                if p and p != '/':
                    self.endpoints.add((urljoin(self.target, p), "GET", "Wayback", "historical"))
            self.log(f"Found {len(r.json())-1} historical URLs", "OK")
        except: pass
    
    def discover_js(self):
        r = self.fetch(self.target)
        if r:
            for m in re.findall(r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']', r.text, re.I):
                f = urljoin(self.target, m)
                if self.base in f: self.js_files.add(f)
        self.log(f"Found {len(self.js_files)} JS files", "OK")
    
    def extract_ghost(self, js):
        r = self.fetch(js)
        if not r: return
        for ptn, mtd in GHOST_PATTERNS:
            for m in re.findall(ptn, r.text, re.I | re.M):
                ep = m if isinstance(m, str) else m[0]
                if ep and len(ep) > 1:
                    if not ep.startswith('/'): ep = '/' + ep
                    if ep.startswith('/'):
                        with self.lock: self.endpoints.add((urljoin(self.target, ep), mtd, "Ghost", "commented"))
    
    def ghost(self):
        self.log("Ghost detection...", "INFO")
        self.discover_js()
        if self.js_files:
            with ThreadPoolExecutor(max_workers=self.threads) as ex:
                list(ex.map(self.extract_ghost, self.js_files))
            self.log(f"Extracted {len(self.endpoints)} ghost endpoints", "OK")
    
    def scan(self):
        if not self.silent:
            print(BANNER)
            print(COMMANDS)
            print(f"\n{C.C}══════════════════════════════════════════════════════════════════════════════════{C.X}")
            print(f"{C.G}🎯 Target: {self.target}  │  ⚙️ Mode: {self.mode.upper()}  │  🔬 Deep: {'ON' if self.deep else 'OFF'}  │  🧵 Threads: {self.threads}{C.X}")
            print(f"{C.C}══════════════════════════════════════════════════════════════════════════════════{C.X}\n")
        
        r = self.fetch(self.target)
        if r:
            detected = None
            for waf, sigs in WAF_SIGS.items():
                if any(s in str(r.headers).lower() or s in r.text.lower() for s in sigs):
                    detected = waf
                    break
            if detected:
                self.waf_info = {'detected': True, 'waf': detected}
                self.log(f"WAF DETECTED: {detected}", "WAF")
        
        if self.mode in ['all', 'gobuster']: self.gobuster()
        if self.mode in ['all', 'ffuf']: self.ffuf()
        if self.mode in ['all', 'subdomain']: self.subdomain()
        if self.mode in ['all', 'wayback']: self.wayback()
        if self.mode in ['all', 'ghost']: self.ghost()
        
        if self.endpoints:
            tests = [(u, m, s, t) for u, m, s, t in self.endpoints]
            self._run(tests)
        
        return self.results
    
    def display(self):
        if not self.results:
            print(f"\n{C.Y}[!] No endpoints found.{C.X}")
            return
        
        st = defaultdict(int)
        risks = defaultdict(int)
        types = defaultdict(int)
        for r in self.results:
            st[r['status']] += 1
            risks[r['risk']] += 1
            types[r['type']] += 1
        
        print(f"\n{C.C}══════════════════════════════════════════════════════════════════════════════════{C.X}")
        print(f"{C.G}{C.BD}✅ SCAN COMPLETE{C.X}")
        print(f"{C.C}══════════════════════════════════════════════════════════════════════════════════{C.X}\n")
        
        if self.waf_info:
            print(f"  {C.Y}🛡️ WAF: {self.waf_info['waf']}{C.X}\n")
        
        print(f"  {C.BD}STATUS CODES:{C.X}")
        for s, c in sorted(st.items()):
            col = C.G if s==200 else (C.Y if s in [401,403] else C.C if s in [301,302] else C.M if s>=500 else C.W)
            print(f"    {col}{s}{C.X}: {c}")
        
        print(f"\n  {C.BD}RISK LEVELS:{C.X}")
        print(f"    {C.R}CRITICAL: {risks.get('CRITICAL', 0)}{C.X}  {C.R}HIGH: {risks.get('HIGH', 0)}{C.X}  {C.Y}MEDIUM: {risks.get('MEDIUM', 0)}{C.X}  {C.B}LOW: {risks.get('LOW', 0)}{C.X}")
        
        print(f"\n  {C.BD}ENDPOINT TYPES:{C.X}")
        for t, c in sorted(types.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {C.C}{t}{C.X}: {c}")
        
        print(f"\n{C.C}══════════════════════════════════════════════════════════════════════════════════{C.X}")
        print(f"  {C.BD}📋 TOTAL ENDPOINTS: {len(self.results)}  │  🌐 SUBDOMAINS: {len(self.subdomains)}  │  🔥 VULNS: {len(self.vulns)}{C.X}")
        print(f"{C.C}══════════════════════════════════════════════════════════════════════════════════{C.X}")
        
        critical = [r for r in self.results if r['risk'] in ['CRITICAL', 'HIGH']]
        if critical:
            print(f"\n{C.R}{C.BD}🔥 CRITICAL/HIGH FINDINGS:{C.X}")
            for i, r in enumerate(critical[:10], 1):
                print(f"  {i:>2}. {C.R}[{r['risk']}]{C.X} {r['url']}")
        
        if self.vulns:
            print(f"\n{C.R}{C.BD}💀 VULNERABILITIES:{C.X}")
            for v in self.vulns[:5]:
                print(f"  {C.R}[{v['type']}]{C.X} {v['url']}")
    
    def export_json(self, fname):
        data = {
            'target': self.target, 'scan_id': self.scan_id, 'time': datetime.now().isoformat(),
            'mode': self.mode, 'deep': self.deep, 'crafted_by': 'P.H.O.E.N.I.X',
            'waf': self.waf_info, 'stats': {'endpoints': len(self.results), 'subdomains': len(self.subdomains), 'vulns': len(self.vulns)},
            'findings': self.results, 'vulnerabilities': self.vulns, 'subdomains': self.subdomains
        }
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.log(f"JSON saved: {fname}", "OK")
    
    def export_txt(self, fname):
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(f"GHOSTROUTE PRO v6.0 - REPORT\n{'═'*60}\n\nTarget: {self.target}\nScan ID: {self.scan_id}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            if self.waf_info: f.write(f"WAF: {self.waf_info['waf']}\n\n")
            f.write(f"ENDPOINTS ({len(self.results)})\n{'─'*40}\n")
            for r in self.results:
                f.write(f"[{r['status']}] {r['method']} {r['url']} ({r['risk']})\n")
            if self.vulns:
                f.write(f"\nVULNERABILITIES ({len(self.vulns)})\n{'─'*40}\n")
                for v in self.vulns: f.write(f"[{v['type']}] {v['url']}\n")
        self.log(f"TXT saved: {fname}", "OK")

# ============================================================================
# INTERACTIVE
# ============================================================================
def interactive():
    print(BANNER)
    print(f"\n{C.G}🎯 Enter target URL:{C.X}")
    t = input(f"{C.Y}   → {C.X}").strip()
    if not t: return None, None, None
    if not t.startswith(('http://', 'https://')): t = 'https://' + t
    
    print(f"\n{C.G}🔍 Scan mode:{C.X}")
    print(f"   1. ALL  2. Gobuster  3. FFUF  4. Subdomain  5. Wayback  6. Ghost")
    m = input(f"{C.Y}   → Choice (1-6) [1]: {C.X}").strip()
    modes = ['all', 'gobuster', 'ffuf', 'subdomain', 'wayback', 'ghost']
    mode = modes[int(m)-1] if m.isdigit() and 1<=int(m)<=6 else 'all'
    
    print(f"\n{C.G}🔬 Deep scan (SQLi, XSS, LFI)?{C.X}")
    d = input(f"{C.Y}   → (y/n) [n]: {C.X}").strip().lower()
    return t, mode, d == 'y'

# ============================================================================
# MAIN
# ============================================================================
def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-t', '--target')
    parser.add_argument('-m', '--mode', default='all')
    parser.add_argument('-d', '--deep', action='store_true')
    parser.add_argument('--threads', type=int, default=30)
    parser.add_argument('--timeout', type=int, default=8)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-s', '--silent', action='store_true')
    parser.add_argument('--proxy')
    parser.add_argument('--cookie')
    parser.add_argument('--json')
    parser.add_argument('--txt')
    parser.add_argument('-h', '--help', action='store_true')
    
    args = parser.parse_args()
    
    if args.help or len(sys.argv) == 1:
        print(BANNER)
        print(COMMANDS)
        if len(sys.argv) == 1:
            t, m, d = interactive()
            if not t: return 1
            args.target, args.mode, args.deep = t, m, d
        else: return 0
    
    if not args.target:
        print(f"{C.R}[-] Target required!{C.X}")
        return 1
    
    if not args.target.startswith(('http://', 'https://')):
        args.target = 'https://' + args.target
    
    cookies = {}
    if args.cookie:
        for c in args.cookie.split(';'):
            if '=' in c: k, v = c.strip().split('=', 1); cookies[k] = v
    
    scanner = GhostRoute(target=args.target, mode=args.mode, threads=args.threads, timeout=args.timeout,
                         verbose=args.verbose, silent=args.silent, deep=args.deep,
                         cookies=cookies, proxy=args.proxy)
    
    start = time.time()
    scanner.scan()
    
    if not args.silent:
        print(f"\n{C.G}⏱️  Completed in {time.time()-start:.2f}s{C.X}")
    
    scanner.display()
    
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    scanner.export_json(args.json or f"ghostroute_{scanner.scan_id}.json")
    scanner.export_txt(args.txt or f"ghostroute_{scanner.scan_id}.txt")
    
    if not args.silent: print(CREDIT)
    return 0

if __name__ == "__main__":
    try: sys.exit(main())
    except KeyboardInterrupt: print(f"\n{C.Y}[!] Interrupted{C.X}"); sys.exit(130)
