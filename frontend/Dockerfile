FROM node:22-alpine

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json ./
COPY pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install

# Copy app
COPY . .

# Expose port
EXPOSE 3000

# Start dev server
CMD ["pnpm", "dev", "--host", "0.0.0.0"]
