// Wikilink Helper Content Script

const ID_PATTERN = /^\d{14}-/;

// Utility to create the toast element
function createToast() {
    let toast = document.getElementById('wikilink-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'wikilink-toast';
        document.body.appendChild(toast);
    }
    return toast;
}

// Show toast message
function showToast(message) {
    const toast = createToast();
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 2000);
}

// Logic to parse the wikilink content
function parseWikilink(rawText) {
    // Remove [[ and ]]
    const content = rawText.slice(2, -2);

    if (!content.includes('|')) {
        return { id: content, text: content };
    }

    const parts = content.split('|');
    const first = parts[0];
    const second = parts.slice(1).join('|');

    // Dendron Check: if second part looks like ID, use that
    if (ID_PATTERN.test(second)) {
        return { id: second, text: first };
    }
    // Standard: id|text, or fallback
    return { id: first, text: second };
}

// Handle click event on the link
function handleLinkClick(event, linkData) {
    event.preventDefault();
    event.stopPropagation();

    chrome.storage.local.get(['copyMode'], (result) => {
        const mode = result.copyMode || 'id'; // default to id
        let textToCopy = '';

        if (mode === 'id') {
            textToCopy = linkData.id;
        } else if (mode === 'text') {
            textToCopy = linkData.text;
        } else if (mode === 'both') {
            textToCopy = `${linkData.id} ${linkData.text}`;
        }

        navigator.clipboard.writeText(textToCopy).then(() => {
            showToast(`Copied: ${textToCopy}`);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
            showToast('Failed to copy');
        });
    });
}

// Function to replace text nodes with interactive elements
function processNode(node) {
    if (node.nodeType === 3) { // Text node
        const text = node.nodeValue;
        const regex = /\[\[(.*?)\]\]/g;

        if (regex.test(text)) {
            const fragment = document.createDocumentFragment();
            let lastIndex = 0;
            let match;

            // Reset regex
            regex.lastIndex = 0;

            while ((match = regex.exec(text)) !== null) {
                // Add text before match
                if (match.index > lastIndex) {
                    fragment.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
                }

                // Parse the link
                const rawMatch = match[0];
                const { id, text: displayText } = parseWikilink(rawMatch);

                // Create span element
                const span = document.createElement('span');
                span.className = 'wikilink-helper';
                span.textContent = displayText;
                span.title = `ID: ${id}\nClick to copy`;

                span.addEventListener('click', (e) => handleLinkClick(e, { id, text: displayText }));

                fragment.appendChild(span);
                lastIndex = regex.lastIndex;
            }

            // Add remaining text
            if (lastIndex < text.length) {
                fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
            }

            node.parentNode.replaceChild(fragment, node);
        }
    } else if (node.nodeType === 1) { // Element node
        // Skip script, style, textarea, input, and already processed nodes
        const tagName = node.tagName.toLowerCase();
        if (tagName === 'script' || tagName === 'style' || tagName === 'textarea' || tagName === 'input' || node.classList.contains('wikilink-helper')) {
            return;
        }

        // Recursively process children
        Array.from(node.childNodes).forEach(processNode);
    }
}

// Run initially
processNode(document.body);

// Observe for DOM changes (optional but good for dynamic sites)
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
            processNode(node);
        });
    });
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});
