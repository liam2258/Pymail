# Specificy the version of Python as the parent image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the contents into the container at /app
COPY . /app

# Expose the port the application runs on
EXPOSE $PORT

# Set environment variable for gmail API key
ENV API_KEY=${API_KEY}

# Set environment variable for sender email address
ENV SENDER_EMAIL=${SENDER_EMAIL}

# Set environment variable for receiving email address
ENV RECEIVER_EMAIL=${RECEIVER_EMAIL}

# Set environment variable for database url
ENV DATABASE_URL=${DATABASE_URL}

# Specify commands to run the application
CMD ["python", "main.py"]
