import json
import re
import os
from typing import Pattern
from dotenv import load_dotenv

import aiohttp
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.resolver.base import (
    BaseDIDResolver,
    DIDNotFound,
    ResolverError,
    ResolverType,
)
from pydid import DID

# Load environment variables from .env file
load_dotenv()

class SopraResolver(BaseDIDResolver):
    """Sopra Resolver."""

    def __init__(self):
        super().__init__(ResolverType.NATIVE)
        # Load the regex pattern from the environment variable
        self._supported_did_regex = re.compile(os.getenv("SOPRA_DID_REGEX"))
        # Load the URL pattern from the environment variable
        self.url_pattern = os.getenv("SOPRA_DID_URL_PATTERN")

    @property
    def supported_did_regex(self) -> Pattern:
        """Return list of supported methods."""
        return self._supported_did_regex

    async def setup(self, context):
        """Setup the Sopra resolver (none required)."""

    async def _resolve(self, profile: Profile, did: str) -> dict:
        """Resolve Sopra DIDs."""
        as_did = DID(did)
        # Construct the URL using the DID and the pattern from .env
        url = f"{self.url_pattern}{as_did.did}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    try:
                        return json.loads(await response.text())
                    except Exception as err:
                        raise ResolverError(
                            "Response was incorrectly formatted"
                        ) from err
                if response.status == 404:
                    raise DIDNotFound(f"No document found for {did}")
                raise ResolverError(
                    "Could not find doc for {}: {}".format(did, await response.text())
                )
