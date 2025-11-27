from django.shortcuts import render
from .utils import fetch_milk_prices, fetch_dairy_news
from .parsers import parse_prices_from_markdown, parse_news_from_markdown
from datetime import datetime

def milk_market_dashboard(request):
    selected_state = request.GET.get("state", "")
    
    # Fetch data
    price_result = fetch_milk_prices()
    news_result = fetch_dairy_news()
    
    # Parse data
    milk_prices = parse_prices_from_markdown(price_result["content"]) if price_result["success"] else []
    news_articles = parse_news_from_markdown(news_result["content"]) if news_result["success"] else []
    
    # Extract available states from parsed data
    available_states = sorted(list(set([price["state"] for price in milk_prices])))
    
    # Filter by state if selected
    if selected_state:
        milk_prices = [p for p in milk_prices if p["state"].lower() == selected_state.lower()]
    
    context = {
        "milk_prices": milk_prices,
        "news_articles": news_articles,
        "selected_state": selected_state,
        "available_states": available_states,
        "last_updated": datetime.now().strftime("%d %B %Y, %H:%M")
    }
    return render(request, "milk_prices_dashboard.html", context)

def homepage_view(request):
    return render(request, "homepage.html")


