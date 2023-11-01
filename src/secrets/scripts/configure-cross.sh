#!/bin/bash

# Set environment variables needed for cross-compilation in current shell
set_env() {
    echo "PKG_CONFIG_SYSROOT_DIR=/" >> $GITHUB_ENV
    echo "RUSTFLAGS=-L $1 $RUSTFLAGS" >> $GITHUB_ENV
    echo "PKG_CONFIG_PATH=$1/pkgconfig" >> $GITHUB_ENV
}

case "$1" in
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
