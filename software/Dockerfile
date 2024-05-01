# 
FROM python:3.11-bullseye
# the bullseye version was used to avoid a `can't add extra threads` error

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./backend /code/app
# COPY ./app/static/ /code/app/static/
# COPY ./app/templates/ /code/app/templates/


ENV PYTHONPATH "${PYTHONPATH}:/code/app/" 
# this is necessary to use the local file

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]