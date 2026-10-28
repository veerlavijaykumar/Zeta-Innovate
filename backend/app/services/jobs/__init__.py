"""Job services package initialization - registers connectors."""
from app.services.jobs.base import ConnectorRegistry
from app.services.jobs.remotive_connector import RemotiveConnector
from app.services.jobs.adzuna_connector import AdzunaConnector

# Register Remotive (100% Free Public API)
remotive = RemotiveConnector()
ConnectorRegistry.register(remotive)

# Register Adzuna (Optional / Paid tier)
adzuna = AdzunaConnector()
ConnectorRegistry.register(adzuna)

__all__ = ["ConnectorRegistry", "RemotiveConnector", "AdzunaConnector"]
