from datetime import datetime
from uuid import uuid4
import orjson

# custom imports
from app.bedrock import OpenAIResponse


class Collector:
    """A simple data collector to gather input prompts and output responses."""

    def __init__(self):
        self.data = []


    def collect(self, messages: list, output: str):
        """
        Collect a new data entry with messages and output.
        
        Args:
            messages (list): List of message dicts or OpenAIResponse objects.
            output (str): The output response string.
        """
        now = datetime.now()
        message_list = [
            m.model_dump() if isinstance(m, OpenAIResponse) else m for m in messages
        ]
        item = {
            "id": str(uuid4()),
            "timestamp": now.isoformat(),
            "messages": message_list,
            "output": output
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
                f.write(orjson.dumps(entry) + '\n')
        print(f"Data dumped to {filename}")
        if reset:
            self.data = []
            print("Collector data reset.")


# Global collector instance
global_collector = Collector()
