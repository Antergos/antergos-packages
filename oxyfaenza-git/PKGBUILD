# Maintainer: Xolan <jonassvarvaa at gmail dot com>
# Author: Deevad

pkgname=oxyfaenza-git
pkgver=0.3.3f99d66
pkgrel=1
pkgdesc="Yet another Faenza icon theme for KDE. Target: no-missing icons for my KDE apps relying on Oxygen too often, and GTK relying on Gnome/hi-color too often too. Repacking initiated by Deevad."
arch=('any')
url="https://github.com/Deevad/oxyfaenza"
license=('GPL')
makedepends=('git')
options=('emptydirs')
source=('git+git://github.com/Deevad/oxyfaenza.git')
sha1sums=('SKIP')
_gitname="oxyfaenza"

pkgver() {
  cd "${srcdir}/${_gitname}"
  echo "0.$(git rev-list --count HEAD).$(git describe --always)"
}

package() {
  cd "$srcdir"
  rm -rf "${srcdir}/${_gitname}-build"
  git clone "${srcdir}/${_gitname}" "${srcdir}/${_gitname}-build"
  cd "${srcdir}/${_gitname}-build"

  install -d "$pkgdir/usr/share/icons/$_gitname"
  cp -R * "$pkgdir/usr/share/icons/$_gitname/"
}

# vim:set ts=2 sw=2 et:
