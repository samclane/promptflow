class MermaidConverter:
    """Handles converting a flowchart to mermaid syntax"""

    def __init__(self, flowchart):
        self.flowchart = flowchart

    def sanitize_uid(self, uid):
        return uid.replace(" ", "_")

    def convert_node(self, node):
        return f'\t{self.sanitize_uid(node.uid)}["{node.label}"]\n'

    def convert_connector(self, connector):
        if connector.condition_label:
            return f"\t{self.sanitize_uid(connector.prev.uid)} -->|{connector.condition_label}| {self.sanitize_uid(connector.next.uid)}\n"
        else:
            return f"\t{self.sanitize_uid(connector.prev.uid)} --> {self.sanitize_uid(connector.next.uid)}\n"

    def to_mermaid(self) -> str:
        mermaid_str = "flowchart TD\n"
        for node in self.flowchart.nodes:
            mermaid_str += self.convert_node(node)
        for connector in self.flowchart.connectors:
            mermaid_str += self.convert_connector(connector)
        return mermaid_str
