In order to make this connector work you need to follow the instructions 
described in section `2` in the [CEB Connector implementation guide](https://www.csob.cz/portal/documents/10710/15532355/csob-business-connector-implementacni-prirucka.pdf) 

Namely you need to:

- enable the CSOB CEB service
- get the authentication certificate
- register the certificate in the portal
- configure the CSOB service - enable bank statements via API in the `TXT (BB-TXT)` [format](https://www.csob.cz/portal/documents/10710/1927786/ceb-vypisy-format-txt.pdf).
