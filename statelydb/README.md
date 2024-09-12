# StatelyDB SDK for Python

This is the Python client for the Stately Cloud API. We're still in an invite-only
preview mode - if you're interested, please reach out to preview@stately.cloud.

This client is not meant for direct usage. You should instead setup a schema and
use our [CLI](https://stately.cloud/downloads) to generate your own personalized
Python package which will wrap this client.


The client library can be installed as such:

```
pip install statelydb
```

When you join the preview program, we'll set you up with a few bits of information:

1. `STATELY_CLIENT_ID` - a client identifier so we know what client you are.
2. `STATELY_CLIENT_SECRET` - a sensitive secret that lets your applications authenticate with the API.
3. A store ID that identifies which store in your organization you're using.
4. A link to more in-depth documentation than this README.

