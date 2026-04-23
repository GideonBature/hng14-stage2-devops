# Build stage
FROM node:22-alpine AS builder

WORKDIR /app

# Upgrade packages
RUN apk upgrade --no-cache

# Copy package files
COPY package*.json ./

# Install dependencies and update vulnerable packages
RUN npm install --omit=dev && \
    npm update

# Production stage
FROM node:22-alpine AS production

# Upgrade packages and create non-root user
RUN apk upgrade --no-cache && \
    addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001 && \
    rm -rf /usr/local/lib/node_modules/npm && \
    rm -f /usr/local/bin/npm /usr/local/bin/npx

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/node_modules ./node_modules

# Copy application code
COPY app.js .
COPY views ./views

# Change ownership to non-root user
RUN chown -R nodejs:nodejs /app

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Run the application
CMD ["node", "app.js"]
