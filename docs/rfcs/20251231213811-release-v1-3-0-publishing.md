# 20251231213811 Release v1.3.0 Publishing and Build System

**Status**: Implemented
**Date**: 2025-12-31

## Context
We are finalizing version 1.3.0 of the Wikilink Helper extension. We need to prepare artifacts for distribution, specifically for the Chrome Web Store, and ensure a reproducible build process across different operating systems.

## Implementation Details

### Build System
- **Scripts**: Moved build logic to `scripts/` directory.
    - `pack_crx.py`: Cross-platform Python script to pack the extension into `.crx` (signed) and `.zip` (source) formats. It auto-detects Chrome executable paths on Windows, macOS, and Linux.
    - `build.cmd`: Windows batch script wrapper.
    - `build.sh`: Linux/macOS shell script wrapper.
- **Security**: Added `key.pem` to `.gitignore` to prevent accidental leakage of the private key.

### Publishing Artifacts
- The build process now generates two files in `dist/` with a timestamp prefix:
    - `[TIMESTAMP]-wikilink-helper-1.3.0.crx`: Signed extension for local/enterprise install.
    - `[TIMESTAMP]-wikilink-helper-1.3.0.zip`: Source archive for Chrome Web Store submission.
- **Documentation**: Created `PUBLISHING.md` to guide the manual submission process to the Chrome Web Store.

### Privacy & Compliance
- Created `PRIVACY.md` to clarify data usage (local processing only).
- Clarified `<all_urls>` permission usage for the Web Store review process.

## Decisions
- **CRX vs ZIP**: We generate both. CRX is useful for archiving and testing signed builds locally. ZIP is required for the Web Store.
- **Cross-Platform**: Using Python for the core logic ensures the build works on all developer machines.
