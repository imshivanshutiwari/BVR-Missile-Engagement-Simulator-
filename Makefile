.PHONY: install server client run test nez physics build lint clean

install:
	pip install -r requirements.txt && npm install

server:
	uvicorn server.main:app --port 8000 --reload &

client:
	npm run dev &

run: server client
	sleep 3 && start http://localhost:5173

test:
	pytest tests/ -v --color=yes

nez:
	python -c "from physics.engagement.nez_computer import NoEscapeZoneComputer; n=NoEscapeZoneComputer(); r=n.compute_full_nez({'speed':250,'alt':8000}); print(f'NEZ computed: {len(r)} points')"

physics:
	python -c "from physics.engagement.engagement_engine import EngagementEngine; e=EngagementEngine(); r=e.run('head_on'); print(f'Intercept: {r[\"intercept_achieved\"]}, Miss: {r[\"miss_distance_m\"]:.2f}m, Pk: {r[\"pk\"]:.3f}')"

build:
	npm run build

lint:
	flake8 physics/ server/ --max-line-length=100

clean:
	find . -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
