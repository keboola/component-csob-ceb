# CSOB CEB extractor

Component allowing automated extraction of bank statements (VYPIS) using the [CEB Business Connector API](https://www.csob.cz/portal/firmy/prehled-on-line-kanalu-a-aplikaci/csob-ceb)

**Table of contents:**  
  
[TOC]


# Prerequisites

In order to make this connector work you need to follow the instructions 
described in section `2` in the [CEB Connector implementation guide](https://www.csob.cz/portal/documents/10710/15532355/csob-business-connector-implementacni-prirucka.pdf) 

Namely you need to:

- enable the CSOB CEB service
- get the authentication certificate
- register the certificate in the portal
- configure the CSOB service - enable bank statements via API in the `TXT (BB-TXT)` [format](https://www.csob.cz/portal/documents/10710/1927786/ceb-vypisy-format-txt.pdf).

# Configuration

## CEB Certificate

Retrieve your certificate and private key and paste it here in the `.pem` format.

The certificate should look similarly like this:

```
-----BEGIN CERTIFICATE-----
asdasdasdasd
-----END CERTIFICATE-----
-----BEGIN PRIVATE KEY-----
pkeyssssss
-----END PRIVATE KEY-----
```

## CSOB contract number

Your CSOB contract number.

## Period from date

Start date.

## Relative period from now

Relative period in format: '5 hours ago', 'yesterday','3 days ago', '4 months ago', '2 years ago', 'today'.
 
**Overrides** the `from` parameter.


## Development

If required, change local data folder (the `CUSTOM_FOLDER` placeholder) path to your custom path in the docker-compose file:

```yaml
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
```

Clone this repository, init the workspace and run the component with following command:

```
git clone repo_path my-new-component
cd my-new-component
docker-compose build
docker-compose run --rm dev
```

Run the test suite and lint check using this command:

```
docker-compose run --rm test
```

# Integration

For information about deployment and integration with KBC, please refer to the [deployment section of developers documentation](https://developers.keboola.com/extend/component/deployment/) 