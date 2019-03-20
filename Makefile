test:
	python ./pre-commit

json:
	python scripts/regimen_to_json.py > regimen.json

integration:
	docker-compose -f integration/docker-compose.yml
	python integration/integration_test.py