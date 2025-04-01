import os



main_hook_imports = """
import {
    BrokerValueData,
    DataBrokerData,
    DataInputComponentData,
    DataOutputComponentData,
    RecipeData,
    CompiledRecipeData,
    AppletData,
    AiAgentData,
    AiSettingsData,
    AiModelEndpointData,
    AiEndpointData,
    AiModelData,
    ActionData,
    AiProviderData,
    ArgData,
    AudioLabelData,
    AudioRecordingData,
    AudioRecordingUsersData,
    AutomationBoundaryBrokerData,
    AutomationMatrixData,
    BrokerData,
    BucketStructuresData,
    BucketTreeStructuresData,
    CategoryData,
    DisplayOptionData,
    EmailsData,
    ExtractorData,
    FileStructureData,
    FlashcardDataData,
    FlashcardHistoryData,
    FlashcardImagesData,
    FlashcardSetRelationsData,
    FlashcardSetsData,
    MessageBrokerData,
    MessageTemplateData,
    ProcessorData,
    ProjectMembersData,
    ProjectsData,
    RecipeBrokerData,
    RecipeDisplayData,
    RecipeFunctionData,
    RecipeMessageData,
    RecipeModelData,
    RecipeProcessorData,
    RecipeToolData,
    RegisteredFunctionData,
    SubcategoryData,
    SystemFunctionData,
    TaskAssignmentsData,
    TaskAttachmentsData,
    TaskCommentsData,
    TasksData,
    ToolData,
    TransformerData,
    UserPreferencesData,
    WcClaimData,
    WcImpairmentDefinitionData,
    RecipeMessageReorderQueueData,
    MessageData,
    ConversationData,
    WcInjuryData,
    WcReportData,
} from "@/types";
import { MatrxRecordId, QuickReferenceRecord } from "../types/stateTypes";
import { EntitySelectors } from "../selectors";
import { EntityActions } from "../slice";
import { FetchMode } from "../actions";
import { useEntityWithFetch } from "./useAllData";
"""


def to_camel_case(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.capitalize() for x in components[1:])


def to_pascal_case(snake_str):
    components = snake_str.split("_")
    return "".join(x.capitalize() for x in components)


def generate_entity_main_hook(entity_name_snake):
    camel_case = to_camel_case(entity_name_snake)
    pascal_case = to_pascal_case(entity_name_snake)

    type_template = f"""type Use{pascal_case}WithFetchReturn = {{
    {camel_case}Selectors: EntitySelectors<"{camel_case}">;
    {camel_case}Actions: EntityActions<"{camel_case}">;
    {camel_case}Records: Record<MatrxRecordId, {pascal_case}Data>;
    {camel_case}UnsavedRecords: Record<MatrxRecordId, Partial<{pascal_case}Data>>;
    {camel_case}SelectedRecordIds: MatrxRecordId[];
    {camel_case}IsLoading: boolean;
    {camel_case}IsError: boolean;
    {camel_case}QuickRefRecords: QuickReferenceRecord[];
    add{pascal_case}MatrxId: (recordId: MatrxRecordId) => void;
    add{pascal_case}MatrxIds: (recordIds: MatrxRecordId[]) => void;
    remove{pascal_case}MatrxId: (recordId: MatrxRecordId) => void;
    remove{pascal_case}MatrxIds: (recordIds: MatrxRecordId[]) => void;
    add{pascal_case}PkValue: (pkValue: string) => void;
    add{pascal_case}PkValues: (pkValues: Record<string, unknown>) => void;
    remove{pascal_case}PkValue: (pkValue: string) => void;
    remove{pascal_case}PkValues: (pkValues: Record<string, unknown>) => void;
    is{pascal_case}MissingRecords: boolean;
    set{pascal_case}ShouldFetch: (shouldFetch: boolean) => void;
    set{pascal_case}FetchMode: (fetchMode: FetchMode) => void;
    fetch{pascal_case}QuickRefs: () => void;
    fetch{pascal_case}One: (recordId: MatrxRecordId) => void;
    fetch{pascal_case}OneWithFkIfk: (recordId: MatrxRecordId) => void;
    fetch{pascal_case}All: () => void;
    fetch{pascal_case}Paginated: (page: number, pageSize: number) => void;
}};

export const use{pascal_case}WithFetch = (): Use{pascal_case}WithFetchReturn => {{
    const {{
        selectors: {camel_case}Selectors,
        actions: {camel_case}Actions,
        allRecords: {camel_case}Records,
        unsavedRecords: {camel_case}UnsavedRecords,
        selectedRecordIds: {camel_case}SelectedRecordIds,
        isLoading: {camel_case}IsLoading,
        isError: {camel_case}IsError,
        quickRefRecords: {camel_case}QuickRefRecords,
        addMatrxId: add{pascal_case}MatrxId,
        addMatrxIds: add{pascal_case}MatrxIds,
        removeMatrxId: remove{pascal_case}MatrxId,
        removeMatrxIds: remove{pascal_case}MatrxIds,
        addPkValue: add{pascal_case}PkValue,
        addPkValues: add{pascal_case}PkValues,
        removePkValue: remove{pascal_case}PkValue,
        removePkValues: remove{pascal_case}PkValues,
        isMissingRecords: is{pascal_case}MissingRecords,
        setShouldFetch: set{pascal_case}ShouldFetch,
        setFetchMode: set{pascal_case}FetchMode,
        fetchQuickRefs: fetch{pascal_case}QuickRefs,
        fetchOne: fetch{pascal_case}One,
        fetchOneWithFkIfk: fetch{pascal_case}OneWithFkIfk,
        fetchAll: fetch{pascal_case}All,
        fetchPaginated: fetch{pascal_case}Paginated,

    }} = useEntityWithFetch("{camel_case}");

    return {{
        {camel_case}Selectors,
        {camel_case}Actions,
        {camel_case}Records,
        {camel_case}UnsavedRecords,
        {camel_case}SelectedRecordIds,
        {camel_case}IsLoading,
        {camel_case}IsError,
        {camel_case}QuickRefRecords,
        add{pascal_case}MatrxId,
        add{pascal_case}MatrxIds,
        remove{pascal_case}MatrxId,
        remove{pascal_case}MatrxIds,
        add{pascal_case}PkValue,
        add{pascal_case}PkValues,
        remove{pascal_case}PkValue,
        remove{pascal_case}PkValues,
        is{pascal_case}MissingRecords,
        set{pascal_case}ShouldFetch,
        set{pascal_case}FetchMode,
        fetch{pascal_case}QuickRefs,
        fetch{pascal_case}One,
        fetch{pascal_case}OneWithFkIfk,
        fetch{pascal_case}All,
        fetch{pascal_case}Paginated,
    }};
}};
"""
    return type_template


def generate_all_entity_main_hooks(entity_names):
    entries = [generate_entity_main_hook(name) for name in entity_names]
    return "\n\n\n".join(entries)


if __name__ == "__main__":
    os.system("cls")

    entity_names = ["ai_model", "ai_endpoint", "ai_model_endpoint", "ai_settings", "ai_agent", "conversation", "message"]

    result = generate_all_entity_main_hooks(entity_names)
    print(result)

# # Optionally, write to a file
# with open('generated_types.ts', 'w') as f:
#     f.write(result)
