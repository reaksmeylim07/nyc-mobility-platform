# Official Airflow image, pinned to the same Python version as our project
FROM apache/airflow:3.3.2-python3.12

ARG AIRFLOW_VERSION=3.3.2
ARG PYTHON_VERSION=3.12

# Install our package into Airflow's environment, using Airflow's tested version
# constraints so we never upgrade a library Airflow depends on.
COPY pyproject.toml /opt/nyc-mobility/pyproject.toml
COPY src/ /opt/nyc-mobility/src/
RUN pip install --no-cache-dir \
      --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt" \
      /opt/nyc-mobility