css: ## watch mode for development
	uv run tailwindcss -i assets/tailwind.input.css -o static/css/tailwind.min.css --watch

css-build: ## minified, for commit/deploy
	uv run tailwindcss -i assets/tailwind.input.css -o static/css/tailwind.min.css --minify

dev:
	uv run manage.py runserver

lint:
	uv run ruff check . && uv run ruff format --check .

# --- Production Commands ---

prod-build: css-build ## Build assets for production
	DJANGO_SETTINGS_MODULE=config.settings.prod uv run manage.py collectstatic --noinput

prod-migrate: ## Run production database migrations
	DJANGO_SETTINGS_MODULE=config.settings.prod uv run manage.py migrate --noinput

deploy: prod-build prod-migrate ## Full production build and deployment routine
