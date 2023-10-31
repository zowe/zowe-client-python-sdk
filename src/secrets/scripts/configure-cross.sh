#!/bin/bash

# Set environment variables needed for cross-compilation in current shell
set_env() {
    export PKG_CONFIG_SYSROOT_DIR="${CHROOT:-/}"
    export RUSTFLAGS="-L $CHROOT$1 $RUSTFLAGS"
    export PKG_CONFIG_PATH="$CHROOT$1/pkgconfig"
}

CROSS_DEB_ARCH=$1
dpkg --add-architecture $CROSS_DEB_ARCH
apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libsecret-1-dev:$CROSS_DEB_ARCH

case "$CROSS_DEB_ARCH" in
    "aarch64")
        set_env "/usr/lib/aarch64-linux-gnu"
        ;;
    "armv7")
        set_env "/usr/lib/arm-linux-gnueabihf"
        ;;
    "ppc64le")
        set_env "/usr/lib/powerpc64le-unknown-linux-gnu"
        ;;
    "s390x")
        set_env "/usr/lib/s390x-unknown-linux-gnu"
        ;;
    "x86")
        set_env "/usr/lib/i386-linux-gnu"
        ;;
    "x86_64")
        set_env "/usr/lib/x86_64-linux-gnu"
        ;;
    *)
        ;;
esac
