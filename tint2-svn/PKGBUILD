# Contributor: zoulnix <http://goo.gl/HQaP>
# Maintainer: vicky91 <vickypaiers@gmail.com>
pkgname=tint2-svn
pkgver=682
pkgrel=1
pkgdesc="A basic, good-looking task manager for WMs."
arch=('i686' 'x86_64')
url="http://code.google.com/p/tint2/"
license=('GPL')
depends=('libxcomposite' 'libxinerama' 'libxrandr' 'pango' 'imlib2')
makedepends=('cmake' 'subversion'  'pkg-config')
options=('!libtool')
provides=('tint2')
conflicts=('tint2' 'tint')
source=("svn+http://tint2.googlecode.com/svn/trunk" 'zombie-fix.patch' 'clock.patch' 'freespace.patch' 'launcher_apps_dir-v2.patch' 'src-task-align.patch' 
'https://gist.githubusercontent.com/dorkster/51e39d358d5cf49df29c/raw/f75b2d1dc6189537595b8f4b7bb6e9bdbb5d4cfa/graph.patch' 
'tint2-systray.patch' 'two-line-battery-format.patch')

md5sums=('SKIP'
         'cdb83cd911e005a3529e5d1cd952a956'
         'bc0bab2979dacff551a97bdf2c2fdedc'
         'deb1ff7fafdde77f76c890b1adca83d4'
         '13218765dd684ae825967d3ffb4f4a75'
         'f0d7f51ec8dbf2e7b6bcca942f0fd6c0'
         '99011fae4b0c651bbb94af7477c3e0bf'
         'b3d864b8286e3f87992d789ea754cb18'
         'f47f816e1b84d697b571ecb8238c4481')

pkgver() {
  cd "$SRCDEST/trunk"
  svnversion | tr -d [A-z]
}

build() {
  cd "$srcdir/trunk"
  patch -Np1 -i "$srcdir/zombie-fix.patch"
  patch -Np1 -i "$srcdir/clock.patch"
  #patch -Np1 -i "$srcdir/freespace.patch"
  patch -Np1 -i "$srcdir/launcher_apps_dir-v2.patch"
  patch -Np1 -i "$srcdir/src-task-align.patch"
  patch -Np1 -i "$srcdir/graph.patch"
  patch -Np1 -i "$srcdir/tint2-systray.patch"
  patch -Np1 -i "$srcdir/two-line-battery-format.patch"
  cmake . -DCMAKE_INSTALL_PREFIX=/usr \
	  -DENABLE_TINT2CONF=0

  make
}

package() {
  make -C "$srcdir/trunk" DESTDIR="$pkgdir" install
}
