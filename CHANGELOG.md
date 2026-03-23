# Changelog

All notable changes to RED-AI will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.0.0] - 2024-01-01

### Added
- Ollama/Mistral AI integration for natural language command generation
- 230+ local RHEL command patterns for offline fallback
- Dry-run mode for safe command preview
- Risk level classification (low/medium/high)
- Execution history and logging to `/var/log/red-ai/`
- System information display (`--info`)
- RPM packaging via `build_rpm.sh`
- Categories: kernel, security, storage, network, services, users, packages, performance, logging, boot

### Security
- Root requirement enforced for live execution
- Confirmation prompts before command execution
- Hardcoded secrets scanning in CI

## [1.0.0] - 2023-06-01

### Added
- Initial release
- Basic CLI interface
- Local command matching
