# Cardeep frontend image (Openship "services" integration — see openship.json +
# docs/runbook/DEPLOY_OPENSHIP.md). Two stages: build the Vite/React SPA, then serve
# the static output through nginx, which also reverse-proxies the API so the browser
# never needs to know the API's real address.
#
# Build:  docker build -t cardeep-web web/
# Run:    docker run -p 8080:80 cardeep-web

# ---- Stage 1: build the static bundle -----------------------------------------
# Node 22 — matches .github/workflows/ci.yml's frontend-build job exactly (setup-node
# node-version: "22"), so this image builds with the same runtime CI already validates.
FROM node:22-alpine AS build
WORKDIR /app

# Dependency layer first — cached until package-lock.json changes.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# VITE_* vars are inlined into the JS bundle at BUILD time (Vite, unlike a server
# framework, has no runtime env). Default to the same-origin "/api" prefix that
# nginx.conf proxies to the `api` service below — this needs no real domain to work,
# so the image is deployable before the owner has provisioned one. To point a build
# at a standalone API domain instead (e.g. once api.<domain> exists), override at
# build time: `docker build --build-arg VITE_API_BASE=https://api.example.com web/`.
# VITE_API_KEY trips Docker's generic "secret in ARG/ENV" linter — a false positive
# here: Vite inlines it into the public JS bundle by design (any VITE_-prefixed var
# is shipped to the browser), so it is already public once served, not a build secret.
ARG VITE_API_BASE=/api
ARG VITE_API_KEY=
ENV VITE_API_BASE=$VITE_API_BASE
ENV VITE_API_KEY=$VITE_API_KEY
RUN npm run build

# ---- Stage 2: serve the bundle + proxy the API ---------------------------------
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1
