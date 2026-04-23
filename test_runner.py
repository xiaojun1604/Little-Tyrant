import sys
import traceback
import os

print("--- Test 1: Import Module Check ---")
try:
    import PyQt5
    print("[PASS] PyQt5 module is available.")
    # Add project root to sys path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from ui.main_window import MainWindow
    from core.adb_manager import AdbManager
    from core.worker_thread import InstallWorker
    print("[PASS] All core and UI project modules imported successfully without errors.")
except Exception as e:
    print("[FAIL] Import Failed!")
    traceback.print_exc()

print("\n--- Test 2: AdbManager - ADB Execution Check ---")
try:
    from core.adb_manager import AdbManager
    # Try fetching devices
    devices = AdbManager.get_connected_devices()
    print(f"[INFO] ADB returned devices: {devices}")
    print("[PASS] ADB Command executed successfully (list parses without throwing).")
except Exception as e:
    print("[FAIL] AdbManager devices check Failed! Error:")
    traceback.print_exc()

print("\n--- Test 3: AdbManager - Local Filesystem Filtering ---")
try:
    from core.adb_manager import AdbManager
    
    dummy_dir = 'dummy_apk_dir_test_output'
    os.makedirs(dummy_dir, exist_ok=True)
    with open(os.path.join(dummy_dir, 'game1.apk'), 'w') as f: f.write('dummy')
    with open(os.path.join(dummy_dir, 'game2.Apk'), 'w') as f: f.write('dummy')
    with open(os.path.join(dummy_dir, 'readme.txt'), 'w') as f: f.write('dummy')
    
    apks = AdbManager.list_apks_in_directory(dummy_dir)
    print(f"[INFO] Detected APKs in folder: {apks}")
    
    if len(apks) == 2 and 'game1.apk' in apks and 'game2.Apk' in apks:
        print("[PASS] APK filtering logic works correctly (case-insensitive checking).")
    else:
        print("[FAIL] APK filtering missed or included wrong files!")
    
    # Cleanup
    for f in os.listdir(dummy_dir): os.remove(os.path.join(dummy_dir, f))
    os.rmdir(dummy_dir)
except Exception as e:
    print("[FAIL] AdbManager apk path checking Failed!")
    traceback.print_exc()
