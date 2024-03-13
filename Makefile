.PHONY: serve

serve: env
	env/bin/uvicorn loglyzer:app --reload

env: requirements.txt
	touch -c env
	test -d env || python -m venv env
	env/bin/pip install -r requirements.txt
