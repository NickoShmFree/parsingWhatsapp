FROM python:3.12

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip

WORKDIR /app
COPY . .

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем браузеры Playwright
RUN playwright install --with-deps

# Запускаем скрипт без poetry
CMD ["python", "main.py"]
