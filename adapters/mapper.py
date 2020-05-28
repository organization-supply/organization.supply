

class Mapper():
    def __init__(self, entities_local, entities_external, field_id_local, field_id_external, field_mapping_id, import_function=None):
        self.entities_local = entities_local
        self.entities_external = entities_external
        self.field_id_local = field_id_local
        self.field_id_external = field_id_external
        self.field_mapping_id = field_mapping_id
        self.import_function = import_function

    def assign(self, local_id, external_id):
        # Get the local entity from the list of django objects
        entity_local = self.entities_local.filter(**{self.field_id_local: local_id}).first()

        # Set the attribute to the external id
        setattr(entity_local, self.field_mapping_id, external_id)

        # And finally save the object
        entity_local.save()