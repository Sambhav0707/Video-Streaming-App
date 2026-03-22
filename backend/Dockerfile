# Import the base python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app 

# Copy the requirement file to the working directory
# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY requirement.txt .

# Install the python dependencies (using uv is faster)
RUN uv pip install --system --no-cache -r requirement.txt

# Copy the application code to the container
COPY . .

# Expose port 8000 for access
EXPOSE 8000

ENV FORCE_COLOR=1
ENV PYTHONUNBUFFERED=1

# Command to run the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--use-colors"]
