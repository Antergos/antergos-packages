# $Id$
# Maintainer: Ramon Buldó <ramon@manjaro.org>

pkgname=ckbcomp
pkgver=1.120
pkgrel=1
pkgdesc="Compile a XKB keyboard description to a keymap suitable for loadkeys or kbdcontrol"
arch=(any)
url="http://anonscm.debian.org/cgit/d-i/console-setup.git/"
license=('GPL2')
depends=('perl')
source=("http://ftp.de.debian.org/debian/pool/main/c/console-setup/console-setup_1.120.tar.xz")
sha256sums=('685e2ffbf4cb1a20d39d5dbc6eb1c2551e9f4f049dcba5cd558fa23e5a3fb253')

package() {
  cd console-setup-${pkgver}
  install -d ${pkgdir}/usr/bin/
  install -m755 Keyboard/ckbcomp ${pkgdir}/usr/bin/
}
 
