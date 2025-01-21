# ---- Base Python Image ----
    FROM python:3.9-slim

    # ---- Set working directory ----
    WORKDIR /app
    
    # ---- Install OS-level dependencies (if any) ----
    # RUN apt-get update && apt-get install -y <dependencies you need>
    
    # ---- Copy files into the container ----
    COPY requirements.txt .
    RUN pip install --no-cache-dir --upgrade pip && \
        pip install --no-cache-dir -r requirements.txt
    
    COPY . .
    
    # ---- Expose Streamlit default port ----
    EXPOSE 8501
    


    # ---- Command to run on container start ----
    CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
    