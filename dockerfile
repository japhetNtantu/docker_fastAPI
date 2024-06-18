FROM python:3.9-slim
 

WORKDIR /app
 
COPY requirements.txt .
 
# Install dependencies
RUN pip install -r requirements.txt
 
COPY . .
 
# Expose port 8000 for the web application
EXPOSE 8000
 
 
# Set working directory and run the command to start the web application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]