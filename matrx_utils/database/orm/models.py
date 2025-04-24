# File: database/orm/models.py
from matrx_utils.database.orm.core.fields import (CharField, EnumField, DateField, TextField, IntegerField, FloatField, BooleanField, DateTimeField, UUIDField, JSONField, DecimalField, BigIntegerField, SmallIntegerField, JSONBField, UUIDArrayField, JSONBArrayField, ForeignKey)
from matrx_utils.database.orm.core.base import Model
from matrx_utils.database.orm.core.registry import model_registry
from enum import Enum
from dataclasses import dataclass
from matrx_utils.database.orm.core.extended import BaseDTO, BaseManager

verbose = False
debug = False
info = True

class Users(Model):
        id = UUIDField(primary_key=True, null=False)
        email = CharField(null=False)




class RecipeStatus(str, Enum):
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
    status = EnumField(enum_class=RecipeStatus, null=False, default='draft')
    version = SmallIntegerField(default='1')
    post_result_options = JSONBField()
    user_id = ForeignKey(to_model=Users, to_column='id', )
    _inverse_foreign_keys = {'compiled_recipes': {'from_model': 'CompiledRecipe', 'from_field': 'recipe_id', 'referenced_field': 'id', 'related_name': 'compiled_recipes'}, 'ai_agents': {'from_model': 'AiAgent', 'from_field': 'recipe_id', 'referenced_field': 'id', 'related_name': 'ai_agents'}, 'recipe_displays': {'from_model': 'RecipeDisplay', 'from_field': 'recipe', 'referenced_field': 'id', 'related_name': 'recipe_displays'}, 'recipe_processors': {'from_model': 'RecipeProcessor', 'from_field': 'recipe', 'referenced_field': 'id', 'related_name': 'recipe_processors'}, 'recipe_models': {'from_model': 'RecipeModel', 'from_field': 'recipe', 'referenced_field': 'id', 'related_name': 'recipe_models'}, 'recipe_brokers': {'from_model': 'RecipeBroker', 'from_field': 'recipe', 'referenced_field': 'id', 'related_name': 'recipe_brokers'}, 'recipe_messages': {'from_model': 'RecipeMessage', 'from_field': 'recipe_id', 'referenced_field': 'id', 'related_name': 'recipe_messages'}, 'recipe_tools': {'from_model': 'RecipeTool', 'from_field': 'recipe', 'referenced_field': 'id', 'related_name': 'recipe_tools'}, 'recipe_functions': {'from_model': 'RecipeFunction', 'from_field': 'recipe', 'referenced_field': 'id', 'related_name': 'recipe_functions'}}

class ScrapeDomain(Model):
    id = UUIDField(primary_key=True, null=False)
    url = CharField()
    common_name = CharField()
    scrape_allowed = BooleanField(default=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=True)
    _inverse_foreign_keys = {'scrape_path_patterns': {'from_model': 'ScrapePathPattern', 'from_field': 'scrape_domain_id', 'referenced_field': 'id', 'related_name': 'scrape_path_patterns'}, 'scrape_jobs': {'from_model': 'ScrapeJob', 'from_field': 'scrape_domain_id', 'referenced_field': 'id', 'related_name': 'scrape_jobs'}, 'scrape_domain_quick_scrape_settingss': {'from_model': 'ScrapeDomainQuickScrapeSettings', 'from_field': 'scrape_domain_id', 'referenced_field': 'id', 'related_name': 'scrape_domain_quick_scrape_settingss'}, 'scrape_domain_disallowed_notess': {'from_model': 'ScrapeDomainDisallowedNotes', 'from_field': 'scrape_domain_id', 'referenced_field': 'id', 'related_name': 'scrape_domain_disallowed_notess'}, 'scrape_domain_robots_txts': {'from_model': 'ScrapeDomainRobotsTxt', 'from_field': 'scrape_domain_id', 'referenced_field': 'id', 'related_name': 'scrape_domain_robots_txts'}, 'scrape_domain_notess': {'from_model': 'ScrapeDomainNotes', 'from_field': 'scrape_domain_id', 'referenced_field': 'id', 'related_name': 'scrape_domain_notess'}, 'scrape_domain_sitemaps': {'from_model': 'ScrapeDomainSitemap', 'from_field': 'scrape_domain_id', 'referenced_field': 'id', 'related_name': 'scrape_domain_sitemaps'}, 'scrape_tasks': {'from_model': 'ScrapeTask', 'from_field': 'scrape_domain_id', 'referenced_field': 'id', 'related_name': 'scrape_tasks'}, 'scrape_quick_failure_logs': {'from_model': 'ScrapeQuickFailureLog', 'from_field': 'scrape_domain_id', 'referenced_field': 'id', 'related_name': 'scrape_quick_failure_logs'}}

class ScrapeJob(Model):
    id = UUIDField(primary_key=True, null=False)
    scrape_domain_id = ForeignKey(to_model=ScrapeDomain, to_column='id', null=False)
    start_urls = JSONBField(null=False)
    scrape_status = CharField(null=False)
    parse_status = CharField(null=False)
    attempt_limit = SmallIntegerField(null=False, default='3')
    started_at = DateTimeField()
    finished_at = DateTimeField()
    name = CharField()
    description = CharField()
    user_id = ForeignKey(to_model=Users, to_column='id', )
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=False)
    _inverse_foreign_keys = {'scrape_cycle_trackers': {'from_model': 'ScrapeCycleTracker', 'from_field': 'scrape_job_id', 'referenced_field': 'id', 'related_name': 'scrape_cycle_trackers'}, 'scrape_tasks': {'from_model': 'ScrapeTask', 'from_field': 'scrape_job_id', 'referenced_field': 'id', 'related_name': 'scrape_tasks'}}

class AiProvider(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField()
    company_description = TextField()
    documentation_link = CharField()
    models_link = CharField()
    _inverse_foreign_keys = {'ai_settingss': {'from_model': 'AiSettings', 'from_field': 'ai_provider', 'referenced_field': 'id', 'related_name': 'ai_settingss'}, 'ai_models': {'from_model': 'AiModel', 'from_field': 'model_provider', 'referenced_field': 'id', 'related_name': 'ai_models'}}



class DefaultComponent(str, Enum):
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

class Size(str, Enum):
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

class Orientation(str, Enum):
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
    component = EnumField(enum_class=DefaultComponent, null=False, default='BrokerTextarea')
    name = CharField()
    description = TextField()
    placeholder = TextField()
    container_class_name = CharField()
    collapsible_class_name = CharField()
    label_class_name = CharField()
    description_class_name = CharField()
    component_class_name = CharField()
    size = EnumField(enum_class=Size, )
    height = EnumField(enum_class=Size, )
    width = EnumField(enum_class=Size, )
    min_height = EnumField(enum_class=Size, )
    max_height = EnumField(enum_class=Size, )
    min_width = EnumField(enum_class=Size, )
    max_width = EnumField(enum_class=Size, )
    orientation = EnumField(enum_class=Orientation, default='vertical')
    _inverse_foreign_keys = {'message_brokers': {'from_model': 'MessageBroker', 'from_field': 'default_component', 'referenced_field': 'id', 'related_name': 'message_brokers'}, 'brokers': {'from_model': 'Broker', 'from_field': 'custom_source_component', 'referenced_field': 'id', 'related_name': 'brokers'}, 'data_brokers': {'from_model': 'DataBroker', 'from_field': 'input_component', 'referenced_field': 'id', 'related_name': 'data_brokers'}}

class ScrapeCachePolicy(Model):
    id = UUIDField(primary_key=True, null=False)
    rescrape_after = IntegerField(null=False, default='2592000')
    stale_after = IntegerField(null=False, default='5184000')
    user_id = ForeignKey(to_model=Users, to_column='id', )
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=False)
    _inverse_foreign_keys = {'scrape_path_pattern_cache_policys': {'from_model': 'ScrapePathPatternCachePolicy', 'from_field': 'scrape_cache_policy_id', 'referenced_field': 'id', 'related_name': 'scrape_path_pattern_cache_policys'}}

class ScrapePathPattern(Model):
    id = UUIDField(primary_key=True, null=False)
    scrape_domain_id = ForeignKey(to_model=ScrapeDomain, to_column='id', )
    path_pattern = CharField(default='/*')
    created_at = DateTimeField()
    updated_at = DateTimeField()
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=True)
    _inverse_foreign_keys = {'scrape_configurations': {'from_model': 'ScrapeConfiguration', 'from_field': 'scrape_path_pattern_id', 'referenced_field': 'id', 'related_name': 'scrape_configurations'}, 'scrape_path_pattern_overrides': {'from_model': 'ScrapePathPatternOverride', 'from_field': 'scrape_path_pattern_id', 'referenced_field': 'id', 'related_name': 'scrape_path_pattern_overrides'}, 'scrape_path_pattern_cache_policys': {'from_model': 'ScrapePathPatternCachePolicy', 'from_field': 'scrape_path_pattern_id', 'referenced_field': 'id', 'related_name': 'scrape_path_pattern_cache_policys'}}

class ScrapePathPatternCachePolicy(Model):
    id = UUIDField(primary_key=True, null=False)
    scrape_cache_policy_id = ForeignKey(to_model=ScrapeCachePolicy, to_column='id', null=False)
    scrape_path_pattern_id = ForeignKey(to_model=ScrapePathPattern, to_column='id', null=False)
    user_id = UUIDField()
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=False)
    _inverse_foreign_keys = {'scrape_cycle_trackers': {'from_model': 'ScrapeCycleTracker', 'from_field': 'scrape_path_pattern_cache_policy_id', 'referenced_field': 'id', 'related_name': 'scrape_cycle_trackers'}, 'scrape_parsed_pages': {'from_model': 'ScrapeParsedPage', 'from_field': 'scrape_path_pattern_cache_policy_id', 'referenced_field': 'id', 'related_name': 'scrape_parsed_pages'}}

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
    model_provider = ForeignKey(to_model=AiProvider, to_column='id', )
    _inverse_foreign_keys = {'ai_model_endpoints': {'from_model': 'AiModelEndpoint', 'from_field': 'ai_model_id', 'referenced_field': 'id', 'related_name': 'ai_model_endpoints'}, 'ai_settingss': {'from_model': 'AiSettings', 'from_field': 'ai_model', 'referenced_field': 'id', 'related_name': 'ai_settingss'}, 'recipe_models': {'from_model': 'RecipeModel', 'from_field': 'ai_model', 'referenced_field': 'id', 'related_name': 'recipe_models'}}



class DataType(str, Enum):
    BOOL = "bool"
    DICT = "dict"
    FLOAT = "float"
    INT = "int"
    LIST = "list"
    STR = "str"
    URL = "url"

class DataSource(str, Enum):
    API = "api"
    CHANCE = "chance"
    DATABASE = "database"
    ENVIRONMENT = "environment"
    FILE = "file"
    FUNCTION = "function"
    GENERATED_DATA = "generated_data"
    NONE = "none"
    USER_INPUT = "user_input"

class DataDestination(str, Enum):
    API_RESPONSE = "api_response"
    DATABASE = "database"
    FILE = "file"
    FUNCTION = "function"
    USER_OUTPUT = "user_output"

class DestinationComponent(str, Enum):
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
    value = JSONBField(default={'broker_value': None})
    data_type = EnumField(enum_class=DataType, null=False, default='str')
    ready = BooleanField(default=False)
    default_source = EnumField(enum_class=DataSource, default='none')
    display_name = CharField()
    description = TextField()
    tooltip = TextField()
    validation_rules = JSONBField()
    sample_entries = TextField()
    custom_source_component = ForeignKey(to_model=DataInputComponent, to_column='id', )
    additional_params = JSONBField()
    other_source_params = JSONBField()
    default_destination = EnumField(enum_class=DataDestination, )
    output_component = EnumField(enum_class=DestinationComponent, )
    tags = JSONBField(default=[])
    string_value = TextField()
    _inverse_foreign_keys = {'recipe_brokers': {'from_model': 'RecipeBroker', 'from_field': 'broker', 'referenced_field': 'id', 'related_name': 'recipe_brokers'}, 'registered_functions': {'from_model': 'RegisteredFunction', 'from_field': 'return_broker', 'referenced_field': 'id', 'related_name': 'registered_functions'}, 'automation_boundary_brokers': {'from_model': 'AutomationBoundaryBroker', 'from_field': 'broker', 'referenced_field': 'id', 'related_name': 'automation_boundary_brokers'}}



class DestinationComponent(str, Enum):
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
    component_type = EnumField(enum_class=DestinationComponent, )
    ui_component = CharField()
    props = JSONBField()
    additional_params = JSONBField()
    _inverse_foreign_keys = {'data_brokers': {'from_model': 'DataBroker', 'from_field': 'output_component', 'referenced_field': 'id', 'related_name': 'data_brokers'}}

class FlashcardData(Model):
    id = UUIDField(primary_key=True, null=False)
    user_id = ForeignKey(to_model=Users, to_column='id', null=False)
    topic = TextField()
    lesson = TextField()
    difficulty = TextField()
    front = TextField(null=False)
    back = TextField(null=False)
    example = TextField()
    detailed_explanation = TextField()
    audio_explanation = TextField()
    personal_notes = TextField()
    is_deleted = BooleanField(default=False)
    public = BooleanField(default=False)
    shared_with = UUIDArrayField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    _inverse_foreign_keys = {'flashcard_historys': {'from_model': 'FlashcardHistory', 'from_field': 'flashcard_id', 'referenced_field': 'id', 'related_name': 'flashcard_historys'}, 'flashcard_set_relationss': {'from_model': 'FlashcardSetRelations', 'from_field': 'flashcard_id', 'referenced_field': 'id', 'related_name': 'flashcard_set_relationss'}, 'flashcard_imagess': {'from_model': 'FlashcardImages', 'from_field': 'flashcard_id', 'referenced_field': 'id', 'related_name': 'flashcard_imagess'}}

class Organizations(Model):
    id = UUIDField(primary_key=True, null=False)
    name = TextField(null=False)
    slug = TextField(null=False, unique=True)
    description = TextField()
    logo_url = TextField()
    website = TextField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    created_by = ForeignKey(to_model=Users, to_column='id', )
    is_personal = BooleanField(default=False)
    settings = JSONBField(default={})
    _inverse_foreign_keys = {'permissionss': {'from_model': 'Permissions', 'from_field': 'granted_to_organization_id', 'referenced_field': 'id', 'related_name': 'permissionss'}, 'organization_memberss': {'from_model': 'OrganizationMembers', 'from_field': 'organization_id', 'referenced_field': 'id', 'related_name': 'organization_memberss'}, 'organization_invitationss': {'from_model': 'OrganizationInvitations', 'from_field': 'organization_id', 'referenced_field': 'id', 'related_name': 'organization_invitationss'}}

class Projects(Model):
    id = UUIDField(primary_key=True, null=False)
    name = TextField(null=False)
    description = TextField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    created_by = ForeignKey(to_model=Users, to_column='id', )
    _inverse_foreign_keys = {'project_memberss': {'from_model': 'ProjectMembers', 'from_field': 'project_id', 'referenced_field': 'id', 'related_name': 'project_memberss'}, 'taskss': {'from_model': 'Tasks', 'from_field': 'project_id', 'referenced_field': 'id', 'related_name': 'taskss'}}

class ScrapeCycleTracker(Model):
    id = UUIDField(primary_key=True, null=False)
    target_url = CharField()
    page_name = CharField()
    scrape_path_pattern_cache_policy_id = ForeignKey(to_model=ScrapePathPatternCachePolicy, to_column='id', )
    scrape_job_id = ForeignKey(to_model=ScrapeJob, to_column='id', )
    last_run_at = DateTimeField()
    next_run_at = DateTimeField()
    is_active = BooleanField(default=True)
    user_id = ForeignKey(to_model=Users, to_column='id', )
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=False)
    _inverse_foreign_keys = {'scrape_cycle_runs': {'from_model': 'ScrapeCycleRun', 'from_field': 'scrape_cycle_tracker_id', 'referenced_field': 'id', 'related_name': 'scrape_cycle_runs'}, 'scrape_parsed_pages': {'from_model': 'ScrapeParsedPage', 'from_field': 'scrape_cycle_tracker_id', 'referenced_field': 'id', 'related_name': 'scrape_parsed_pages'}}

class Tasks(Model):
    id = UUIDField(primary_key=True, null=False)
    title = TextField(null=False)
    description = TextField()
    project_id = ForeignKey(to_model=Projects, to_column='id', )
    status = TextField(null=False, default='incomplete')
    due_date = DateField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    created_by = ForeignKey(to_model=Users, to_column='id', )
    _inverse_foreign_keys = {'task_assignmentss': {'from_model': 'TaskAssignments', 'from_field': 'task_id', 'referenced_field': 'id', 'related_name': 'task_assignmentss'}, 'task_attachmentss': {'from_model': 'TaskAttachments', 'from_field': 'task_id', 'referenced_field': 'id', 'related_name': 'task_attachmentss'}, 'task_commentss': {'from_model': 'TaskComments', 'from_field': 'task_id', 'referenced_field': 'id', 'related_name': 'task_commentss'}}

class AiEndpoint(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    provider = CharField()
    description = TextField()
    additional_cost = BooleanField(default=True)
    cost_details = JSONBField()
    params = JSONField()
    _inverse_foreign_keys = {'ai_model_endpoints': {'from_model': 'AiModelEndpoint', 'from_field': 'ai_endpoint_id', 'referenced_field': 'id', 'related_name': 'ai_model_endpoints'}, 'ai_settingss': {'from_model': 'AiSettings', 'from_field': 'ai_endpoint', 'referenced_field': 'id', 'related_name': 'ai_settingss'}}



class CognitionMatrices(str, Enum):
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
    cognition_matrices = EnumField(enum_class=CognitionMatrices, )
    _inverse_foreign_keys = {'actions': {'from_model': 'Action', 'from_field': 'matrix', 'referenced_field': 'id', 'related_name': 'actions'}, 'automation_boundary_brokers': {'from_model': 'AutomationBoundaryBroker', 'from_field': 'matrix', 'referenced_field': 'id', 'related_name': 'automation_boundary_brokers'}}



class DataType(str, Enum):
    BOOL = "bool"
    DICT = "dict"
    FLOAT = "float"
    INT = "int"
    LIST = "list"
    STR = "str"
    URL = "url"

class Color(str, Enum):
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
    data_type = EnumField(enum_class=DataType, default='str')
    default_value = TextField()
    input_component = ForeignKey(to_model=DataInputComponent, to_column='id', )
    color = EnumField(enum_class=Color, default='blue')
    output_component = ForeignKey(to_model=DataOutputComponent, to_column='id', )
    _inverse_foreign_keys = {'broker_values': {'from_model': 'BrokerValue', 'from_field': 'data_broker', 'referenced_field': 'id', 'related_name': 'broker_values'}, 'message_brokers': {'from_model': 'MessageBroker', 'from_field': 'broker_id', 'referenced_field': 'id', 'related_name': 'message_brokers'}}



class MessageRole(str, Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    USER = "user"

class MessageType(str, Enum):
    BASE64_IMAGE = "base64_image"
    BLOB = "blob"
    IMAGE_URL = "image_url"
    JSON_OBJECT = "json_object"
    MIXED = "mixed"
    OTHER = "other"
    TEXT = "text"
    TOOL_RESULT = "tool_result"

class MessageTemplate(Model):
    id = UUIDField(primary_key=True, null=False)
    role = EnumField(enum_class=MessageRole, null=False, default='user')
    type = EnumField(enum_class=MessageType, null=False, default='text')
    created_at = DateTimeField(null=False)
    content = TextField()
    _inverse_foreign_keys = {'message_brokers': {'from_model': 'MessageBroker', 'from_field': 'message_id', 'referenced_field': 'id', 'related_name': 'message_brokers'}, 'recipe_messages': {'from_model': 'RecipeMessage', 'from_field': 'message_id', 'referenced_field': 'id', 'related_name': 'recipe_messages'}}

class RegisteredFunction(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    module_path = CharField(null=False)
    class_name = CharField()
    description = TextField()
    return_broker = ForeignKey(to_model=Broker, to_column='id', )
    _inverse_foreign_keys = {'system_functions': {'from_model': 'SystemFunction', 'from_field': 'rf_id', 'referenced_field': 'id', 'related_name': 'system_functions'}, 'args': {'from_model': 'Arg', 'from_field': 'registered_function', 'referenced_field': 'id', 'related_name': 'args'}}

class ScrapeCycleRun(Model):
    id = UUIDField(primary_key=True, null=False)
    scrape_cycle_tracker_id = ForeignKey(to_model=ScrapeCycleTracker, to_column='id', null=False)
    run_number = SmallIntegerField(null=False)
    completed_at = DateTimeField()
    allow_pattern = CharField()
    disallow_patterns = JSONBField()
    user_id = UUIDField()
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=False)
    _inverse_foreign_keys = {'scrape_tasks': {'from_model': 'ScrapeTask', 'from_field': 'scrape_cycle_run_id', 'referenced_field': 'id', 'related_name': 'scrape_tasks'}, 'scrape_parsed_pages': {'from_model': 'ScrapeParsedPage', 'from_field': 'scrape_cycle_run_id', 'referenced_field': 'id', 'related_name': 'scrape_parsed_pages'}}

class ScrapeOverride(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    config_type = CharField(null=False)
    selector_type = CharField()
    match_type = CharField()
    action = CharField(null=False)
    user_id = ForeignKey(to_model=Users, to_column='id', )
    created_at = DateTimeField()
    updated_at = DateTimeField()
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=True)
    _inverse_foreign_keys = {'scrape_override_values': {'from_model': 'ScrapeOverrideValue', 'from_field': 'scrape_override_id', 'referenced_field': 'id', 'related_name': 'scrape_override_values'}, 'scrape_path_pattern_overrides': {'from_model': 'ScrapePathPatternOverride', 'from_field': 'scrape_override_id', 'referenced_field': 'id', 'related_name': 'scrape_path_pattern_overrides'}}

class ScrapeTask(Model):
    id = UUIDField(primary_key=True, null=False)
    target_url = CharField(null=False)
    page_name = CharField(null=False)
    scrape_domain_id = ForeignKey(to_model=ScrapeDomain, to_column='id', )
    parent_task = UUIDField()
    attempts_left = SmallIntegerField(null=False)
    scrape_mode = CharField(null=False, default='normal')
    interaction_config = JSONBField()
    scrape_job_id = ForeignKey(to_model=ScrapeJob, to_column='id', )
    priority = SmallIntegerField()
    discovered_links = JSONBField()
    spawned_concurrent_tasks = BooleanField(default=False)
    scrape_cycle_run_id = ForeignKey(to_model=ScrapeCycleRun, to_column='id', )
    failure_reason = CharField()
    scrape_status = CharField()
    parse_status = CharField()
    cancel_message = CharField()
    user_id = ForeignKey(to_model=Users, to_column='id', )
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=False)
    _inverse_foreign_keys = {'scrape_task_responses': {'from_model': 'ScrapeTaskResponse', 'from_field': 'scrape_task_id', 'referenced_field': 'id', 'related_name': 'scrape_task_responses'}, 'scrape_parsed_pages': {'from_model': 'ScrapeParsedPage', 'from_field': 'scrape_task_id', 'referenced_field': 'id', 'related_name': 'scrape_parsed_pages'}}

class SystemFunction(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    description = TextField()
    sample = TextField()
    input_params = JSONBField()
    output_options = JSONBField()
    rf_id = ForeignKey(to_model=RegisteredFunction, to_column='id', null=False)
    _inverse_foreign_keys = {'tools': {'from_model': 'Tool', 'from_field': 'system_function', 'referenced_field': 'id', 'related_name': 'tools'}, 'recipe_functions': {'from_model': 'RecipeFunction', 'from_field': 'function', 'referenced_field': 'id', 'related_name': 'recipe_functions'}}

class UserTables(Model):
    id = UUIDField(primary_key=True, null=False)
    table_name = CharField(null=False, max_length=255, unique=True)
    description = TextField()
    version = IntegerField(null=False, default='1')
    user_id = ForeignKey(to_model=Users, to_column='id', null=False, unique=True)
    is_public = BooleanField(null=False, default=False)
    authenticated_read = BooleanField(null=False, default=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    _inverse_foreign_keys = {'table_fieldss': {'from_model': 'TableFields', 'from_field': 'table_id', 'referenced_field': 'id', 'related_name': 'table_fieldss'}, 'table_datas': {'from_model': 'TableData', 'from_field': 'table_id', 'referenced_field': 'id', 'related_name': 'table_datas'}}

class AiSettings(Model):
    id = UUIDField(primary_key=True, null=False)
    ai_endpoint = ForeignKey(to_model=AiEndpoint, to_column='id', default='4bedf336-b274-4cdb-8202-59fd282ae6a0')
    ai_provider = ForeignKey(to_model=AiProvider, to_column='id', default='99fa34b1-4c36-427f-ab73-cc56f1d5c4a0')
    ai_model = ForeignKey(to_model=AiModel, to_column='id', default='dd45b76e-f470-4765-b6c4-1a275d7860bf')
    temperature = FloatField(default='0.25')
    max_tokens = SmallIntegerField(default='3000')
    top_p = SmallIntegerField(default='1')
    frequency_penalty = SmallIntegerField(default='0')
    presence_penalty = SmallIntegerField(default='0')
    stream = BooleanField(default=True)
    response_format = CharField(default='text')
    size = CharField()
    quality = CharField()
    count = SmallIntegerField(default='1')
    audio_voice = CharField()
    audio_format = CharField()
    modalities = JSONBField(default={})
    tools = JSONBField(default={})
    preset_name = CharField()
    _inverse_foreign_keys = {'ai_agents': {'from_model': 'AiAgent', 'from_field': 'ai_settings_id', 'referenced_field': 'id', 'related_name': 'ai_agents'}}

class AudioLabel(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    name = CharField(null=False)
    description = TextField()
    _inverse_foreign_keys = {'audio_recordings': {'from_model': 'AudioRecording', 'from_field': 'label', 'referenced_field': 'id', 'related_name': 'audio_recordings'}}

class Category(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False, unique=True)
    description = TextField()
    slug = CharField(null=False)
    icon = CharField(default='Briefcase')
    created_at = DateTimeField(null=False)
    _inverse_foreign_keys = {'subcategorys': {'from_model': 'Subcategory', 'from_field': 'category_id', 'referenced_field': 'id', 'related_name': 'subcategorys'}}

class CompiledRecipe(Model):
    id = UUIDField(primary_key=True, null=False)
    recipe_id = ForeignKey(to_model=Recipe, to_column='id', )
    version = SmallIntegerField()
    compiled_recipe = JSONBField(null=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    user_id = ForeignKey(to_model=Users, to_column='id', )
    is_public = BooleanField(null=False, default=False)
    authenticated_read = BooleanField(null=False, default=False)
    _inverse_foreign_keys = {'applets': {'from_model': 'Applet', 'from_field': 'compiled_recipe_id', 'referenced_field': 'id', 'related_name': 'applets'}}

class Conversation(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField()
    user_id = ForeignKey(to_model=Users, to_column='id', )
    metadata = JSONBField()
    label = CharField(default='New Conversation')
    is_public = BooleanField(default=False)
    description = TextField()
    keywords = JSONBField()
    _inverse_foreign_keys = {'messages': {'from_model': 'Message', 'from_field': 'conversation_id', 'referenced_field': 'id', 'related_name': 'messages'}}

class DisplayOption(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField()
    default_params = JSONBField()
    customizable_params = JSONBField()
    additional_params = JSONBField()
    _inverse_foreign_keys = {'recipe_displays': {'from_model': 'RecipeDisplay', 'from_field': 'display', 'referenced_field': 'id', 'related_name': 'recipe_displays'}}

class FlashcardSets(Model):
    set_id = UUIDField(primary_key=True, null=False)
    user_id = ForeignKey(to_model=Users, to_column='id', null=False)
    name = TextField(null=False)
    created_at = DateTimeField()
    updated_at = DateTimeField()
    shared_with = UUIDArrayField()
    public = BooleanField(default=False)
    topic = TextField()
    lesson = TextField()
    difficulty = TextField()
    audio_overview = TextField()
    _inverse_foreign_keys = {'flashcard_set_relationss': {'from_model': 'FlashcardSetRelations', 'from_field': 'set_id', 'referenced_field': 'set_id', 'related_name': 'flashcard_set_relationss'}}

class Processor(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    depends_default = ForeignKey(to_model='Processor', to_column='id', )
    default_extractors = JSONBField()
    params = JSONBField()
    _inverse_foreign_keys = {'recipe_processors': {'from_model': 'RecipeProcessor', 'from_field': 'processor', 'referenced_field': 'id', 'related_name': 'recipe_processors'}}

class ScrapeConfiguration(Model):
    id = UUIDField(primary_key=True, null=False)
    scrape_mode = CharField(null=False)
    interaction_settings_id = UUIDField()
    scrape_path_pattern_id = ForeignKey(to_model=ScrapePathPattern, to_column='id', null=False)
    is_active = BooleanField(default=True)
    user_id = ForeignKey(to_model=Users, to_column='id', )
    created_at = DateTimeField()
    updated_at = DateTimeField()
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=True)
    _inverse_foreign_keys = {'scrape_parsed_pages': {'from_model': 'ScrapeParsedPage', 'from_field': 'scrape_configuration_id', 'referenced_field': 'id', 'related_name': 'scrape_parsed_pages'}}

class ScrapePathPatternOverride(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    scrape_path_pattern_id = ForeignKey(to_model=ScrapePathPattern, to_column='id', null=False)
    scrape_override_id = ForeignKey(to_model=ScrapeOverride, to_column='id', null=False)
    is_active = BooleanField(null=False, default=True)
    user_id = ForeignKey(to_model=Users, to_column='id', )
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    is_public = BooleanField(null=False, default=False)
    authenticated_read = BooleanField(null=False, default=True)
    _inverse_foreign_keys = {'scrape_parsed_pages': {'from_model': 'ScrapeParsedPage', 'from_field': 'scrape_path_pattern_override_id', 'referenced_field': 'id', 'related_name': 'scrape_parsed_pages'}}

class ScrapeTaskResponse(Model):
    id = UUIDField(primary_key=True, null=False)
    scrape_task_id = ForeignKey(to_model=ScrapeTask, to_column='id', null=False)
    failure_reason = CharField()
    status_code = SmallIntegerField()
    content_path = CharField(null=False)
    content_size = SmallIntegerField()
    content_type = CharField()
    response_headers = JSONBField(null=False)
    response_url = CharField(null=False)
    error_log = TextField()
    user_id = ForeignKey(to_model=Users, to_column='id', )
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=False)
    _inverse_foreign_keys = {'scrape_parsed_pages': {'from_model': 'ScrapeParsedPage', 'from_field': 'scrape_task_response_id', 'referenced_field': 'id', 'related_name': 'scrape_parsed_pages'}}

class Subcategory(Model):
    id = UUIDField(primary_key=True, null=False)
    category_id = ForeignKey(to_model=Category, to_column='id', null=False)
    name = CharField(null=False)
    description = CharField()
    slug = CharField()
    icon = CharField(default='Target')
    features = JSONBField(null=False)
    created_at = DateTimeField(null=False)
    _inverse_foreign_keys = {'applets': {'from_model': 'Applet', 'from_field': 'subcategory_id', 'referenced_field': 'id', 'related_name': 'applets'}}

class Tool(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    source = JSONBField(null=False, default={'host': 'ame'})
    description = TextField()
    parameters = JSONBField()
    required_args = JSONBField()
    system_function = ForeignKey(to_model=SystemFunction, to_column='id', )
    additional_params = JSONBField()
    _inverse_foreign_keys = {'recipe_tools': {'from_model': 'RecipeTool', 'from_field': 'tool', 'referenced_field': 'id', 'related_name': 'recipe_tools'}}

class Transformer(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField()
    input_params = JSONBField()
    output_params = JSONBField()
    _inverse_foreign_keys = {'actions': {'from_model': 'Action', 'from_field': 'transformer', 'referenced_field': 'id', 'related_name': 'actions'}}

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
    _inverse_foreign_keys = {'wc_reports': {'from_model': 'WcReport', 'from_field': 'claim_id', 'referenced_field': 'id', 'related_name': 'wc_reports'}}



class WcFingerType(str, Enum):
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
    finger_type = EnumField(enum_class=WcFingerType, )
    _inverse_foreign_keys = {'wc_injurys': {'from_model': 'WcInjury', 'from_field': 'impairment_definition_id', 'referenced_field': 'id', 'related_name': 'wc_injurys'}}

class WcReport(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    claim_id = ForeignKey(to_model=WcClaim, to_column='id', null=False)
    final_rating = SmallIntegerField()
    left_side_total = SmallIntegerField()
    right_side_total = SmallIntegerField()
    default_side_total = SmallIntegerField()
    compensation_amount = FloatField()
    compensation_weeks = SmallIntegerField()
    compensation_days = SmallIntegerField()
    _inverse_foreign_keys = {'wc_injurys': {'from_model': 'WcInjury', 'from_field': 'report_id', 'referenced_field': 'id', 'related_name': 'wc_injurys'}}

class Action(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False, max_length=255)
    matrix = ForeignKey(to_model=AutomationMatrix, to_column='id', null=False)
    transformer = ForeignKey(to_model=Transformer, to_column='id', )
    node_type = CharField(null=False, max_length=50)
    reference_id = UUIDField(null=False)
    _inverse_foreign_keys = {}

class Admins(Model):
    user_id = ForeignKey(to_model=Users, to_column='id', primary_key=True, null=False)
    created_at = DateTimeField()
    _inverse_foreign_keys = {}

class AiAgent(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    recipe_id = ForeignKey(to_model=Recipe, to_column='id', )
    ai_settings_id = ForeignKey(to_model=AiSettings, to_column='id', )
    system_message_override = TextField()
    _inverse_foreign_keys = {}

class AiModelEndpoint(Model):
    id = UUIDField(primary_key=True, null=False)
    ai_model_id = ForeignKey(to_model=AiModel, to_column='id', )
    ai_endpoint_id = ForeignKey(to_model=AiEndpoint, to_column='id', )
    available = BooleanField(null=False, default=True)
    endpoint_priority = SmallIntegerField()
    configuration = JSONBField(default={})
    notes = TextField()
    created_at = DateTimeField(null=False)
    _inverse_foreign_keys = {}

class AiTrainingData(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField()
    user_id = ForeignKey(to_model=Users, to_column='id', )
    is_public = BooleanField(default=False)
    system_prompt = TextField()
    user_query = TextField()
    thinking_content = TextField()
    response_content = TextField()
    reflection_content = TextField()
    quality_score = DecimalField()
    source = TextField()
    metadata = JSONBField()
    questions_thinking = TextField()
    questions_content = TextField()
    structured_questions = JSONBField()
    reflection_thinking = TextField()
    _inverse_foreign_keys = {}



class AppType(str, Enum):
    OTHER = "other"
    RECIPE = "recipe"
    WORKFLOW = "workflow"

class Applet(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False, unique=True)
    description = TextField()
    creator = CharField()
    type = EnumField(enum_class=AppType, null=False)
    compiled_recipe_id = ForeignKey(to_model=CompiledRecipe, to_column='id', )
    slug = CharField(null=False, unique=True)
    created_at = DateTimeField(null=False)
    user_id = UUIDField()
    is_public = BooleanField()
    data_source_config = JSONBField()
    result_component_config = JSONBField()
    next_step_config = JSONBField()
    subcategory_id = ForeignKey(to_model=Subcategory, to_column='id', )
    cta_text = CharField(default='Get Results')
    theme = CharField(default='default')
    _inverse_foreign_keys = {}



class DataType(str, Enum):
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
    required = BooleanField(default=True)
    default = TextField()
    data_type = EnumField(enum_class=DataType, default='str')
    ready = BooleanField(default=False)
    registered_function = ForeignKey(to_model=RegisteredFunction, to_column='id', )
    _inverse_foreign_keys = {}

class AudioRecording(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    user_id = ForeignKey(to_model=Users, to_column='id', null=False)
    name = CharField(null=False)
    label = ForeignKey(to_model=AudioLabel, to_column='id', )
    file_url = CharField(null=False)
    duration = DecimalField()
    local_path = CharField()
    size = DecimalField()
    is_public = BooleanField(null=False, default=False)
    _inverse_foreign_keys = {}

class AudioRecordingUsers(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    first_name = TextField()
    last_name = TextField()
    email = TextField()
    _inverse_foreign_keys = {}



class DataSource(str, Enum):
    API = "api"
    CHANCE = "chance"
    DATABASE = "database"
    ENVIRONMENT = "environment"
    FILE = "file"
    FUNCTION = "function"
    GENERATED_DATA = "generated_data"
    NONE = "none"
    USER_INPUT = "user_input"

class DataDestination(str, Enum):
    API_RESPONSE = "api_response"
    DATABASE = "database"
    FILE = "file"
    FUNCTION = "function"
    USER_OUTPUT = "user_output"

class AutomationBoundaryBroker(Model):
    id = UUIDField(primary_key=True, null=False)
    matrix = ForeignKey(to_model=AutomationMatrix, to_column='id', )
    broker = ForeignKey(to_model=Broker, to_column='id', )
    spark_source = EnumField(enum_class=DataSource, )
    beacon_destination = EnumField(enum_class=DataDestination, )
    _inverse_foreign_keys = {}

class BrokerValue(Model):
    id = UUIDField(primary_key=True, null=False)
    user_id = ForeignKey(to_model=Users, to_column='id', )
    data_broker = ForeignKey(to_model=DataBroker, to_column='id', )
    data = JSONBField(default={'value': None})
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
    is_read = BooleanField(default=False)
    _inverse_foreign_keys = {}



class DataType(str, Enum):
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
    output_type = EnumField(enum_class=DataType, )
    default_identifier = CharField()
    default_index = SmallIntegerField()
    _inverse_foreign_keys = {}

class FileStructure(Model):
    id = IntegerField(primary_key=True, null=False, default='file_structure_id_seq')
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
    flashcard_id = ForeignKey(to_model=FlashcardData, to_column='id', )
    user_id = ForeignKey(to_model=Users, to_column='id', null=False)
    review_count = SmallIntegerField(default='0')
    correct_count = SmallIntegerField(default='0')
    incorrect_count = SmallIntegerField(default='0')
    created_at = DateTimeField()
    updated_at = DateTimeField()
    _inverse_foreign_keys = {}

class FlashcardImages(Model):
    id = UUIDField(primary_key=True, null=False)
    flashcard_id = ForeignKey(to_model=FlashcardData, to_column='id', )
    file_path = TextField(null=False)
    file_name = TextField(null=False)
    mime_type = TextField(null=False)
    size = IntegerField(null=False)
    created_at = DateTimeField()
    _inverse_foreign_keys = {}

class FlashcardSetRelations(Model):
    flashcard_id = ForeignKey(to_model=FlashcardData, to_column='id', primary_key=True, null=False)
    set_id = ForeignKey(to_model=FlashcardSets, to_column='set_id', primary_key=True, null=False)
    order = IntegerField()
    _inverse_foreign_keys = {}

class FullSpectrumPositions(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField()
    title = CharField()
    description = TextField()
    alternate_titles = TextField()
    qualifications = TextField()
    sizzle_questions = TextField()
    red_flags = TextField()
    additional_details = TextField()
    _inverse_foreign_keys = {}



class MessageRole(str, Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    USER = "user"

class MessageType(str, Enum):
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
    conversation_id = ForeignKey(to_model=Conversation, to_column='id', null=False)
    role = EnumField(enum_class=MessageRole, null=False)
    content = TextField()
    type = EnumField(enum_class=MessageType, null=False)
    display_order = SmallIntegerField()
    system_order = SmallIntegerField()
    created_at = DateTimeField(null=False)
    metadata = JSONBField()
    user_id = ForeignKey(to_model=Users, to_column='id', )
    is_public = BooleanField(default=False)
    _inverse_foreign_keys = {}

class MessageBroker(Model):
    id = UUIDField(primary_key=True, null=False)
    message_id = ForeignKey(to_model=MessageTemplate, to_column='id', null=False)
    broker_id = ForeignKey(to_model=DataBroker, to_column='id', null=False)
    default_value = TextField()
    default_component = ForeignKey(to_model=DataInputComponent, to_column='id', )
    _inverse_foreign_keys = {}



class OrgRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    OWNER = "owner"

class OrganizationInvitations(Model):
    id = UUIDField(primary_key=True, null=False)
    organization_id = ForeignKey(to_model=Organizations, to_column='id', null=False, unique=True)
    email = TextField(null=False, unique=True)
    token = TextField(null=False, unique=True)
    role = EnumField(enum_class=OrgRole, null=False, default='member')
    invited_at = DateTimeField()
    invited_by = ForeignKey(to_model=Users, to_column='id', )
    expires_at = DateTimeField(null=False)
    _inverse_foreign_keys = {}



class OrgRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    OWNER = "owner"

class OrganizationMembers(Model):
    id = UUIDField(primary_key=True, null=False)
    organization_id = ForeignKey(to_model=Organizations, to_column='id', null=False, unique=True)
    user_id = ForeignKey(to_model=Users, to_column='id', null=False, unique=True)
    role = EnumField(enum_class=OrgRole, null=False, default='member')
    joined_at = DateTimeField()
    invited_by = ForeignKey(to_model=Users, to_column='id', )
    _inverse_foreign_keys = {}



class ResourceType(str, Enum):
    APPLET = "applet"
    BROKER_VALUE = "broker_value"
    CONVERSATION = "conversation"
    DOCUMENT = "document"
    MESSAGE = "message"
    ORGANIZATION = "organization"
    RECIPE = "recipe"
    SCRAPE_DOMAIN = "scrape_domain"
    WORKFLOW = "workflow"

class PermissionLevel(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    VIWWER = "viwwer"

class Permissions(Model):
    id = UUIDField(primary_key=True, null=False)
    resource_type = EnumField(enum_class=ResourceType, null=False, unique=True)
    resource_id = UUIDField(null=False, unique=True)
    granted_to_user_id = ForeignKey(to_model=Users, to_column='id', unique=True)
    granted_to_organization_id = ForeignKey(to_model=Organizations, to_column='id', unique=True)
    is_public = BooleanField(default=False)
    permission_level = EnumField(enum_class=PermissionLevel, null=False, default='viewer')
    created_at = DateTimeField()
    created_by = ForeignKey(to_model=Users, to_column='id', )
    _inverse_foreign_keys = {}

class ProjectMembers(Model):
    id = UUIDField(primary_key=True, null=False)
    project_id = ForeignKey(to_model=Projects, to_column='id', unique=True)
    user_id = ForeignKey(to_model=Users, to_column='id', unique=True)
    role = TextField(null=False)
    created_at = DateTimeField()
    _inverse_foreign_keys = {}



class BrokerRole(str, Enum):
    INPUT_BROKER = "input_broker"
    OUTPUT_BROKER = "output_broker"

class RecipeBroker(Model):
    id = UUIDField(primary_key=True, null=False)
    recipe = ForeignKey(to_model=Recipe, to_column='id', null=False)
    broker = ForeignKey(to_model=Broker, to_column='id', null=False)
    broker_role = EnumField(enum_class=BrokerRole, null=False)
    required = BooleanField(default=True)
    _inverse_foreign_keys = {}

class RecipeDisplay(Model):
    id = UUIDField(primary_key=True, null=False)
    recipe = ForeignKey(to_model=Recipe, to_column='id', null=False)
    display = ForeignKey(to_model=DisplayOption, to_column='id', null=False)
    priority = SmallIntegerField(default='1')
    display_settings = JSONBField()
    _inverse_foreign_keys = {}



class FunctionRole(str, Enum):
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
    recipe = ForeignKey(to_model=Recipe, to_column='id', null=False)
    function = ForeignKey(to_model=SystemFunction, to_column='id', null=False)
    role = EnumField(enum_class=FunctionRole, null=False)
    params = JSONBField()
    _inverse_foreign_keys = {}

class RecipeMessage(Model):
    id = UUIDField(primary_key=True, null=False)
    message_id = ForeignKey(to_model=MessageTemplate, to_column='id', null=False, unique=True)
    recipe_id = ForeignKey(to_model=Recipe, to_column='id', null=False, unique=True)
    order = SmallIntegerField(null=False, default='1')
    _inverse_foreign_keys = {}

class RecipeMessageReorderQueue(Model):
    recipe_id = UUIDField(primary_key=True, null=False)
    last_modified = DateTimeField()
    _inverse_foreign_keys = {}



class ModelRole(str, Enum):
    PRIMARY_MODEL = "primary_model"
    TRIAL_MODEL = "trial_model"
    VERIFIED_MODEL = "verified_model"

class RecipeModel(Model):
    id = UUIDField(primary_key=True, null=False)
    recipe = ForeignKey(to_model=Recipe, to_column='id', null=False)
    ai_model = ForeignKey(to_model=AiModel, to_column='id', null=False)
    role = EnumField(enum_class=ModelRole, null=False, default='primary_model')
    priority = SmallIntegerField(default='1')
    _inverse_foreign_keys = {}

class RecipeProcessor(Model):
    id = UUIDField(primary_key=True, null=False)
    recipe = ForeignKey(to_model=Recipe, to_column='id', null=False)
    processor = ForeignKey(to_model=Processor, to_column='id', null=False)
    params = JSONBField()
    _inverse_foreign_keys = {}

class RecipeTool(Model):
    id = UUIDField(primary_key=True, null=False)
    recipe = ForeignKey(to_model=Recipe, to_column='id', null=False)
    tool = ForeignKey(to_model=Tool, to_column='id', null=False)
    params = JSONBField()
    _inverse_foreign_keys = {}

class ScrapeBaseConfig(Model):
    id = UUIDField(primary_key=True, null=False)
    selector_type = CharField(null=False, unique=True)
    exact = JSONBField()
    partial = JSONBField()
    regex = JSONBField()
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=False)
    _inverse_foreign_keys = {}

class ScrapeDomainDisallowedNotes(Model):
    id = UUIDField(primary_key=True, null=False)
    scrape_domain_id = ForeignKey(to_model=ScrapeDomain, to_column='id', null=False)
    notes = TextField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=False)
    _inverse_foreign_keys = {}

class ScrapeDomainNotes(Model):
    id = UUIDField(primary_key=True, null=False)
    scrape_domain_id = ForeignKey(to_model=ScrapeDomain, to_column='id', )
    notes = TextField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=False)
    _inverse_foreign_keys = {}

class ScrapeDomainQuickScrapeSettings(Model):
    id = UUIDField(primary_key=True, null=False)
    scrape_domain_id = ForeignKey(to_model=ScrapeDomain, to_column='id', null=False)
    enabled = BooleanField(null=False, default=True)
    proxy_type = CharField(default='datacenter')
    created_at = DateTimeField()
    updated_at = DateTimeField()
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=True)
    _inverse_foreign_keys = {}

class ScrapeDomainRobotsTxt(Model):
    id = UUIDField(primary_key=True, null=False)
    scrape_domain_id = ForeignKey(to_model=ScrapeDomain, to_column='id', )
    robots_txt = TextField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=False)
    _inverse_foreign_keys = {}

class ScrapeDomainSitemap(Model):
    id = UUIDField(primary_key=True, null=False)
    scrape_domain_id = ForeignKey(to_model=ScrapeDomain, to_column='id', )
    sitemap = TextField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=False)
    _inverse_foreign_keys = {}

class ScrapeOverrideValue(Model):
    id = UUIDField(primary_key=True, null=False)
    value = CharField(null=False)
    scrape_override_id = ForeignKey(to_model=ScrapeOverride, to_column='id', null=False)
    user_id = ForeignKey(to_model=Users, to_column='id', )
    created_at = DateTimeField()
    updated_at = DateTimeField()
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=True)
    _inverse_foreign_keys = {}

class ScrapeParsedPage(Model):
    id = UUIDField(primary_key=True, null=False)
    page_name = CharField(null=False)
    validity = CharField(null=False)
    remote_path = CharField()
    local_path = CharField()
    scrape_path_pattern_cache_policy_id = ForeignKey(to_model=ScrapePathPatternCachePolicy, to_column='id', )
    scrape_task_id = ForeignKey(to_model=ScrapeTask, to_column='id', )
    scrape_task_response_id = ForeignKey(to_model=ScrapeTaskResponse, to_column='id', )
    scrape_cycle_run_id = ForeignKey(to_model=ScrapeCycleRun, to_column='id', )
    scrape_cycle_tracker_id = ForeignKey(to_model=ScrapeCycleTracker, to_column='id', )
    scrape_configuration_id = ForeignKey(to_model=ScrapeConfiguration, to_column='id', )
    scrape_path_pattern_override_id = ForeignKey(to_model=ScrapePathPatternOverride, to_column='id', )
    scraped_at = DateTimeField()
    user_id = ForeignKey(to_model=Users, to_column='id', )
    created_at = DateTimeField()
    updated_at = DateTimeField()
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=False)
    expires_at = DateTimeField()
    _inverse_foreign_keys = {}

class ScrapeQuickFailureLog(Model):
    id = UUIDField(primary_key=True, null=False)
    scrape_domain_id = ForeignKey(to_model=ScrapeDomain, to_column='id', )
    domain_name = CharField()
    target_url = CharField(null=False)
    failure_reason = CharField()
    error_log = TextField()
    user_id = ForeignKey(to_model=Users, to_column='id', )
    created_at = DateTimeField()
    updated_at = DateTimeField()
    is_public = BooleanField(default=False)
    authenticated_read = BooleanField(default=False)
    _inverse_foreign_keys = {}

class TableData(Model):
    id = UUIDField(primary_key=True, null=False, unique=True)
    table_id = ForeignKey(to_model=UserTables, to_column='id', null=False, unique=True)
    data = JSONBField(null=False)
    user_id = ForeignKey(to_model=Users, to_column='id', null=False)
    is_public = BooleanField(null=False, default=False)
    authenticated_read = BooleanField(null=False, default=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    _inverse_foreign_keys = {}



class FieldDataType(str, Enum):
    ARRAY = "array"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    INTEGER = "integer"
    JSON = "json"
    NUMBER = "number"
    STRING = "string"

class TableFields(Model):
    id = UUIDField(primary_key=True, null=False)
    table_id = ForeignKey(to_model=UserTables, to_column='id', null=False, unique=True)
    field_name = CharField(null=False, max_length=100, unique=True)
    display_name = CharField(null=False, max_length=255)
    data_type = EnumField(enum_class=FieldDataType, null=False, default='string')
    field_order = IntegerField(null=False, default='0')
    is_required = BooleanField(null=False, default=False)
    default_value = JSONBField()
    validation_rules = JSONBField()
    user_id = ForeignKey(to_model=Users, to_column='id', null=False)
    is_public = BooleanField(null=False, default=False)
    authenticated_read = BooleanField(null=False, default=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    _inverse_foreign_keys = {}

class TaskAssignments(Model):
    id = UUIDField(primary_key=True, null=False)
    task_id = ForeignKey(to_model=Tasks, to_column='id', unique=True)
    user_id = ForeignKey(to_model=Users, to_column='id', unique=True)
    assigned_by = ForeignKey(to_model=Users, to_column='id', )
    assigned_at = DateTimeField()
    _inverse_foreign_keys = {}

class TaskAttachments(Model):
    id = UUIDField(primary_key=True, null=False)
    task_id = ForeignKey(to_model=Tasks, to_column='id', )
    file_name = TextField(null=False)
    file_type = TextField()
    file_size = IntegerField()
    file_path = TextField(null=False)
    uploaded_by = ForeignKey(to_model=Users, to_column='id', )
    uploaded_at = DateTimeField()
    _inverse_foreign_keys = {}

class TaskComments(Model):
    id = UUIDField(primary_key=True, null=False)
    task_id = ForeignKey(to_model=Tasks, to_column='id', )
    user_id = ForeignKey(to_model=Users, to_column='id', )
    content = TextField(null=False)
    created_at = DateTimeField()
    updated_at = DateTimeField()
    _inverse_foreign_keys = {}

class UserPreferences(Model):
    user_id = ForeignKey(to_model=Users, to_column='id', primary_key=True, null=False)
    preferences = JSONBField(null=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    _inverse_foreign_keys = {}



class WcSide(str, Enum):
    DEFAULT = "default"
    LEFT = "left"
    RIGHT = "right"

class WcInjury(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    report_id = ForeignKey(to_model=WcReport, to_column='id', )
    impairment_definition_id = ForeignKey(to_model=WcImpairmentDefinition, to_column='id', )
    digit = SmallIntegerField()
    le = SmallIntegerField()
    side = EnumField(enum_class=WcSide, default='default')
    ue = SmallIntegerField()
    wpi = SmallIntegerField()
    pain = SmallIntegerField(default='0')
    industrial = SmallIntegerField(default='100')
    rating = SmallIntegerField()
    formula = CharField()
    updated_at = DateTimeField()
    _inverse_foreign_keys = {}


model_registry.register_all(
[
        Action,
        Admins,
        AiAgent,
        AiEndpoint,
        AiModel,
        AiModelEndpoint,
        AiProvider,
        AiSettings,
        AiTrainingData,
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
        FullSpectrumPositions,
        Message,
        MessageBroker,
        MessageTemplate,
        OrganizationInvitations,
        OrganizationMembers,
        Organizations,
        Permissions,
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
        ScrapeBaseConfig,
        ScrapeCachePolicy,
        ScrapeConfiguration,
        ScrapeCycleRun,
        ScrapeCycleTracker,
        ScrapeDomain,
        ScrapeDomainDisallowedNotes,
        ScrapeDomainNotes,
        ScrapeDomainQuickScrapeSettings,
        ScrapeDomainRobotsTxt,
        ScrapeDomainSitemap,
        ScrapeJob,
        ScrapeOverride,
        ScrapeOverrideValue,
        ScrapeParsedPage,
        ScrapePathPattern,
        ScrapePathPatternCachePolicy,
        ScrapePathPatternOverride,
        ScrapeQuickFailureLog,
        ScrapeTask,
        ScrapeTaskResponse,
        Subcategory,
        SystemFunction,
        TableData,
        TableFields,
        TaskAssignments,
        TaskAttachments,
        TaskComments,
        Tasks,
        Tool,
        Transformer,
        UserPreferences,
        UserTables,
        WcClaim,
        WcImpairmentDefinition,
        WcInjury,
        WcReport,
        Users
    ]
)



@dataclass
class RecipeDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class RecipeManager(BaseManager):
    def __init__(self):
        super().__init__(Recipe, RecipeDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe):
        pass
    


@dataclass
class ScrapeDomainDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeDomainManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeDomain, ScrapeDomainDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_domain):
        pass
    


@dataclass
class ScrapeJobDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeJobManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeJob, ScrapeJobDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_job):
        pass
    


@dataclass
class AiProviderDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class AiProviderManager(BaseManager):
    def __init__(self):
        super().__init__(AiProvider, AiProviderDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_provider):
        pass
    


@dataclass
class DataInputComponentDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class DataInputComponentManager(BaseManager):
    def __init__(self):
        super().__init__(DataInputComponent, DataInputComponentDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, data_input_component):
        pass
    


@dataclass
class ScrapeCachePolicyDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeCachePolicyManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeCachePolicy, ScrapeCachePolicyDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_cache_policy):
        pass
    


@dataclass
class ScrapePathPatternDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapePathPatternManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapePathPattern, ScrapePathPatternDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_path_pattern):
        pass
    


@dataclass
class ScrapePathPatternCachePolicyDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapePathPatternCachePolicyManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapePathPatternCachePolicy, ScrapePathPatternCachePolicyDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_path_pattern_cache_policy):
        pass
    


@dataclass
class AiModelDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class AiModelManager(BaseManager):
    def __init__(self):
        super().__init__(AiModel, AiModelDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_model):
        pass
    


@dataclass
class BrokerDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class BrokerManager(BaseManager):
    def __init__(self):
        super().__init__(Broker, BrokerDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, broker):
        pass
    


@dataclass
class DataOutputComponentDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class DataOutputComponentManager(BaseManager):
    def __init__(self):
        super().__init__(DataOutputComponent, DataOutputComponentDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, data_output_component):
        pass
    


@dataclass
class FlashcardDataDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class FlashcardDataManager(BaseManager):
    def __init__(self):
        super().__init__(FlashcardData, FlashcardDataDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, flashcard_data):
        pass
    


@dataclass
class OrganizationsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class OrganizationsManager(BaseManager):
    def __init__(self):
        super().__init__(Organizations, OrganizationsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, organizations):
        pass
    


@dataclass
class ProjectsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ProjectsManager(BaseManager):
    def __init__(self):
        super().__init__(Projects, ProjectsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, projects):
        pass
    


@dataclass
class ScrapeCycleTrackerDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeCycleTrackerManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeCycleTracker, ScrapeCycleTrackerDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_cycle_tracker):
        pass
    


@dataclass
class TasksDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class TasksManager(BaseManager):
    def __init__(self):
        super().__init__(Tasks, TasksDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, tasks):
        pass
    


@dataclass
class AiEndpointDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class AiEndpointManager(BaseManager):
    def __init__(self):
        super().__init__(AiEndpoint, AiEndpointDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_endpoint):
        pass
    


@dataclass
class AutomationMatrixDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class AutomationMatrixManager(BaseManager):
    def __init__(self):
        super().__init__(AutomationMatrix, AutomationMatrixDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, automation_matrix):
        pass
    


@dataclass
class DataBrokerDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class DataBrokerManager(BaseManager):
    def __init__(self):
        super().__init__(DataBroker, DataBrokerDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, data_broker):
        pass
    


@dataclass
class MessageTemplateDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class MessageTemplateManager(BaseManager):
    def __init__(self):
        super().__init__(MessageTemplate, MessageTemplateDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, message_template):
        pass
    


@dataclass
class RegisteredFunctionDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class RegisteredFunctionManager(BaseManager):
    def __init__(self):
        super().__init__(RegisteredFunction, RegisteredFunctionDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, registered_function):
        pass
    


@dataclass
class ScrapeCycleRunDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeCycleRunManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeCycleRun, ScrapeCycleRunDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_cycle_run):
        pass
    


@dataclass
class ScrapeOverrideDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeOverrideManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeOverride, ScrapeOverrideDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_override):
        pass
    


@dataclass
class ScrapeTaskDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeTaskManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeTask, ScrapeTaskDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_task):
        pass
    


@dataclass
class SystemFunctionDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class SystemFunctionManager(BaseManager):
    def __init__(self):
        super().__init__(SystemFunction, SystemFunctionDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, system_function):
        pass
    


@dataclass
class UserTablesDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class UserTablesManager(BaseManager):
    def __init__(self):
        super().__init__(UserTables, UserTablesDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, user_tables):
        pass
    


@dataclass
class AiSettingsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class AiSettingsManager(BaseManager):
    def __init__(self):
        super().__init__(AiSettings, AiSettingsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_settings):
        pass
    


@dataclass
class AudioLabelDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class AudioLabelManager(BaseManager):
    def __init__(self):
        super().__init__(AudioLabel, AudioLabelDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, audio_label):
        pass
    


@dataclass
class CategoryDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class CategoryManager(BaseManager):
    def __init__(self):
        super().__init__(Category, CategoryDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, category):
        pass
    


@dataclass
class CompiledRecipeDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class CompiledRecipeManager(BaseManager):
    def __init__(self):
        super().__init__(CompiledRecipe, CompiledRecipeDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, compiled_recipe):
        pass
    


@dataclass
class ConversationDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ConversationManager(BaseManager):
    def __init__(self):
        super().__init__(Conversation, ConversationDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, conversation):
        pass
    


@dataclass
class DisplayOptionDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class DisplayOptionManager(BaseManager):
    def __init__(self):
        super().__init__(DisplayOption, DisplayOptionDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, display_option):
        pass
    


@dataclass
class FlashcardSetsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class FlashcardSetsManager(BaseManager):
    def __init__(self):
        super().__init__(FlashcardSets, FlashcardSetsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, flashcard_sets):
        pass
    


@dataclass
class ProcessorDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ProcessorManager(BaseManager):
    def __init__(self):
        super().__init__(Processor, ProcessorDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, processor):
        pass
    


@dataclass
class ScrapeConfigurationDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeConfigurationManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeConfiguration, ScrapeConfigurationDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_configuration):
        pass
    


@dataclass
class ScrapePathPatternOverrideDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapePathPatternOverrideManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapePathPatternOverride, ScrapePathPatternOverrideDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_path_pattern_override):
        pass
    


@dataclass
class ScrapeTaskResponseDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeTaskResponseManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeTaskResponse, ScrapeTaskResponseDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_task_response):
        pass
    


@dataclass
class SubcategoryDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class SubcategoryManager(BaseManager):
    def __init__(self):
        super().__init__(Subcategory, SubcategoryDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, subcategory):
        pass
    


@dataclass
class ToolDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ToolManager(BaseManager):
    def __init__(self):
        super().__init__(Tool, ToolDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, tool):
        pass
    


@dataclass
class TransformerDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class TransformerManager(BaseManager):
    def __init__(self):
        super().__init__(Transformer, TransformerDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, transformer):
        pass
    


@dataclass
class WcClaimDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class WcClaimManager(BaseManager):
    def __init__(self):
        super().__init__(WcClaim, WcClaimDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, wc_claim):
        pass
    


@dataclass
class WcImpairmentDefinitionDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class WcImpairmentDefinitionManager(BaseManager):
    def __init__(self):
        super().__init__(WcImpairmentDefinition, WcImpairmentDefinitionDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, wc_impairment_definition):
        pass
    


@dataclass
class WcReportDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class WcReportManager(BaseManager):
    def __init__(self):
        super().__init__(WcReport, WcReportDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, wc_report):
        pass
    


@dataclass
class ActionDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ActionManager(BaseManager):
    def __init__(self):
        super().__init__(Action, ActionDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, action):
        pass
    


@dataclass
class AdminsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class AdminsManager(BaseManager):
    def __init__(self):
        super().__init__(Admins, AdminsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, admins):
        pass
    


@dataclass
class AiAgentDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class AiAgentManager(BaseManager):
    def __init__(self):
        super().__init__(AiAgent, AiAgentDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_agent):
        pass
    


@dataclass
class AiModelEndpointDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class AiModelEndpointManager(BaseManager):
    def __init__(self):
        super().__init__(AiModelEndpoint, AiModelEndpointDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_model_endpoint):
        pass
    


@dataclass
class AiTrainingDataDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class AiTrainingDataManager(BaseManager):
    def __init__(self):
        super().__init__(AiTrainingData, AiTrainingDataDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_training_data):
        pass
    


@dataclass
class AppletDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class AppletManager(BaseManager):
    def __init__(self):
        super().__init__(Applet, AppletDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, applet):
        pass
    


@dataclass
class ArgDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ArgManager(BaseManager):
    def __init__(self):
        super().__init__(Arg, ArgDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, arg):
        pass
    


@dataclass
class AudioRecordingDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class AudioRecordingManager(BaseManager):
    def __init__(self):
        super().__init__(AudioRecording, AudioRecordingDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, audio_recording):
        pass
    


@dataclass
class AudioRecordingUsersDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class AudioRecordingUsersManager(BaseManager):
    def __init__(self):
        super().__init__(AudioRecordingUsers, AudioRecordingUsersDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, audio_recording_users):
        pass
    


@dataclass
class AutomationBoundaryBrokerDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class AutomationBoundaryBrokerManager(BaseManager):
    def __init__(self):
        super().__init__(AutomationBoundaryBroker, AutomationBoundaryBrokerDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, automation_boundary_broker):
        pass
    


@dataclass
class BrokerValueDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class BrokerValueManager(BaseManager):
    def __init__(self):
        super().__init__(BrokerValue, BrokerValueDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, broker_value):
        pass
    


@dataclass
class BucketStructuresDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class BucketStructuresManager(BaseManager):
    def __init__(self):
        super().__init__(BucketStructures, BucketStructuresDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, bucket_structures):
        pass
    


@dataclass
class BucketTreeStructuresDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class BucketTreeStructuresManager(BaseManager):
    def __init__(self):
        super().__init__(BucketTreeStructures, BucketTreeStructuresDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, bucket_tree_structures):
        pass
    


@dataclass
class EmailsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class EmailsManager(BaseManager):
    def __init__(self):
        super().__init__(Emails, EmailsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, emails):
        pass
    


@dataclass
class ExtractorDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ExtractorManager(BaseManager):
    def __init__(self):
        super().__init__(Extractor, ExtractorDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, extractor):
        pass
    


@dataclass
class FileStructureDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class FileStructureManager(BaseManager):
    def __init__(self):
        super().__init__(FileStructure, FileStructureDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, file_structure):
        pass
    


@dataclass
class FlashcardHistoryDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class FlashcardHistoryManager(BaseManager):
    def __init__(self):
        super().__init__(FlashcardHistory, FlashcardHistoryDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, flashcard_history):
        pass
    


@dataclass
class FlashcardImagesDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class FlashcardImagesManager(BaseManager):
    def __init__(self):
        super().__init__(FlashcardImages, FlashcardImagesDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, flashcard_images):
        pass
    


@dataclass
class FlashcardSetRelationsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class FlashcardSetRelationsManager(BaseManager):
    def __init__(self):
        super().__init__(FlashcardSetRelations, FlashcardSetRelationsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, flashcard_set_relations):
        pass
    


@dataclass
class FullSpectrumPositionsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class FullSpectrumPositionsManager(BaseManager):
    def __init__(self):
        super().__init__(FullSpectrumPositions, FullSpectrumPositionsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, full_spectrum_positions):
        pass
    


@dataclass
class MessageDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class MessageManager(BaseManager):
    def __init__(self):
        super().__init__(Message, MessageDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, message):
        pass
    


@dataclass
class MessageBrokerDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class MessageBrokerManager(BaseManager):
    def __init__(self):
        super().__init__(MessageBroker, MessageBrokerDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, message_broker):
        pass
    


@dataclass
class OrganizationInvitationsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class OrganizationInvitationsManager(BaseManager):
    def __init__(self):
        super().__init__(OrganizationInvitations, OrganizationInvitationsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, organization_invitations):
        pass
    


@dataclass
class OrganizationMembersDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class OrganizationMembersManager(BaseManager):
    def __init__(self):
        super().__init__(OrganizationMembers, OrganizationMembersDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, organization_members):
        pass
    


@dataclass
class PermissionsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class PermissionsManager(BaseManager):
    def __init__(self):
        super().__init__(Permissions, PermissionsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, permissions):
        pass
    


@dataclass
class ProjectMembersDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ProjectMembersManager(BaseManager):
    def __init__(self):
        super().__init__(ProjectMembers, ProjectMembersDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, project_members):
        pass
    


@dataclass
class RecipeBrokerDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class RecipeBrokerManager(BaseManager):
    def __init__(self):
        super().__init__(RecipeBroker, RecipeBrokerDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_broker):
        pass
    


@dataclass
class RecipeDisplayDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class RecipeDisplayManager(BaseManager):
    def __init__(self):
        super().__init__(RecipeDisplay, RecipeDisplayDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_display):
        pass
    


@dataclass
class RecipeFunctionDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class RecipeFunctionManager(BaseManager):
    def __init__(self):
        super().__init__(RecipeFunction, RecipeFunctionDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_function):
        pass
    


@dataclass
class RecipeMessageDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class RecipeMessageManager(BaseManager):
    def __init__(self):
        super().__init__(RecipeMessage, RecipeMessageDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_message):
        pass
    


@dataclass
class RecipeMessageReorderQueueDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class RecipeMessageReorderQueueManager(BaseManager):
    def __init__(self):
        super().__init__(RecipeMessageReorderQueue, RecipeMessageReorderQueueDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_message_reorder_queue):
        pass
    


@dataclass
class RecipeModelDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class RecipeModelManager(BaseManager):
    def __init__(self):
        super().__init__(RecipeModel, RecipeModelDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_model):
        pass
    


@dataclass
class RecipeProcessorDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class RecipeProcessorManager(BaseManager):
    def __init__(self):
        super().__init__(RecipeProcessor, RecipeProcessorDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_processor):
        pass
    


@dataclass
class RecipeToolDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class RecipeToolManager(BaseManager):
    def __init__(self):
        super().__init__(RecipeTool, RecipeToolDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_tool):
        pass
    


@dataclass
class ScrapeBaseConfigDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeBaseConfigManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeBaseConfig, ScrapeBaseConfigDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_base_config):
        pass
    


@dataclass
class ScrapeDomainDisallowedNotesDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeDomainDisallowedNotesManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeDomainDisallowedNotes, ScrapeDomainDisallowedNotesDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_domain_disallowed_notes):
        pass
    


@dataclass
class ScrapeDomainNotesDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeDomainNotesManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeDomainNotes, ScrapeDomainNotesDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_domain_notes):
        pass
    


@dataclass
class ScrapeDomainQuickScrapeSettingsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeDomainQuickScrapeSettingsManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeDomainQuickScrapeSettings, ScrapeDomainQuickScrapeSettingsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_domain_quick_scrape_settings):
        pass
    


@dataclass
class ScrapeDomainRobotsTxtDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeDomainRobotsTxtManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeDomainRobotsTxt, ScrapeDomainRobotsTxtDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_domain_robots_txt):
        pass
    


@dataclass
class ScrapeDomainSitemapDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeDomainSitemapManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeDomainSitemap, ScrapeDomainSitemapDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_domain_sitemap):
        pass
    


@dataclass
class ScrapeOverrideValueDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeOverrideValueManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeOverrideValue, ScrapeOverrideValueDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_override_value):
        pass
    


@dataclass
class ScrapeParsedPageDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeParsedPageManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeParsedPage, ScrapeParsedPageDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_parsed_page):
        pass
    


@dataclass
class ScrapeQuickFailureLogDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class ScrapeQuickFailureLogManager(BaseManager):
    def __init__(self):
        super().__init__(ScrapeQuickFailureLog, ScrapeQuickFailureLogDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_quick_failure_log):
        pass
    


@dataclass
class TableDataDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class TableDataManager(BaseManager):
    def __init__(self):
        super().__init__(TableData, TableDataDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, table_data):
        pass
    


@dataclass
class TableFieldsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class TableFieldsManager(BaseManager):
    def __init__(self):
        super().__init__(TableFields, TableFieldsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, table_fields):
        pass
    


@dataclass
class TaskAssignmentsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class TaskAssignmentsManager(BaseManager):
    def __init__(self):
        super().__init__(TaskAssignments, TaskAssignmentsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, task_assignments):
        pass
    


@dataclass
class TaskAttachmentsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class TaskAttachmentsManager(BaseManager):
    def __init__(self):
        super().__init__(TaskAttachments, TaskAttachmentsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, task_attachments):
        pass
    


@dataclass
class TaskCommentsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class TaskCommentsManager(BaseManager):
    def __init__(self):
        super().__init__(TaskComments, TaskCommentsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, task_comments):
        pass
    


@dataclass
class UserPreferencesDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class UserPreferencesManager(BaseManager):
    def __init__(self):
        super().__init__(UserPreferences, UserPreferencesDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, user_preferences):
        pass
    


@dataclass
class WcInjuryDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class WcInjuryManager(BaseManager):
    def __init__(self):
        super().__init__(WcInjury, WcInjuryDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, wc_injury):
        pass