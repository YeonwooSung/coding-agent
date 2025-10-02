from datetime import datetime
from uuid import uuid4
import orjson


class Collector:
    def __init__(self):
        self.data = []

    def collect(self, messages: list, output: str):
        now = datetime.now()
        item = {
            "id": str(uuid4()),
            "timestamp": now.isoformat(),
            "messages": messages,
            "output": output
        }
        self.data.append(item)

    def dump(self, reset: bool = True):
        # save as JSONL file
        filename = f"collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(filename, 'w') as f:
            for entry in self.data:
                f.write(orjson.dumps(entry) + '\n')
        print(f"Data dumped to {filename}")
        if reset:
            self.data = []
            print("Collector data reset.")


global_collector = Collector()
