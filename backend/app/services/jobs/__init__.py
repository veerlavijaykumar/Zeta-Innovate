"""Job services package initialization - registers connectors."""
from app.services.jobs.base import ConnectorRegistry
from app.services.jobs.adzuna_connector import AdzunaConnector

# Initialize and register known connectors
adzuna = AdzunaConnector()
ConnectorRegistry.register(adzuna)

__all__ = ["ConnectorRegistry", "AdzunaConnector"]
