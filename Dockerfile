FROM python:3.12

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN playwright install --with-deps

CMD ["python", "main.py"]
