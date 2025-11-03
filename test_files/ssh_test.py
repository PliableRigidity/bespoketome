# #!/usr/bin/env python3
# import paramiko

# HOST = "Skyline"
# USER = "ishaan"
# CMD  = "bash -lc 'ifconfig'"   # <<< changed

# def main():
#     pw = "101110"

#     client = paramiko.SSHClient()
#     client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     try:
#         client.connect(
#             HOST,
#             port=22,
#             username=USER,
#             password=pw,
#             look_for_keys=False,
#             allow_agent=False,
#             timeout=10,
#         )
#         stdin, stdout, stderr = client.exec_command(CMD)  # you can also add get_pty=True
#         print(stdout.read().decode(), end="")
#         err = stderr.read().decode()
#         if err:
#             print(err, end="")
#     finally:
#         client.close()

# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
# interactive_ssh_unix.py

#!/usr/bin/env python3
# interactive_ssh_windows.py — interactive SSH session (Windows-friendly)

import paramiko
import threading
import sys
import getpass

HOST = "Skyline"   # your Raspberry Pi hostname or IP
USER = "ishaan"

def write_all(chan):
    """Thread that sends keyboard input to the SSH channel."""
    try:
        while True:
            data = sys.stdin.read(1)
            if not data:
                break
            # Ctrl-] to quit
            if data == "\x1d":
                break
            chan.send(data)
    except Exception:
        pass

def main():
    pw = "101110"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=pw, look_for_keys=False)

    chan = client.invoke_shell()   # open an interactive shell
    print(f"\nConnected to {HOST}. Type commands directly here. Press Ctrl-] to exit.\n")

    writer = threading.Thread(target=write_all, args=(chan,), daemon=True)
    writer.start()

    try:
        while True:
            data = chan.recv(1024)
            if not data:
                break
            sys.stdout.write(data.decode(errors="ignore"))
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        chan.close()
        client.close()
        print("\nDisconnected.")

if __name__ == "__main__":
    main()
