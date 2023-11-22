#!/bin/bash

# Set environment variables needed for cross-compilation in GITHUB_ENV
set_env() {
    echo "CROSS_DEB_ARCH=$1" >> $GITHUB_ENV
    echo "PKG_CONFIG_SYSROOT_DIR=/" >> $GITHUB_ENV
    echo "RUSTFLAGS=-L $2 $RUSTFLAGS" >> $GITHUB_ENV
    echo "PKG_CONFIG_PATH=$2/pkgconfig" >> $GITHUB_ENV
}

case "$1" in
    "aarch64")
        set_env arm64 "/usr/lib/aarch64-linux-gnu"
        ;;
    "armv7")
        set_env armhf "/usr/lib/arm-linux-gnueabihf"
        ;;
    "ppc64le")
        set_env ppc64el "/usr/lib/powerpc64le-linux-gnu"
        ;;
    "s390x")
        set_env s390x "/usr/lib/s390x-linux-gnu"
        ;;
    "x86")
        set_env i686 "/usr/lib/i386-linux-gnu"
        ;;
    "x86_64")
        set_env x86_64 "/usr/lib/x86_64-linux-gnu"
        ;;
    *)
        ;;
esac
