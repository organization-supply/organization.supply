
REGISTERED_ADAPTERS = {}

def register(adapter):
    # Instantiate the adapter to get the service ID.
    REGISTERED_ADAPTERS[getattr(adapter, 'service_id')] = adapter
    return adapter

class AdapterFactory():
    def list_as_choices(self):
        adapters = list(map(lambda adapter: (adapter.service_id, adapter.service_name), REGISTERED_ADAPTERS.values()))
        return adapters.append(('', 'None'))

    def list_available_adapters(self):
        return REGISTERED_ADAPTERS.values()

    def create_for_service(self, external_service_id):
        # Build a list of adapters
        adapter = REGISTERED_ADAPTERS.get(external_service_id, None)
        if adapter:
            return adapter()
