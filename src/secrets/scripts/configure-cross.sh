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

case "$1" in
    "aarch64")
        install_libs arm64
        set_env "/usr/lib/aarch64-linux-gnu"
        ;;
    "armv7")
        install_libs armhf
        set_env "/usr/lib/arm-linux-gnueabihf"
        ;;
    "ppc64le")
        install_libs ppc64el
        set_env "/usr/lib/powerpc64le-unknown-linux-gnu"
        ;;
    "s390x")
        install_libs s390x
        set_env "/usr/lib/s390x-unknown-linux-gnu"
        ;;
    "x86")
        install_libs i386
        set_env "/usr/lib/i386-linux-gnu"
        ;;
    "x86_64")
        install_libs amd64
        set_env "/usr/lib/x86_64-linux-gnu"
        ;;
    *)
        ;;
esac
