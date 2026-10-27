# Restaurant Analytics LLM

A development prototype for exploring synthetic restaurant data with a Streamlit dashboard and FastAPI API. Google Gemini generates SQL from questions and commentary from query results. SQLAlchemy models and a local SQLite generator provide the demo data; these are not live restaurant results or measured business improvements.

## Safety and data flow

**Use a disposable synthetic database, not customer or business records.** Questions, result samples, and summary statistics are sent to Gemini. The application is not an offline or private-only analytics system.

The current query path generates SQL and executes it through a normal writable SQLite connection. `validate_query_safety` is a substring-check helper, but `process_natural_language_query` does **not** call it. There is no enforced read-only database boundary. Model instructions and the helper's unit tests do not make generated queries safe; do not expose this prototype as a trusted query service.

## Development setup

```bash
git clone https://github.com/Zinga18018/restaurant-analytics-llm.git
cd restaurant-analytics-llm
python -m venv .venv-local
source .venv-local/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate with `.venv-local\Scripts\activate`. The pinned dependency set is historical, not a verified current compatibility matrix.

Set `GOOGLE_AI_API_KEY` in your local environment or an untracked `.env` file; this is the variable read by [config.py](config.py). Do not commit a key. The launcher [run.py](run.py) instead checks for `GOOGLE_API_KEY`, so its environment check disagrees with the service configuration. The direct entry points below avoid that launcher, not the query-safety limitations.

From the repository root, initialize a fresh, disposable demo database once:

```bash
python -m database.data_generator
```

The generator writes `restaurant_analytics.db` using unseeded random/Faker values and current dates. It creates restaurants, customers, menu items, orders, and reviews; repeated runs are not a deterministic reset.

Then choose an interface:

```bash
python -m streamlit run app.py --server.address 127.0.0.1
# Or, in a separate terminal:
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Cloud queries require an authorized account and may incur provider charges. The service hard-codes `gemini-1.5-pro` and `restaurant_analytics.db`; changing `MODEL_NAME` or `DATABASE_URL` in configuration does not consistently change those paths. Model availability and end-to-end compatibility must be checked before relying on this setup.

## Implementation

- [app.py](app.py): Streamlit metrics and question interface.
- [api/main.py](api/main.py): FastAPI endpoints; interactive documentation at `/docs`.
- [database/models.py](database/models.py) and [database/data_generator.py](database/data_generator.py): schema and synthetic data.
- [services/llm_service.py](services/llm_service.py): SQL generation, execution, and result commentary.
- [tests/test_llm_service.py](tests/test_llm_service.py): mocked service/helper tests, not an end-to-end cloud or SQL-security guarantee.

No frozen aggregate readout or reproducible performance benchmark is committed. The earlier README labels the project MIT, but no license file accompanies that statement; license terms need clarification before reuse.
