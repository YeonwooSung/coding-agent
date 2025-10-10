from datetime import datetime
from uuid import uuid4
import json

# custom imports
from app.bedrock import OpenAIResponse
from openai.types.chat import ChatCompletionMessage


class Collector:
    """A simple data collector to gather input prompts and output responses."""

    def __init__(self):
        self.data = []


    def collect(self, messages: list[ChatCompletionMessage], output: str | OpenAIResponse | ChatCompletionMessage):
        """
        Collect a new data entry with messages and output.
        
        Args:
            messages (list): List of message dicts or OpenAIResponse objects.
            output (str | OpenAIResponse | ChatCompletionMessage): The output response string or OpenAIResponse object or ChatCompletionMessage object.
        """
        now = datetime.now()
        message_list = [
            {
                "role": msg["role"],
                "content": msg["content"]
            } for msg in messages
        ]

        if isinstance(output, OpenAIResponse):
            output_str = output.model_dump()
        elif isinstance(output, str):
            output_str = output
        elif isinstance(output, ChatCompletionMessage):
            output_str = output.content
        else:
            output_str = str(output)

        item = {
            "id": str(uuid4()),
            "timestamp": now.isoformat(),
            "messages": message_list,
            "output": output_str
        }
        self.data.append(item)


    def dump(self, reset: bool = True):
        """
        Dump collected data to a JSONL file and optionally reset the collector.

        Args:
            reset (bool): Whether to reset the collected data after dumping.
        """
        # save as JSONL file
        filename = f"collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(filename, 'w') as f:
            for entry in self.data:
                print(entry)
                f.write(json.dumps(entry) + '\n')
        print(f"Data dumped to {filename}")
        if reset:
            self.data = []
            print("Collector data reset.")


# Global collector instance
global_collector = Collector()
