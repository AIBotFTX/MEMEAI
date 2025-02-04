from memeai.agents.retriever import TweetHistoryRetriever


async def main():
    retriever = TweetHistoryRetriever(
        base_url="http://localhost:8000",
        max_tweets=10,
        time_window_days=2,
        relevance_threshold=0.7,
    )
    queries = ["APY", "HYPE airdrop", "maximize EV", "irrelevant query"]
    for query in queries:
        print(f"\nQuery: {query}")
        print("=" * 50)
        documents = await retriever._aget_relevant_documents(query)
        if documents:
            for doc in documents:
                print(f"\nTweet: {doc.page_content}")
                print(f"Relevance: {doc.metadata['relevance_score']:.2f}")
                print(f"Created at: {doc.metadata['created_at']}")
                print("-" * 50)
        else:
            print("No relevant tweets found")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
