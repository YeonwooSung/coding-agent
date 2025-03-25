from googlesearch import search

from app.tool.search.base import WebSearchEngine


class GoogleSearchEngine(WebSearchEngine):
    def perform_search(self, query: str, num_results=10, *args, **kwargs):
        """Google search engine."""
        if not isinstance(query, str):
            raise TypeError("Query must be a string.")

        query = query.strip()
        if query == "":
            raise ValueError("Query cannot be empty.")
        return search(query, num_results=num_results)
