FROM python:3.11-slim

WORKDIR /app

# Build context is the repository root so that both the master service
# source tree AND the top-level `ansible/` directory (served to nodes by
# the `/api/v1/static/ansible.tar.gz` endpoint) are available inside the
# image. Without this, Path(__file__).parent.parent.parent / "ansible"
# resolves to a non-existent path in the container and the install.sh
# bootstrap flow 500s.
COPY master/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY master/ /app/
COPY ansible/ /app/ansible/

ENV PYTHONPATH=/app
ENV KOSATKA_ANSIBLE_DIR=/app/ansible

CMD ["uvicorn", "kosatka_master.main:app", "--host", "0.0.0.0", "--port", "8000"]
