# Run tests and lint
python -m pip install -r requirements.txt
python -m pytest -q --disable-warnings --maxfail=1
