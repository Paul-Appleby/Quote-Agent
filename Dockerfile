FROM python:3.9-slim

# Set up working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for webhook data
RUN mkdir -p webhook_data

# Run the Flask server with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "server:app"] 