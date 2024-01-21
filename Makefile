# Do a goal to test with poetry and pytest
# Usage: make rebalance
rebalance:
	poetry run python pyfinance/rebalance.py 5 /tmp/portfolio.csv 
# Usage: make test
test:
	poetry run pytest tests/test_rebalance.py
