# Use official Python image
FROM python:3.10-slim

ENV ALPACA_API_KEY_ID=PKQ339A898RGXEO6NK9F
ENV ALPACA_SECRET_KEY=u1IFlQhrUy097zSB7zOa2LGDxeO2GRia3yCP0aK7
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy all project files into the container
COPY . .

# Install pipenv or pip packages
RUN pip install --upgrade pip

# Install requirements (you must have requirements.txt in your root)
RUN pip install -r requirements.txt

# Expose the port Uvicorn will run on
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
