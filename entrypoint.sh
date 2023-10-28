#!/bin/bash

cd /fashion/

gunicorn -k uvicorn.workers.UvicornWorker fashion.asgi:application -b 0.0.0.0:8000