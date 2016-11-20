INSTALL_PATH = $(DESTDIR)/usr/share/gnome-shell/extensions
INSTALL_NAME = TopIcons@phocean.net

install: build
	mkdir -p $(INSTALL_PATH)
	cp -r _build $(INSTALL_PATH)/$(INSTALL_NAME)
	echo Installed in $(INSTALL_PATH)/$(INSTALL_NAME)

build: compile-schema
	mkdir _build
	cp -r schemas convenience.js extension.js metadata.json prefs.js README.md _build
	echo Build was successfull 

compile-schema: ./schemas/org.gnome.shell.extensions.topicons.gschema.xml
	glib-compile-schemas schemas

clean:
	rm -rf _build
