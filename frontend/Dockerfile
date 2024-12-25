
FROM node:23
WORKDIR /app
COPY frontend/package*.json /app/
RUN npm install
COPY frontend/ /app/
EXPOSE 3000
# Command to start the React app
CMD ["npm", "start"]
