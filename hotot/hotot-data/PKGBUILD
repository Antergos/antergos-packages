# Maintainer: speps <speps at aur dot archlinux dot org>

_uname=lyricat
_commit=1f68d33
pkgname=hotot-data
pkgver=0.9.8.14
pkgrel=1
pkgdesc="A lightweight & open source microblogging software (twitter identi.ca)."
arch=('any')
url="http://www.hotot.org/"
license=('LGPL3')
depends=('hicolor-icon-theme')
makedepends=('cmake' 'intltool' 'python2')
install="hotot-data.install"
source=("https://github.com/$_uname/Hotot/archive/$pkgver.tar.gz")
md5sums=('7437f5132a50f7239e1b4bd09f410a17')

build() {
  cd ${srcdir}/Hotot-*
  [ -d bld ] || mkdir bld && cd bld
  cmake .. -DCMAKE_INSTALL_PREFIX=/usr \
           -DWITH_GTK=OFF \
           -DWITH_GIR=OFF \
           -DWITH_QT=OFF \
           -DWITH_KDE=OFF \
           -DWITH_CHROME=OFF \
           -DPYTHON_EXECUTABLE=/usr/bin/python2
  make
}

package() {
  cd ${srcdir}/Hotot-*/bld/misc
  DESTDIR="$pkgdir/" cmake -P cmake_install.cmake

  cd ${srcdir}/Hotot-*/bld/po
  DESTDIR="$pkgdir/" cmake -P cmake_install.cmake

  # remove google analytics tracking code (tnx to ianux)
  find "$pkgdir" -name hotot.js -exec \
    sed -i '/\/\/ 7. run track code/,+12d' {} \;
}

# vim:set ts=2 sw=2 et:
