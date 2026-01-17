# ==========================================
# 🐍 BACKEND : DÉVELOPPEMENT
# ==========================================
FROM python:3.13-slim as backend_dev
WORKDIR /backend
COPY backend/ ./
RUN pip install -r requirements.txt
CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "3000"]
EXPOSE 3000

# ==========================================
# 🐍 BACKEND : PRODUCTION
# ==========================================
FROM python:3.13-slim as backend_prod
WORKDIR /backend
COPY backend/ ./
RUN pip install -r requirements.txt
CMD ["fastapi", "run", "--port", "3000"]
EXPOSE 3000

# ==========================================
# 🎨 FRONTEND : DÉVELOPPEMENT
# ==========================================
FROM node:lts-alpine as frontend_dev
WORKDIR /frontend
COPY frontend/ ./
RUN npm install 
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "7958"]
EXPOSE 7958

# ==========================================
# 🏗️ FRONTEND : CONSTRUCTION (BUILD)
# ==========================================
FROM node:lts-alpine as frontend_build
WORKDIR /frontend
COPY frontend/ ./
RUN npm install
RUN npm run build  

# ... (le début du fichier reste identique)

# ==========================================
# 🚀 FRONTEND : PRODUCTION (NGINX)
# ==========================================
FROM nginx:alpine as frontend_prod

COPY nginx.conf /etc/nginx/nginx.conf

COPY --from=frontend_build /frontend/dist /usr/share/nginx/html

EXPOSE 80