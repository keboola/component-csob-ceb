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



## Development

If required, change local data folder (the `CUSTOM_FOLDER` placeholder) path to your custom path in the docker-compose file:

```yaml
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
```

**NOTE**: For generation of the config.json using a friendly GUI form use [this link](http://jeremydorn.com/json-editor/?schema=N4IgLgngDgpiBcID2AjAVjAxmEAacAlmADZyIDCSAdgGYEDmArgE4CGYB1eIzMAjowK8AJggDaIRgGcYzbgGIorKVIDuSZqPwwqwqEgJUc+Ye2VIWmGFO77ixAPoBbJMLgBdfFGZJYzDtYIoNKyQeDQZCBSYMyG9NwcJJEAKqwopKyMAAQhzFlUrE5wXj5+kADymqHwAIwADHUAvviKymoaovCgkLAIUTFxCUSkfanpMJk5MnlKKuqa3DQaTux9s+0LJb6yFVVy8ABMDc0gOnoGRmE9kdGxVPH4iSOIYxnZ0wBuslkAggAKAEksmd9IZjCBvNt/BBKm59gcAKxNLxIezOVxkboRPpURhOFChR7DSJ/VHELIuNzcNxSTCxKAcLiIAE0LIyMBZMBILIAAwAmtYeZyABYwTmxej0b6qAj2LKqVhELJLPKsOUDSWyGDCLJoVBSTncuhUAhSYW4LJIMCi5gymRZJUy9USqWq9Wi3X6rKsXTKwym4VsxiYKwqGiMewQLIS4Uc1g0MCyAB0tlKOxhewQABYEQjtLinOI6rgap4QG4aJliDh4MXkAzOFQbF1TgWHE9AvAJAA5JDcAU2dyNE6mMDmSydrG9RCsZhsCBDJKjNJvLKj8fMUPU6x0ggNpkgAAypo5SFZ66kFk31nlREDMAAHjFWNgDVzxQxXUmsr3EyL2CKWoUtIHIEt6UCQt4BDsGKY5SAA1lIAD0tKisIEY3uyyoaN67rWGKl4TgaVo2nasEeo+WCMIyVC3nKlaytwRAwE4zagCqKw1iA9CxFo4TTsg6BYOCHZ9AAok+bDYNwvACEI2riCABRFAkrAPCAxCCHx1wgGWkE7AQk5KYUmL8TcAz3IuzwgAAImYbJXlY+QmSmJg7vSNF9AAPCgAB8ABK/CCCIXlIX5WR2WODkTs5RTegaSyML6hhZK8EyMK5EJptCsLVPUxyPGpVzYogtyDESS6IJFrDRdenJqZlNK7vuVB9OULVqmu9mEXVY70PF2FJTqKVpZkmX6TlmaHA0yIaVpxUCWVlkVdZaXvLIXx5ElBACGKh4AKoAjZlqstaYoXo5YoABTKNGMDePhRjalkHzQb8gIAJTbrSHmNm1HXkttu1dXBl0Om4RgEHQ3wEEmMDfg+D41AcAC0ADMaMHFmKM1JjaMWqwHyKsQK5iq9NX/AC37JMKprAk2LA3kDjBigQEMcHQmDsI2J2ASDG5WN+LJsrAmBQ4ZwgWmdWQAOR9TLWRKGwRSJnkdMMFQGjauN2W7HCCBozNJw6S2Oh4opgU0LwZoSc+2CpAh3AAlQdIsToYC21JYAO/Bun4L4NFsa2eLtsSzYSAAYhGxBOy7vBFEYaq6cbJX9Hc6miYglvW4GOluT9e6eYgnsvhyvBW9YufYm5lYRlxUf2KmUJ69UWZG8OHdAAA=&value=N4IgrgzgpgTiBcIQBoQGIAOBDCEDuA9jACYJKpQB2xGBAlpQC5koi0A27A+gLYHFQEABlTEsjHATAwAxlAgIA2qEpYegxDlKoJAczJbW7MHVKJWjAJ4YNIAEpQAZjHkALAKIAPRjCwzGACo4ANYgAL4AumFAAA==&theme=bootstrap2&iconlib=fontawesome4&object_layout=normal&show_errors=interaction)

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