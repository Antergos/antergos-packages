# Maintainer: Christian Hesse <mail@eworm.de>

pkgname=gtk-engine-unico-bzr
pkgver=139
pkgrel=1
pkgdesc="Unico GTK3 theme engine"
arch=('i686' 'x86_64')
url="http://launchpad.net/unico"
license=('GPL')
depends=('gtk3')
makedepends=('bzr' 'gnome-common')
provides=('gtk-engine-unico')
conflicts=('gtk-engine-unico')
options=(!libtool)

_bzrtrunk="https://code.launchpad.net/unico/trunk"
_bzrmod="unico"

build() {
  cd "${srcdir}"
  msg "Connecting to Bazaar server...."

  if [[ -d "${_bzrmod}" ]]; then
    cd "${_bzrmod}" && bzr --no-plugins pull "${_bzrtrunk}" -r "${pkgver}"
    msg "The local files are updated."
  else
    bzr --no-plugins branch "${_bzrtrunk}" "${_bzrmod}" -q -r "${pkgver}"
  fi

  msg "Bazaar checkout done or server timeout"
  msg "Starting build..."

  rm -rf "${srcdir}/${_bzrmod}-build"
  cp -r "${srcdir}/${_bzrmod}" "${srcdir}/${_bzrmod}-build"
  cd "${srcdir}/${_bzrmod}-build"

  sed -i "/^AC_SUBST(gtk_req,/s|3.5.2|3.4.4|" configure.ac
  ./autogen.sh --prefix=/usr --disable-static
  make
}

package() {
  cd "$srcdir/$_bzrmod-build"
  make DESTDIR="$pkgdir/" install
}

# vim:set ts=2 sw=2 et:
