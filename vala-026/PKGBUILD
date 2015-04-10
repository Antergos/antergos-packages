# $Id$
# Maintainer : Ionut Biru <ibiru@archlinux.org>
# Contributor: Timm Preetz <timm@preetz.us>

pkgname=vala-026
pkgver=0.26.2
pkgrel=1
pkgdesc="Compiler for the GObject type system"
arch=('i686' 'x86_64')
url="http://live.gnome.org/Vala"
license=('LGPL')
depends=('glib2')
makedepends=('libxslt')
checkdepends=('dbus' 'libx11' 'gobject-introspection')
source=(http://ftp.gnome.org/pub/gnome/sources/vala/${pkgver:0:4}/vala-$pkgver.tar.xz)
sha256sums=('37f13f430c56a93b6dac85239084681fd8f31c407d386809c43bc2f2836e03c4')
provides=("vala=$pkgver")
conflicts=('vala')

build() {
    cd vala-$pkgver
    ./configure --prefix=/usr --enable-vapigen
    make
}

check() {
    cd vala-$pkgver
    make check
}

package() {
    cd vala-$pkgver
    make DESTDIR="$pkgdir" install
}
