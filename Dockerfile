# Use the official Python image
FROM python:3.13-slim

# Set the working directory
WORKDIR /bot

# Install Poetry
RUN pip install poetry

# Copy the project files
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev

# Copy the rest of the application
COPY . .

# Run the application
CMD ["poetry", "run", "python", "main.py"]
