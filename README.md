# Flask URL Shortener

A simple URL shortener built with Flask and PostgreSQL.

## Prerequisites

- Python
- Flask
- PostgreSQL

## Setup

### 1. Clone the repository:

```bash
git clone https://github.com/leonidlouis/flask-sample-url-shortener
cd flask-sample-url-shortener
```

### 2. Set up a virtual environment (optional, but recommended):

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install the necessary packages:

```bash
pip install -r requirements.txt
```

### 4. Set up the PostgreSQL database:

Ensure PostgreSQL is running and execute the SQL script to create the required table:

```sql
CREATE TABLE urls (
    id SERIAL PRIMARY KEY,
    original_url TEXT NOT NULL,
    short_code VARCHAR(6) NOT NULL UNIQUE
);
```

### 5. Configure .env:

Create a .env file and fill it in with the appropriate information, example is in `.env.example`.

### 6. Run the application:

```bash
python main.py
```

By default, the server will start on port 3000.

## Usage

- **Shorten URL**: Send a POST request to `/api/shorten` with a JSON payload containing the original URL. Example:

  ```json
  {
    "original_url": "https://www.example.com"
  }
  ```

- **Access Shortened URL**: Navigate to `http://localhost:[PORT]/[short_code]` in your browser.

- **Retrieve Original URL**: Send a GET request to `/api/[short_code]`.

- **Update Original URL**: Send a PUT request to `/api/[short_code]` with a new original URL in the JSON payload. Example:

  ```json
  {
    "original_url": "https://www.updated-example.com"
  }
  ```

- **Delete Short URL**: Send a DELETE request to `/api/[short_code]`.
