import requests
import base64
import aiohttp
import asyncio


class ApiCredentials:
    def __init__(self, username, password):
        """
        Initializes an instance of ApiCredentials.

        Args:
            username (str): The username for API authentication.
            password (str): The password for API authentication.
        """
        self.username = username
        self.password = password

    def get_encoded_credentials(self):
        """
        Returns the Base64 encoded username and password for API authentication.
        """
        credentials = f"{self.username}:{self.password}"
        return base64.b64encode(credentials.encode()).decode()


class Client:
    def __init__(self, base_url, api_credentials):
        self.base_url = base_url
        self.api_credentials = api_credentials
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.api_credentials.get_encoded_credentials()}",
        }

    def req(self, payload, method, config):
        try:
            if method == "POST":
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=config["timeout"],
                )
            elif method == "GET":
                response = requests.get(
                    self.base_url, headers=self.headers, timeout=config["timeout"]
                )
            else:
                print(f"Unsupported method: {method}")
                return None

            response.raise_for_status()

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error occurred: {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            print(
                f"Timeout error. The request to {self.base_url} with method {method} has timed out."
            )
            return None
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
            print(response.text)
            return None
        except requests.exceptions.RequestException as err:
            print(f"Error occurred: {err}")
            return None


class ClientAsync:
    def __init__(self, base_url, api_credentials):
        self.base_url = base_url
        self.api_credentials = api_credentials
        self.session = None
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.api_credentials.get_encoded_credentials()}",
        }

    async def __aenter__(self):
        await self.ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def get_job_id(self, payload):
        try:
            async with self.session.post(
                    self.base_url, headers=self.headers, json=payload
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data["id"]
        except aiohttp.ClientResponseError as e:
            print(f"HTTP error occurred: {e.status}")
        except aiohttp.ClientConnectionError as e:
            print(f"Connection error occurred: {e}")
        except asyncio.TimeoutError:
            print(f"Timeout error. The request to {self.base_url} has timed out.")
        except Exception as e:
            print(f"An error occurred: {e}")
        return None

    async def poll_job_status(self, job_id, poll_interval):
        job_status_url = f"{self.base_url}/{job_id}"
        while True:
            try:
                async with self.session.get(
                    job_status_url, headers=self.headers
                ) as response:
                    response.raise_for_status()
                    job = await response.json()
                    if job["status"] == "done":
                        return True
                    elif job["status"] == "faulted":
                        raise Exception("Job faulted")
            except aiohttp.ClientResponseError as e:
                print(f"HTTP error occurred: {e.status} - {e.message}")
                return None
            except aiohttp.ClientConnectionError as e:
                print(f"Connection error occurred: {e}")
                return None
            except asyncio.TimeoutError:
                print(
                    f"Timeout error. The request to {job_status_url} has timed out."
                )
                return None
            except Exception as e:
                print(f"Unexpected error processing your query: {e}")
                return None
            await asyncio.sleep(poll_interval)

    async def get_http_resp(self, job_id):
        result_url = f"{self.base_url}/{job_id}/results"
        try:
            async with self.session.get(result_url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            print(f"HTTP error occurred: {e.status}")
        except aiohttp.ClientConnectionError as e:
            print(f"Connection error occurred: {e}")
        except asyncio.TimeoutError:
            print(f"Timeout error. The request to {result_url} has timed out.")
        except Exception as e:
            print(f"An error occurred: {e}")
        return None

    async def execute_with_timeout(self, payload, config):
        job_id = await self.get_job_id(payload)

        await self.poll_job_status(job_id, config["poll_interval"])

        return await self.get_http_resp(job_id)
