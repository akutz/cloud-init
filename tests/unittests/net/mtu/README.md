From the root of this repository:

1. Build the image:

    ```shell
    podman build -f ./tests/unittests/net/mtu/Dockerfile --tag cloud-init-mtu-test:latest .
    ```

2. Run the container:

    ```shell
    podman run -it --rm -v "$(pwd):/src/cloud-init" cloud-init-mtu-test:latest
    ```

3. Set up the virtual environment:

    ```shell
    python3 -m venv /tmp/venv && \
    . /tmp/venv/bin/activate && \
    pip3 install -r test-requirements.txt && \
    pip3 install cffi
    ```

4. Run the test:

    ```shell
    make clean_pyc && \
    PYTHONPATH="$(pwd):/tmp/netplan/main/usr/lib/python3/dist-packages/" \
    python3 -m pytest -v tests/unittests/net/test_netplan.py -vv
    ```