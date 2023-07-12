(Connector)=
# Connectors

Connectors are how flow is controlled in the Flowchart. They are the arrows that connect [Nodes](nodes.md) together.

Conditions are represented by Python functions. They use the same general signature as [Functions](Function), but instead of returning a value, they return a boolean. If the condition returns `True`, the flow will continue down that connector. If the condition returns `False`, the flow will continue down the next connector. If no connectors are `True`, the flow will halt.

