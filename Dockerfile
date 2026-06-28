# Stable Python 3.11 version ka use karenge jahan error nahi aata
FROM python:3.11-slim

# Linux ke zaroori tools install karne ke liye
RUN apt-get update && apt-get install -y gcc g++ git && rm -rf /var/lib/apt/lists/*

# Project folder set karein
WORKDIR /app

# Sabse pehle requirements copy aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Baki saara code copy karein
COPY . .

# Bot ko chalu karne ki command
CMD ["python", "main.py"]
