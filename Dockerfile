# Gunakan Python versi 3.11 (sesuai project Anda)
FROM python:3.11-slim

# Set folder kerja di dalam container
WORKDIR /app

# --- BAGIAN INI DIPERBAIKI ---
# Menghapus 'software-properties-common' yang menyebabkan error
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*
# -----------------------------

# Copy requirements dan install library Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode project ke dalam container
COPY . .

# Buka port untuk Streamlit
EXPOSE 8501

# Cek kesehatan container
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Command default
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]