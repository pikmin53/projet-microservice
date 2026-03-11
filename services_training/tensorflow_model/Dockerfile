# fast and light python image
FROM python:3.11-slim

WORKDIR /app

# Copy the requirements
COPY requirements.txt .

# Install the requirements
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory
RUN mkdir -p /app/data

# Téléchargement du dataset au build avec stockage dans /app/data
RUN KERAS_HOME=/app/data python -c "import os; os.environ['TF_CPP_MIN_LOG_LEVEL']='3'; import tensorflow as tf; tf.keras.datasets.cifar100.load_data()"

# Copy the code
COPY . .

# The next command will be surcharged in docker-compose, but will be used in prod

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]