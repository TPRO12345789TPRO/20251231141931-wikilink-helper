document.addEventListener('DOMContentLoaded', () => {
    // Load saved setting
    chrome.storage.local.get(['copyMode'], (result) => {
        const mode = result.copyMode || 'id';
        const radio = document.querySelector(`input[name="copyMode"][value="${mode}"]`);
        if (radio) {
            radio.checked = true;
        }
    });

    // Save setting on change
    document.querySelectorAll('input[name="copyMode"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.checked) {
                chrome.storage.local.set({ copyMode: e.target.value });
            }
        });
    });
});
