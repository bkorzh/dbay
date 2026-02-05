build: 
	@echo "Building frontend..."
	cd .. && cd .. && cd frontend && npm run build && npm run move && cd .. && cd backend/backend

serve:
	@echo "Starting server..."
	cd .. && cd .. && cd frontend && npm run build && npm run move && cd .. && cd backend/backend && fastapi dev main.py --host 0.0.0.0

build-python:
	@echo "Building python..."
	yes | pyinstaller main.spec&& cp -r dist/main/* ../../frontend/src-tauri/python_binary/
	cp ../../frontend/src-tauri/python_binary/main ../../frontend/src-tauri/python_binary/main-aarch64-apple-darwin


build-tauri:
	@echo "Building tauri..."
	cd ../../frontend && npm run tauri build




# steps
# go into frontend
# npm run build
# npm run move   # that moves the built files to /dbay_control/
# 

# run "pyinstaller main.spec"