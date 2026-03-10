import asyncio
import time
from httpx import Response
from app import get_data_pool_stats


class MockApp:
    class MockState:
        class MockClient:
            async def get(self, url, params=None):
                await asyncio.sleep(0.5)  # simulate network delay
                if "count_over_time" in params.get("query", ""):
                    if 'installation_id!=""' in params.get("query", ""):
                        return Response(
                            200,
                            json={
                                "status": "success",
                                "data": {"result": [{"value": [0, "100"]}]},
                            },
                        )
                    else:
                        return Response(
                            200,
                            json={
                                "status": "success",
                                "data": {"result": [{"value": [0, "100000"]}]},
                            },
                        )
                return Response(200, json={})

        http_client = MockClient()

    state = MockState()


class MockRequest:
    app = MockApp()


async def run_benchmark():
    request = MockRequest()
    start_time = time.time()
    await get_data_pool_stats(request)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
