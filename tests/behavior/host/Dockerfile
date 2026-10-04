FROM node:22.23.1-alpine
RUN apk add --no-cache python3 git jq bash curl \
 && npm install --global @anthropic-ai/claude-code@2.1.289 \
 && git config --system --add safe.directory '*' \
 && adduser -D -u 1001 trial
USER trial
ENV HOME=/home/trial
WORKDIR /home/trial
