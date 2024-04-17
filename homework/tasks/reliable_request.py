import abc
import asyncio
import httpx


class ResultsObserver(abc.ABC):
    @abc.abstractmethod
    def observe(self, data: bytes) -> None: ...


async def do_reliable_request(url: str, observer: ResultsObserver) -> None:
    """
    Одна из главных проблем распределённых систем - это ненадёжность связи.

    Ваша задача заключается в том, чтобы таким образом исправить этот код, чтобы он
    умел переживать возвраты ошибок и таймауты со стороны сервера, гарантируя
    успешный запрос (в реальной жизни такая гарантия невозможна, но мы чуть упростим себе задачу).

    Все успешно полученные результаты должны регистрироваться с помощью обсёрвера.
    """

    async with httpx.AsyncClient() as client:
        retry = 0
        max_retries = 5
        while retry < max_retries:
            try:
                response = await client.get(url, timeout=15)
                response.raise_for_status()
                data = response.read()

                observer.observe(data)
                return
            except (
                httpx.TimeoutException,
                httpx.HTTPStatusError,
                httpx.NetworkError,
            ):
                retry += 1
                await asyncio.sleep(0.1 * retry)
                continue
        return
