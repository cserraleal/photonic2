# Photonic2

This project provides a solar calculator built with Streamlit.  The code is now organised as a Python package inside the `photonic` directory for better modularity and easier imports.

## Folder structure

```
photonic2/
├── photonic/           # package containing the application
│   ├── app.py          # Streamlit entry point
│   ├── main.py         # example CLI usage
│   ├── config/         # constants and configuration
│   ├── logic/          # calculation modules
│   └── pages/          # Streamlit pages
├── data/               # JSON data files
├── assets/             # static assets
├── setup.sh            # create virtual environment and install deps
├── run.sh              # run the Streamlit app
```

## Setup

From a terminal on macOS run:

```bash
bash setup.sh
```

This creates a virtual environment in `venv` and installs all required dependencies.

## Running the app

Activate the environment and start the server with:

```bash
bash run.sh
```

A browser window will open with the Streamlit interface.

