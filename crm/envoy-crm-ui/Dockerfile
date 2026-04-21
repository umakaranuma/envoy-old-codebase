# syntax=docker/dockerfile:1

ARG NODE_VERSION=22

FROM node:${NODE_VERSION}-alpine AS base

ARG S3_REGION
ARG S3_BUCKET_NAME
ARG S3_SECRET_ACCESS_KEY 
ARG S3_ACCESS_KEY_ID
ARG S3CDN
ARG S3CDN_Domain

ARG BUILD_ARGUMENT_ENV

WORKDIR /app

FROM base AS deps

RUN apk add --no-cache libc6-compat

COPY package.json package-lock.json* ./

RUN \
    if [ -f package.json ]; then npm install; \
    else echo "Package not found." && exit 1; \
    fi

FROM deps AS build

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN if [ "$BUILD_ARGUMENT_ENV" = "default" ]; then echo "Set BUILD_ARGUMENT_ENV in docker build-args like --build-arg BUILD_ARGUMENT_ENV=dev" && exit 2; \
    elif [ "$BUILD_ARGUMENT_ENV" = "dev" ]; then echo "Building development environment."; cp docker/dev/.env.production.example .env.production; \
    elif [ "$BUILD_ARGUMENT_ENV" = "qa" ]; then echo "Building test environment."; cp docker/qa/.env.production.example .env.production; \
    elif [ "$BUILD_ARGUMENT_ENV" = "demo" ]; then echo "Building demo environment."; cp docker/demo/.env.production.example .env.production; \
    elif [ "$BUILD_ARGUMENT_ENV" = "uat" ]; then echo "Building staging environment."; cp docker/uat/.env.production.example .env.production; \
    else echo "Set correct BUILD_ARGUMENT_ENV in docker build-args like --build-arg BUILD_ARGUMENT_ENV=qa. Available choices are dev,qa,demo & prod." && exit 2; \
    fi

ENV NEXT_TELEMETRY_DISABLED=1

ENV S3_REGION=${S3_REGION}
ENV S3_BUCKET_NAME=${S3_BUCKET_NAME}
ENV S3_SECRET_ACCESS_KEY=${S3_SECRET_ACCESS_KEY}
ENV S3_ACCESS_KEY_ID=${S3_ACCESS_KEY_ID}
ENV S3CDN=${S3CDN}
ENV S3CDN_Domain=${S3CDN_Domain}

RUN \
    if [ -f package.json ]; npm run wordbook:pull; then npm run build; \
    else echo "Package not found." && exit 1; \
    fi

FROM base AS final

ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0
ENV PORT=3000

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

RUN mkdir .next
RUN chown nextjs:nodejs .next

COPY --from=build --chown=nextjs:nodejs /app/public ./public
COPY --from=build --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=build --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000

ENTRYPOINT ["node", "server.js"]
