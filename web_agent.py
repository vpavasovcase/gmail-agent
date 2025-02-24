import os
import asyncio
from pydantic_ai import Agent, RunContext
from tavily import TavilyClient
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Define a structured output model for the agent's response
class SearchResponse(BaseModel):
    answer: str = Field(description="The concise answer to the user's query")
    source: str = Field(description="The source URL or reference for the answer")

# Initialize the agent
browse_agent = Agent(
    model="openai:gpt-4o",  # Using OpenAI's GPT-4o model
    result_type=SearchResponse,  # Structured output type
    system_prompt=(
        "You are a web browsing agent. Use the `web_search` tool for general queries, "
        "the `browse_website` tool for static content from a URL, or the "
        "`browse_website_dynamic` tool for dynamic content requiring JavaScript. "
        "Provide a concise, accurate answer and always include a source."       
    ),
)

# Tool for web searching (unchanged from previous example)
@browse_agent.tool
async def web_search(ctx: RunContext[None], query: str) -> str:
    """Search the web for the given query and return raw results."""
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = tavily_client.search(query, max_results=3)
    results = "\n".join(
        f"Snippet: {result['content']}\nSource: {result['url']}"
        for result in response["results"]
    )
    return results

# New tool for browsing a specific website
@browse_agent.tool
async def browse_website(ctx: RunContext[None], url: str) -> str:
    """Visit a specific URL and return the main text content."""
    try:
        # Fetch the webpage
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract readable text (e.g., from paragraphs)
        paragraphs = soup.find_all("p")
        text_content = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        if not text_content:
            return f"No readable content found at {url}"
        return f"Content from {url}:\n{text_content}"
    except requests.RequestException as e:
        return f"Error browsing {url}: {str(e)}"

@browse_agent.tool
async def browse_website_dynamic(ctx: RunContext[None], url: str) -> str:
    """Visit a URL dynamically and return the rendered content after JavaScript execution."""
    try:
        options = Options()
        options.add_argument("--headless")  # Run without UI
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        driver.get(url)

        # Wait for the page body to load (adjust timeout or condition as needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        content = driver.find_element(By.TAG_NAME, "body").text
        
        driver.quit()
        return f"Dynamic content from {url}:\n{content}"
    except Exception as e:
        return f"Error browsing {url} dynamically: {str(e)}"
    
# Async function to run the agent
async def run_agent(query: str):
    result = await browse_agent.run(query)
    return result.data

# Example usage
async def main():
    # Example 1: General search
    query1 = "What is the capital of Brazil?"
    response1 = await run_agent(query1)
    print(f"Query: {query1}")
    print(f"Answer: {response1.answer}")
    print(f"Source: {response1.source}\n")

    # Example 2: Browse a specific website
    query2 = "Browse https://en.wikipedia.org/wiki/Brasília and tell me about the city."
    response2 = await run_agent(query2)
    print(f"Query: {query2}")
    print(f"Answer: {response2.answer}")
    print(f"Source: {response2.source}")

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())