FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make the start script executable
RUN chmod +x ./start.sh

# Expose the ports for both services
EXPOSE 8000 
EXPOSE 8501

# The start command will run our script
CMD ["bash", "./start.sh"]
