build:

	npm run tauri build


fix-osx:
	cd "src-tauri/target/release/bundle/macos/Device Bay.app/Contents/" && \
	mkdir -p "Frameworks" && \
	mv Resources/python_binary/_internal/* Frameworks/
