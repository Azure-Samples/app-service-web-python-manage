---
services: app-service
platforms: python
author: lmazuel
---

# Manage Azure websites with Python

This sample demonstrates how to manage your Azure websites using a Python client.

**On this page**

- [Run this sample](#run)
- [What does example.py do?](#sample)
    - [Create a server farm](#create-server-farm)
    - [Create a website](#create-website)
    - [List websites](#list-websites)
    - [Get website details](#details)
    - [Delete a website](#update)

<a id="run"></a>
1. If you don't already have it, [install Python](https://www.python.org/downloads/).

1. We recommend to use a [virtual environnement](https://docs.python.org/3/tutorial/venv.html) to run this example, but it's not mandatory. You can initialize a virtualenv this way:

    ```
    pip install virtualenv
    virtualenv mytestenv
    cd mytestenv
    source bin/activate
    ```

1. Clone the repository.

    ```
    git clone https://github.com:Azure-Samples/app-service-web-python-manage.git
    ```

1. Install the dependencies using pip.

    ```
    cd app-service-web-python-manage
    pip install -r requirements.txt
    ```

1. Create an Azure service principal either through
    [Azure CLI](https://azure.microsoft.com/documentation/articles/resource-group-authenticate-service-principal-cli/),
    [PowerShell](https://azure.microsoft.com/documentation/articles/resource-group-authenticate-service-principal/)
    or [the portal](https://azure.microsoft.com/documentation/articles/resource-group-create-service-principal-portal/).

1. Set the following environment variables using the information from the service principal that you created.

    ```
    export AZURE_TENANT_ID={your tenant id}
    export AZURE_CLIENT_ID={your client id}
    export AZURE_CLIENT_SECRET={your client secret}
    export AZURE_SUBSCRIPTION_ID={your subscription id}
    ```

    > [AZURE.NOTE] On Windows, use `set` instead of `export`.

1. Run the sample.

    ```
    python example.py
    ```

<a id="sample"></a>
## What does example.py do?

The sample creates, lists and updates a website.
It starts by setting up a ResourceManagementClient and a WebSiteManagementClient object using your subscription and credentials.

```python
import os
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.web import WebSiteManagementClient

subscription_id = os.environ.get(
    'AZURE_SUBSCRIPTION_ID',
    '11111111-1111-1111-1111-111111111111') # your Azure Subscription Id
credentials = ServicePrincipalCredentials(
    client_id=os.environ['AZURE_CLIENT_ID'],
    secret=os.environ['AZURE_CLIENT_SECRET'],
    tenant=os.environ['AZURE_TENANT_ID']
)
resource_client = ResourceManagementClient(credentials, subscription_id)
web_client = WebSiteManagementClient(credentials, subscription_id)
```

The sample then sets up a resource group in which it will create the website.

```python
resource_group_params = {'location':'westus'}
```

<a id="create-server-farm"></a>
### Create a server farm

Create a server farm to host your website.

```python
from azure.mgmt.web.models import ServerFarmWithRichSku, SkuDescription

server_farm_async_operation = web_client.server_farms.create_or_update_server_farm(
    GROUP_NAME,
    SERVER_FARM_NAME,
    ServerFarmWithRichSku(
        location=WEST_US,
        sku=SkuDescription(
            name='S1',
            capacity=1,
            tier='Standard'
        )
    )
)
server_farm = server_farm_async_operation.result()
print_item(server_farm)
```

<a id="create-website"></a>
### Create a website

```python
from azure.mgmt.web.models import Site

site_async_operation = web_client.sites.create_or_update_site(
    GROUP_NAME,
    SITE_NAME,
    Site(
        location=WEST_US,
        server_farm_id=server_farm.id
    )
)
site = site_async_operation.result()
print_item(site)
```

<a id="list-websites"></a>
### List websites in the resourcegroup

```python
for site in web_client.sites.get_sites(GROUP_NAME).value:
    print_item(site)
```

<a id="details"></a>
### Get details for the given website

```python
web_client.sites.get_site(GROUP_NAME, SITE_NAME)
```

<a id="delete-site"></a>
### Delete a website

```python
web_client.sites.delete_site(GROUP_NAME, SITE_NAME)
```

At this point, the sample also deletes the resource group that it created.

```python
delete_async_operation = resource_client.resource_groups.delete(GROUP_NAME)
delete_async_operation.wait()
``` 


## More information
Please refer to [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python) for more information.
