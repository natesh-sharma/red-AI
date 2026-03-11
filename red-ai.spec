Name:           red-ai
Version:        2.0.0
Release:        1%{?dist}
Summary:        AI-powered RHEL configuration tool
License:        Proprietary
URL:            https://github.com/natesh-sharma/red-AI

Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
Requires:       python3

%description
RED-AI is an intelligent command-line tool for RHEL Linux that simplifies
system configuration using natural language prompts. It uses a local Ollama
LLM for AI-powered command generation and includes a built-in command
database for offline fallback.

Developed by Natesh Sharma.

%prep
%autosetup -n %{name}-%{version}

%build
%py3_build

%install
%py3_install
mkdir -p %{buildroot}/var/log/red-ai

%files
%doc README.md
%{python3_sitelib}/red_ai/
%{python3_sitelib}/red_ai-*.egg-info/
%{_bindir}/red-ai
%dir /var/log/red-ai

%changelog
* Tue Mar 11 2026 Natesh Sharma <natesh@redhat.com> - 2.0.0-1
- Rewrite in Python with local Ollama AI and offline fallback
- Built-in command database with 100+ RHEL commands
- Support for RHEL 7, 8, and 9
