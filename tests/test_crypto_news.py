import pytest
from memeai.twitter.services.news_service import CryptoNewsService
from unittest.mock import Mock, patch
import aiohttp
from aioresponses import aioresponses

@pytest.fixture
def news_service():
    return CryptoNewsService()

@pytest.fixture
def mock_trending_response():
    return {
        "coins": [
            {
                "item": {
                    "id": "bitcoin",
                    "name": "Bitcoin",
                    "symbol": "btc",
                    "market_cap_rank": 1,
                    "price_btc": 1.0
                }
            },
            {
                "item": {
                    "id": "ethereum",
                    "name": "Ethereum",
                    "symbol": "eth",
                    "market_cap_rank": 2,
                    "price_btc": 0.05
                }
            }
        ]
    }

@pytest.fixture
def mock_price_response():
    return {
        "bitcoin": {
            "usd": 50000,
            "usd_24h_change": 5.5,
            "usd_market_cap": 1000000000
        },
        "ethereum": {
            "usd": 3000,
            "usd_24h_change": -2.1,
            "usd_market_cap": 500000000
        }
    }

@pytest.fixture
def mock_global_response():
    return {
        "data": {
            "total_market_cap": {
                "usd": 2000000000000
            },
            "market_cap_change_percentage_24h_usd": 3.2,
            "market_cap_percentage": {
                "btc": 42.5
            }
        }
    }

@pytest.mark.asyncio
async def test_get_news_success(
    news_service,
    mock_trending_response,
    mock_price_response,
    mock_global_response
):
    with aioresponses() as m:
        # Mock trending endpoint
        m.get(
            f"{news_service.base_url}/search/trending",
            payload=mock_trending_response
        )
        
        # Mock price endpoint
        m.get(
            f"{news_service.base_url}/simple/price",
            payload=mock_price_response
        )
        
        # Mock global endpoint
        m.get(
            f"{news_service.base_url}/global",
            payload=mock_global_response
        )

        result = await news_service.get_news(
            coins=["bitcoin", "ethereum"]
        )

        assert len(result) > 0
        # Verify trending data
        assert any(item['type'] == 'trending' for item in result)
        # Verify price data
        assert any(item['type'] == 'price' for item in result)
        # Verify global data
        assert any(item['type'] == 'global' for item in result)

@pytest.mark.asyncio
async def test_get_news_api_error(news_service):
    with aioresponses() as m:
        # Mock API error
        m.get(
            f"{news_service.base_url}/search/trending",
            status=404
        )
        m.get(
            f"{news_service.base_url}/simple/price",
            status=500
        )
        m.get(
            f"{news_service.base_url}/global",
            status=403
        )

        result = await news_service.get_news()
        assert result == []

@pytest.mark.asyncio
async def test_get_news_network_error(news_service):
    with aioresponses() as m:
        # Mock network error
        m.get(
            f"{news_service.base_url}/search/trending",
            exception=aiohttp.ClientError()
        )
        m.get(
            f"{news_service.base_url}/simple/price",
            exception=aiohttp.ClientError()
        )
        m.get(
            f"{news_service.base_url}/global",
            exception=aiohttp.ClientError()
        )

        result = await news_service.get_news()
        assert result == []

@pytest.mark.asyncio
async def test_format_tweet(news_service):
    # Test trending tweet format
    trending_item = {
        'type': 'trending',
        'title': '🔥 Bitcoin (BTC) is trending!',
        'price_btc': 1.0,
        'market_cap_rank': 1,
        'tickers': ['BTC']
    }
    trending_tweet = news_service.format_tweet(trending_item)
    assert '🔥' in trending_tweet
    assert 'BTC' in trending_tweet
    assert '#BTC' in trending_tweet

    # Test price tweet format
    price_item = {
        'type': 'price',
        'title': 'BTC at $50,000',
        'price_change_24h': 5.5,
        'market_cap': 1000000000,
        'sentiment': 'positive',
        'tickers': ['BTC']
    }
    price_tweet = news_service.format_tweet(price_item)
    assert '$' in price_tweet
    assert '%' in price_tweet
    assert '#BTC' in price_tweet

    # Test global tweet format
    global_item = {
        'type': 'global',
        'title': 'Global Crypto Market Cap: $2,000,000,000,000',
        'market_cap_change_24h': 3.2,
        'btc_dominance': 42.5,
        'sentiment': 'neutral',
        'tickers': ['BTC', 'GLOBAL']
    }
    global_tweet = news_service.format_tweet(global_item)
    assert 'Global' in global_tweet
    assert '%' in global_tweet
    assert '#BTC' in global_tweet
    assert '#GLOBAL' in global_tweet
