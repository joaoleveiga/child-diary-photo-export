#!/usr/bin/env python3
"""Generate static GitHub.io page with latest releases."""

import json
import os
import requests
from datetime import datetime
from pathlib import Path

REPO = "SamuelNLP/child-diary-photo-export"
GITHUB_API = f"https://api.github.com/repos/{REPO}/releases"

# CSS content
CSS = """
/* Simple, elegant styling */
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
    --primary: #C47F47;
    --primary-dark: #8B3A2B;
    --bg: #fafafa;
    --text: #333;
    --text-light: #666;
    --border: #e0e0e0;
    --shadow: 0 2px 8px rgba(0,0,0,0.08);
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: var(--text);
    background: var(--bg);
}

.container { max-width: 800px; margin: 0 auto; padding: 0 20px; }

header { padding: 40px 0; border-bottom: 1px solid var(--border); background: white; }
header .container { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; }
.logo { display: flex; align-items: center; gap: 12px; }
.logo h1 { font-size: 1.5rem; font-weight: 600; color: var(--text); }

nav { display: flex; gap: 10px; }
.lang-link { padding: 8px 16px; border: 1px solid var(--border); background: white; border-radius: 6px; text-decoration: none; color: var(--text); font-size: 0.9rem; }
.lang-link:hover { border-color: var(--primary); color: var(--primary); }
.lang-link.active { background: var(--primary); color: white; border-color: var(--primary); }
.lang-sep { color: var(--text-light); }

main { padding: 40px 0; }
.hero { text-align: center; padding: 20px 0 40px; }
.tagline { font-size: 1.25rem; color: var(--text-light); max-width: 600px; margin: 0 auto; }
.description { text-align: center; font-size: 1.1rem; color: var(--text); margin-bottom: 60px; }

h2 { font-size: 1.5rem; color: var(--text); margin-bottom: 30px; font-weight: 600; }

.releases-list { display: grid; gap: 20px; }
.release-card { background: white; border-radius: 12px; padding: 24px; box-shadow: var(--shadow); border: 1px solid var(--border); }
.release-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.release-version { font-size: 1.25rem; font-weight: 600; color: var(--primary); }
.release-date { font-size: 0.875rem; color: var(--text-light); text-align: right; }
.release-body { color: var(--text-light); margin-bottom: 20px; font-size: 0.95rem; }

.downloads { display: flex; gap: 12px; flex-wrap: wrap; }
.download-btn { display: inline-flex; align-items: center; gap: 8px; padding: 10px 16px; border-radius: 8px; font-size: 0.9rem; font-weight: 500; text-decoration: none; }
.download-btn:hover { transform: translateY(-1px); }
.download-btn.macos { background: #f0f0f0; color: var(--text); border: 1px solid var(--border); }
.download-btn.macos:hover { background: #e0e0e0; }
.download-btn.windows { background: #0078d4; color: white; }
.download-btn.windows:hover { background: #0063b1; }
.download-btn.linux { background: #e95420; color: white; }
.download-btn.linux:hover { background: #c94617; }
.download-btn span { font-size: 0.8rem; opacity: 0.8; }

.instructions, .features { margin: 40px 0; }
.instructions ol, .features ul { padding-left: 24px; margin-bottom: 20px; }
.instructions li, .features li { margin-bottom: 12px; color: var(--text); }

footer { padding: 40px 0; border-top: 1px solid var(--border); text-align: center; color: var(--text-light); font-size: 0.9rem; }
footer a { color: var(--primary); text-decoration: none; }
footer a:hover { text-decoration: underline; }

@media (max-width: 600px) {
    header .container { flex-direction: column; align-items: flex-start; }
    .logo { margin-bottom: 16px; }
    nav { width: 100%; }
    .lang-link { flex: 1; text-align: center; }
    .tagline { font-size: 1.1rem; }
}
"""

# Icon SVG
ICON_SVG = """<svg viewBox="0 0 100 100" width="40" height="40">
<defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#6F2F20"/>
        <stop offset="11%" stop-color="#7E3525"/>
        <stop offset="22%" stop-color="#8B3A2B"/>
        <stop offset="33%" stop-color="#9E5020"/>
        <stop offset="44%" stop-color="#A65E2B"/>
        <stop offset="55%" stop-color="#B85C3E"/>
        <stop offset="66%" stop-color="#C47F47"/>
        <stop offset="77%" stop-color="#D88032"/>
        <stop offset="88%" stop-color="#E8A872"/>
        <stop offset="100%" stop-color="#F5E6D3"/>
    </linearGradient>
</defs>
<path d="M25 25 L25 75 L75 75 L75 40 L50 40 L50 25 Z" fill="url(#grad)" stroke="#8B3A2B" stroke-width="2"/>
<path d="M50 25 L50 40 L75 40" fill="none" stroke="#8B3A2B" stroke-width="2"/>
<rect x="30" y="30" width="40" height="5" fill="#F5D5B0"/>
</svg>"""

# HTML template
EN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChildDiary Export | Download</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <div class="container">
            <div class="logo">
                {icon_svg}
                <h1>ChildDiary Export</h1>
            </div>
            <nav>
                <a href="index.html" class="lang-link active">English</a>
                <span class="lang-sep">|</span>
                <a href="pt/index.html" class="lang-link">Português</a>
            </nav>
        </div>
    </header>

    <main class="container">
        <section class="hero">
            <p class="tagline">Export your ChildDiary photos easily</p>
        </section>

        <section class="description">
            A simple tool to download and save all your photos from ChildDiary app.
        </section>

        <section class="releases">
            <h2>Latest Releases</h2>
            {releases_html}
        </section>

        <section class="instructions">
            <h2>How to Use</h2>
            <ol>
                <li>Download the executable for your platform</li>
                <li>Run the application</li>
                <li>Enter your ChildDiary credentials when prompted</li>
                <li>Select output directory and options</li>
                <li>Start the export!</li>
            </ol>
        </section>

        <section class="features">
            <h2>Features</h2>
            <ul>
                <li>Export all media from ChildDiary</li>
                <li>Optional compression (zip, gzip, bz2)</li>
                <li>Resume from specific page</li>
                <li>Secure credential storage via keyring</li>
            </ul>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>Open source on GitHub</p>
            <p><a href="https://github.com/SamuelNLP/child-diary-photo-export">SamuelNLP/child-diary-photo-export</a></p>
        </div>
    </footer>
</body>
</html>"""

PT_HTML = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChildDiary Export | Download</title>
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <header>
        <div class="container">
            <div class="logo">
                {icon_svg}
                <h1>ChildDiary Export</h1>
            </div>
            <nav>
                <a href="../index.html" class="lang-link">English</a>
                <span class="lang-sep">|</span>
                <a href="index.html" class="lang-link active">Português</a>
            </nav>
        </div>
    </header>

    <main class="container">
        <section class="hero">
            <p class="tagline">Exporte as suas fotos do ChildDiary facilmente</p>
        </section>

        <section class="description">
            Uma ferramenta simples para transferir e guardar todas as suas fotos do aplicativo ChildDiary.
        </section>

        <section class="releases">
            <h2>Últimas Versões</h2>
            {releases_html}
        </section>

        <section class="instructions">
            <h2>Como Usar</h2>
            <ol>
                <li>Transfira o executável para a sua plataforma</li>
                <li>Execute a aplicação</li>
                <li>Introduza as suas credenciais do ChildDiary quando solicitado</li>
                <li>Seleccione a pasta de destino e opções</li>
                <li>Inicie a exportação!</li>
            </ol>
        </section>

        <section class="features">
            <h2>Funcionalidades</h2>
            <ul>
                <li>Exportar todos os media do ChildDiary</li>
                <li>Compressão opcional (zip, gzip, bz2)</li>
                <li>Retomar de uma página específica</li>
                <li>Armazenamento seguro de credenciais via keyring</li>
            </ul>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>Código aberto no GitHub</p>
            <p><a href="https://github.com/SamuelNLP/child-diary-photo-export">SamuelNLP/child-diary-photo-export</a></p>
        </div>
    </footer>
</body>
</html>"""


def format_bytes(size):
    """Format bytes to human-readable string."""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"


def detect_platform(asset_name):
    """Detect platform from asset name."""
    name = asset_name.lower()
    if 'macos' in name or 'dmg' in name:
        return 'macos', '🍎', 'macOS'
    elif 'windows' in name or 'msi' in name or 'exe' in name:
        return 'windows', '🪟', 'Windows'
    elif 'linux' in name or 'tar' in name or 'appimage' in name:
        return 'linux', '🐧', 'Linux'
    return 'unknown', '📦', 'Download'


def generate_release_card(release):
    """Generate HTML for a single release card."""
    date = datetime.strptime(release['published_at'], '%Y-%m-%dT%H:%M:%SZ')
    date_str = date.strftime('%b %d, %Y')
    version = release['tag_name']
    
    buttons = []
    for asset in release.get('assets', []):
        platform, icon, label = detect_platform(asset['name'])
        size = format_bytes(asset['size'])
        url = asset['browser_download_url']
        
        buttons.append(
            f'<a href="{url}" class="download-btn {platform}" download="{asset["name"]}">'
            f'{icon} {label}<span>({size})</span></a>'
        )
    
    body = release.get('body', '')
    if body:
        body = body.split('\n')[0][:200]
    
    return f'''
        <div class="release-card">
            <div class="release-header">
                <div class="release-version">v{version}</div>
                <div class="release-date">{date_str}</div>
            </div>
            <div class="release-body">{body}</div>
            <div class="downloads">
                {"\n".join(buttons)}
            </div>
        </div>
    '''


def main():
    # Create output directories
    site_dir = Path('_site')
    pt_dir = site_dir / 'pt'
    site_dir.mkdir(exist_ok=True)
    pt_dir.mkdir(exist_ok=True)
    
    # Write CSS
    (site_dir / 'style.css').write_text(CSS)
    
    # Fetch releases
    try:
        response = requests.get(GITHUB_API, timeout=10)
        response.raise_for_status()
        releases = response.json()
        
        # Filter releases with assets, sort by date
        releases = [r for r in releases if r.get('assets')]
        releases.sort(key=lambda r: r['published_at'], reverse=True)
        
    except Exception as e:
        print(f"Warning: Could not fetch releases: {e}")
        releases = []
    
    # Generate releases HTML
    if releases:
        releases_html = "\n".join(generate_release_card(r) for r in releases[:3])
    else:
        releases_html = '<p style="text-align: center; color: var(--text-light);">No releases with binaries available yet.</p>'
    
    # Generate English page
    en_html = EN_HTML.format(
        icon_svg=ICON_SVG,
        releases_html=releases_html
    )
    (site_dir / 'index.html').write_text(en_html)
    
    # Generate Portuguese page
    pt_html = PT_HTML.format(
        icon_svg=ICON_SVG,
        releases_html=releases_html
    )
    (pt_dir / 'index.html').write_text(pt_html)
    
    # Copy CSS to pt directory
    (pt_dir / 'style.css').write_text(CSS)
    
    print(f"Generated {len(releases)} release cards")
    print(f"Output: {site_dir.absolute()}")


if __name__ == '__main__':
    main()
