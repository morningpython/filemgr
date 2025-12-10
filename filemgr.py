#!/usr/bin/env python3
"""
filemgr.py - Interactive CLI file management prototype for Windows (works on other platforms too)

Features:
- Interactive REPL with commands: ls, preview, size, rm, trash, force, takeown, unlock, exit
- Dry-run mode / preview
- Move-to-trash (quarantine) instead of permanent delete
- Force delete (takeown + grant permissions on Windows)
- Optionally finds locking processes using Sysinternals handle.exe (if provided)
- Logging and simple undo by restoring from trash

NOTE: This is a prototype. Please review and test carefully before running on important data.
"""

import os
import sys
import shutil
import argparse
import subprocess
import logging
import datetime
import getpass
from pathlib import Path

# Logging
LOGFILE = Path(__file__).parent / 'filemgr.log'
logging.basicConfig(filename=str(LOGFILE), level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Utilities

def human_readable(num, suffix='B'):
    for unit in ['','K','M','G','T','P']:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}E{suffix}"


def get_total_size(path):
    total = 0
    for root, dirs, files in os.walk(path, onerror=lambda e: None):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def preview(path, n=20):
    print(f"Previewing top {n} items under: {path}")
    count = 0
    for root, dirs, files in os.walk(path, topdown=True):
        for name in dirs + files:
            print(os.path.join(root, name))
            count += 1
            if count >= n:
                return


def confirm(prompt):
    ans = input(f"{prompt} [y/N]: ").strip().lower()
    return ans in ('y','yes')


def get_drive_root(path):
    p = Path(path)
    # On Windows this will be like 'M:\'
    try:
        return p.anchor
    except Exception:
        return str(p)


def ensure_trash_root(root):
    trash_root = Path(root) / '.filemgr_trash'
    try:
        if not trash_root.exists():
            trash_root.mkdir(parents=True, exist_ok=True)
        return trash_root
    except Exception:
        # Fallback: try to create .filemgr_trash in the user's temp dir or the
        # parent directory of the provided root path. This helps CI runners
        # or locked/system roots where creating a root-level folder fails.
        import tempfile

        fallback = Path(tempfile.gettempdir()) / '.filemgr_trash'
        try:
            fallback.mkdir(parents=True, exist_ok=True)
            return fallback
        except Exception:
            # Final fallback: use current working directory
            cwd_trash = Path.cwd() / '.filemgr_trash'
            cwd_trash.mkdir(parents=True, exist_ok=True)
            return cwd_trash


def move_to_trash(path):
    root = get_drive_root(path)
    trash_root = ensure_trash_root(root)
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = trash_root / f"deleted_{ts}"
    try:
        shutil.move(path, str(dest))
        logging.info(f"Moved to trash: {path} -> {dest}")
        return dest
    except Exception as e:
        logging.error(f"Failed to move to trash: {path} - {e}")
        raise


def remove_recursive(path, force=False, to_trash=True):
    path = Path(path)
    if not path.exists():
        print("경로가 존재하지 않습니다.")
        return False

    if to_trash:
        try:
            dest = move_to_trash(str(path))
            print(f"이동 완료 (복원 가능): {dest}")
            return True
        except Exception:
            print("파일을 휴지통(격리소)에 옮기는 데 실패했습니다. 강제 삭제를 시도합니다.")

    # try to delete
    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        logging.info(f"Deleted: {path}")
        print("삭제 완료")
        return True
    except Exception as e:
        logging.error(f"Delete failed: {path} - {e}")
        print(f"삭제 실패: {e}")
        if force and os.name == 'nt':
            print("Windows 권한 강제 조정 후 재시도합니다...")
            if windows_takeown_and_icacls(str(path)):
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                except Exception as e2:
                    logging.error(f"Delete after ownership change failed: {e2}")
                    print(f"여전히 삭제 실패: {e2}")
                    return False
                logging.info(f"Deleted after takeown: {path}")
                print("삭제 완료")
                return True
        return False


def windows_takeown_and_icacls(path):
    try:
        # Using cmd to run takeown and icacls
        print("takeown 실행 중...")
        subprocess.run(['cmd', '/c', f'takeown /F "{path}" /R /D Y'], check=True)
        print("icacls 권한 부여 중...")
        subprocess.run(['cmd', '/c', f'icacls "{path}" /grant Administrators:F /T'], check=True)
        logging.info(f"Took ownership and granted permissions: {path}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"takeown/icacls failed: {e}")
        print("takeown/icacls 실패: 관리자 권한으로 실행되어야 할 수 있습니다.")
        return False


def find_handles_using_handle(path):
    # 'handle.exe' must be in PATH or in the same folder
    exe = shutil.which('handle.exe')
    if not exe:
        print("'handle.exe'를 찾을 수 없습니다. Sysinternals Handle 도구를 설치하고 PATH에 추가하세요.")
        return None
    try:
        proc = subprocess.run([exe, '-a', path], capture_output=True, text=True)
        return proc.stdout
    except Exception as e:
        print(f"handle.exe 실행 실패: {e}")
        return None


def list_roots():
    # Windows specific: enumerate drive letters
    roots = []
    if os.name == 'nt':
        for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drive = f"{d}:\\"
            if os.path.exists(drive):
                roots.append(drive)
    else:
        roots = ['/']
    return roots


# Interactive REPL

def repl():
    print("CLI File Manager Prototype - Type 'help' for commands (Windows focused)")
    while True:
        try:
            line = input('filemgr> ').strip()
        except EOFError:
            print('')
            break
        if not line:
            continue
        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ('exit','quit'):
            break
        elif cmd == 'help':
            print("""
Commands:
  ls <path>          - List a folder's contents
  preview <path>     - Show top 20 items under path
  size <path>        - Show total size
  rm <path>          - Delete with confirmation (moves to .filemgr_trash by default)
  rm! <path>         - Force delete (try ownership change)
  trash <path>       - Move to trash/quarantine
  takeown <path>     - Run takeown/icacls for path (Windows)
  handles <path>     - Show handle.exe output (if installed)
  roots              - List available drive roots
  help               - Show this help
  exit               - Exit
""")

        elif cmd == 'roots':
            print('Available roots:')
            for r in list_roots():
                print('  ', r)

        elif cmd == 'ls' and args:
            p = args[0]
            try:
                for entry in os.listdir(p):
                    print(entry)
            except Exception as e:
                print(e)

        elif cmd == 'preview' and args:
            preview(args[0], n=20)

        elif cmd == 'size' and args:
            p = args[0]
            if Path(p).exists():
                s = get_total_size(p)
                print('총 크기:', human_readable(s))
            else:
                print('경로가 존재하지 않습니다.')

        elif cmd == 'rm' and args:
            p = args[0]
            print('미리보기:')
            preview(p, n=10)
            if confirm('정말 삭제하시겠습니까? (휴지통으로 이동)'):
                remove_recursive(p, force=False, to_trash=True)

        elif cmd == 'rm!' and args:
            p = args[0]
            print('미리보기:')
            preview(p, n=10)
            if confirm('정말 강제 삭제하시겠습니까? (권한 취득 시도 후 삭제)'):
                remove_recursive(p, force=True, to_trash=False)

        elif cmd == 'trash' and args:
            p = args[0]
            if confirm('정말 휴지통으로 이동하시겠습니까?'):
                try:
                    dest = move_to_trash(p)
                    print(f'휴지통으로 이동됨: {dest}')
                except Exception as e:
                    print(e)

        elif cmd == 'takeown' and args:
            p = args[0]
            windows_takeown_and_icacls(p)

        elif cmd == 'handles' and args:
            p = args[0]
            out = find_handles_using_handle(p)
            if out is not None:
                print(out)

        else:
            print('알 수 없는 명령 혹은 인자가 비어있습니다. help를 참고하세요.')


# Command-line entry

def main():
    parser = argparse.ArgumentParser(description='Interactive CLI File Manager (prototype)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Start interactive shell')
    parser.add_argument('cmd', nargs='*', help='Optional CLI command (see help)')
    args = parser.parse_args()

    if args.interactive or not args.cmd:
        repl()
    else:
        # Allow some single shot commands like: filemgr.py rm "M:\\temp\\Takeout" --force
        # Very limited parsing
        parts = args.cmd
        if parts[0] == 'preview' and len(parts) > 1:
            preview(parts[1])
        elif parts[0] == 'size' and len(parts) > 1:
            s = get_total_size(parts[1]); print(human_readable(s))
        elif parts[0] == 'rm' and len(parts) > 1:
            remove_recursive(parts[1], force='--force' in parts)
        else:
            print('단일 명령 파싱 불가 혹은 지원되지 않음. interactive 모드로 실행하세요.')


if __name__ == '__main__':
    main()
