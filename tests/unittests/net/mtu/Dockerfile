FROM ubuntu:latest

RUN apt-get update --assume-no
RUN apt-get install --assume-yes \
  cloud-init \
  git \
  netplan-generator \
  python3-netplan \
  python3-pip \
  python3-venv \
  meson \
  pkg-config \
  glib2.0 \
  libyaml-dev \
  libsystemd-dev \
  bash-completion \
  pandoc \
  pyflakes3 \
  pycodestyle \
  python3-pytest \
  python3-coverage \
  python3-cffi \
  cmake \
  libcmocka-dev \
  python3-nose

RUN git clone https://github.com/canonical/cloud-init /src/cloud-init

RUN git clone https://github.com/canonical/netplan /src/netplan
WORKDIR /src/netplan

RUN git checkout -b 0.107.1 0.107.1 && \
    meson setup build --wipe --prefix=/usr && \
    meson compile -C build && \
    meson install -C build --destdir /tmp/netplan/0.107.1 && \
    ln -s /tmp/netplan/0.107.1/usr/lib/aarch64-linux-gnu/libnetplan.so.0.0 /usr/lib/aarch64-linux-gnu

RUN git checkout -b 1.0 1.0 && \
    meson setup build --wipe --prefix=/usr && \
    meson compile -C build && \
    meson install -C build --destdir /tmp/netplan/1.0

RUN git checkout main && \
    meson setup build --wipe --prefix=/usr && \
    meson compile -C build && \
    meson install -C build --destdir /tmp/netplan/main

WORKDIR /src/cloud-init