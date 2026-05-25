"""
Marketing OS — Development Entrypoint

Quick Start:
  1. cp .env.example .env        (fill in GROQ_API_KEY and APIFY_API_KEY)
  2. make dev                     (start all Docker services)
  3. make migrate                 (run DB migrations)
  4. make seed                    (seed dev data)
  5. make qdrant-init             (create vector collections)

Service URLs (after `make dev`):
  Frontend:              http://localhost:3000
  Intake API:            http://localhost:8001/docs
  Scraper API:           http://localhost:8002/docs
  Intelligence API:      http://localhost:8003/docs
  Positioning API:       http://localhost:8004/docs
  ICP API:               http://localhost:8005/docs
  Embedding API:         http://localhost:8006/docs
  Campaign Context API:  http://localhost:8007/docs
  Orchestrator API:      http://localhost:8008/docs
  Notification API:      http://localhost:8009/docs
  Temporal UI:           http://localhost:8080
"""

if __name__ == "__main__":
    print(__doc__)
