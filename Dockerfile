# Imagem base leve
FROM python:3.11-slim

# Evita prompts interativos
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependências do sistema (yt-dlp + ffmpeg)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instalar yt-dlp
RUN pip install --no-cache-dir yt-dlp

# Criar diretório da aplicação
WORKDIR /app

# Copiar arquivos
COPY app.py /app/app.py

# Instalar Flask
RUN pip install --no-cache-dir flask

# Porta padrão (Railway ignora, mas é boa prática)
EXPOSE 8080

# Comando de execução
CMD ["python", "app.py"]