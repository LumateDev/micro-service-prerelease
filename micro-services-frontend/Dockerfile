## BUILD ENVIRONMENT
FROM node:20-alpine AS build

# Рабочая директория
WORKDIR /usr/src/app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем проект
COPY . .

# Сборка приложения
RUN npm run build

## PRODUCTION ENVIRONMENT
FROM nginx:stable-alpine

# Копируем конфигурацию Nginx (из папки nginx в проекте)
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Копируем билд React
COPY --from=build /usr/src/app/build /usr/share/nginx/html

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]