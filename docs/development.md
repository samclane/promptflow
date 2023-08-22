(Development)=

# Development

One of the best ways to contribute is to create a new Node. This section will walk you through the process of creating a new Node.

## Creating a New Node


### 1. Import NodeBase Class

You'll need to import the `NodeBase` class from the appropriate module.

```python
from promptflow.src.nodes.node_base import NodeBase
```

### 2. Define Your Custom Node

Create a new class that inherits from `NodeBase`.

```python
class CustomNode(NodeBase):

```

### 3. Implement the Constructor

Define the constructor (`__init__`) for your node, and make sure to call the superclass's constructor. You can also add any custom initialization.

```python
def __init__(self, flowchart, label, custom_attribute=None, **kwargs):
    super().__init__(flowchart: Flowchart, label: str, **kwargs)
    self.custom_attribute = custom_attribute
```

### 4. Implement the run_subclass Method

Define the `run_subclass` method to handle your custom node logic. This is where you'll format the text or perform other actions.

```python
def run_subclass(self, before_result, state) -> str:
    # Your custom logic here
    return result
```

### 5. Serialization and Other Methods

You may want to implement additional methods like `serialize`, `deserialize`, or `cost`. These are optional, but may be useful depending on your node's implementation. For example, here's the `serialize` method for the `OpenAINode`:

```python
    def serialize(self):
        return super().serialize() | {
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "n": self.n,
            "max_tokens": self.max_tokens,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty,
        }

```

This method calls the superclass's `serialize` method, and then adds additional attributes to the serialized dictionary.

### 6. Create an Instance of Your Node

Finally, create an instance of your custom node and use it within your flowchart.

```python
my_node = CustomNode(flowchart, label="My Custom Node", custom_attribute="value", uid="custom_1")
```