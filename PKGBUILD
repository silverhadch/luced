# Maintainer: Hadi Chokr <hadichokr@icloud.com>
pkgname=luced
pkgver=2.0
pkgrel=1
pkgdesc="Open Source Nano Ripoff in Python"
arch=('any')
url="https://github.com/silverhadch/luced"
license=('GPL3')
depends=('python' 'python-pyperclip' 'python-pyinstaller')
source=("$pkgname-$pkgver.tar.gz::https://github.com/silverhadch/luced/archive/refs/heads/master.tar.gz")
sha256sums=('SKIP')

build() {
  cd "$srcdir/luced-master"
  # Use system-wide pyinstaller if available
  pyinstaller --onefile main.py --name luced
}

package() {
  cd "$srcdir/luced-master"
  # Install the executable
  install -Dm755 "dist/luced" "$pkgdir/bin/luced"
  # Install the man page
  install -Dm644 "docs/man/luced.1" "$pkgdir/usr/share/man/man1/luced.1"
}
