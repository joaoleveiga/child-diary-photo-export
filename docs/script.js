// Language switching
const langButtons = document.querySelectorAll('.lang-btn');
const currentLang = () => {
    const active = document.querySelector('.lang-btn.active');
    return active ? active.dataset.lang : 'en';
};

// Update all text elements with data-en/data-pt attributes
function updateLanguage(lang) {
    document.querySelectorAll('[data-en], [data-pt]').forEach(el => {
        const text = el.dataset[lang] || el.dataset.en || el.textContent;
        
        // Handle nested elements (like lists)
        if (el.tagName === 'LI' || el.tagName === 'P' || el.tagName === 'SPAN' || 
            el.tagName === 'H1' || el.tagName === 'H2' || el.tagName === 'LABEL') {
            el.textContent = text;
        } else if (el.tagName === 'A') {
            el.textContent = text;
        } else if (el.tagName === 'TITLE') {
            document.title = text;
        }
    });
    
    // Store preference
    localStorage.setItem('lang', lang);
}

// Initialize language
langButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        langButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        updateLanguage(btn.dataset.lang);
    });
});

// Load saved language preference
const savedLang = localStorage.getItem('lang') || 'en';
if (savedLang) {
    const savedBtn = document.querySelector(`.lang-btn[data-lang="${savedLang}"]`);
    if (savedBtn) {
        langButtons.forEach(b => b.classList.remove('active'));
        savedBtn.classList.add('active');
        updateLanguage(savedLang);
    }
}

// Platform icons as emoji
const platformIcons = {
    macos: '🍎',
    windows: '🪟',
    linux: '🐧'
};

// Platform names
const platformNames = {
    en: {
        macos: 'macOS',
        windows: 'Windows',
        linux: 'Linux'
    },
    pt: {
        macos: 'macOS',
        windows: 'Windows',
        linux: 'Linux'
    }
};

// Fetch releases from GitHub API
async function fetchReleases() {
    const repo = 'SamuelNLP/child-diary-photo-export';
    const apiUrl = `https://api.github.com/repos/${repo}/releases`;
    
    try {
        const response = await fetch(apiUrl);
        const releases = await response.json();
        
        // Only show releases with assets (binaries)
        const releasesWithAssets = releases.filter(r => r.assets && r.assets.length > 0);
        
        // Sort by published_at, newest first
        releasesWithAssets.sort((a, b) => 
            new Date(b.published_at) - new Date(a.published_at)
        );
        
        // Only show latest 3 releases
        const latestReleases = releasesWithAssets.slice(0, 3);
        
        if (latestReleases.length === 0) {
            document.getElementById('releases-list').innerHTML = `
                <p style="text-align: center; color: var(--text-light);">
                    No releases with binaries available yet.
                </p>
            `;
            return;
        }
        
        const lang = currentLang();
        const releasesHtml = latestReleases.map(release => {
            const date = new Date(release.published_at).toLocaleDateString(lang === 'pt' ? 'pt-PT' : 'en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
            
            // Group assets by platform
            const assetsByPlatform = {};
            release.assets.forEach(asset => {
                const name = asset.name.toLowerCase();
                let platform = 'unknown';
                
                if (name.includes('macos') || name.includes('dmg')) {
                    platform = 'macos';
                } else if (name.includes('windows') || name.includes('msi') || name.includes('exe')) {
                    platform = 'windows';
                } else if (name.includes('linux') || name.includes('tar') || name.includes('appimage')) {
                    platform = 'linux';
                }
                
                if (!assetsByPlatform[platform]) {
                    assetsByPlatform[platform] = [];
                }
                assetsByPlatform[platform].push(asset);
            });
            
            // Build download buttons
            const downloadButtons = Object.entries(assetsByPlatform)
                .map(([platform, assets]) => {
                    // Get the first asset for this platform
                    const asset = assets[0];
                    const icon = platformIcons[platform] || '';
                    const platformName = platformNames[lang][platform] || platform;
                    const fileSize = formatBytes(asset.size);
                    
                    return `
                        <a href="${asset.browser_download_url}" 
                           class="download-btn ${platform}" 
                           download="${asset.name}">
                            ${icon} ${platformName}
                            <span>(${fileSize})</span>
                        </a>
                    `;
                })
                .join('');
            
            // Build release body (first line of body, truncated)
            const body = release.body ? release.body.split('\n')[0].substring(0, 200) : '';
            
            return `
                <div class="release-card">
                    <div class="release-header">
                        <div class="release-version">v${release.tag_name}</div>
                        <div class="release-date">${date}</div>
                    </div>
                    <div class="release-body">${body}</div>
                    <div class="downloads">
                        ${downloadButtons}
                    </div>
                </div>
            `;
        }).join('');
        
        document.getElementById('releases-list').innerHTML = releasesHtml;
        
    } catch (error) {
        console.error('Error fetching releases:', error);
        document.getElementById('releases-list').innerHTML = `
            <p style="text-align: center; color: var(--text-light);">
                Error loading releases. Please try again later.
            </p>
        `;
    }
}

// Format bytes to human-readable string
function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', fetchReleases);
