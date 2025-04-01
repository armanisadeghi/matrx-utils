# File: database/orm/models.py
from database.orm.core.fields import (
    CharField,
    EnumField,
    DateField,
    TextField,
    IntegerField,
    FloatField,
    BooleanField,
    DateTimeField,
    UUIDField,
    JSONField,
    DecimalField,
    BigIntegerField,
    SmallIntegerField,
    JSONBField,
    UUIDArrayField,
    JSONBArrayField,
    ForeignKey,
)
from database.orm.core.base import Model
from database.orm.core.registry import model_registry
# from recipes.compiled.new_utils import update_content_with_runtime_brokers  #Jatin commented this.
from enum import Enum
from common import vcprint
from dataclasses import dataclass
from database.orm.core.extended import BaseDTO, BaseManager

verbose = False
debug = False
info = True


class Users(Model):
    id = UUIDField(primary_key=True, null=False)
    email = CharField(null=False)


class RecipeStatus(Enum):
    ACTIVE_TESTING = "active_testing"
    ARCHIVED = "archived"
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    LIVE = "live"
    OTHER = "other"


class Recipe(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    description = TextField()
    tags = JSONBField()
    sample_output = TextField()
    is_public = BooleanField()
    status = EnumField(enum_class=RecipeStatus, null=False, default="draft")
    version = SmallIntegerField(default="1")
    post_result_options = JSONBField()
    _inverse_foreign_keys = {
        "compiled_recipes": {
            "from_model": "CompiledRecipe",
            "from_field": "recipe_id",
            "referenced_field": "id",
            "related_name": "compiled_recipes",
        },
        "ai_agents": {"from_model": "AiAgent", "from_field": "recipe_id", "referenced_field": "id", "related_name": "ai_agents"},
        "recipe_displays": {
            "from_model": "RecipeDisplay",
            "from_field": "recipe",
            "referenced_field": "id",
            "related_name": "recipe_displays",
        },
        "recipe_processors": {
            "from_model": "RecipeProcessor",
            "from_field": "recipe",
            "referenced_field": "id",
            "related_name": "recipe_processors",
        },
        "recipe_models": {"from_model": "RecipeModel", "from_field": "recipe", "referenced_field": "id", "related_name": "recipe_models"},
        "recipe_brokers": {
            "from_model": "RecipeBroker",
            "from_field": "recipe",
            "referenced_field": "id",
            "related_name": "recipe_brokers",
        },
        "recipe_messages": {
            "from_model": "RecipeMessage",
            "from_field": "recipe_id",
            "referenced_field": "id",
            "related_name": "recipe_messages",
        },
        "recipe_tools": {"from_model": "RecipeTool", "from_field": "recipe", "referenced_field": "id", "related_name": "recipe_tools"},
        "recipe_functions": {
            "from_model": "RecipeFunction",
            "from_field": "recipe",
            "referenced_field": "id",
            "related_name": "recipe_functions",
        },
    }


class AiProvider(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField()
    company_description = TextField()
    documentation_link = CharField()
    models_link = CharField()
    _inverse_foreign_keys = {
        "ai_settingss": {"from_model": "AiSettings", "from_field": "ai_provider", "referenced_field": "id", "related_name": "ai_settingss"},
        "ai_models": {"from_model": "AiModel", "from_field": "model_provider", "referenced_field": "id", "related_name": "ai_models"},
    }


class DefaultComponent(Enum):
    ACCORDION_SELECTED = "Accordion_Selected"
    ACCORDION_VIEW = "Accordion_View"
    ACCORDION_VIEW_ADD_EDIT = "Accordion_View_Add_Edit"
    BROKERCHECKBOX = "BrokerCheckbox"
    BROKERCOLORPICKER = "BrokerColorPicker"
    BROKERCUSTOMINPUT = "BrokerCustomInput"
    BROKERCUSTOMSELECT = "BrokerCustomSelect"
    BROKERINPUT = "BrokerInput"
    BROKERNUMBERINPUT = "BrokerNumberInput"
    BROKERNUMBERPICKER = "BrokerNumberPicker"
    BROKERRADIO = "BrokerRadio"
    BROKERRADIOGROUP = "BrokerRadioGroup"
    BROKERSELECT = "BrokerSelect"
    BROKERSLIDER = "BrokerSlider"
    BROKERSWITCH = "BrokerSwitch"
    BROKERTAILWINDCOLORPICKER = "BrokerTailwindColorPicker"
    BROKERTEXTARRAYINPUT = "BrokerTextArrayInput"
    BROKERTEXTAREA = "BrokerTextarea"
    BROKERTEXTAREAGROW = "BrokerTextareaGrow"
    BUTTON = "Button"
    CHECKBOX = "Checkbox"
    CHIP = "Chip"
    COLOR_PICKER = "Color_Picker"
    DATE_PICKER = "Date_Picker"
    DRAWER = "Drawer"
    FILE_UPLOAD = "File_Upload"
    IMAGE_DISPLAY = "Image_Display"
    INPUT = "Input"
    JSON_EDITOR = "Json_Editor"
    MENU = "Menu"
    NUMBER_INPUT = "Number_Input"
    PHONE_INPUT = "Phone_Input"
    RADIO_GROUP = "Radio_Group"
    RELATIONAL_BUTTON = "Relational_Button"
    RELATIONAL_INPUT = "Relational_Input"
    SEARCH_INPUT = "Search_Input"
    SELECT = "Select"
    SHEET = "Sheet"
    SLIDER = "Slider"
    STAR_RATING = "Star_Rating"
    SWITCH = "Switch"
    TEXTAREA = "Textarea"
    TIME_PICKER = "Time_Picker"
    UUID_ARRAY = "UUID_Array"
    UUID_FIELD = "UUID_Field"


class Size(Enum):
    _2XL = "2xl"
    _2XS = "2xs"
    _3XL = "3xl"
    _3XS = "3xs"
    _4XL = "4xl"
    _5XL = "5xl"
    DEFAULT = "default"
    L = "l"
    M = "m"
    S = "s"
    XL = "xl"
    XS = "xs"


class Orientation(Enum):
    DEFAULT = "default"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class DataInputComponent(Model):
    id = UUIDField(primary_key=True, null=False)
    options = JSONBField()
    include_other = BooleanField()
    min = FloatField()
    max = FloatField()
    step = IntegerField()
    acceptable_filetypes = JSONBField()
    src = TextField()
    color_overrides = JSONBField()
    additional_params = JSONBField()
    sub_component = CharField()
    component = EnumField(enum_class=DefaultComponent, null=False, default="BrokerTextarea")
    name = CharField()
    description = TextField()
    placeholder = TextField()
    container_class_name = CharField()
    collapsible_class_name = CharField()
    label_class_name = CharField()
    description_class_name = CharField()
    component_class_name = CharField()
    size = EnumField(
        enum_class=Size,
    )
    height = EnumField(
        enum_class=Size,
    )
    width = EnumField(
        enum_class=Size,
    )
    min_height = EnumField(
        enum_class=Size,
    )
    max_height = EnumField(
        enum_class=Size,
    )
    min_width = EnumField(
        enum_class=Size,
    )
    max_width = EnumField(
        enum_class=Size,
    )
    orientation = EnumField(enum_class=Orientation, default="vertical")
    _inverse_foreign_keys = {
        "message_brokers": {
            "from_model": "MessageBroker",
            "from_field": "default_component",
            "referenced_field": "id",
            "related_name": "message_brokers",
        },
        "brokers": {"from_model": "Broker", "from_field": "custom_source_component", "referenced_field": "id", "related_name": "brokers"},
        "data_brokers": {
            "from_model": "DataBroker",
            "from_field": "input_component",
            "referenced_field": "id",
            "related_name": "data_brokers",
        },
    }


class AiModel(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    common_name = CharField()
    model_class = CharField(null=False)
    provider = CharField()
    endpoints = JSONBField()
    context_window = BigIntegerField()
    max_tokens = BigIntegerField()
    capabilities = JSONBField()
    controls = JSONBField()
    model_provider = ForeignKey(
        to_model=AiProvider,
        to_column="id",
    )
    _inverse_foreign_keys = {
        "ai_model_endpoints": {
            "from_model": "AiModelEndpoint",
            "from_field": "ai_model_id",
            "referenced_field": "id",
            "related_name": "ai_model_endpoints",
        },
        "ai_settingss": {"from_model": "AiSettings", "from_field": "ai_model", "referenced_field": "id", "related_name": "ai_settingss"},
        "recipe_models": {"from_model": "RecipeModel", "from_field": "ai_model", "referenced_field": "id", "related_name": "recipe_models"},
    }


class DataType(Enum):
    BOOL = "bool"
    DICT = "dict"
    FLOAT = "float"
    INT = "int"
    LIST = "list"
    STR = "str"
    URL = "url"


class DataSource(Enum):
    API = "api"
    CHANCE = "chance"
    DATABASE = "database"
    ENVIRONMENT = "environment"
    FILE = "file"
    FUNCTION = "function"
    GENERATED_DATA = "generated_data"
    NONE = "none"
    USER_INPUT = "user_input"


class DataDestination(Enum):
    API_RESPONSE = "api_response"
    DATABASE = "database"
    FILE = "file"
    FUNCTION = "function"
    USER_OUTPUT = "user_output"


class DestinationComponent(Enum):
    _3DMODELVIEWER = "3DModelViewer"
    AUDIOOUTPUT = "AudioOutput"
    BUCKETLIST = "BucketList"
    BUDGETVISUALIZER = "BudgetVisualizer"
    CALENDAR = "Calendar"
    CAROUSEL = "Carousel"
    CHECKLIST = "Checklist"
    CLOCK = "Clock"
    CODEVIEW = "CodeView"
    COMPLEXMULTI = "ComplexMulti"
    DATAFLOWDIAGRAM = "DataFlowDiagram"
    DECISIONTREE = "DecisionTree"
    DIFFVIEWER = "DiffViewer"
    FILEOUTPUT = "FileOutput"
    FITNESSTRACKER = "FitnessTracker"
    FLOWCHART = "Flowchart"
    FORM = "Form"
    GANTTCHART = "GanttChart"
    GEOGRAPHICMAP = "GeographicMap"
    GLOSSARYVIEW = "GlossaryView"
    HEATMAP = "Heatmap"
    HORIZONTALLIST = "HorizontalList"
    IMAGEVIEW = "ImageView"
    INTERACTIVECHART = "InteractiveChart"
    JSONVIEWER = "JsonViewer"
    KANBANBOARD = "KanbanBoard"
    LATEXRENDERER = "LaTeXRenderer"
    LIVETRAFFIC = "LiveTraffic"
    LOCALEVENTS = "LocalEvents"
    MARKDOWNVIEWER = "MarkdownViewer"
    MEALPLANNER = "MealPlanner"
    MINDMAP = "MindMap"
    NEEDNEWOPTION = "NeedNewOption"
    NETWORKGRAPH = "NetworkGraph"
    NEWSAGGREGATOR = "NewsAggregator"
    PDFVIEWER = "PDFViewer"
    PIVOTTABLE = "PivotTable"
    PLAINTEXT = "PlainText"
    PRESENTATION = "Presentation"
    PUBLICLIVECAM = "PublicLiveCam"
    RICHTEXTEDITOR = "RichTextEditor"
    RUNCODEBACK = "RunCodeBack"
    RUNCODEFRONT = "RunCodeFront"
    SVGEDITOR = "SVGEditor"
    SANKEYDIAGRAM = "SankeyDiagram"
    SATELLITEVIEW = "SatelliteView"
    SOCIALMEDIAINFO = "SocialMediaInfo"
    SPECTRUMANALYZER = "SpectrumAnalyzer"
    SPREADSHEET = "Spreadsheet"
    TABLE = "Table"
    TASKPRIORITIZATION = "TaskPrioritization"
    TEXTAREA = "Textarea"
    THERMOMETER = "Thermometer"
    TIMELINE = "Timeline"
    TRAVELPLANNER = "TravelPlanner"
    TREEVIEW = "TreeView"
    UMLDIAGRAM = "UMLDiagram"
    VERTICALLIST = "VerticalList"
    VOICESENTIMENTANALYSIS = "VoiceSentimentAnalysis"
    WEATHERDASHBOARD = "WeatherDashboard"
    WEATHERMAP = "WeatherMap"
    WORDHIGHLIGHTER = "WordHighlighter"
    WORDMAP = "WordMap"
    CHATRESPONSE = "chatResponse"
    NONE = "none"
    VIDEO = "video"


class Broker(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    value = JSONBField(default={"broker_value": None})
    data_type = EnumField(enum_class=DataType, null=False, default="str")
    ready = BooleanField(default="false")
    default_source = EnumField(enum_class=DataSource, default="none")
    display_name = CharField()
    description = TextField()
    tooltip = TextField()
    validation_rules = JSONBField()
    sample_entries = TextField()
    custom_source_component = ForeignKey(
        to_model=DataInputComponent,
        to_column="id",
    )
    additional_params = JSONBField()
    other_source_params = JSONBField()
    default_destination = EnumField(
        enum_class=DataDestination,
    )
    output_component = EnumField(
        enum_class=DestinationComponent,
    )
    tags = JSONBField(default=[])
    string_value = TextField()
    _inverse_foreign_keys = {
        "recipe_brokers": {
            "from_model": "RecipeBroker",
            "from_field": "broker",
            "referenced_field": "id",
            "related_name": "recipe_brokers",
        },
        "registered_functions": {
            "from_model": "RegisteredFunction",
            "from_field": "return_broker",
            "referenced_field": "id",
            "related_name": "registered_functions",
        },
        "automation_boundary_brokers": {
            "from_model": "AutomationBoundaryBroker",
            "from_field": "broker",
            "referenced_field": "id",
            "related_name": "automation_boundary_brokers",
        },
    }


class DestinationComponent(Enum):
    _3DMODELVIEWER = "3DModelViewer"
    AUDIOOUTPUT = "AudioOutput"
    BUCKETLIST = "BucketList"
    BUDGETVISUALIZER = "BudgetVisualizer"
    CALENDAR = "Calendar"
    CAROUSEL = "Carousel"
    CHECKLIST = "Checklist"
    CLOCK = "Clock"
    CODEVIEW = "CodeView"
    COMPLEXMULTI = "ComplexMulti"
    DATAFLOWDIAGRAM = "DataFlowDiagram"
    DECISIONTREE = "DecisionTree"
    DIFFVIEWER = "DiffViewer"
    FILEOUTPUT = "FileOutput"
    FITNESSTRACKER = "FitnessTracker"
    FLOWCHART = "Flowchart"
    FORM = "Form"
    GANTTCHART = "GanttChart"
    GEOGRAPHICMAP = "GeographicMap"
    GLOSSARYVIEW = "GlossaryView"
    HEATMAP = "Heatmap"
    HORIZONTALLIST = "HorizontalList"
    IMAGEVIEW = "ImageView"
    INTERACTIVECHART = "InteractiveChart"
    JSONVIEWER = "JsonViewer"
    KANBANBOARD = "KanbanBoard"
    LATEXRENDERER = "LaTeXRenderer"
    LIVETRAFFIC = "LiveTraffic"
    LOCALEVENTS = "LocalEvents"
    MARKDOWNVIEWER = "MarkdownViewer"
    MEALPLANNER = "MealPlanner"
    MINDMAP = "MindMap"
    NEEDNEWOPTION = "NeedNewOption"
    NETWORKGRAPH = "NetworkGraph"
    NEWSAGGREGATOR = "NewsAggregator"
    PDFVIEWER = "PDFViewer"
    PIVOTTABLE = "PivotTable"
    PLAINTEXT = "PlainText"
    PRESENTATION = "Presentation"
    PUBLICLIVECAM = "PublicLiveCam"
    RICHTEXTEDITOR = "RichTextEditor"
    RUNCODEBACK = "RunCodeBack"
    RUNCODEFRONT = "RunCodeFront"
    SVGEDITOR = "SVGEditor"
    SANKEYDIAGRAM = "SankeyDiagram"
    SATELLITEVIEW = "SatelliteView"
    SOCIALMEDIAINFO = "SocialMediaInfo"
    SPECTRUMANALYZER = "SpectrumAnalyzer"
    SPREADSHEET = "Spreadsheet"
    TABLE = "Table"
    TASKPRIORITIZATION = "TaskPrioritization"
    TEXTAREA = "Textarea"
    THERMOMETER = "Thermometer"
    TIMELINE = "Timeline"
    TRAVELPLANNER = "TravelPlanner"
    TREEVIEW = "TreeView"
    UMLDIAGRAM = "UMLDiagram"
    VERTICALLIST = "VerticalList"
    VOICESENTIMENTANALYSIS = "VoiceSentimentAnalysis"
    WEATHERDASHBOARD = "WeatherDashboard"
    WEATHERMAP = "WeatherMap"
    WORDHIGHLIGHTER = "WordHighlighter"
    WORDMAP = "WordMap"
    CHATRESPONSE = "chatResponse"
    NONE = "none"
    VIDEO = "video"


class DataOutputComponent(Model):
    id = UUIDField(primary_key=True, null=False)
    component_type = EnumField(
        enum_class=DestinationComponent,
    )
    ui_component = CharField()
    props = JSONBField()
    additional_params = JSONBField()
    _inverse_foreign_keys = {
        "data_brokers": {
            "from_model": "DataBroker",
            "from_field": "output_component",
            "referenced_field": "id",
            "related_name": "data_brokers",
        }
    }


class FlashcardData(Model):
    id = UUIDField(primary_key=True, null=False)
    user_id = ForeignKey(to_model=Users, to_column="id", null=False)
    topic = TextField()
    lesson = TextField()
    difficulty = TextField()
    front = TextField(null=False)
    back = TextField(null=False)
    example = TextField()
    detailed_explanation = TextField()
    audio_explanation = TextField()
    personal_notes = TextField()
    is_deleted = BooleanField(default="false")
    public = BooleanField(default="false")
    shared_with = UUIDArrayField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    _inverse_foreign_keys = {
        "flashcard_historys": {
            "from_model": "FlashcardHistory",
            "from_field": "flashcard_id",
            "referenced_field": "id",
            "related_name": "flashcard_historys",
        },
        "flashcard_set_relationss": {
            "from_model": "FlashcardSetRelations",
            "from_field": "flashcard_id",
            "referenced_field": "id",
            "related_name": "flashcard_set_relationss",
        },
        "flashcard_imagess": {
            "from_model": "FlashcardImages",
            "from_field": "flashcard_id",
            "referenced_field": "id",
            "related_name": "flashcard_imagess",
        },
    }


class Projects(Model):
    id = UUIDField(primary_key=True, null=False)
    name = TextField(null=False)
    description = TextField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    created_by = ForeignKey(
        to_model=Users,
        to_column="id",
    )
    _inverse_foreign_keys = {
        "project_memberss": {
            "from_model": "ProjectMembers",
            "from_field": "project_id",
            "referenced_field": "id",
            "related_name": "project_memberss",
        },
        "taskss": {"from_model": "Tasks", "from_field": "project_id", "referenced_field": "id", "related_name": "taskss"},
    }


class Tasks(Model):
    id = UUIDField(primary_key=True, null=False)
    title = TextField(null=False)
    description = TextField()
    project_id = ForeignKey(
        to_model=Projects,
        to_column="id",
    )
    status = TextField(null=False, default="incomplete")
    due_date = DateField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    created_by = ForeignKey(
        to_model=Users,
        to_column="id",
    )
    _inverse_foreign_keys = {
        "task_assignmentss": {
            "from_model": "TaskAssignments",
            "from_field": "task_id",
            "referenced_field": "id",
            "related_name": "task_assignmentss",
        },
        "task_attachmentss": {
            "from_model": "TaskAttachments",
            "from_field": "task_id",
            "referenced_field": "id",
            "related_name": "task_attachmentss",
        },
        "task_commentss": {
            "from_model": "TaskComments",
            "from_field": "task_id",
            "referenced_field": "id",
            "related_name": "task_commentss",
        },
    }


class AiEndpoint(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    provider = CharField()
    description = TextField()
    additional_cost = BooleanField(default="true")
    cost_details = JSONBField()
    params = JSONField()
    _inverse_foreign_keys = {
        "ai_model_endpoints": {
            "from_model": "AiModelEndpoint",
            "from_field": "ai_endpoint_id",
            "referenced_field": "id",
            "related_name": "ai_model_endpoints",
        },
        "ai_settingss": {"from_model": "AiSettings", "from_field": "ai_endpoint", "referenced_field": "id", "related_name": "ai_settingss"},
    }


class CognitionMatrices(Enum):
    AGENT_CREW = "agent_crew"
    AGENT_MIXTURE = "agent_mixture"
    CONDUCTOR = "conductor"
    HYPERCLUSTER = "hypercluster"
    KNOWLEDGE_MATRIX = "knowledge_matrix"
    MONTE_CARLO = "monte_carlo"
    THE_MATRIX = "the_matrix"
    WORKFLOW = "workflow"


class AutomationMatrix(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    description = TextField()
    average_seconds = SmallIntegerField()
    is_automated = BooleanField()
    cognition_matrices = EnumField(
        enum_class=CognitionMatrices,
    )
    _inverse_foreign_keys = {
        "actions": {"from_model": "Action", "from_field": "matrix", "referenced_field": "id", "related_name": "actions"},
        "automation_boundary_brokers": {
            "from_model": "AutomationBoundaryBroker",
            "from_field": "matrix",
            "referenced_field": "id",
            "related_name": "automation_boundary_brokers",
        },
    }


class DataType(Enum):
    BOOL = "bool"
    DICT = "dict"
    FLOAT = "float"
    INT = "int"
    LIST = "list"
    STR = "str"
    URL = "url"


class Color(Enum):
    AMBER = "amber"
    BLUE = "blue"
    CYAN = "cyan"
    EMERALD = "emerald"
    FUCHSIA = "fuchsia"
    GRAY = "gray"
    GREEN = "green"
    INDIGO = "indigo"
    LIME = "lime"
    NEUTRAL = "neutral"
    ORANGE = "orange"
    PINK = "pink"
    PURPLE = "purple"
    RED = "red"
    ROSE = "rose"
    SKY = "sky"
    SLATE = "slate"
    STONE = "stone"
    TEAL = "teal"
    VIOLET = "violet"
    YELLOW = "yellow"
    ZINC = "zinc"


class DataBroker(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    data_type = EnumField(enum_class=DataType, default="str")
    default_value = TextField()
    input_component = ForeignKey(
        to_model=DataInputComponent,
        to_column="id",
    )
    color = EnumField(enum_class=Color, default="blue")
    output_component = ForeignKey(
        to_model=DataOutputComponent,
        to_column="id",
    )
    _inverse_foreign_keys = {
        "broker_values": {
            "from_model": "BrokerValue",
            "from_field": "data_broker",
            "referenced_field": "id",
            "related_name": "broker_values",
        },
        "message_brokers": {
            "from_model": "MessageBroker",
            "from_field": "broker_id",
            "referenced_field": "id",
            "related_name": "message_brokers",
        },
    }


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


# Enum for message types
class MessageType(str, Enum):
    TEXT = "text"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    JSON_OBJECT = "json_object"
    IMAGE_URL = "image_url"  # For messages with a public image URL
    BASE64 = "base64"  # For messages with base64-encoded content
    BLOB = "blob"  # For raw binary data (future-proofing)
    MIXED = "mixed"  # For messages combining text and other content (e.g., images/files)
    OTHER = "other"  # For future extensibility


class MessageTemplate(Model):
    id = UUIDField(primary_key=True, null=False)
    role = EnumField(enum_class=MessageRole, null=False, default="user")
    type = EnumField(enum_class=MessageType, null=False, default="text")
    created_at = DateTimeField(null=False)
    content = TextField()
    _inverse_foreign_keys = {
        "message_brokers": {
            "from_model": "MessageBroker",
            "from_field": "message_id",
            "referenced_field": "id",
            "related_name": "message_brokers",
        },
        "recipe_messages": {
            "from_model": "RecipeMessage",
            "from_field": "message_id",
            "referenced_field": "id",
            "related_name": "recipe_messages",
        },
    }


class RegisteredFunction(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    module_path = CharField(null=False)
    class_name = CharField()
    description = TextField()
    return_broker = ForeignKey(
        to_model=Broker,
        to_column="id",
    )
    _inverse_foreign_keys = {
        "system_functions": {
            "from_model": "SystemFunction",
            "from_field": "rf_id",
            "referenced_field": "id",
            "related_name": "system_functions",
        },
        "args": {"from_model": "Arg", "from_field": "registered_function", "referenced_field": "id", "related_name": "args"},
    }


class SystemFunction(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    description = TextField()
    sample = TextField()
    input_params = JSONBField()
    output_options = JSONBField()
    rf_id = ForeignKey(to_model=RegisteredFunction, to_column="id", null=False)
    _inverse_foreign_keys = {
        "tools": {"from_model": "Tool", "from_field": "system_function", "referenced_field": "id", "related_name": "tools"},
        "recipe_functions": {
            "from_model": "RecipeFunction",
            "from_field": "function",
            "referenced_field": "id",
            "related_name": "recipe_functions",
        },
    }


class AiSettings(Model):
    id = UUIDField(primary_key=True, null=False)
    ai_endpoint = ForeignKey(to_model=AiEndpoint, to_column="id", default="4bedf336-b274-4cdb-8202-59fd282ae6a0")
    ai_provider = ForeignKey(to_model=AiProvider, to_column="id", default="99fa34b1-4c36-427f-ab73-cc56f1d5c4a0")
    ai_model = ForeignKey(to_model=AiModel, to_column="id", default="dd45b76e-f470-4765-b6c4-1a275d7860bf")
    temperature = FloatField(default="0.25")
    max_tokens = SmallIntegerField(default="3000")
    top_p = SmallIntegerField(default="1")
    frequency_penalty = SmallIntegerField(default="0")
    presence_penalty = SmallIntegerField(default="0")
    stream = BooleanField(default="true")
    response_format = CharField(default="text")
    size = CharField()
    quality = CharField()
    count = SmallIntegerField(default="1")
    audio_voice = CharField()
    audio_format = CharField()
    modalities = JSONBField(default={})
    tools = JSONBField(default={})
    preset_name = CharField()
    _inverse_foreign_keys = {
        "ai_agents": {"from_model": "AiAgent", "from_field": "ai_settings_id", "referenced_field": "id", "related_name": "ai_agents"}
    }


class AudioLabel(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    name = CharField(null=False)
    description = TextField()
    _inverse_foreign_keys = {
        "audio_recordings": {
            "from_model": "AudioRecording",
            "from_field": "label",
            "referenced_field": "id",
            "related_name": "audio_recordings",
        }
    }


class Category(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False, unique=True)
    description = TextField()
    slug = CharField(null=False)
    icon = CharField(default="Briefcase")
    created_at = DateTimeField(null=False)
    _inverse_foreign_keys = {
        "subcategorys": {"from_model": "Subcategory", "from_field": "category_id", "referenced_field": "id", "related_name": "subcategorys"}
    }


class CompiledRecipe(Model):
    id = UUIDField(primary_key=True, null=False)
    recipe_id = ForeignKey(
        to_model=Recipe,
        to_column="id",
    )
    version = SmallIntegerField()
    compiled_recipe = JSONBField(null=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    user_id = ForeignKey(
        to_model=Users,
        to_column="id",
    )
    is_public = BooleanField(null=False, default="false")
    authenticated_read = BooleanField(null=False, default="false")
    _inverse_foreign_keys = {
        "applets": {"from_model": "Applet", "from_field": "compiled_recipe_id", "referenced_field": "id", "related_name": "applets"}
    }


class Conversation(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField()
    user_id = CharField()
    metadata = JSONBField()
    label = CharField()
    _inverse_foreign_keys = {
        "messages": {"from_model": "Message", "from_field": "conversation_id", "referenced_field": "id", "related_name": "messages"}
    }


class DisplayOption(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField()
    default_params = JSONBField()
    customizable_params = JSONBField()
    additional_params = JSONBField()
    _inverse_foreign_keys = {
        "recipe_displays": {
            "from_model": "RecipeDisplay",
            "from_field": "display",
            "referenced_field": "id",
            "related_name": "recipe_displays",
        }
    }


class FlashcardSets(Model):
    set_id = UUIDField(primary_key=True, null=False)
    user_id = ForeignKey(to_model=Users, to_column="id", null=False)
    name = TextField(null=False)
    created_at = DateTimeField()
    updated_at = DateTimeField()
    shared_with = UUIDArrayField()
    public = BooleanField(default="false")
    topic = TextField()
    lesson = TextField()
    difficulty = TextField()
    audio_overview = TextField()
    _inverse_foreign_keys = {
        "flashcard_set_relationss": {
            "from_model": "FlashcardSetRelations",
            "from_field": "set_id",
            "referenced_field": "set_id",
            "related_name": "flashcard_set_relationss",
        }
    }


class Processor(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    depends_default = ForeignKey(
        to_model="Processor",
        to_column="id",
    )
    default_extractors = JSONBField()
    params = JSONBField()
    _inverse_foreign_keys = {
        "recipe_processors": {
            "from_model": "RecipeProcessor",
            "from_field": "processor",
            "referenced_field": "id",
            "related_name": "recipe_processors",
        }
    }


class Subcategory(Model):
    id = UUIDField(primary_key=True, null=False)
    category_id = ForeignKey(to_model=Category, to_column="id", null=False)
    name = CharField(null=False)
    description = CharField()
    slug = CharField()
    icon = CharField(default="Target")
    features = JSONBField(null=False)
    created_at = DateTimeField(null=False)
    _inverse_foreign_keys = {
        "applets": {"from_model": "Applet", "from_field": "subcategory_id", "referenced_field": "id", "related_name": "applets"}
    }


class Tool(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    source = JSONBField(null=False, default={"host": "ame"})
    description = TextField()
    parameters = JSONBField()
    required_args = JSONBField()
    system_function = ForeignKey(
        to_model=SystemFunction,
        to_column="id",
    )
    additional_params = JSONBField()
    _inverse_foreign_keys = {
        "recipe_tools": {"from_model": "RecipeTool", "from_field": "tool", "referenced_field": "id", "related_name": "recipe_tools"}
    }


class Transformer(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField()
    input_params = JSONBField()
    output_params = JSONBField()
    _inverse_foreign_keys = {
        "actions": {"from_model": "Action", "from_field": "transformer", "referenced_field": "id", "related_name": "actions"}
    }


class WcClaim(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    applicant_name = CharField()
    person_id = UUIDField()
    date_of_birth = DateField()
    date_of_injury = DateField()
    age_at_doi = SmallIntegerField()
    occupational_code = SmallIntegerField()
    weekly_earnings = FloatField()
    _inverse_foreign_keys = {
        "wc_reports": {"from_model": "WcReport", "from_field": "claim_id", "referenced_field": "id", "related_name": "wc_reports"}
    }


class WcFingerType(Enum):
    INDEX = "index"
    LITTLE = "little"
    MIDDLE = "middle"
    RING = "ring"
    THUMB = "thumb"


class WcImpairmentDefinition(Model):
    id = UUIDField(primary_key=True, null=False)
    impairment_number = CharField()
    fec_rank = SmallIntegerField()
    name = CharField()
    attributes = JSONBField()
    finger_type = EnumField(
        enum_class=WcFingerType,
    )
    _inverse_foreign_keys = {
        "wc_injurys": {
            "from_model": "WcInjury",
            "from_field": "impairment_definition_id",
            "referenced_field": "id",
            "related_name": "wc_injurys",
        }
    }


class WcReport(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    claim_id = ForeignKey(to_model=WcClaim, to_column="id", null=False)
    final_rating = SmallIntegerField()
    left_side_total = SmallIntegerField()
    right_side_total = SmallIntegerField()
    default_side_total = SmallIntegerField()
    compensation_amount = FloatField()
    compensation_weeks = SmallIntegerField()
    compensation_days = SmallIntegerField()
    _inverse_foreign_keys = {
        "wc_injurys": {"from_model": "WcInjury", "from_field": "report_id", "referenced_field": "id", "related_name": "wc_injurys"}
    }


class Action(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False, max_length=255)
    matrix = ForeignKey(to_model=AutomationMatrix, to_column="id", null=False)
    transformer = ForeignKey(
        to_model=Transformer,
        to_column="id",
    )
    node_type = CharField(null=False, max_length=50)
    reference_id = UUIDField(null=False)
    _inverse_foreign_keys = {}


class AiAgent(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    recipe_id = ForeignKey(
        to_model=Recipe,
        to_column="id",
    )
    ai_settings_id = ForeignKey(
        to_model=AiSettings,
        to_column="id",
    )
    system_message_override = TextField()
    _inverse_foreign_keys = {}


class AiModelEndpoint(Model):
    id = UUIDField(primary_key=True, null=False)
    ai_model_id = ForeignKey(
        to_model=AiModel,
        to_column="id",
    )
    ai_endpoint_id = ForeignKey(
        to_model=AiEndpoint,
        to_column="id",
    )
    available = BooleanField(null=False, default="true")
    endpoint_priority = SmallIntegerField()
    configuration = JSONBField(default={})
    notes = TextField()
    created_at = DateTimeField(null=False)
    _inverse_foreign_keys = {}


class AppType(Enum):
    OTHER = "other"
    RECIPE = "recipe"
    WORKFLOW = "workflow"


class Applet(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False, unique=True)
    description = TextField()
    creator = CharField()
    type = EnumField(enum_class=AppType, null=False)
    compiled_recipe_id = ForeignKey(
        to_model=CompiledRecipe,
        to_column="id",
    )
    slug = CharField(null=False, unique=True)
    created_at = DateTimeField(null=False)
    user_id = UUIDField()
    is_public = BooleanField()
    data_source_config = JSONBField()
    result_component_config = JSONBField()
    next_step_config = JSONBField()
    subcategory_id = ForeignKey(
        to_model=Subcategory,
        to_column="id",
    )
    cta_text = CharField(default="Get Results")
    theme = CharField(default="default")
    _inverse_foreign_keys = {}


class DataType(Enum):
    BOOL = "bool"
    DICT = "dict"
    FLOAT = "float"
    INT = "int"
    LIST = "list"
    STR = "str"
    URL = "url"


class Arg(Model):
    id = UUIDField(primary_key=True, null=False)
    name = TextField(null=False)
    required = BooleanField(default="true")
    default = TextField()
    data_type = EnumField(enum_class=DataType, default="str")
    ready = BooleanField(default="false")
    registered_function = ForeignKey(
        to_model=RegisteredFunction,
        to_column="id",
    )
    _inverse_foreign_keys = {}


class AudioRecording(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    user_id = ForeignKey(to_model=Users, to_column="id", null=False)
    name = CharField(null=False)
    label = ForeignKey(
        to_model=AudioLabel,
        to_column="id",
    )
    file_url = CharField(null=False)
    duration = DecimalField()
    local_path = CharField()
    size = DecimalField()
    is_public = BooleanField(null=False, default="false")
    _inverse_foreign_keys = {}


class AudioRecordingUsers(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    first_name = TextField()
    last_name = TextField()
    email = TextField()
    _inverse_foreign_keys = {}


class DataSource(Enum):
    API = "api"
    CHANCE = "chance"
    DATABASE = "database"
    ENVIRONMENT = "environment"
    FILE = "file"
    FUNCTION = "function"
    GENERATED_DATA = "generated_data"
    NONE = "none"
    USER_INPUT = "user_input"


class DataDestination(Enum):
    API_RESPONSE = "api_response"
    DATABASE = "database"
    FILE = "file"
    FUNCTION = "function"
    USER_OUTPUT = "user_output"


class AutomationBoundaryBroker(Model):
    id = UUIDField(primary_key=True, null=False)
    matrix = ForeignKey(
        to_model=AutomationMatrix,
        to_column="id",
    )
    broker = ForeignKey(
        to_model=Broker,
        to_column="id",
    )
    spark_source = EnumField(
        enum_class=DataSource,
    )
    beacon_destination = EnumField(
        enum_class=DataDestination,
    )
    _inverse_foreign_keys = {}


class BrokerValue(Model):
    id = UUIDField(primary_key=True, null=False)
    user_id = ForeignKey(
        to_model=Users,
        to_column="id",
    )
    data_broker = ForeignKey(
        to_model=DataBroker,
        to_column="id",
    )
    data = JSONBField(default={"value": None})
    category = CharField()
    sub_category = CharField()
    tags = JSONBField()
    comments = TextField()
    created_at = DateTimeField(null=False)
    _inverse_foreign_keys = {}


class BucketStructures(Model):
    bucket_id = TextField(primary_key=True, null=False)
    structure = JSONBField()
    last_updated = DateTimeField()
    _inverse_foreign_keys = {}


class BucketTreeStructures(Model):
    bucket_id = TextField(primary_key=True, null=False)
    tree_structure = JSONBField()
    last_updated = DateTimeField()
    _inverse_foreign_keys = {}


class Emails(Model):
    id = UUIDField(primary_key=True, null=False)
    sender = TextField(null=False)
    recipient = TextField(null=False)
    subject = TextField(null=False)
    body = TextField(null=False)
    timestamp = DateTimeField()
    is_read = BooleanField(default="false")
    _inverse_foreign_keys = {}


class DataType(Enum):
    BOOL = "bool"
    DICT = "dict"
    FLOAT = "float"
    INT = "int"
    LIST = "list"
    STR = "str"
    URL = "url"


class Extractor(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    output_type = EnumField(
        enum_class=DataType,
    )
    default_identifier = CharField()
    default_index = SmallIntegerField()
    _inverse_foreign_keys = {}


class FileStructure(Model):
    id = IntegerField(primary_key=True, null=False, default="public.file_structure_id_seq")
    bucket_id = TextField(null=False)
    path = TextField(null=False)
    is_folder = BooleanField(null=False)
    file_id = UUIDField()
    parent_path = TextField()
    name = TextField(null=False)
    metadata = JSONBField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    _inverse_foreign_keys = {}


class FlashcardHistory(Model):
    id = UUIDField(primary_key=True, null=False)
    flashcard_id = ForeignKey(
        to_model=FlashcardData,
        to_column="id",
    )
    user_id = ForeignKey(to_model=Users, to_column="id", null=False)
    review_count = SmallIntegerField(default="0")
    correct_count = SmallIntegerField(default="0")
    incorrect_count = SmallIntegerField(default="0")
    created_at = DateTimeField()
    updated_at = DateTimeField()
    _inverse_foreign_keys = {}


class FlashcardImages(Model):
    id = UUIDField(primary_key=True, null=False)
    flashcard_id = ForeignKey(
        to_model=FlashcardData,
        to_column="id",
    )
    file_path = TextField(null=False)
    file_name = TextField(null=False)
    mime_type = TextField(null=False)
    size = IntegerField(null=False)
    created_at = DateTimeField()
    _inverse_foreign_keys = {}


class FlashcardSetRelations(Model):
    flashcard_id = ForeignKey(to_model=FlashcardData, to_column="id", primary_key=True, null=False)
    set_id = ForeignKey(to_model=FlashcardSets, to_column="set_id", primary_key=True, null=False)
    order = IntegerField()
    _inverse_foreign_keys = {}


class MessageRole(Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    USER = "user"


class MessageType(Enum):
    BASE64_IMAGE = "base64_image"
    BLOB = "blob"
    IMAGE_URL = "image_url"
    JSON_OBJECT = "json_object"
    MIXED = "mixed"
    OTHER = "other"
    TEXT = "text"
    TOOL_RESULT = "tool_result"


class Message(Model):
    id = UUIDField(primary_key=True, null=False)
    conversation_id = ForeignKey(to_model=Conversation, to_column="id", null=False)
    role = EnumField(enum_class=MessageRole, null=False)
    content = TextField()
    type = EnumField(enum_class=MessageType, null=False)
    display_order = SmallIntegerField()
    system_order = SmallIntegerField()
    created_at = DateTimeField(null=False)
    metadata = JSONBField()
    user_id = ForeignKey(
        to_model=Users,
        to_column="id",
    )
    _inverse_foreign_keys = {}


class MessageBroker(Model):
    id = UUIDField(primary_key=True, null=False)
    message_id = ForeignKey(to_model=MessageTemplate, to_column="id", null=False)
    broker_id = ForeignKey(to_model=DataBroker, to_column="id", null=False)
    default_value = TextField()
    default_component = ForeignKey(
        to_model=DataInputComponent,
        to_column="id",
    )
    _inverse_foreign_keys = {}


class ProjectMembers(Model):
    id = UUIDField(primary_key=True, null=False)
    project_id = ForeignKey(to_model=Projects, to_column="id", unique=True)
    user_id = ForeignKey(to_model=Users, to_column="id", unique=True)
    role = TextField(null=False)
    created_at = DateTimeField()
    _inverse_foreign_keys = {}


class BrokerRole(Enum):
    INPUT_BROKER = "input_broker"
    OUTPUT_BROKER = "output_broker"


class RecipeBroker(Model):
    id = UUIDField(primary_key=True, null=False)
    recipe = ForeignKey(to_model=Recipe, to_column="id", null=False)
    broker = ForeignKey(to_model=Broker, to_column="id", null=False)
    broker_role = EnumField(enum_class=BrokerRole, null=False)
    required = BooleanField(default="true")
    _inverse_foreign_keys = {}


class RecipeDisplay(Model):
    id = UUIDField(primary_key=True, null=False)
    recipe = ForeignKey(to_model=Recipe, to_column="id", null=False)
    display = ForeignKey(to_model=DisplayOption, to_column="id", null=False)
    priority = SmallIntegerField(default="1")
    display_settings = JSONBField()
    _inverse_foreign_keys = {}


class FunctionRole(Enum):
    COMPARISON = "comparison"
    DECISION = "decision"
    OTHER = "other"
    POST_PROCESSING = "post_processing"
    PRE_PROCESSING = "pre-Processing"
    RATING = "rating"
    SAVE_DATA = "save_data"
    VALIDATION = "validation"


class RecipeFunction(Model):
    id = UUIDField(primary_key=True, null=False)
    recipe = ForeignKey(to_model=Recipe, to_column="id", null=False)
    function = ForeignKey(to_model=SystemFunction, to_column="id", null=False)
    role = EnumField(enum_class=FunctionRole, null=False)
    params = JSONBField()
    _inverse_foreign_keys = {}


class RecipeMessage(Model):
    id = UUIDField(primary_key=True, null=False)
    message_id = ForeignKey(to_model=MessageTemplate, to_column="id", null=False, unique=True)
    recipe_id = ForeignKey(to_model=Recipe, to_column="id", null=False, unique=True)
    order = SmallIntegerField(null=False, default="1")
    _inverse_foreign_keys = {}


class RecipeMessageReorderQueue(Model):
    recipe_id = UUIDField(primary_key=True, null=False)
    last_modified = DateTimeField()
    _inverse_foreign_keys = {}


class ModelRole(Enum):
    PRIMARY_MODEL = "primary_model"
    TRIAL_MODEL = "trial_model"
    VERIFIED_MODEL = "verified_model"


class RecipeModel(Model):
    id = UUIDField(primary_key=True, null=False)
    recipe = ForeignKey(to_model=Recipe, to_column="id", null=False)
    ai_model = ForeignKey(to_model=AiModel, to_column="id", null=False)
    role = EnumField(enum_class=ModelRole, null=False, default="primary_model")
    priority = SmallIntegerField(default="1")
    _inverse_foreign_keys = {}


class RecipeProcessor(Model):
    id = UUIDField(primary_key=True, null=False)
    recipe = ForeignKey(to_model=Recipe, to_column="id", null=False)
    processor = ForeignKey(to_model=Processor, to_column="id", null=False)
    params = JSONBField()
    _inverse_foreign_keys = {}


class RecipeTool(Model):
    id = UUIDField(primary_key=True, null=False)
    recipe = ForeignKey(to_model=Recipe, to_column="id", null=False)
    tool = ForeignKey(to_model=Tool, to_column="id", null=False)
    params = JSONBField()
    _inverse_foreign_keys = {}


class TaskAssignments(Model):
    id = UUIDField(primary_key=True, null=False)
    task_id = ForeignKey(to_model=Tasks, to_column="id", unique=True)
    user_id = ForeignKey(to_model=Users, to_column="id", unique=True)
    assigned_by = ForeignKey(
        to_model=Users,
        to_column="id",
    )
    assigned_at = DateTimeField()
    _inverse_foreign_keys = {}


class TaskAttachments(Model):
    id = UUIDField(primary_key=True, null=False)
    task_id = ForeignKey(
        to_model=Tasks,
        to_column="id",
    )
    file_name = TextField(null=False)
    file_type = TextField()
    file_size = IntegerField()
    file_path = TextField(null=False)
    uploaded_by = ForeignKey(
        to_model=Users,
        to_column="id",
    )
    uploaded_at = DateTimeField()
    _inverse_foreign_keys = {}


class TaskComments(Model):
    id = UUIDField(primary_key=True, null=False)
    task_id = ForeignKey(
        to_model=Tasks,
        to_column="id",
    )
    user_id = ForeignKey(
        to_model=Users,
        to_column="id",
    )
    content = TextField(null=False)
    created_at = DateTimeField()
    updated_at = DateTimeField()
    _inverse_foreign_keys = {}


class UserPreferences(Model):
    user_id = ForeignKey(to_model=Users, to_column="id", primary_key=True, null=False)
    preferences = JSONBField(null=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    _inverse_foreign_keys = {}


class WcSide(Enum):
    DEFAULT = "default"
    LEFT = "left"
    RIGHT = "right"


class WcInjury(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    report_id = ForeignKey(
        to_model=WcReport,
        to_column="id",
    )
    impairment_definition_id = ForeignKey(
        to_model=WcImpairmentDefinition,
        to_column="id",
    )
    digit = SmallIntegerField()
    le = SmallIntegerField()
    side = EnumField(enum_class=WcSide, default="default")
    ue = SmallIntegerField()
    wpi = SmallIntegerField()
    pain = SmallIntegerField(default="0")
    industrial = SmallIntegerField(default="100")
    rating = SmallIntegerField()
    formula = CharField()
    updated_at = DateTimeField()
    _inverse_foreign_keys = {}


model_registry.register_all(
    [
        Action,
        AiAgent,
        AiEndpoint,
        AiModel,
        AiModelEndpoint,
        AiProvider,
        AiSettings,
        Applet,
        Arg,
        AudioLabel,
        AudioRecording,
        AudioRecordingUsers,
        AutomationBoundaryBroker,
        AutomationMatrix,
        Broker,
        BrokerValue,
        BucketStructures,
        BucketTreeStructures,
        Category,
        CompiledRecipe,
        Conversation,
        DataBroker,
        DataInputComponent,
        DataOutputComponent,
        DisplayOption,
        Emails,
        Extractor,
        FileStructure,
        FlashcardData,
        FlashcardHistory,
        FlashcardImages,
        FlashcardSetRelations,
        FlashcardSets,
        Message,
        MessageBroker,
        MessageTemplate,
        Processor,
        ProjectMembers,
        Projects,
        Recipe,
        RecipeBroker,
        RecipeDisplay,
        RecipeFunction,
        RecipeMessage,
        RecipeMessageReorderQueue,
        RecipeModel,
        RecipeProcessor,
        RecipeTool,
        RegisteredFunction,
        Subcategory,
        SystemFunction,
        TaskAssignments,
        TaskAttachments,
        TaskComments,
        Tasks,
        Tool,
        Transformer,
        UserPreferences,
        WcClaim,
        WcImpairmentDefinition,
        WcInjury,
        WcReport,
        Users,
    ]
)


# @dataclass
# class RecipeDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class RecipeManager(BaseManager):
#     def __init__(self):
#         super().__init__(Recipe, RecipeDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, recipe):
#         pass
#
#
# @dataclass
# class AiProviderDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class AiProviderManager(BaseManager):
#     def __init__(self):
#         super().__init__(AiProvider, AiProviderDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, ai_provider):
#         pass
#
#
# @dataclass
# class DataInputComponentDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class DataInputComponentManager(BaseManager):
#     def __init__(self):
#         super().__init__(DataInputComponent, DataInputComponentDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, data_input_component):
#         pass
#
#
# @dataclass
# class AiModelDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class AiModelManager(BaseManager):
#     def __init__(self):
#         super().__init__(AiModel, AiModelDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, ai_model):
#         pass
#
#
# @dataclass
# class BrokerDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class BrokerManager(BaseManager):
#     def __init__(self):
#         super().__init__(Broker, BrokerDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, broker):
#         pass
#
#
# @dataclass
# class DataOutputComponentDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class DataOutputComponentManager(BaseManager):
#     def __init__(self):
#         super().__init__(DataOutputComponent, DataOutputComponentDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, data_output_component):
#         pass
#
#
# @dataclass
# class FlashcardDataDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class FlashcardDataManager(BaseManager):
#     def __init__(self):
#         super().__init__(FlashcardData, FlashcardDataDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, flashcard_data):
#         pass
#
#
# @dataclass
# class ProjectsDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class ProjectsManager(BaseManager):
#     def __init__(self):
#         super().__init__(Projects, ProjectsDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, projects):
#         pass
#
#
# @dataclass
# class TasksDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class TasksManager(BaseManager):
#     def __init__(self):
#         super().__init__(Tasks, TasksDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, tasks):
#         pass
#
#
# @dataclass
# class AiEndpointDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class AiEndpointManager(BaseManager):
#     def __init__(self):
#         super().__init__(AiEndpoint, AiEndpointDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, ai_endpoint):
#         pass
#
#
# @dataclass
# class AutomationMatrixDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class AutomationMatrixManager(BaseManager):
#     def __init__(self):
#         super().__init__(AutomationMatrix, AutomationMatrixDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, automation_matrix):
#         pass
#
#
#
# @dataclass
# class MessageTemplateDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class MessageTemplateManager(BaseManager):
#     def __init__(self):
#         super().__init__(MessageTemplate, MessageTemplateDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, message_template):
#         pass
#
#
# @dataclass
# class RegisteredFunctionDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class RegisteredFunctionManager(BaseManager):
#     def __init__(self):
#         super().__init__(RegisteredFunction, RegisteredFunctionDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, registered_function):
#         pass
#
#
# @dataclass
# class SystemFunctionDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class SystemFunctionManager(BaseManager):
#     def __init__(self):
#         super().__init__(SystemFunction, SystemFunctionDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, system_function):
#         pass
#
#
# @dataclass
# class AiSettingsDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class AiSettingsManager(BaseManager):
#     def __init__(self):
#         super().__init__(AiSettings, AiSettingsDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, ai_settings):
#         pass
#
#
# @dataclass
# class AudioLabelDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class AudioLabelManager(BaseManager):
#     def __init__(self):
#         super().__init__(AudioLabel, AudioLabelDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, audio_label):
#         pass
#
#
# @dataclass
# class CategoryDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class CategoryManager(BaseManager):
#     def __init__(self):
#         super().__init__(Category, CategoryDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, category):
#         pass
#
#
#
# @dataclass
# class ConversationDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class ConversationManager(BaseManager):
#     def __init__(self):
#         super().__init__(Conversation, ConversationDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, conversation):
#         pass
#
#
# @dataclass
# class DisplayOptionDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class DisplayOptionManager(BaseManager):
#     def __init__(self):
#         super().__init__(DisplayOption, DisplayOptionDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, display_option):
#         pass
#
#
# @dataclass
# class FlashcardSetsDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class FlashcardSetsManager(BaseManager):
#     def __init__(self):
#         super().__init__(FlashcardSets, FlashcardSetsDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, flashcard_sets):
#         pass
#
#
# @dataclass
# class ProcessorDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class ProcessorManager(BaseManager):
#     def __init__(self):
#         super().__init__(Processor, ProcessorDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, processor):
#         pass
#
#
# @dataclass
# class SubcategoryDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class SubcategoryManager(BaseManager):
#     def __init__(self):
#         super().__init__(Subcategory, SubcategoryDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, subcategory):
#         pass
#
#
# @dataclass
# class ToolDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class ToolManager(BaseManager):
#     def __init__(self):
#         super().__init__(Tool, ToolDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, tool):
#         pass
#
#
# @dataclass
# class TransformerDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class TransformerManager(BaseManager):
#     def __init__(self):
#         super().__init__(Transformer, TransformerDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, transformer):
#         pass
#
#
# @dataclass
# class WcClaimDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class WcClaimManager(BaseManager):
#     def __init__(self):
#         super().__init__(WcClaim, WcClaimDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, wc_claim):
#         pass
#
#
# @dataclass
# class WcImpairmentDefinitionDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class WcImpairmentDefinitionManager(BaseManager):
#     def __init__(self):
#         super().__init__(WcImpairmentDefinition, WcImpairmentDefinitionDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, wc_impairment_definition):
#         pass
#
#
# @dataclass
# class WcReportDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class WcReportManager(BaseManager):
#     def __init__(self):
#         super().__init__(WcReport, WcReportDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, wc_report):
#         pass
#
#
# @dataclass
# class ActionDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class ActionManager(BaseManager):
#     def __init__(self):
#         super().__init__(Action, ActionDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, action):
#         pass
#
#
# @dataclass
# class AiAgentDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class AiAgentManager(BaseManager):
#     def __init__(self):
#         super().__init__(AiAgent, AiAgentDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, ai_agent):
#         pass
#
#
# @dataclass
# class AiModelEndpointDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class AiModelEndpointManager(BaseManager):
#     def __init__(self):
#         super().__init__(AiModelEndpoint, AiModelEndpointDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, ai_model_endpoint):
#         pass
#
#
# @dataclass
# class AppletDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class AppletManager(BaseManager):
#     def __init__(self):
#         super().__init__(Applet, AppletDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, applet):
#         pass
#
#
# @dataclass
# class ArgDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class ArgManager(BaseManager):
#     def __init__(self):
#         super().__init__(Arg, ArgDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, arg):
#         pass
#
#
# @dataclass
# class AudioRecordingDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class AudioRecordingManager(BaseManager):
#     def __init__(self):
#         super().__init__(AudioRecording, AudioRecordingDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, audio_recording):
#         pass
#
#
# @dataclass
# class AudioRecordingUsersDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class AudioRecordingUsersManager(BaseManager):
#     def __init__(self):
#         super().__init__(AudioRecordingUsers, AudioRecordingUsersDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, audio_recording_users):
#         pass
#
#
# @dataclass
# class AutomationBoundaryBrokerDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class AutomationBoundaryBrokerManager(BaseManager):
#     def __init__(self):
#         super().__init__(AutomationBoundaryBroker, AutomationBoundaryBrokerDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, automation_boundary_broker):
#         pass
#
#
# @dataclass
# class BrokerValueDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class BrokerValueManager(BaseManager):
#     def __init__(self):
#         super().__init__(BrokerValue, BrokerValueDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, broker_value):
#         pass
#
#
# @dataclass
# class BucketStructuresDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class BucketStructuresManager(BaseManager):
#     def __init__(self):
#         super().__init__(BucketStructures, BucketStructuresDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, bucket_structures):
#         pass
#
#
# @dataclass
# class BucketTreeStructuresDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class BucketTreeStructuresManager(BaseManager):
#     def __init__(self):
#         super().__init__(BucketTreeStructures, BucketTreeStructuresDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, bucket_tree_structures):
#         pass
#
#
# @dataclass
# class EmailsDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class EmailsManager(BaseManager):
#     def __init__(self):
#         super().__init__(Emails, EmailsDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, emails):
#         pass
#
#
# @dataclass
# class ExtractorDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class ExtractorManager(BaseManager):
#     def __init__(self):
#         super().__init__(Extractor, ExtractorDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, extractor):
#         pass
#
#
# @dataclass
# class FileStructureDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class FileStructureManager(BaseManager):
#     def __init__(self):
#         super().__init__(FileStructure, FileStructureDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, file_structure):
#         pass
#
#
# @dataclass
# class FlashcardHistoryDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class FlashcardHistoryManager(BaseManager):
#     def __init__(self):
#         super().__init__(FlashcardHistory, FlashcardHistoryDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, flashcard_history):
#         pass
#
#
# @dataclass
# class FlashcardImagesDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class FlashcardImagesManager(BaseManager):
#     def __init__(self):
#         super().__init__(FlashcardImages, FlashcardImagesDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, flashcard_images):
#         pass
#
#
# @dataclass
# class FlashcardSetRelationsDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class FlashcardSetRelationsManager(BaseManager):
#     def __init__(self):
#         super().__init__(FlashcardSetRelations, FlashcardSetRelationsDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, flashcard_set_relations):
#         pass
#
#
# @dataclass
# class MessageDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class MessageManager(BaseManager):
#     def __init__(self):
#         super().__init__(Message, MessageDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, message):
#         pass
#
#
# @dataclass
# class MessageBrokerDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class MessageBrokerManager(BaseManager):
#     def __init__(self):
#         super().__init__(MessageBroker, MessageBrokerDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, message_broker):
#         pass
#
#
# @dataclass
# class ProjectMembersDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class ProjectMembersManager(BaseManager):
#     def __init__(self):
#         super().__init__(ProjectMembers, ProjectMembersDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, project_members):
#         pass
#
#
# @dataclass
# class RecipeBrokerDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class RecipeBrokerManager(BaseManager):
#     def __init__(self):
#         super().__init__(RecipeBroker, RecipeBrokerDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, recipe_broker):
#         pass
#
#
# @dataclass
# class RecipeDisplayDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class RecipeDisplayManager(BaseManager):
#     def __init__(self):
#         super().__init__(RecipeDisplay, RecipeDisplayDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, recipe_display):
#         pass
#
#
# @dataclass
# class RecipeFunctionDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class RecipeFunctionManager(BaseManager):
#     def __init__(self):
#         super().__init__(RecipeFunction, RecipeFunctionDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, recipe_function):
#         pass
#
#
# @dataclass
# class RecipeMessageDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class RecipeMessageManager(BaseManager):
#     def __init__(self):
#         super().__init__(RecipeMessage, RecipeMessageDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, recipe_message):
#         pass
#
#
# @dataclass
# class RecipeMessageReorderQueueDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class RecipeMessageReorderQueueManager(BaseManager):
#     def __init__(self):
#         super().__init__(RecipeMessageReorderQueue, RecipeMessageReorderQueueDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, recipe_message_reorder_queue):
#         pass
#
#
# @dataclass
# class RecipeModelDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class RecipeModelManager(BaseManager):
#     def __init__(self):
#         super().__init__(RecipeModel, RecipeModelDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, recipe_model):
#         pass
#
#
# @dataclass
# class RecipeProcessorDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class RecipeProcessorManager(BaseManager):
#     def __init__(self):
#         super().__init__(RecipeProcessor, RecipeProcessorDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, recipe_processor):
#         pass
#
#
# @dataclass
# class RecipeToolDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class RecipeToolManager(BaseManager):
#     def __init__(self):
#         super().__init__(RecipeTool, RecipeToolDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, recipe_tool):
#         pass
#
#
# @dataclass
# class TaskAssignmentsDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class TaskAssignmentsManager(BaseManager):
#     def __init__(self):
#         super().__init__(TaskAssignments, TaskAssignmentsDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, task_assignments):
#         pass
#
#
# @dataclass
# class TaskAttachmentsDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class TaskAttachmentsManager(BaseManager):
#     def __init__(self):
#         super().__init__(TaskAttachments, TaskAttachmentsDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, task_attachments):
#         pass
#
#
# @dataclass
# class TaskCommentsDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class TaskCommentsManager(BaseManager):
#     def __init__(self):
#         super().__init__(TaskComments, TaskCommentsDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, task_comments):
#         pass
#
#
# @dataclass
# class UserPreferencesDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class UserPreferencesManager(BaseManager):
#     def __init__(self):
#         super().__init__(UserPreferences, UserPreferencesDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, user_preferences):
#         pass
#
#
# @dataclass
# class WcInjuryDTO(BaseDTO):
#     id: str
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(id=str(model.id))
#
#
# class WcInjuryManager(BaseManager):
#     def __init__(self):
#         super().__init__(WcInjury, WcInjuryDTO)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#
#     async def _initialize_runtime_data(self, wc_injury):
#         pass
#
#
# # Example with some useful recipe-related methods
# class RecipeManagerTwo(BaseManager):
#     def __init__(self):
#         super().__init__(Recipe)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#         self.computed_fields.add("version_count")
#         self.computed_fields.add("has_compiled_versions")
#         self.relation_fields.add("compiled_recipes")
#
#     async def _initialize_runtime_data(self, recipe):
#         recipe.runtime.version_count = None
#         recipe.runtime.latest_version = None
#         recipe.runtime.has_compiled_versions = False
#
#     async def get_latest_compiled_version(self, recipe):
#         if not recipe.runtime.latest_version:
#             versions = await recipe.fetch_ifk("compiled_recipes")
#             recipe.runtime.latest_version = max(v.version for v in versions) if versions else 0
#         return recipe.runtime.latest_version
#
#
# class CompiledRecipeManagerTwo(BaseManager):
#     def __init__(self):
#         super().__init__(CompiledRecipe)
#
#     def _initialize_manager(self):
#         super()._initialize_manager()
#         self.computed_fields.add("is_latest")
#         self.relation_fields.add("recipe")
#
#     async def _initialize_runtime_data(self, recipe):
#         recipe.runtime.is_latest = None
#         recipe.runtime.parent_recipe = None
#
#     async def check_if_latest(self, compiled_recipe):
#         if compiled_recipe.runtime.is_latest is None:
#             recipe = await compiled_recipe.fetch_fk("recipe_id")
#             if recipe:
#                 latest = await recipe.fetch_ifk("compiled_recipes")
#                 compiled_recipe.runtime.is_latest = (compiled_recipe.version == max(v.version for v in latest)) if latest else True
#         return compiled_recipe.runtime.is_latest
#
#
# @dataclass
# class DataBrokerDTO(BaseDTO):
#     id: str
#     name: str
#     data_type: str = "str"
#     default_value: str = None
#     input_component_id: str = None
#     output_component_id: str = None
#     color: str = "blue"
#     message_brokers: list = None
#     message_count: int = None
#     is_active: bool = False
#     last_used: str = None
#
#     @classmethod
#     async def from_model(cls, model):
#         return cls(
#             id=str(model.id),
#             name=model.name,
#             data_type=model.data_type,
#             default_value=model.default_value,
#             input_component_id=str(model.input_component) if model.input_component else None,
#             output_component_id=str(model.output_component) if model.output_component else None,
#             color=model.color,
#         )
#
#
# class DataBrokerManager(BaseManager):
#     def __init__(self):
#         super().__init__(DataBroker, DataBrokerDTO)
#
#     async def _initialize_dto_runtime(self, dto, item):
#         dto.message_brokers = await item.fetch_ifk("message_brokers")
#         dto.message_count = len(dto.message_brokers) if dto.message_brokers else 0
#
#
# @dataclass
# class CompiledRecipeDTO(BaseDTO):
#     id: str
#     recipe_id: str
#     version: int
#     brokers: list = None
#     raw_messages: list = None
#     clean_messages: list = None
#     ready_messages: list = None
#     settings: list = None
#
#     @classmethod
#     async def from_model(cls, model):
#         import json
#
#         compiled_data = json.loads(model.compiled_recipe) if isinstance(model.compiled_recipe, str) else model.compiled_recipe
#
#         brokers = [
#             {"id": broker["id"], "default_value": broker.get("defaultValue"), "value": broker.get("defaultValue"), "ready": False}
#             for broker in compiled_data.get("brokers", [])
#         ]
#
#         raw_messages = compiled_data.get("messages", [])
#         clean_messages = update_content_with_runtime_brokers(raw_messages, brokers)
#         ready_messages = update_content_with_runtime_brokers(clean_messages, brokers)
#
#         return cls(
#             id=str(model.id),
#             recipe_id=str(model.recipe_id),
#             version=model.version,
#             brokers=brokers,
#             raw_messages=raw_messages,
#             clean_messages=clean_messages,
#             ready_messages=ready_messages,
#             settings=compiled_data.get("settings", []),
#         )
#
#     def update_broker_value(self, broker_id: str, value: str):
#         vcprint(
#             {"broker_id": broker_id, "value": value},
#             "[COMPILED RECIPE DTO] Updating Broker Value",
#             verbose=True,
#             pretty=True,
#             color="yellow",
#         )
#         for broker in self.brokers:
#             if broker["id"] == broker_id:
#                 broker["value"] = value
#                 broker["ready"] = True
#                 break
#         vcprint(self.brokers, "[COMPILED RECIPE DTO] All Brokers", verbose=True, pretty=True, color="yellow")
#         self._update_messages()
#
#     def update_broker_values(self, broker_values: dict):
#         for broker in broker_values:
#             self.update_broker_value(broker["id"], broker["value"])
#
#     def add_broker(self, broker):
#         vcprint(broker, "Broker", verbose=debug, pretty=True, color="yellow")
#         broker_id = broker.id if hasattr(broker, "id") else broker["id"]
#         default_value = broker.default_value if hasattr(broker, "default_value") else broker.get("defaultValue")
#
#         # Check if broker already exists
#         existing_broker = next((broker for broker in self.brokers if broker["id"] == broker_id), None)
#
#         if existing_broker:
#             # Update existing broker's value and ready status
#             existing_broker["value"] = default_value
#             existing_broker["ready"] = True
#         else:
#             # Add new broker
#             new_broker = {"id": broker_id, "default_value": default_value, "value": default_value, "ready": False}
#             self.brokers.append(new_broker)
#
#         self._update_messages()
#
#     def _update_messages(self):
#         self.clean_messages = update_content_with_runtime_brokers(self.raw_messages, self.brokers)
#         self.ready_messages = update_content_with_runtime_brokers(self.clean_messages, self.brokers)
#
#     def get_final_structure(self):
#         return {
#             "id": self.id,
#             "recipe_id": self.recipe_id,
#             "version": self.version,
#             "messages": self.ready_messages,
#             "settings": self.settings,
#         }
#
#     def to_dict(self) -> dict:
#         return {key: getattr(self, key) for key in self.__annotations__ if getattr(self, key) is not None}
#
#
# class CompiledRecipeManager(BaseManager):
#     def __init__(self):
#         super().__init__(CompiledRecipe, CompiledRecipeDTO)
#
#     async def get_final_structure(self, compiled_recipe_id: str):
#         item = await self.load_item(id=compiled_recipe_id)
#         return item.runtime.dto.get_final_structure() if item else None
#
#     async def update_broker_value(self, compiled_recipe_id: str, broker_id: str, value: str):
#         item = await self.load_item(id=compiled_recipe_id)
#         if item and item.runtime.dto:
#             item.runtime.dto.update_broker_value(broker_id, value)
#             return item.runtime.dto.to_dict()
#         return None
#
#     async def update_broker_values(self, compiled_recipe_id: str, broker_values: dict):
#         item = await self.load_item(id=compiled_recipe_id)
#         if item and item.runtime.dto:
#             item.runtime.dto.update_broker_values(broker_values)
#             return item.runtime.dto.to_dict()
#         return None
#
#     async def add_broker(self, compiled_recipe_id: str, broker):
#         item = await self.load_item(id=compiled_recipe_id)
#         if item and item.runtime.dto:
#             item.runtime.dto.add_broker(broker)
#             return item.runtime.dto.to_dict()
#         return None
#
#     async def get_brokers(self, compiled_recipe_id: str):
#         item = await self.load_item(id=compiled_recipe_id)
#         return item.runtime.dto.brokers if item else None
#
#     # If we need to find all compiled versions for a recipe:
#     async def get_compiled_versions_for_recipe(self, recipe_id: str):
#         return await self.model.filter(recipe_id=recipe_id).all()
