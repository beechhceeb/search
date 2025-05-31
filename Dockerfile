FROM python:3.13

# Copy necessary files
COPY ./poetry.lock /mpb/poetry.lock
COPY ./pyproject.toml /mpb/pyproject.toml
COPY ./package.json /mpb/package.json
COPY ./package-lock.json /mpb/package-lock.json
COPY ./webpack.config.js /mpb/webpack.config.js
COPY ./src /mpb/src

# This should be done by webpack, but it isn't working when deployed
COPY ./node_modules/piexifjs/piexif.js /mpb/src/static/piexif.js
COPY ./node_modules/progressbar.js/dist/progressbar.js /mpb/src/static/progressbar.js

WORKDIR /mpb/

# Install dependencies
RUN pip install -U pip
RUN pip install poetry
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean
RUN poetry config virtualenvs.create false
RUN npm ci
RUN npm run build
RUN bash -c "poetry install --no-root;"


# Expose the application port
EXPOSE 8080

# Set environment variables
ENV FLASK_APP=/mpb/src/app.py
ENV FLASK_DEBUG=1
ENV FLASK_RUN_PORT=8080
ENV PYTHONPATH=/mpb/src

# Set the default command to run the Flask application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]