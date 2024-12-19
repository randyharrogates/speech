FROM continuumio/miniconda3:latest

# Set the working directory to the root of your project
WORKDIR /app

# Copy the entire project into the container
COPY . .

# Set the working directory to the `src` directory
WORKDIR /app/src

# Set PYTHONPATH to include the src directory
ENV PYTHONPATH=/app/src

# Create the Conda environment using the environment.yml file
RUN conda env create -f /app/environment.yml

# Ensure the application runs in the correct Conda environment using Uvicorn
CMD ["conda", "run", "--no-capture-output", "-n", "dating", "uvicorn", "dating_plan_ai_agents.fastapi.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Expose the required port
EXPOSE 8000
