{
  "apps": [
    {
      "name": "ptsp-backend",
      "script": "rag_api.py",
      "cwd": "/home/user/ptspRag",
      "interpreter": "/home/user/ptspRag/venv/bin/python",
      "env": {
        "PYTHONPATH": "/home/user/ptspRag",
        "PORT": "8001",
        "HOST": "0.0.0.0"
      },
      "instances": 1,
      "exec_mode": "fork",
      "watch": false,
      "max_memory_restart": "1G",
      "error_file": "./logs/backend-error.log",
      "out_file": "./logs/backend-out.log",
      "log_file": "./logs/backend-combined.log",
      "time": true
    },
    {
      "name": "ptsp-frontend",
      "script": "npm",
      "args": "start",
      "cwd": "/home/user/ptspRag/ptsp-chat",
      "env": {
        "NODE_ENV": "production",
        "PORT": "3000",
        "NEXT_PUBLIC_API_URL": "http://localhost:8001"
      },
      "instances": 1,
      "exec_mode": "fork",
      "watch": false,
      "max_memory_restart": "512M",
      "error_file": "./logs/frontend-error.log",
      "out_file": "./logs/frontend-out.log",
      "log_file": "./logs/frontend-combined.log",
      "time": true
    }
  ]
}
