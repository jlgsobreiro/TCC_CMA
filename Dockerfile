FROM python:3.12-alpine as flask_container

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade redis

# Make port 80 available to the world outside this container
EXPOSE 5000

# run app.py when the container launches
CMD ["python", "app.py"]
