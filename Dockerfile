FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY Requirement.txt .
RUN pip install --no-cache-dir -r Requirement.txt

# Copy source code (adjust if you don’t have src folder)
COPY main.py .
COPY fetch_url.py .
COPY llm_helper.py .
COPY post_generator.py .
COPY preprocess.py .
COPY fewshots.py .
COPY data/ ./data/

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
