AWS regions
-----------

To get a list of regions, run GET against **/api/aws-regions/** as authenticated user.
Example rendering of the region object:

.. code-block:: javascript

    {
        "url": "http://example.com/api/aws-regions/f14e1801d34d47b094f8917055bc4d2a/",
        "uuid": "f14e1801d34d47b094f8917055bc4d2a",
        "name": "Asia Pacific (Singapore)"
    }

AWS sizes
---------

To get a list of sizes, run GET against **/api/aws-sizes/** as authenticated user.
Example rendering of the size object:

.. code-block:: javascript

    {
        "url": "http://example.com/api/aws-sizes/a88803a3b1cf41e6a49a6424d6df18c2/",
        "uuid": "a88803a3b1cf41e6a49a6424d6df18c2",
        "name": "Burstable Performance Micro Instance",
        "cores": 1,
        "ram": 1024,
        "disk": 0,
        "regions": [
            {
                "url": "http://example.com/api/aws-regions/a8390dc63fe54c7596c2b32e33ca7e8f/",
                "uuid": "a8390dc63fe54c7596c2b32e33ca7e8f",
                "name": "US East (N. Virginia)"
            },
            {
                "url": "http://example.com/api/aws-regions/260453b61ee74175a692981df0fa5e55/",
                "uuid": "260453b61ee74175a692981df0fa5e55",
                "name": "US West (Oregon)"
            },
            {
                "url": "http://example.com/api/aws-regions/3dc5a04442eb4a94aa0d6b91442bb450/",
                "uuid": "3dc5a04442eb4a94aa0d6b91442bb450",
                "name": "US West (N. California)"
            },
            {
                "url": "http://example.com/api/aws-regions/4d0fb1b741f44423af7bd992dad4d200/",
                "uuid": "4d0fb1b741f44423af7bd992dad4d200",
                "name": "EU (Ireland)"
            },
            {
                "url": "http://example.com/api/aws-regions/73555b5b5f2b4ebabae10606e7d490c7/",
                "uuid": "73555b5b5f2b4ebabae10606e7d490c7",
                "name": "EU (Frankfurt)"
            },
            {
                "url": "http://example.com/api/aws-regions/f14e1801d34d47b094f8917055bc4d2a/",
                "uuid": "f14e1801d34d47b094f8917055bc4d2a",
                "name": "Asia Pacific (Singapore)"
            },
            {
                "url": "http://example.com/api/aws-regions/bf98b3890029481bba9c29cc5ce97df3/",
                "uuid": "bf98b3890029481bba9c29cc5ce97df3",
                "name": "Asia Pacific (Sydney)"
            },
            {
                "url": "http://example.com/api/aws-regions/a88eb0b0aa2541d2b74bd4e8b5c18ae3/",
                "uuid": "a88eb0b0aa2541d2b74bd4e8b5c18ae3",
                "name": "Asia Pacific (Tokyo)"
            },
            {
                "url": "http://example.com/api/aws-regions/f0d40391d44b41faa8b764932a195f09/",
                "uuid": "f0d40391d44b41faa8b764932a195f09",
                "name": "South America (Sao Paulo)"
            }
        ]
    }

In order to filter sizes by region, pass UUID of region as `region` parameter in GET request.

AWS images
----------

To get a list of images, run GET against **/api/aws-images/** as authenticated user.
Example rendering of the image object:

.. code-block:: javascript

    {
        "url": "http://example.com/api/aws-images/93d3c4df41b64e4caa532c88d21761be/",
        "uuid": "93d3c4df41b64e4caa532c88d21761be",
        "name": ".NET Beanstalk Cfn Container v1.0.0.0 on Windows 2008",
        "region": {
            "url": "http://example.com/api/aws-regions/a8390dc63fe54c7596c2b32e33ca7e8f/",
            "uuid": "a8390dc63fe54c7596c2b32e33ca7e8f",
            "name": "US East (N. Virginia)"
        }
    }

In order to filter images by region, pass UUID of region as `region` parameter in GET request.


AWS instances
-------------

To provision new instance in AWS EC2, issue a POST to **/api/aws-instances/** as a customer owner.

Request parameters:

 - name - instance name,
 - service_project_link - URL of service project link,
 - ssh_public_key - URL of uploaded SSH key object,
 - region - URL of AWS region object,
 - image - URL of AWS image object,
 - size - URL of AWS size object.


Example of a request:

.. code-block:: http

    POST /api/aws-instances/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "name": "Ubuntu Instance",
        "service_project_link": "http://example.com/api/aws-service-project-link/1/",
        "ssh_public_key": "http://example.com/api/keys/d8027a36fc204bcda34c7c6e8631a2db/",
        "region": "http://example.com/api/aws-regions/f14e1801d34d47b094f8917055bc4d2a/",
        "image": "http://example.com/api/aws-images/93d3c4df41b64e4caa532c88d21761be/",
        "size": "http://example.com/api/aws-sizes/d3f986df73dc493bb89eb6a405573655/"
    }

Example rendering of AWS instance object.

.. code-block:: javascript

    {
        "url": "http://example.com/api/aws-instances/466044cf0e9a4bfaada1081af6d95b9b/",
        "uuid": "466044cf0e9a4bfaada1081af6d95b9b",
        "name": "Ubuntu Instance",
        "description": "Ubuntu Instance",
        "start_time": null,
        "service": "http://example.com/api/aws/d9e5d1869093452bb7b741a326999b3a/",
        "service_name": "Amazon",
        "service_uuid": "d9e5d1869093452bb7b741a326999b3a",
        "project": "http://example.com/api/projects/e63838e3e68f4fc4aa39617b7550cef3/",
        "project_name": "Default",
        "project_uuid": "e63838e3e68f4fc4aa39617b7550cef3",
        "customer": "http://example.com/api/customers/eea999ddf31540aea6bd4f591aa353d1/",
        "customer_name": "Alice",
        "customer_native_name": "",
        "customer_abbreviation": "",
        "project_groups": [],
        "tags": [],
        "error_message": "",
        "resource_type": "Amazon.Instance",
        "state": "Provisioning Scheduled",
        "created": "2015-12-25T09:07:27.680Z",
        "backend_id": "",
        "cores": 1,
        "ram": 627,
        "disk": 15360,
        "external_ips": [],
        "internal_ips": []
    }

Import instances
^^^^^^^^^^^^^^^^

To get a list of instances available for import issue a GET to **/api/aws/<service-uuid>/link/** as a customer owner.

.. code-block:: http

    GET /api/aws/93a689d7e1f740238bbbf71dd1c1599f/link/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    [
        {
            "name": "docker-build-host",
            "created": "2015-11-12T11:03:41Z",
            "ram": 3840,
            "cores": 1,
            "disk": 10240,
            "id": "i-b32a05de"
        }
    ]

To import instance issue POST against the same endpoint with project URL, instance backend id.

.. code-block:: http

    POST /api/aws/93a689d7e1f740238bbbf71dd1c1599f/link/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "backend_id": "i-b32a05de",
        "project": "http://example.com/api/projects/e5f973af2eb14d2d8c38d62bcbaccb33/"
    }
