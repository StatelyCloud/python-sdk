# StatelyDB SDK for Python

This is the Python SDK for [StatelyDB](https://stately.cloud).

### Getting started:

##### Disclaimer:

We're still in an invite-only preview mode - if you're interested, please reach out to [preview@stately.cloud](mailto:preview@stately.cloud?subject=Early%20Access%20Program).

Begin by following our [Getting Started Guide] which will help you define, generate, and publish a DB schema so that it can be used.

##### Install the SDK

```sh
pip install statelydb
```


### Usage:

Create an authenticated client, then import your item types from your generated schema module and use the client!

```python
from schema import Client, MyItem
async def put_my_item() -> None:
    # Create a client. This will use the environment variable
    # STATELY_ACCESS_KEY to read your access key.
    client = Client(store_id=<store-id>)

    # Instantiate an item from your schema
    item = MyItem(name="Jane Doe")

    # put and get the item!
    put_result = await client.put(item)
    get_result = await client.get(MyItem, put_result.key_path())
    assert put_result == get_result
```

---

[Getting Started Guide]: https://docs.stately.cloud/guides/getting-started/
[Defining Schema]: https://docs.stately.cloud/guides/schema/