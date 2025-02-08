FROM public.ecr.aws/sam/build-python3.12:latest

WORKDIR /app

# Copy the backend source code into the container
COPY src /app/src
COPY src/requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app/src

# Define an entrypoint which will run the main app using the Gunicorn WSGI server.
ENTRYPOINT ["gunicorn", "-b", ":8080", "src.api:app"]
