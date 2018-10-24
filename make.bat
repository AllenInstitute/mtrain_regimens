if "%1" == "test" (
	python ./pre-commit
)

if "%1" == "json" (
	python scripts/regimen_to_json.py > regimen.json
)
