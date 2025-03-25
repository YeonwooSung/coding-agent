from duckduckgo_search import DDGS

from app.tool.search.base import WebSearchEngine


class DuckDuckGoSearchEngine(WebSearchEngine):
    def perform_search(self, query:str , num_results=10, *args, **kwargs):
        """DuckDuckGo search engine."""
        if not isinstance(query, str):
            raise TypeError("Query must be a string.")

        query = query.strip()
        if query == "":
            raise ValueError("Query cannot be empty.")

        return DDGS.text(query, num_results=num_results)
