import os
import subprocess
import sys

# Configuration
SOURCE_DIR = "skills_all"
BATCH_SIZE = 10
START_BATCH = 38  # 从第 38 批开始

def run_command(command, ignore_error=False):
    try:
        result = subprocess.run(command, check=not ignore_error, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        if not ignore_error:
            print(f"Error running command: {command}")
            print(e.stderr.decode())
            sys.exit(1)
        return None

def has_staged_changes():
    status = run_command("git diff --cached --name-only")
    return len(status) > 0

def main():
    dirs = [d for d in os.listdir(SOURCE_DIR) if os.path.isdir(os.path.join(SOURCE_DIR, d))]
    dirs.sort()
    
    total_dirs = len(dirs)
    print(f"Found {total_dirs} directories in {SOURCE_DIR}. Resuming from batch {START_BATCH}...")

    # 计算起始索引
    start_idx = (START_BATCH - 1) * BATCH_SIZE

    for i in range(start_idx, total_dirs, BATCH_SIZE):
        batch = dirs[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (total_dirs + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"Processing batch {batch_num}/{total_batches}...")
        
        paths = [f"{SOURCE_DIR}/{d}" for d in batch]
        paths_str = " ".join(f"'{p}'" for p in paths)
        
        run_command(f"git add {paths_str}")
        
        if has_staged_changes():
            print(f"  - Committing batch {batch_num}...")
            commit_msg = f"feat: add skills batch {batch_num} ({batch[0]} to {batch[-1]})"
            run_command(f"git commit -m \"{commit_msg}\"")
        
        print(f"  - Pushing...")
        run_command("git push origin main")
        print(f"Batch {batch_num} complete.\n")

    print("All remaining batches processed successfully!")

if __name__ == "__main__":
    main()
