# twitch_api.py
import aiohttp
from typing import List, Dict, Any

async def fetch_followed_streams(session: aiohttp.ClientSession, client_id: str, token: str, user_id: str) -> List[Dict[str, Any]]:
    """
    Fetches online followed streams from the Twitch Helix API.

    Raises:
        Exception: If the API returns an error status code.
    """
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {token}'
    }
    url = f'https://api.twitch.tv/helix/streams/followed?user_id={user_id}'
    
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return (await response.json()).get('data', [])
        elif response.status == 401:
            raise Exception("Unauthorized: Please check your Access Token.")
        else:
            error_text = await response.text()
            raise Exception(f"API Error ({response.status}): {error_text}")