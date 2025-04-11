# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code and tests into the container at /app
COPY src/ ./src
COPY tests/ ./tests 
# Note: We don't strictly need tests in the final image, but including them 
# allows running tests inside the container image if needed later.

# Create output directory within the container
RUN mkdir /app/output 

# Specify the command to run on container start
CMD ["python", "src/fetch_data.py"]
