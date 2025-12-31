// Test script to verify wikilink regex logic
// Run with node test_regex.js

const tests = [
    {
        input: '[[20251231140239-target-page|Displayed Text]]',
        desc: 'Standard format: ID first',
        expected: { id: '20251231140239-target-page', text: 'Displayed Text' }
    },
    {
        input: '[[Displayed Text|20251231140239-target-page]]',
        desc: 'Dendron format: Text first',
        expected: { id: '20251231140239-target-page', text: 'Displayed Text' }
    },
    {
        input: '[[20251231140239-simple]]',
        desc: 'ID only (no pipe)',
        expected: { id: '20251231140239-simple', text: '20251231140239-simple' }
    },
    {
        input: 'Some text [[20251231140239-target|Text]] here',
        desc: 'Embedded in text',
        expected: { id: '20251231140239-target', text: 'Text' }
    }
];

// Regex to capture the content inside [[...]]
const LINK_REGEX = /\[\[(.*?)\]\]/g;
// Regex to identify ID (timestamp-based)
const ID_PATTERN = /^\d{14}-/;

function parseLink(rawInside) {
    if (!rawInside.includes('|')) {
        return { id: rawInside, text: rawInside };
    }

    const parts = rawInside.split('|');
    const first = parts[0];
    const second = parts.slice(1).join('|'); // Join back just in case, though usually 2 parts

    // Determine which part is ID
    if (ID_PATTERN.test(first)) {
        return { id: first, text: second };
    } else if (ID_PATTERN.test(second)) {
        return { id: second, text: first };
    } else {
        // Fallback: Default to standard ID|Text if no timestamp pattern found? 
        // Or assume first is ID? The user requirement specifically mentions checking ID pattern for Dendron support.
        // If neither looks like an ID, we might assume standard [[ID|Text]] format.
        return { id: first, text: second };
    }
}

console.log('Running Regex Tests...\n');

tests.forEach(test => {
    // Reset regex state
    LINK_REGEX.lastIndex = 0;
    const match = LINK_REGEX.exec(test.input);

    if (!match) {
        console.error(`❌ ${test.desc}: No match found`);
        return;
    }

    const result = parseLink(match[1]);

    if (result.id === test.expected.id && result.text === test.expected.text) {
        console.log(`✅ ${test.desc}`);
    } else {
        console.error(`❌ ${test.desc}`);
        console.error(`   Expected:`, test.expected);
        console.error(`   Got:     `, result);
    }
});
