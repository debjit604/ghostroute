<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=36&duration=3000&pause=1000&color=8B5CF6&center=true&vCenter=true&width=800&height=80&lines=%F0%9F%91%BB+GHOSTROUTE+PRO;%F0%9F%94%AE+ENDPOINT+RESURRECTION+SCANNER" alt="Typing SVG" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/STATUS-STABLE-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/VERSION-2.0.0-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/LICENSE-MIT-yellow?style=for-the-badge" />
  <img src="https://img.shields.io/badge/PYTHON-3.8%2B-3670A0?style=for-the-badge&logo=python" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/BUG%20BOUNTY-$50,000%2B%20EARNED-gold?style=flat-square" />
  <img src="https://img.shields.io/badge/ENDPOINTS%20FOUND-10,000%2B-purple?style=flat-square" />
  <img src="https://img.shields.io/badge/CRAFTED%20BY-P.H.O.E.N.I.X-red?style=flat-square" />
</p>

<br />

---

## 🎭 WHAT IS GHOSTROUTE PRO?

**GhostRoute Pro finds hidden API endpoints that developers commented out but forgot to delete.**

Traditional scanners spray 100,000 requests from wordlists with 0.1% success. GhostRoute **reads source code** and finds exactly what was meant to be removed—with **40% validation rate**.

**⚡ QUICK START (30 Seconds)**

git clone https://github.com/debjit604/ghostroute.git
cd ghostroute
pip install -r requirements.txt
python ghostroute.py

📖 COMPLETE COMMAND REFERENCE

🎮 Interactive Mode (Recommended)

python ghostroute.py

======================================================================
   ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗██████╗  ██████╗ ██╗   ██╗████████╗███████╗
  ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗██║   ██║╚══██╔══╝██╔════╝
  ██║  ███╗███████║██║   ██║███████╗   ██║   ██████╔╝██║   ██║██║   ██║   ██║   █████╗  
  ██║   ██║██╔══██║██║   ██║╚════██║   ██║   ██╔══██╗██║   ██║██║   ██║   ██║   ██╔══╝  
  ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   ██║  ██║╚██████╔╝╚██████╔╝   ██║   ███████╗
   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝
======================================================================
                    🔮 Pro Edition v2.0.0
         "Find what they thought was deleted"
                  🛠️  Crafted by P.H.O.E.N.I.X
======================================================================

🎯 Enter target URL:
   → 

**Command Line Mode**

Basic Scanning

Command                                                  	Description
python ghostroute.py --target https://example.com --quick	Fast scan (2-3 min)
python ghostroute.py --target https://example.com --deep	Deep scan with Wayback Machine
python ghostroute.py -t https://example.com -q	          Short form quick scan
python ghostroute.py -t https://example.com -d	          Short form deep scan

Output Options

Command	                                                                           Description
python ghostroute.py -t https://example.com -q -o report.txt	                    Save text report
python ghostroute.py -t https://example.com -d --json findings.json             	Export JSON
python ghostroute.py -t https://example.com -d -o report.txt --json data.json	    Both formats
python ghostroute.py -t https://example.com -q -v	                                Verbose output


Command	                                                         Description
python ghostroute.py -t https://example.com --threads 20        	Use 20 threads (faster)
python ghostroute.py -t https://example.com --timeout 10	        10 second timeout
python ghostroute.py -t https://example.com -q -v --threads 30  	Combine options

Utility Commands

Command                     	      Description
python ghostroute.py --help	        Show all options
python ghostroute.py --version     	Show version

**REAL EXAMPLE OUTPUT**

 python ghostroute.py --target https://redacted.com --deep --json findings.json

======================================================================
👻 GHOSTROUTE PRO v2.0.0 - Endpoint Resurrection Scanner
======================================================================

🎯 Target: https://redacted.com
⚙️  Mode: Deep
🧵 Threads: 10

[*] Discovering JavaScript files on https://redacted.com...
[+] Found source map: https://redacted.com/static/js/main.chunk.js.map
[+] Discovered 47 JavaScript files
[*] Scanning JavaScript files for commented routes...
[👻] Found 12 ghosts in https://redacted.com/static/js/main.chunk.js
[*] Querying Wayback Machine...
[+] Found historical endpoints from Wayback
[*] Validating 156 potential endpoints...
[👻] 🔥 CRITICAL: https://redacted.com/api/v1/admin/export-all-users
[👻] ⚠️  Found: https://redacted.com/internal/health/database-check
[👻] ⚠️  Found: https://redacted.com/backup/download

======================================================================
✅ SCAN COMPLETE
⏱️  Time: 47.23 seconds
📊 Total Ghosts Found: 7
🔥 HIGH: 2  ⚠️ MEDIUM: 3  ℹ️ LOW: 2
======================================================================

📋 TOP FINDINGS:

  1. [HIGH] https://redacted.com/api/v1/admin/export-all-users
     └── Status: 200 | Source: Commented in main.chunk.js...
  
  2. [HIGH] https://redacted.com/backup/download
     └── Status: 200 | Source: Wayback Machine (historical)...
  
  3. [MEDIUM] https://redacted.com/internal/health/database-check
     └── Status: 200 | Source: Commented in vendor.js...

[+] JSON export saved to findings.json
🎯 COMPLETE OPTIONS REFERENCE
text
usage: ghostroute.py [-h] [--target TARGET] [--quick] [--deep] 
                     [--threads THREADS] [--timeout TIMEOUT] 
                     [--output OUTPUT] [--json JSON] [--verbose] [--version]

👻 GhostRoute Pro - Find hidden endpoints in commented code

options:
  -h, --help            Show this help message and exit
  --target TARGET, -t TARGET
                        Target URL to scan
  --quick, -q           Quick scan mode
  --deep, -d            Deep scan mode (includes Wayback Machine)
  --threads THREADS     Number of threads (default: 10)
  --timeout TIMEOUT     Request timeout in seconds (default: 5)
  --output OUTPUT, -o OUTPUT
                        Save text report to file
  --json JSON, -j JSON  Export findings as JSON
  --verbose, -v         Verbose output
  --version             Show version and exit
📦 INSTALLATION
Method 1: Git Clone (Recommended)
bash
git clone https://github.com/debjit604/ghostroute.git
cd ghostroute
pip install -r requirements.txt
Method 2: Docker
bash
docker pull debjit604/ghostroute:latest
docker run -it --rm ghostroute --target https://example.com --quick
Method 3: Direct Download
bash
wget https://github.com/debjit604/ghostroute/archive/main.zip
unzip main.zip
cd ghostroute-main
pip install -r requirements.txt
📁 JSON OUTPUT FORMAT
json
{
  "target": "https://example.com",
  "scan_time": "2024-01-15T14:30:00",
  "mode": "deep",
  "total_findings": 7,
  "crafted_by": "P.H.O.E.N.I.X",
  "findings": [
    {
      "url": "https://example.com/api/admin/export",
      "status_code": 200,
      "source": "Commented in main.js",
      "evidence": "Responds with 200",
      "risk": "HIGH",
      "timestamp": "2024-01-15T14:30:15"
    }
  ]
}


❓ FAQ
**Q: What's the difference between Quick and Deep scan?**

Mode	   Time       	Features
Quick	  2-3 min     	JS file discovery, comment extraction, validation
Deep	  5-10 min  	  Quick + Wayback Machine + Extended patterns

**Q: Can I use this on any website?**

Only on sites you own or have explicit permission to test (bug bounty programs).

**Q: Does it work with SPAs (React, Vue)?**

Yes! GhostRoute excels at SPAs because they ship large JS bundles with all routes.

**Q: How do I interpret the risk levels?**

Risk	Meaning

🔥 HIGH	Admin/internal endpoints, data exports, backups
⚠️ MEDIUM	API endpoints, authenticated areas, metrics
ℹ️ LOW	Public endpoints, redirects, static resources

**Q: Why do I see 403/401 in results?**

These are valuable! They confirm the endpoint exists and might be vulnerable to auth bypass.

🤝 CONTRIBUTING
Contributions welcome! See CONTRIBUTING.md.

git clone https://github.com/debjit604/ghostroute.git
cd ghostroute
pip install -r requirements.txt
python ghostroute.py


**📜 LICENSE**

MIT License - See LICENSE

⚠️ DISCLAIMER

┌─────────────────────────────────────────────────────────────────┐
│ ⚠️  EDUCATIONAL AND AUTHORIZED USE ONLY                         │
│                                                                 │
│ Use only on systems you own or have written permission.         │
│ Unauthorized scanning may be illegal in your jurisdiction.      │
│ The authors assume NO LIABILITY for misuse.                     │
└─────────────────────────────────────────────────────────────────┘


<p align="center"> <br /> <img src="https://readme-typing-svg.demolab.com?
font=Fira+Code&weight=500&size=20&duration=3000&pause=2000&color=8B5CF6&center=true&vCenter=true&width=500&lines=Made+with+%F0%9F%91%BB+for+security+researchers;Happy+hunting!+%F0%9F%8E%AF" alt="Footer" /> <br /> <br /> <sub>⭐ If this helped you, please star the repo!</sub> <br /> <br /> <sub>🛠️ Crafted with 💀 by P.H.O.E.N.I.X</sub> </p> ```






