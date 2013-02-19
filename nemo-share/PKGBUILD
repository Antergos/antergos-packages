# Maintainer: Alex Filgueira <alexfilgueira@cinnarch.com>

pkgname=nemo-share
pkgver=1.1.2
pkgrel=2
pkgdesc="Nemo share extension"
arch=('i686' 'x86_64')
url="https://github.com/linuxmint/nemo-extensions"
license=('GPL')
source=("$pkgname-$pkgver.tar.gz::http://github.com/linuxmint/nemo-extensions/archive/master.tar.gz")
depends=('nemo' 'samba')
options=('!libtool' '!emptydirs')
sha256sums=('b15f7cd536f595acd070cdff5b9c5c59df44bbc7bf91a1fd560702875b0f3669')

build() {

  
  cd nemo-extensions-master/${pkgname}

  autoreconf -fi
  
  ./configure --prefix=/usr --sysconfdir=/etc
  make
}

package() {
  cd nemo-extensions-master/${pkgname}
  make DESTDIR="${pkgdir}" install
}


