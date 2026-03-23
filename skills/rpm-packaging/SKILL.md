# RPM Build Process for RED-AI

## Key Files
- `red-ai.spec` -- RPM spec file defining package metadata and build steps
- `build_rpm.sh` -- Wrapper script that creates tarball, sets up rpmbuild tree, and invokes rpmbuild

## Spec File Structure

```
Name:           red-ai
Version:        2.0.0          # Update for each release
Release:        1%{?dist}      # %{dist} auto-appends .el7, .el8, .el9
BuildArch:      noarch         # Pure Python, no compiled code
Requires:       python3        # Only runtime dependency
```

### Sections
- `%prep` / `%autosetup` -- unpacks source tarball
- `%build` / `%py3_build` -- runs `setup.py build`
- `%install` / `%py3_install` -- runs `setup.py install`, creates `/var/log/red-ai`
- `%files` -- lists installed files: package dir, egg-info, binary, log dir, LICENSE, README

## build_rpm.sh Usage

```bash
# Prerequisites (on RHEL/CentOS/Fedora)
yum install -y rpm-build python3-devel python3-setuptools

# Build
./build_rpm.sh

# Output location
~/rpmbuild/RPMS/noarch/red-ai-2.0.0-1.el8.noarch.rpm

# Install
sudo yum install -y ~/rpmbuild/RPMS/noarch/red-ai-2.0.0-1.el8.noarch.rpm
```

## Versioning

Version is defined in three places that must stay in sync:
1. `red_ai/__init__.py` -- `__version__ = "2.0.0"`
2. `red-ai.spec` -- `Version: 2.0.0`
3. `build_rpm.sh` -- `VERSION="2.0.0"`

When bumping version:
```bash
# Update all three files, then rebuild
sed -i 's/2.0.0/2.1.0/g' red_ai/__init__.py red-ai.spec build_rpm.sh
```

## RHEL 7/8/9 Compatibility

### Python Differences
| RHEL Version | Default Python | Package Name |
|-------------|---------------|-------------|
| RHEL 7      | 2.7 (system)  | python36, python3 |
| RHEL 8      | 3.6           | python3 |
| RHEL 9      | 3.9           | python3 |

The spec uses `Requires: python3` which resolves correctly on RHEL 8/9. For RHEL 7, users may need `yum install python3` from EPEL or SCL first.

### Build Macro Differences
- `%py3_build` and `%py3_install` are available on RHEL 8/9 via `python3-rpm-macros`
- On RHEL 7, you may need: `BuildRequires: python36-devel python36-setuptools`

### Testing Across Versions
```bash
# Use containers to test builds
podman run --rm -v $(pwd):/src:z rhel7:latest bash -c "cd /src && ./build_rpm.sh"
podman run --rm -v $(pwd):/src:z rhel8:latest bash -c "cd /src && ./build_rpm.sh"
podman run --rm -v $(pwd):/src:z rhel9:latest bash -c "cd /src && ./build_rpm.sh"
```

## Adding Files to the RPM
If you add new files (e.g., config files, man pages), update both `build_rpm.sh` (the `cp -r` line) and the `%files` section in `red-ai.spec`. Missing entries cause build failures.

## Changelog
Always add a changelog entry in `red-ai.spec` when releasing:
```
%changelog
* Mon Mar 23 2026 Your Name <email> - 2.1.0-1
- Description of changes
```
