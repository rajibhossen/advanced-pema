class KeyValuePair:
    def __init__(self):
        self.key = None  # string
        self.value = None  # any


class Link:
    def __init__(self):
        self.url = None  # string
        self.text = None  # string


class Log:
    def __init__(self):
        self.timestamp = None  # number
        self.field = []  # array<keyvaluepari>


class Process:
    def __init__(self, process):
        self.servicename = process["serviceName"]
        self.tags = process["tags"]


class SpanReference:
    def __init__(self, ref_data, span):
        self.refType = ref_data["refType"]
        self.span = span
        self.spanID = ref_data["spanID"]
        self.traceID = ref_data["traceID"]


class Span:
    def __init__(self, span_id, span):
        self.spanID = span_id
        self.references = []
        self.traceID = span["traceID"]
        self.processID = span["processID"]
        self.operationName = span["operationName"]
        self.startTime = span["startTime"]
        self.duration = span["duration"]
        self.process = Process()
        self.depth = None
        self.hasChildren = True
        self.relativeStartTime = None
        self.subsidiarilyReferencedBy = []


class Trace:
    def __init__(self):
        self.traceID = None
        self.startTime = None
        self.endTime = None
        self.duration = None
        self.spans = []