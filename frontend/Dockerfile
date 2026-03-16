# Etapa 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY . .

# Compilar la aplicación
RUN npm run build

# Etapa 2: Runtime
FROM node:18-alpine

WORKDIR /app

# Instalar serve para servir la aplicación React
RUN npm install -g serve

# Copiar archivos compilados desde builder
COPY --from=builder /app/build ./build
COPY --from=builder /app/package*.json ./

# Instalar dependencias de producción
RUN npm ci --production

# Exponer puerto
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD npm list serve > /dev/null 2>&1 || exit 1

# Comando para ejecutar la aplicación
CMD ["serve", "-s", "build", "-l", "3000"]
