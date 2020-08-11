import uuid

from homeassistant import config_entries


class MockConfigEntry(config_entries.ConfigEntry):
    """Helper for creating config entries that adds some defaults."""

    def __init__(
        self,
        *,
        domain="test",
        data=None,
        version=1,
        entry_id=None,
        source=config_entries.SOURCE_USER,
        title="Mock Title",
        state=None,
        options={},
        system_options={},
        connection_class=config_entries.CONN_CLASS_UNKNOWN,
        unique_id=None,
    ):
        """Initialize a mock config entry."""
        kwargs = {
            "entry_id": entry_id or uuid.uuid4().hex,
            "domain": domain,
            "data": data or {},
            "system_options": system_options,
            "options": options,
            "version": version,
            "title": title,
            "connection_class": connection_class,
            "unique_id": unique_id,
        }
        if source is not None:
            kwargs["source"] = source
        if state is not None:
            kwargs["state"] = state
        super().__init__(**kwargs)

    def add_to_hass(self, hass):
        """Test helper to add entry to hass."""
        hass.config_entries._entries.append(self)

    def add_to_manager(self, manager):
        """Test helper to add entry to entry manager."""
        manager._entries.append(self)
