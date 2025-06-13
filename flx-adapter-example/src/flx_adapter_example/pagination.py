"""Pagination utilities for API client.

This module provides classes and functions for handling pagination in API responses,
including iterators for automatic paging through result sets.
"""

from collections.abc import Callable, Iterator
from typing import Any, TypeVar

from .client import ApiClient
from .models import FlxResponse

T = TypeVar("T")


class PageInfo:
    """Information about pagination for a response.

    This class encapsulates pagination metadata such as the current page,
    total pages, total items, and more.
    """

    def __init__(
        self,
        page: int = 1,
        page_size: int = 0,
        total_pages: int = 0,
        total_items: int = 0,
        next_page: int | None = None,
        prev_page: int | None = None,
    ) -> None:
        """Initialize PageInfo.

        Args:
            page: Current page number (1-based)
            page_size: Number of items per page
            total_pages: Total number of pages
            total_items: Total number of items across all pages
            next_page: Next page number or None if there is no next page
            prev_page: Previous page number or None if there is no previous page
        """
        self.page = page
        self.page_size = page_size
        self.total_pages = total_pages
        self.total_items = total_items
        self.next_page = next_page
        self.prev_page = prev_page

    @property
    def has_next(self) -> bool:
        """Check if there is a next page."""
        return self.next_page is not None

    @property
    def has_prev(self) -> bool:
        """Check if there is a previous page."""
        return self.prev_page is not None

    @classmethod
    def from_response(cls, response: dict[str, Any]) -> "PageInfo":
        """Create PageInfo from API response.

        This method supports multiple pagination formats including:
        - Offset-based pagination (page, limit, total)
        - Page-based pagination (current_page, per_page, total_pages)
        - Link-based pagination with metadata (pagination object)

        Args:
            response: API response data

        Returns:
            PageInfo: Pagination information
        """
        # Default values
        page = 1
        page_size = 0
        total_pages = 0
        total_items = 0
        next_page = None
        prev_page = None

        # Extract pagination info from response
        if "pagination" in response and isinstance(response["pagination"], dict):
            # Format: {"pagination": {"page": 1, "page_size": 10, "total_pages": 5, "total": 45}}
            pagination = response["pagination"]
            page = pagination.get("page", pagination.get("current_page", 1))
            page_size = pagination.get("page_size", pagination.get("per_page", 0))
            total_pages = pagination.get("total_pages", 0)
            total_items = pagination.get("total", pagination.get("total_items", 0))

            # Calculate next/prev pages
            if page < total_pages:
                next_page = page + 1
            if page > 1:
                prev_page = page - 1
        elif "meta" in response and isinstance(response["meta"], dict):
            # Format: {"meta": {"page": 1, "limit": 10, "total": 45}}
            meta = response["meta"]
            page = meta.get("page", meta.get("current_page", 1))
            page_size = meta.get("limit", meta.get("per_page", 0))
            total_items = meta.get("total", meta.get("total_items", 0))

            # Calculate total pages
            if page_size > 0 and total_items > 0:
                total_pages = (total_items + page_size - 1) // page_size

            # Calculate next/prev pages
            if page < total_pages:
                next_page = page + 1
            if page > 1:
                prev_page = page - 1
        else:
            # Try to extract pagination from query parameters in links
            links = response.get("links", {})
            if links and isinstance(links, dict):
                # Format: {"links": {"next": "?page=2", "prev": null}}
                next_link = links.get("next")
                prev_link = links.get("prev")

                if next_link and isinstance(next_link, str):
                    # Extract page from next link
                    import re

                    match = re.search(r"page=(\d+)", next_link)
                    if match:
                        next_page = int(match.group(1))
                        page = next_page - 1 if next_page > 1 else 1

                if prev_link and isinstance(prev_link, str):
                    # Extract page from prev link
                    import re

                    match = re.search(r"page=(\d+)", prev_link)
                    if match:
                        prev_page = int(match.group(1))

        return cls(
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_items=total_items,
            next_page=next_page,
            prev_page=prev_page,
        )


class PagedResponse[T]:
    """Paginated API response.

    This class encapsulates an API response with pagination, providing
    access to the current page of data and pagination metadata.
    """

    def __init__(
        self,
        data: list[T],
        page_info: PageInfo,
        raw_response: FlxResponse | None = None,
    ) -> None:
        """Initialize PagedResponse.

        Args:
            data: Current page of data
            page_info: Pagination information
            raw_response: Original API response
        """
        self.data = data
        self.page_info = page_info
        self.raw_response = raw_response

    def __len__(self) -> int:
        """Return the number of items in the current page."""
        return len(self.data)

    def __iter__(self) -> Iterator[T]:
        """Iterate through the items in the current page."""
        return iter(self.data)

    def __getitem__(self, index: int) -> T:
        """Get an item from the current page by index."""
        return self.data[index]


class PaginatedIterator[T]:
    """Iterator for paginated API responses.

    This class provides an iterator that automatically fetches all pages
    of results from a paginated API endpoint.
    """

    def __init__(
        self,
        client: ApiClient,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data_key: str = "data",
        page_param: str = "page",
        page_size_param: str = "page_size",
        page_size: int = 20,
        transform_func: Callable[[dict[str, Any]], T] | None = None,
        model_class: type | None = None,
    ) -> None:
        """Initialize PaginatedIterator.

        Args:
            client: API client instance
            endpoint: API endpoint path
            params: Query parameters (optional)
            data_key: Key in the response that contains the data items
            page_param: Parameter name for page number
            page_size_param: Parameter name for page size
            page_size: Number of items per page
            transform_func: Function to transform each data item (optional)
            model_class: Model class for data validation and conversion (optional)
        """
        self.client = client
        self.endpoint = endpoint
        self.params = params or {}
        self.data_key = data_key
        self.page_param = page_param
        self.page_size_param = page_size_param
        self.page_size = page_size
        self.transform_func = transform_func
        self.model_class = model_class

        # Set initial parameters
        self.params[self.page_size_param] = self.page_size
        self.params[self.page_param] = 1

        # State for iteration
        self.current_page: PagedResponse[T] | None = None
        self.item_index = 0
        self.exhausted = False

    def __iter__(self) -> "PaginatedIterator[T]":
        """Return iterator object."""
        return self

    def __next__(self) -> T:
        """Get the next item from the paginated results."""
        if self.exhausted:
            raise StopIteration

        # Fetch first page if we haven't started yet
        if self.current_page is None:
            self._fetch_next_page()

        # If we've reached the end of the current page, fetch the next page
        if self.item_index >= len(self.current_page.data):
            if not self.current_page.page_info.has_next:
                self.exhausted = True
                raise StopIteration

            self._fetch_next_page()
            self.item_index = 0

        # Get the current item and increment the index
        item = self.current_page.data[self.item_index]
        self.item_index += 1
        return item

    def _fetch_next_page(self) -> None:
        """Fetch the next page of results."""
        # If we already have a current page, update the page parameter
        if self.current_page is not None:
            next_page = self.current_page.page_info.next_page
            if next_page is None:
                self.exhausted = True
                raise StopIteration

            self.params[self.page_param] = next_page

        # Make the API request
        response = self.client.get(self.endpoint, params=self.params)

        if not response.success or not isinstance(response.data, dict):
            self.exhausted = True
            raise StopIteration

        # Extract data and pagination info
        data = response.data.get(self.data_key, [])
        if not isinstance(data, list):
            self.exhausted = True
            raise StopIteration

        # Transform data if needed
        if self.transform_func:
            data = [self.transform_func(item) for item in data]
        elif self.model_class:
            data = [self.model_class.model_validate(item) for item in data]

        # Create page info
        page_info = PageInfo.from_response(response.data)

        # Update current page
        self.current_page = PagedResponse(data, page_info, response)


def paginate[T](
    client: ApiClient,
    endpoint: str,
    params: dict[str, Any] | None = None,
    data_key: str = "data",
    page_param: str = "page",
    page_size_param: str = "page_size",
    page_size: int = 20,
    transform_func: Callable[[dict[str, Any]], T] | None = None,
    model_class: type | None = None,
) -> PaginatedIterator[T]:
    """Create a paginated iterator for an API endpoint.

    Args:
        client: API client instance
        endpoint: API endpoint path
        params: Query parameters (optional)
        data_key: Key in the response that contains the data items
        page_param: Parameter name for page number
        page_size_param: Parameter name for page size
        page_size: Number of items per page
        transform_func: Function to transform each data item (optional)
        model_class: Model class for data validation and conversion (optional)

    Returns:
        PaginatedIterator: Iterator for paginated results
    """
    return PaginatedIterator(
        client=client,
        endpoint=endpoint,
        params=params,
        data_key=data_key,
        page_param=page_param,
        page_size_param=page_size_param,
        page_size=page_size,
        transform_func=transform_func,
        model_class=model_class,
    )
