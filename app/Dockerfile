# Use a multi-stage build for efficiency
FROM python:3.11.4-slim-buster as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Final stage
FROM python:3.11.4-slim-buster

# Set environment variables
ENV HOME=/home/app
ENV APP_HOME=/home/app/web

# Create app directories and set work directory
RUN mkdir -p $APP_HOME/staticfiles $APP_HOME/mediafiles
WORKDIR $APP_HOME

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends netcat tini && \
    rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder stage
COPY --from=builder /wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy project files
COPY . $APP_HOME

# Verify the contents of the $APP_HOME directory
RUN ls -lah $APP_HOME

# Ensure the app user owns all files and directories under $APP_HOME
RUN addgroup --system app && adduser --system --group app && \
    chown -R app:app $APP_HOME && \
    chmod -R 755 $APP_HOME

# Verify that app-entrypoint.sh exists, set ownership, and ensure it is executable
COPY ./app-entrypoint.sh /home/app/web/app-entrypoint.sh
RUN chown app:app /home/app/web/app-entrypoint.sh && chmod +x /home/app/web/app-entrypoint.sh

# Switch to the app user
USER app

# Set entrypoint
ENTRYPOINT ["tini", "--", "/home/app/web/app-entrypoint.sh"]

