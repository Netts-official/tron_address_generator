# 🧪 TRON Vanity Address Generator

This Python script generates random TRON blockchain addresses in multiple threads and stops when it finds one ending with `Netts` or `Nettsio`.

---

## ✨ Features

- 🔁 Multi-threaded (default: 50 threads)
- 📝 Saves generated addresses and private keys to per-thread files
- 📦 Logging to both `console.log` and `address_generator.log`
- 🛑 Graceful stop once a matching address is found

---

## 📁 Project Structure

```
project_root/
├── app/
│   └── address_generator.py
├── logs/
│   ├── address_generator.log
│   └── console.log
```

---

## 🧰 Requirements

Install Python dependencies:

```bash
pip install tronpy
```

---

## 🚀 Run Script in Background

Use `nohup` to keep the process running after terminal close:

```bash
nohup python3 app/address_generator.py > logs/console.log 2>&1 &
```

This will:

- Start address generation in 50 threads
- Write logs to `logs/address_generator.log`
- Redirect stdout/stderr to `logs/console.log`

---

## 📄 Output

Each thread writes to its own file:

```
addresses_thread_1.txt
addresses_thread_2.txt
...
addresses_thread_50.txt
```

Each line:

```
Address: TXXX..., PrivateKey: XXXXX...
```

---

## 🛑 Stop the Process

Find the process:

```bash
ps aux | grep address_generator.py
```

Then kill it:

```bash
kill <PID>
```

---

## ⚙️ Customize

You can change the number of threads in the `main()` function:

```python
num_threads = 50
```

---

## 📜 License

MIT — Use freely, modify for your needs.

# Commands

'python3 -m venv venv'
'source venv/bin/activate'
'deactivate'
'pip install requests'
'pip install -r requirements.txt'
'chmod +x star_pool.sh'
'pip freeze > requirements.txt'
'ps aux | grep python'
