import asyncio
import httpx

API_URL = "http://0.0.0.0:80/video/8"
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMSIsImV4cCI6MTc0NzIwMTcwMX0.CmaczJfsIRqUW4mZZy8IdJ0UH3BDQWqKT-SDd3fBdBQ"  # 실제 토큰으로 대체


async def call_video_api():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            API_URL,
            headers={"Authorization": AUTH_TOKEN},
        )
        print(response.status_code, response.text)


async def main():
    # 동시에 5번 요청
    await asyncio.gather(*[call_video_api() for _ in range(5)])


if __name__ == "__main__":
    asyncio.run(main())
