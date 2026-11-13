FROM ruby:3.3-slim

ARG UID=1000
ARG GID=1000

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git ca-certificates libssl-dev pkg-config zlib1g-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -g "${GID}" -o jekyll \
    && useradd -m -u "${UID}" -g "${GID}" -o -s /bin/bash jekyll \
    && git config --system --add safe.directory '*'

ENV BUNDLE_PATH=/usr/local/bundle \
    BUNDLE_APP_CONFIG=/usr/local/bundle \
    BUNDLE_BIN=/usr/local/bundle/bin \
    LANG=C.UTF-8

WORKDIR /workspace/docs

COPY Gemfile Gemfile.lock* ./
RUN bundle install --jobs 4 --retry 3 \
    && chmod -R a+rX /usr/local/bundle

USER jekyll
EXPOSE 4000 35729

CMD ["bundle", "exec", "jekyll", "serve", "--host", "0.0.0.0", "--incremental", "--livereload", "--config", "_config.yml,_config.docker.yml"]
