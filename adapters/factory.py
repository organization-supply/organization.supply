
REGISTERED_ADAPTERS = {}

def register(adapter):
    # Instantiate the adapter to get the service ID.
    REGISTERED_ADAPTERS[getattr(adapter, 'service_id')] = adapter
    return adapter

class AdapterFactory():
    def available_adapters(self):
        print(REGISTERED_ADAPTERS)
        return list(map(
            lambda adapter: (adapter.service_id, adapter.service_name), 
            REGISTERED_ADAPTERS.values()
        ))

    def create(self, service_id, organization):
        # Build a list of adapters
        adapter = REGISTERED_ADAPTERS.get(service_id, None)
        if adapter:
            return adapter(organization)
