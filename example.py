"""Sample code demonstrating management of Azure web apps.

This script expects that the following environment vars are set:

AZURE_TENANT_ID: with your Azure Active Directory tenant id or domain
AZURE_CLIENT_ID: with your Azure Active Directory Application Client ID
AZURE_CLIENT_SECRET: with your Azure Active Directory Application Secret
AZURE_SUBSCRIPTION_ID: with your Azure Subscription Id
"""

import os

from haikunator import Haikunator
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.web.models import AppServicePlan, SkuDescription, Site

WEST_US = 'westus'
GROUP_NAME = 'azure-sample-group'
SERVER_FARM_NAME = 'sample-server-farm'
SITE_NAME = Haikunator().haikunate()


def run_example():
    """Web Site management example."""
    #
    # Create the Resource Manager Client with an Application (service principal) token provider
    #
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']

    credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_CLIENT_ID'],
        secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant=os.environ['AZURE_TENANT_ID']
    )
    resource_client = ResourceManagementClient(credentials, subscription_id)
    web_client = WebSiteManagementClient(credentials, subscription_id)

    # Register for required namespace
    resource_client.providers.register('Microsoft.Web')

    # Create Resource group
    print('Create Resource Group')
    resource_group_params = {'location':'westus'}
    print_item(resource_client.resource_groups.create_or_update(GROUP_NAME, resource_group_params))

    #
    # Create a Server Farm for your WebApp
    #
    print('Create a Server Farm for your WebApp')

    server_farm_async_operation = web_client.app_service_plans.create_or_update(
        GROUP_NAME,
        SERVER_FARM_NAME,
        AppServicePlan(
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

    #
    # Create a Site to be hosted in the Server Farm
    #
    print('Create a Site to be hosted in the Server Farm')
    site_async_operation = web_client.web_apps.create_or_update(
        GROUP_NAME,
        SITE_NAME,
        Site(
            location=WEST_US,
            server_farm_id=server_farm.id
        )
    )
    site = site_async_operation.result()
    print_item(site)

    #
    # List Sites by Resource Group
    #
    print('List Sites by Resource Group')
    for site in web_client.web_apps.list_by_resource_group(GROUP_NAME):
        print_item(site)

    #
    # Get a single Site
    #
    print('Get a single Site')
    site = web_client.web_apps.get(GROUP_NAME, SITE_NAME)
    print_item(site)

    print("Your site and server farm have been created. " \
      "You can now go and visit at http://{}/".format(site.default_host_name))
    input("Press enter to delete the site and server farm.")

    #
    # Delete a Site
    #
    print('Deleting the Site')
    web_client.web_apps.delete(GROUP_NAME, SITE_NAME)

    #
    # Delete the Resource Group
    #
    print('Deleting the resource group')
    delete_async_operation = resource_client.resource_groups.delete(GROUP_NAME)
    delete_async_operation.wait()


def print_item(group):
    """Print an instance."""
    print("\tName: {}".format(group.name))
    print("\tId: {}".format(group.id))
    print("\tLocation: {}".format(group.location))
    print("\tTags: {}".format(group.tags))
    if hasattr(group, 'status'): # ServerFarmWithRichSku
        print("\tStatus: {}".format(group.status))
    if hasattr(group, 'state'): # Site
        print("\tStatus: {}".format(group.state))
    if hasattr(group, 'properties'):
        print_properties(group.properties)
    print("\n\n")


def print_properties(props):
    """Print a Site properties instance."""
    if props and props.provisioning_state:
        print("\tProperties:")
        print("\t\tProvisioning State: {}".format(props.provisioning_state))


if __name__ == "__main__":
    run_example()
