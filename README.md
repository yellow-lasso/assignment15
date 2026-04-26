## Running with Gunicorn

Gunicorn is included as the production WSGI server for deployment.

Note: Gunicorn is not supported on Windows environments due to its dependency on Unix-based modules (e.g., fcntl). As a result, it cannot be run locally on Windows.

However, the application is fully compatible with Gunicorn in Linux-based environments such as cloud deployment platforms.

# Congressional Trade Disclosure Analysis Tool (Web Application – Assignment 14)

## Overview

This project extends the Congressional Trade Disclosure Analysis Tool by preparing the application for production deployment. The application now follows standard professional practices for dependency management, configuration, and server execution.

In this version, sensitive configuration values are managed using environment variables, dependencies are tracked in a requirements file, and the application is configured to run using a production-grade WSGI server (Gunicorn). These improvements align the project with real-world deployment standards.

---

## Features

### 1. Dependency Management

- All required Python packages are listed in `requirements.txt`.
- Dependencies can be installed using:

```bash
pip install -r requirements.txt