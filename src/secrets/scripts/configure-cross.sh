#!/bin/bash

# Install libsecret for the architecture we are compiling for
install_libs() {
    dpkg --add-architecture $1
    apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libsecret-1-dev:$1
}

# Set environment variables needed for cross-compilation in current shell
set_env() {
    export PKG_CONFIG_SYSROOT_DIR="${CHROOT:-/}"
    export RUSTFLAGS="-L $CHROOT$1 $RUSTFLAGS"
    export PKG_CONFIG_PATH="$CHROOT$1/pkgconfig"
}

CROSS_DEB_ARCH=$1
case "$1" in
    "aarch64")
        CROSS_DEB_ARCH=arm64
        set_env "/usr/lib/aarch64-linux-gnu"
        ;;
    "armv7")
        CROSS_DEB_ARCH=armhf
        set_env "/usr/lib/arm-linux-gnueabihf"
        ;;
    "ppc64le")
        CROSS_DEB_ARCH=ppc64el
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
install_libs $CROSS_DEB_ARCH
