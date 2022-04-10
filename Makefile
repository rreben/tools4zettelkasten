MODULE := tools4zettelkasten
BLUE='\033[0;34m'
NC='\033[0m' # No Color

run:
	@python -m $(MODULE)

test:
	@pytest

testdebug:
	@pytest --pdb

coverage:
	coverage run -m pytest
	coverage html

lint:
	@echo "\n${BLUE}Running Pylint against source and test files...${NC}\n"
	@pylint --rcfile=setup.cfg **/*.py
	@echo "\n${BLUE}Running Flake8 against source and test files...${NC}\n"
	@flake8
	@echo "\n${BLUE}Running Bandit against source files...${NC}\n"
	@bandit -r --ini setup.cfg

clean:
	rm -rf .pytest_cache .coverage .pytest_cache coverage.xml reports/ htmlcov/ dist/ build/ tools4zettelkasten.egg-info//

.PHONY: clean test