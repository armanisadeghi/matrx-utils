class CodeGenerationManager:
    def __init__(self, schema_manager, config_manager):
        self.schema_manager = schema_manager
        self.config_manager = config_manager
        self.technology_manager = TechnologyManager(config_manager)

    def generate_code(self, technologies):
        for table in self.schema_manager.tables:
            for tech in technologies:
                generator = self.technology_manager.get_generator(tech)
                generator.generate(table)

