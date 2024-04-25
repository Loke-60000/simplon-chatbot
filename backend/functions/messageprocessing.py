from functions.webbrowsingllm import find_url, extract_content_from_urls, perform_content_search

def process_message(message: str) -> str:
    urls = find_url(message)
    response_text = extract_content_from_urls(urls) if urls else ""

    search_keywords = ["search", "look for", "find", "online", "web"]
    if not response_text and any(keyword in message.lower() for keyword in search_keywords):
        search_query = message.split(next(
            keyword for keyword in search_keywords if keyword in message.lower()), 1)[1].strip()
        response_text = perform_content_search(search_query)

    return response_text or "Please provide a URL or specify a search query."
