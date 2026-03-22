# Import the base python image
FROM python:3.11-slim

# Installing ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean && rm -rf var/lib/apt/lists/*

# Copy the requirement file to the working directory
# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY requirements.txt .

# Install the python dependencies (using uv is faster)
RUN uv pip install --system --no-cache -r requirements.txt

# Copy the application code to the container
COPY . .

ENV FORCE_COLOR=1
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python" , "main.py"]


