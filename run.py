import sys
import os
import socket
import subprocess
import uvicorn
import webbrowser
import threading
import time

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

backend_dir = os.path.join(os.path.dirname(__file__), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


# Cổng mặc định là 3000 (khớp với tab đang mở trên trình duyệt của bạn)
DEFAULT_PORT = 3000
ALT_PORT = 8000
if len(sys.argv) > 1 and sys.argv[1].isdigit():
    DEFAULT_PORT = int(sys.argv[1])

def free_port(port):
    """Kiểm tra và giải phóng port nếu có tiến trình cũ đang chiếm giữ"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return # Port đang trống
        
        if sys.platform == "win32":
            cmd = f'powershell -Command "(Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue).OwningProcess"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            pids = set(result.stdout.strip().split())
            current_pid = str(os.getpid())
            for pid in pids:
                if pid and pid != current_pid and pid != "0":
                    print(f">>> Đang giải phóng cổng {port} (Đóng tiến trình cũ PID: {pid})...")
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
            time.sleep(0.8)
    except Exception as e:
        print(f"Lưu ý kiểm tra port {port}: {e}")

def start_port_forwarder(from_port, to_port):
    """Chuyển tiếp cổng 8000 sang 3000 để truy cập cổng nào cũng hoạt động"""
    def forward_worker():
        try:
            free_port(from_port)
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('127.0.0.1', from_port))
            server.listen(50)
            while True:
                client_sock, _ = server.accept()
                threading.Thread(target=handle_client, args=(client_sock, to_port), daemon=True).start()
        except Exception:
            pass

    def handle_client(client_sock, dest_port):
        try:
            target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_sock.connect(('127.0.0.1', dest_port))
            def pipe(s1, s2):
                try:
                    while True:
                        data = s1.recv(8192)
                        if not data:
                            break
                        s2.sendall(data)
                except Exception:
                    pass
                finally:
                    try: s1.close()
                    except Exception: pass
                    try: s2.close()
                    except Exception: pass

            threading.Thread(target=pipe, args=(client_sock, target_sock), daemon=True).start()
            threading.Thread(target=pipe, args=(target_sock, client_sock), daemon=True).start()
        except Exception:
            try: client_sock.close()
            except Exception: pass

    threading.Thread(target=forward_worker, daemon=True).start()

def open_browser():
    time.sleep(1.8)
    print(f">>> Đang mở giao diện PetCare AI Pro trên trình duyệt: http://localhost:{DEFAULT_PORT}")
    webbrowser.open(f"http://localhost:{DEFAULT_PORT}")

if __name__ == "__main__":
    print("=" * 70)
    print("HỆ THỐNG QUẢN LÝ THÚ CƯNG & LỊCH CHĂM SÓC CÓ TÍCH HỢP AI (PETCARE AI PRO)")
    print("ĐẠI HỌC THÁI NGUYÊN - TRƯỜNG ĐH CNTT & TT (ICTU)")
    print("Học phần: AIA331 - Ứng dụng trí tuệ nhân tạo | Mã số: 80286")
    print(f"Hỗ trợ cả 2 cổng: http://localhost:{DEFAULT_PORT} và http://localhost:{ALT_PORT}")
    print("=" * 70)

    # 1. Giải phóng cổng 3000 & 8000
    free_port(DEFAULT_PORT)
    free_port(ALT_PORT)

    # 2. Khởi động cầu nối chuyển tiếp 8000 -> 3000
    start_port_forwarder(ALT_PORT, DEFAULT_PORT)

    # 3. Mở trình duyệt tự động
    threading.Thread(target=open_browser, daemon=True).start()

    # 4. Khởi động máy chủ chính FastAPI trên port 3000
    print(f"Máy chủ đang phục vụ tại:")
    print(f" - http://localhost:{DEFAULT_PORT}")
    print(f" - http://localhost:{ALT_PORT}")
    print(f" - Tài liệu Swagger API: http://localhost:{DEFAULT_PORT}/docs")
    print("=" * 70)

    uvicorn.run("main:app", host="127.0.0.1", port=DEFAULT_PORT, reload=False)
