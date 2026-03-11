#!/bin/bash
# Build RPM package for red-ai
# Run this on a RHEL/CentOS/Fedora system with rpm-build installed
#
# Prerequisites:
#   yum install -y rpm-build python3-devel python3-setuptools
#
# Usage:
#   ./build_rpm.sh
#
# Output:
#   RPM will be in ~/rpmbuild/RPMS/noarch/

set -e

NAME="red-ai"
VERSION="2.0.0"
TOPDIR="$HOME/rpmbuild"

echo "=== Building ${NAME}-${VERSION} RPM ==="

# Create rpmbuild directory structure
mkdir -p "${TOPDIR}"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Create source tarball
echo "Creating source tarball..."
TMPDIR=$(mktemp -d)
mkdir -p "${TMPDIR}/${NAME}-${VERSION}"
cp -r red_ai setup.py README.md requirements.txt LICENSE "${TMPDIR}/${NAME}-${VERSION}/"
tar czf "${TOPDIR}/SOURCES/${NAME}-${VERSION}.tar.gz" -C "${TMPDIR}" "${NAME}-${VERSION}"
rm -rf "${TMPDIR}"

# Copy spec file
cp "${NAME}.spec" "${TOPDIR}/SPECS/"

# Build RPM
echo "Building RPM..."
rpmbuild -ba "${TOPDIR}/SPECS/${NAME}.spec"

echo ""
echo "=== Build complete ==="
echo "RPM: $(find "${TOPDIR}/RPMS" -name "${NAME}-*.rpm")"
echo "SRPM: $(find "${TOPDIR}/SRPMS" -name "${NAME}-*.rpm")"
echo ""
echo "Install with:"
echo "  sudo yum install -y $(find "${TOPDIR}/RPMS" -name "${NAME}-*.noarch.rpm" | head -1)"
