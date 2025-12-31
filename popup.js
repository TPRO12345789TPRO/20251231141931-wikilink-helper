document.addEventListener('DOMContentLoaded', () => {
    // Load saved settings
    chrome.storage.local.get(['copyMode', 'linkFormat'], (result) => {
        // Load copyMode
        const mode = result.copyMode || 'id';
        const modeRadio = document.querySelector(`input[name="copyMode"][value="${mode}"]`);
        if (modeRadio) {
            modeRadio.checked = true;
        }

        // Load linkFormat
        const format = result.linkFormat || 'auto';
        const formatRadio = document.querySelector(`input[name="linkFormat"][value="${format}"]`);
        if (formatRadio) {
            formatRadio.checked = true;
        }
    });

    // Save copyMode on change
    document.querySelectorAll('input[name="copyMode"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.checked) {
                chrome.storage.local.set({ copyMode: e.target.value });
            }
        });
    });

    // Save linkFormat on change
    document.querySelectorAll('input[name="linkFormat"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.checked) {
                chrome.storage.local.set({ linkFormat: e.target.value });
            }
        });
    });
});
