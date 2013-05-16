# Maintainer: Hexchain Tong <i@hexchain.org>

pkgname=cinnamon-theme-nadia
pkgver=1.0
pkgrel=2
pkgdesc="Nadia theme for Cinnamon desktop"
arch=('any')
url="http://cinnamon-spices.linuxmint.com/themes/view/144"
license=('GPL')
depends=('cinnamon')
options=('!strip')
source=('http://cinnamon-spices.linuxmint.com/uploads/themes/F34H-DYYD-WRWQ.zip')

package() {
    cd nadiathemes
    for i in *; do
        find "$i" -type f -exec install -Dm644 '{}' "$pkgdir/usr/share/themes/{}" \;
    done
}

md5sums=('8f21c9f725ee47e2ae1808196060002c')
