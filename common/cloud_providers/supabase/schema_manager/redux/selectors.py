# common/supabase/schema_manager/redux/selectors.py
from common.supabase.schema_manager.technology_base import Technology



class Selector(Technology):
    def initialize_technology(self):
        self.selector_names = self.generate_selector_names()
        self.selectors = self.generate_selectors()
        self.file_content = self.generate_selector_file()

    def generate_selector_names(self):
        names = {
            'byId': f"select{self.table.PascalCaseName}ById",
            'all': f"selectAll{self.table.PascalCaseName}s",
            'ids': f"select{self.table.PascalCaseName}Ids",
            'total': f"select{self.table.PascalCaseName}Total"
        }
        for relation in self.table.relations:
            if relation['type'] == 'outbound':
                names[relation['local_referencing_column_camel_case']] = f"select{relation['referenced_table_pascal_case']}By{self.table.PascalCaseName}Id"
            else:
                names[relation['referencing_table_camel_case']] = f"select{relation['referencing_table_pascal_case']}sFor{self.table.PascalCaseName}"
        return names

    def get_common_imports(self):
        return f"""{self.create_selector}
{self.redux_root_store}
{self.type_import_statement}
"""

    def generate_selector_by_id(self):
        return f"""export const {self.selector_names['byId']} = (state: RootState, id: string): {self.table.PascalCaseName} | undefined =>
        state.{self.table.camelCaseName}.find({self.table.camelCaseName} => {self.table.camelCaseName}.id === id);"""

    def generate_selector_all(self):
        return f"""export const {self.selector_names['all']} = (state: RootState): {self.table.PascalCaseName}[] =>
        state.{self.table.camelCaseName};"""

    def generate_selector_ids(self):
        return f"""export const {self.selector_names['ids']} = createSelector(
    {self.selector_names['all']},
    ({self.table.camelCaseName}s) => {self.table.camelCaseName}s.map({self.table.camelCaseName} => {self.table.camelCaseName}.id)
);"""

    def generate_selector_total(self):
        return f"""export const {self.selector_names['total']} = createSelector(
    {self.selector_names['all']},
    ({self.table.camelCaseName}s) => {self.table.camelCaseName}s.length
);"""

    def generate_selector_related(self, relation):
        if relation['type'] == 'outbound':
            return f"""export const {self.selector_names[relation['local_referencing_column_camel_case']]} = createSelector(
    [
        state => state.{self.table.camelCaseName},
        state => state.{relation['referenced_table_camel_case']},
        (state, {self.table.camelCaseName}Id: string) => {self.table.camelCaseName}Id
    ],
    ({self.table.camelCaseName}s, {relation['referenced_table_camel_case']}s, {self.table.camelCaseName}Id) => {{
        const {self.table.camelCaseName} = {self.table.camelCaseName}s.find({self.table.camelCaseName} => {self.table.camelCaseName}.id === {self.table.camelCaseName}Id);
        return {self.table.camelCaseName} ? {relation['referenced_table_camel_case']}s.find(item => item.id === {self.table.camelCaseName}.{relation['local_referencing_column_camel_case']}) : null;
    }}
);"""
        else:
            # The inbound relationship selector remains the same
            return f"""export const {self.selector_names[relation['referencing_table_camel_case']]} = createSelector(
    [state => state.{self.table.camelCaseName}, state => state.{relation['referencing_table_camel_case']}, (state, {self.table.camelCaseName}Id: string) => {self.table.camelCaseName}Id],
    ({self.table.camelCaseName}s, {relation['referencing_table_camel_case']}s, {self.table.camelCaseName}Id) => {{
        const {self.table.camelCaseName} = {self.table.camelCaseName}s.find({self.table.camelCaseName} => {self.table.camelCaseName}.id === {self.table.camelCaseName}Id);
        return {self.table.camelCaseName} ? {relation['referencing_table_camel_case']}s.filter({relation['referencing_table_camel_case']} => {relation['referencing_table_camel_case']}.{self.table.camelCaseName}Id === {self.table.camelCaseName}Id) : [];
    }}
);"""
    def generate_selectors(self):
        selectors = [
            self.generate_selector_by_id(),
            self.generate_selector_all(),
            self.generate_selector_ids(),
            self.generate_selector_total()
        ]

        for relation in self.table.relations:
            selectors.append(self.generate_selector_related(relation))

        return "\n\n".join(selectors)

    def generate_selector_file(self):
        return f"""{self.file_location_print}
{self.get_common_imports()}

{self.selectors}

const {self.name} = {{
    {', '.join(self.selector_names.values())}
}};

export default {self.name};
"""
