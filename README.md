# FastAPI Starter

Simple skeleton for starting a FastAPI project, with no database or authentication.


## Setting up the development environment

### `uv`

This project uses [`uv`](https://docs.astral.sh/uv/) to manage the Python interpreter and virtual environment. To install `uv` using Homebrew:

```bash
brew install uv
```

To install with the standalone installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Once `uv` is installed, synchronize the virtual environment with:

```bash
uv sync
```


### Configure environment variables

Create an `.env` file in the root of the project by starting with the `local-example.env` file:

```bash
cp local-example.env .env
```

Edit the `.env` file to set the environment variables as needed.

You can check that the app loads the environment variables correctly by running:

```bash
uv run fastapi-starter config show
```


### Running tests

To run the tests, use the following command:

```bash
uv run pytest
```


### Running the API server

To run the API server for development, use the following command:

```bash
uv run fastapi-starter serve --reload
```

You can see the API docs and interact with the API by visiting [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.
