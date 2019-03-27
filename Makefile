test:
	python ./pre-commit

json:
	python scripts/regimen_to_json.py > regimen.json

integration-test:
	cd ./integration && make test
	cd ..