from httpx import Client, Response


class JiraClient(object):
    __slots__ = ("base_url", "email", "token", "client", "app")

    def __init__(self, base_url: str, email: str, token: str) -> None:
        self.base_url = base_url
        self.email = email
        self.token = token
        self.client = Client(
            base_url=self.base_url,
            auth=(self.email, self.token),
            headers={"Content-Type": "application/json"},
        )

    def request(
            self,
            method: str,
            url: str,
            params: dict = None,
            json: dict = None,
    ) -> Response:
        return self.client.request(method=method, url=url, params=params, json=json)