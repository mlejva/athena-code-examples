FROM node:18-alpine

WORKDIR /code

COPY . .
# COPY package.json \
#      package-lock.json \
#      app \
#      public \
#      next.config.js \
#      postcss.config.js \
#      tailwind.config.ts \
#      tsconfig.json ./
# ADD ./* ./
# COPY app ./
# COPY public ./
# COPY app ./
# COPY

RUN npm i

RUN ls -la


EXPOSE 3000
CMD ["npm", "run", "dev"]
