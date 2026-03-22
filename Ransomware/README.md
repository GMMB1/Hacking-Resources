# 🔐 Ransomware — Educational Demo

> ⚠️ **DISCLAIMER**: This project is strictly for **educational and research purposes** in a controlled lab environment. It demonstrates how ransomware operates at a conceptual level. **Do NOT run this code on any system you do not own or have explicit written permission to test.** Misuse of this code is illegal and unethical.

---

## 📖 Overview

A simple proof-of-concept ransomware simulation written in Python. It demonstrates:

- XOR-based file encryption / decryption
- Multi-threaded file processing using a thread pool + queue
- A basic C2 (Command & Control) server that receives the encryption key from the victim machine

---

## 📁 File Structure

| File | Description |
|------|-------------|
| `ec.py` | Encryption client — encrypts all files on the Desktop and sends the key to the server |
| `dc.py` | Decryption client — prompts for the key and restores encrypted files |
| `server.py` | C2 listener — receives and logs the hostname + encryption key |
| `main.py` | Entry point placeholder |

---

## ⚙️ Configuration

Before running, set your server IP and port via environment variables (no hardcoded values):

```bash
# Linux / macOS
export C2_IP="192.168.x.x"
export C2_PORT="5678"

# Windows (PowerShell)
$env:C2_IP="192.168.x.x"
$env:C2_PORT="5678"
```

---

## 🚀 Usage (Lab Environment Only)

1. Start the C2 server on your attacker machine:
   ```bash
   python server.py
   ```
2. Run the encryptor on the victim machine:
   ```bash
   python ec.py
   ```
3. To restore files, run the decryptor with the key logged by the server:
   ```bash
   python dc.py
   ```

---

## 🛡️ How It Works

1. `ec.py` generates a random 64-byte XOR key, encrypts every file on the Desktop byte-by-byte, and sends the key + hostname to the C2 server over a TCP socket.
2. `server.py` listens for the incoming connection and saves the hostname:key pair.
3. `dc.py` accepts the key as input and reverses the XOR operation to restore the original files.

---

## 📚 Learning Objectives

- Understand how symmetric encryption (XOR) can be misused
- Understand basic C2 communication patterns
- Learn how to defend against such attacks (network segmentation, EDR, backups)

---

## 📜 License

MIT — for educational use only.
