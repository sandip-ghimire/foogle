FROM python:3.11.1

RUN apt-get update \
	&& apt-get install --no-install-recommends -y \
	nginx 

COPY nginx.conf /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log
	
RUN mkdir /app
WORKDIR /app
ADD . /app/
RUN chown -R www-data:www-data /app/foogal

ENV VIRTUAL_ENV=/app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt install dos2unix
RUN apt install nano
RUN apt install -y uglifyjs
RUN dos2unix manage.py
RUN chmod +x manage.py start-service.sh
RUN ./manage.py migrate
RUN ./manage.py makemigrations foogal
RUN ./manage.py migrate foogal
RUN ./manage.py initial_setup
RUN ./manage.py collectstatic --noinput
RUN ./manage.py compress --force

CMD ["/app/start-service.sh"]
