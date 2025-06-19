# Oracle WMS REST API Guide

> **Function**: Oracle Warehouse Management Cloud REST API reference | **Audience**: Integration developers, API consumers | **Status**: Stable

[![Oracle WMS](https://img.shields.io/badge/oracle-WMS_25B-red.svg)](./index.md)
[![REST API](https://img.shields.io/badge/api-REST-blue.svg)](../../api-reference/index.md)
[![Framework](https://img.shields.io/badge/framework-FLX_0.4.0-orange.svg)](../../index.md)

**Comprehensive guide for integrating with Oracle Warehouse Management Cloud via REST API using FLX Framework**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Oracle Guides](./index.md) → **📄 Current**: WMS REST API Guide

### **📍 Learning Path Position**

```
[Oracle Integration Hub](./index.md) → **[WMS REST API]** → [WMS Comprehensive Guide](./oracle-wms-comprehensive-guide.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Oracle Guides Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Related**: [WMS Adapter](../../guides/adapters/flx_http_oracle_wms-adapter.md)

---

## 📋 **Overview**

This guide covers the Oracle Warehouse Management Cloud REST API (version 25B) integration patterns using the FLX Framework. The Oracle WMS REST API provides comprehensive access to warehouse operations through structured endpoints.

### **API Overview**

The Oracle WMS REST API is organized into six main chapters:

1. Visão geral
   • Princípios REST e uso dos métodos HTTP (GET, POST, PATCH, DELETE, HEAD).
   • Formatos de entrada (JSON, XML), codificação de dados e tratamento de fusos horários.
   • Autenticação (BasicAuth, OAuth2) e controle de permissões (lgfapi_read/create/update/delete_access).
   • Versionamento da API, URLs, paginação, ordenação, seleção de campos e filtros avançados (operadores **gt,**lt, \_\_in, etc.).

2. Tratamento de respostas HTTP
   • Códigos de status comuns (200, 201, 204, 400, 404, 409, 500).
   • Formatos de erro padronizados (reference, code, message, details).
   • Esquemas de paginação (“paged” e “sequenced”) e uso dos cabeçalhos de paginação.

3. Módulo Entity
   • Consulta (“list” e “retrieve”), criação (POST) e modificação (PATCH) de recursos de negócio (IBLPN, OBLPN, inventory, order, container, etc.).
   • Filtros por campos, relacionamentos (“\_\_” para navegar por associações) e buscas por lote de valores.
   • Operações específicas de cada entidade (alocar, distribuir, paletizar, despachar, bloqueios em massa, QC, movimentação, etc.).
   • APIs de ciclo de contagem, notificação de eventos (tasks), anexos, mudanças de contexto de usuário e auditoria.

4. Módulos adicionais
   • Funções fora do core “entity”: data extract, pick-pack, printing, repack, replenishment, report, sort_receive, stage_track_record.
   • Cada módulo tem suas operações dedicadas (por exemplo, repack de LPNs, geração de relatórios, extração assíncrona de dados, impressão de etiquetas).

5. Operações disponíveis
   • Lista detalhada de endpoints para cada entidade e módulo: criação, atualização, operações em lote, consultas, geração de documentos e relatórios, métodos de tarefas, localização de trailers, execução de ondas de trabalho, etc.
   • Exemplos de payloads JSON/XML e descrições de parâmetros.

6. Extração de dados (Data Extract)
   • API para empurrar dados paramétricos de entidades a um bucket em Object Store (OCI, AWS S3, GCS, Azure Blob).
   • Configuração de endpoints, formatos de arquivo (CSV, JSON, Parquet), tamanho de partição, compressão e monitoramento de status assíncrono.

Em suma, o guia descreve em profundidade como integrar sistemas externos à Oracle WMS Cloud via REST, incluindo padrões de design, formas de autenticação e autorização, métodos de consulta e modificação de dados de estoque, orders, LPNs, tarefas e geração de relatórios, além de mecanismos para extração automatizada de grandes volumes de dados.

## Conteúdo extraído

Oracle Warehouse
Management Cloud
WMS REST API Guide
Release 25B

Oracle Warehouse Management Cloud
WMS REST API Guide
Release 25B
G29901-03
Copyright © 2025, Oracle and/or its affiliates.
Author: Oracle WMS Cloud Product Team

Oracle Warehouse Management Cloud
WMS REST API Guide
Contents
Get Help ................................................................................................................................ i
1 Overview 1
Change History ................................................................................................................................................................................ 1
End User License Agreement ...................................................................................................................................................... 4
Restful Web Services ..................................................................................................................................................................... 4
HTTP Requests ............................................................................................................................................................................... 5
Data Input Methodology ............................................................................................................................................................... 7
2 HTTP Response 11
Status Codes ................................................................................................................................................................................... 11
Response Formats ........................................................................................................................................................................ 12
Response Data Encoding ............................................................................................................................................................ 13
Response Data Formats .............................................................................................................................................................. 13
3 Entity Module 17
Supported Entities ........................................................................................................................................................................ 17
Entity Metadata ............................................................................................................................................................................. 17
Input Data Types ........................................................................................................................................................................... 17
Resource Result Set Filtering .................................................................................................................................................... 20
Resource Representations (GET) .............................................................................................................................................. 25
Resource Existence and Modification (HEAD) ....................................................................................................................... 36
Creating a Resource (POST) ...................................................................................................................................................... 38
Updating a Resource (PATCH) ................................................................................................................................................... 41
Entity Operations (GET /POST) .................................................................................................................................................. 59
4 Other API Modules 63
Additional API Modules .............................................................................................................................................................. 63
5 Supported Operations 65
Batch Number ............................................................................................................................................................................... 65

Oracle Warehouse Management Cloud
WMS REST API Guide
Bulk Change Eligible Group ....................................................................................................................................................... 65
Company ........................................................................................................................................................................................ 66
Container ........................................................................................................................................................................................ 67
Cycle Count .................................................................................................................................................................................... 75
Describe Entity ............................................................................................................................................................................. 90
Facility ............................................................................................................................................................................................. 90
IBLPN ............................................................................................................................................................................................... 91
IB Shipment .................................................................................................................................................................................. 119
Item ................................................................................................................................................................................................ 120
Inventory ........................................................................................................................................................................................ 121
Load ............................................................................................................................................................................................... 135
Location ........................................................................................................................................................................................ 138
OBLPN ........................................................................................................................................................................................... 146
Order Detail Serial Number ...................................................................................................................................................... 157
Pallet .............................................................................................................................................................................................. 158
Pick-Pack ....................................................................................................................................................................................... 161
Planned Parcel Shipment .......................................................................................................................................................... 177
Print ............................................................................................................................................................................................... 178
Putaway ......................................................................................................................................................................................... 185
Repack ........................................................................................................................................................................................... 190
Replenishment ............................................................................................................................................................................. 197
Report ........................................................................................................................................................................................... 202
Sales Order Header ................................................................................................................................................................... 203
SQL Selection (Rule Tree) ........................................................................................................................................................ 208
Sort and Receive ........................................................................................................................................................................ 209
T ask ................................................................................................................................................................................................ 213
Trailer ............................................................................................................................................................................................. 221
Waves ............................................................................................................................................................................................ 224
Attachments ................................................................................................................................................................................ 229
6 Data Extract 237
Data Extract ................................................................................................................................................................................. 237

Oracle Warehouse Management Cloud
WMS REST API Guide
Get Help
Get Help
There are a number of ways to learn more about your product and interact with Oracle and other users.
Get Help in the Applications
Access the online help from the user drop-down menu in the Warehouse Management application.
Get Support
You can get support at My Oracle Support. For accessible support, visit Oracle Accessibility Learning and Support.
Get Training
Increase your knowledge of Oracle Cloud by taking courses at Oracle University.
Join Our Community
Use Cloud Customer Connect to get information from industry experts at Oracle and in the partner community. You can
join forums to connect with other customers, post questions, and watch events.
Learn About Accessibility
For information about Oracle's commitment to accessibility, visit the Oracle Accessibility Program. (if videos) Videos
included in this guide are provided as a media alternative for text-based topics also available in this guide.
Share Your Feedback
We welcome your feedback about Oracle Warehouse Managment. If you need clarification, or find an error, you can
direct your questions via a service request to My Oracle Support.
i

Oracle Warehouse Management Cloud
WMS REST API Guide
Get Help
ii

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 1
Overview
1 Overview
Change History
Review what's new in this document.
Change Type Date Description
25B revisions Edits 4/16/25 Added sample payload to:
• IBLPN - Direct Consume API
• IBLPN - Split LPN API
25B release edits Edits 4/4/5 • Added Receive Sorted Item API
• User Eligible Facility API
• User Eligible Groups API
• User Eligible Company API
• Added the following fields to PATCH Order
Header:
◦ Priority
◦ Reference Number
◦ Special Instructions
◦ Sales Channel
◦ Gift Message
◦ Required Ship Date
◦ Start Ship Date and Stop Ship Date
• From Manufacturing Transaction
◦ from*manufacturing_transaction_hdr
◦ from_manufacturing_transaction_dtl
◦ from_manufacturing_transaction_dtl*
serial_nbr
• IBLPN/Receive API - added:
◦ allow_inv_exp_override_flg parameter
◦ allow_rem_exp_override_flg parameter
25A revisions Edits 2/19/25 • Repack/Pack Inventory - “to_oblpn_nbr"
and "orig_to_oblpn_nbr" parameters
• Added Other API Modules section
• Added Data Extract section (includes
Object Store API and Async Status API)
• Locate to Yard API
1

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 1
Overview
Change Type Date Description
25A revisions Edits 2/12/25 • Repack Close LPN, to_oblpn_lpn_type
parameter
• Cycle Count List API
• Print Shipping Label - added Print Parcel
Carrier Labels section
• Planned Parcel Shipment
25A release edits Edits 12/18/24 Added the following API updates:

• Print OBLPN Packing Slip
• Print Pallet Packing Slip
• Print Order Packing Slip
• Pick Pack/Pick Confirm – Allow Wave
Number as Optional Field
• IBLPN – Split LPN
• Report/Dock to Stock Per Day
• Report/Dock to Stock Per Shipment
• GET Cycle Count Adjustment Approval
Rule
• GET T ask Type
24D release edits Edits 9/19/24 Added the following API updates:
• Movement Request (parameters)
• Cycle Count Adjustment Summary
• Cycle Count Adjustment

Included new parameters to track user activity
in the following APIs:

• Modify Item Quantity
• Composite Create IBLPN
• Receive
• Split LPN for Replenishment
• Update Active Inventory API
• Create From IBLPN
• Pick Confirm
• Pack Inventory
• Replenish to Active

Included additional information about time
zone in the Input Data Types section.

24C revisions Edits 8/5/24 Updated the following APIs:
2

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 1
Overview
Change Type Date Description
• Inventory - Manufacturing Transaction
• IBLPN - Receive API, Item List
• Pick Pack - Pack Full LPN API
24C release edits Edits 7 /1/24 Added the follow APIs:

• Attachment Upload/GET /Delete
• Sort and Receive
• Manufacturing Transaction
• IBLPN GET All Distributions
• IBLPN Distribute
• IBLPN GET Next Distribution
24B release edits Edits 5/17 /24 Updated "Using the Wave Template" section in
Waves - Run Template.
24B release edits Edits 4/9/24 Added the following API updates:
• Movement Request API
24A revisions Edits 3/11/24 Added note about T asks for pick*pack/pick*
confirm API.
Updated Print Shipping Labels, Print LPN Labels
and Print Pallet Labels.

24A revisions Edits 2/13/24 Updated parameter for IBLPN - Deallocate API.
24A release edits Edits 1/9/24 Release T ask API - Print Labels
23D revisions Edits 11/16/23 Updates to Move LPN API, Pick Confirm API,
Repack Close LPN API.
23D release edits Edits 10/13/23 Updates to Receive API
23C revisions Edits 8/24/23 Locate LPN or Pallet
23C release edits Edits 7 /14/23 Added the following API updates:
• IB Shipment Patch API
• IB Shipment entity
• Receive API
• (Replenishment) Move LPN
• Cancel OBLPN
• Unload OBLPN
• Bulk Cancel

23B revisions Edits 6/7 /23 Added updates to Replenish to Active API
3

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 1
Overview
Change Type Date Description
23B release edits. Edits 4/14/23 Added the following API updates:
• Replenishment
• Receive Entire Shipment
• Update Lock Code/Expiry Date on an
Existing Batch
• Repack
• Receive API - receive UOM while receiving
a shipment
• Updated Pagination section in Resource
Representations

23A release edits. Edits 1/13/23 Added the following API updates:
Bulk Create, Batch Number

End User License Agreement
This guide is intended for REST API software developers with customers or system implementors. While the content
includes a reasonable overview of REST concepts, the assumption is that the audience understands REST, HTTP
communication, response codes, and related topics.
Restful Web Services
Representational State Transfer (REST) is a web standards-based architecture utilizing the HTTP protocol for data
communication. RESTful web services are a light weight, scalable, and maintainable way to allow web-based system-to-
system communication, irrespective of the respective application platforms (interoperability).
RESTful web services use HTTP methods in combination with a Universal Resource Identifier (URI) to implement the
REST architecture. For reference, a URL is a type of URI. This combination allows consumers to interact with application
data via a set of controlled, stateless, and idempotent methods.
Oracle Fusion Cloud Warehouse Management has had REST API’s prior to update 18C, however they were not designed
to provide fine grained access. These legacy API’s continue to be available. Once all the functionality provided by these
API’s are incorporated into the newer APIs, the legacy ones will be retired with sufficient notice. The new APIs also
adhere to RESTful practices better and simplify some of the data encoding requirements.
Note: Any APIs not documented in the “REST API Guide” or the “Integration API Guide” books are meant for internal
use by Oracle and subject to change without notice. We do not recommend you use them, but if you do, it is at your
own risk. Such APIs may change or be dropped at any time, either mid-release or with the next release.
4

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 1
Overview
HTTP Requests
RESTful web services are built on top of the HTTP protocol, which carries some important implications. First, each
request is stateless. This means that each request is independent of any other requests and the request itself must
contain all relevant data to fulfill the request. Second, certain types of requests should be idempotent; making identical
requests should yield the same result on the server. This is a safety measure that also provides consistency. For
example, when reading data the same request should always yield the same result assuming the resource’s state on the
server has not changed between requests.
HTTP Methods
The APIs may utilize the following five HTTP methods in order to provide users with Create-Read-Update-Delete (CRUD)
functionality. Note that not all APIs support all methods.
GET
Return a read-only representation of the selected resource(s) in the response body.
HEAD
Read-only check for resource existence and/or modification. Does not return a response body.
POST
Create resources or submit data to be processed by a resource operation.
PATCH
Modify existing resource(s).
DELETE
Remove/deactivate existing resource.
URL Format
The lgfapi URL structure is broken down into several components.
In general, lgfapi URLs following the following schema:
The first portion of the URL (protocol, domain, environment, and app) is consistent with the URL of the environment’s
UI accessed via a web browser. The remaining pieces after “lgfapi” are specific to the lgfapi and designate the version
and path to any child modules and/or resources.
5

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 1
Overview
Versioning
Lgfapi requires a version number in all URLs. The format is “v#’, starting with “v9” as the first release. New versions are
created only for major releases of the Oracle WMS Cloud application, not for minor versions. For example, the release
of WMS 9.0.0 included the lgfapi v9 release, but there will not be a new lgfapi version number with the release of WMS
9.0.1. However, the APIs will continue to be updated with new features and improvements along with the minor releases
of WMS.
The purpose of version control is to give customers some ability to remain on their current integrations until they can
complete any changes required to handle the newest lgfapi version. It is strongly encouraged that all customers use
the latest version of lgfapi. Version control is a tool to assist with upgrades and testing, it is not meant to be used in
production for extended periods of time. The previous versions of lgfapi will unavoidably become out of sync with
newer versions of WMS, and eventually will no longer be compatible. Oracle will not make changes to previous versions
of lgfapi in order to maintain expired functionality or compatibility. Therefore, it is always in the best interest to use
the latest version. New API versions are planned approximately once a year. Older API versions will be supported
approximately one year after a newer one is released.
lgfapi Modules
Lgfapi contains modules that can be utilized by customers. These are groupings of functionality that may have their
own formats and requirements. For example, lgfapi’s “entity” module is designed to allow customers to examine and
interact with OCWMS business resources from outside the application.
Resource Path
The final component to the URI is the resource path. This may take many different forms depending on the HTTP
method and any module-specific requirements.
Optional Trailing Slashes
A trailing slash at the end of and lgfapi URIs is optional and does not affect functionality.
lgfapi Archive Level
The lgfapi Archive Level feature in Warehouse Management will record data in the lgfapi Archive UI if you enable the
field ‘lgfapi Archive level’ for a user in the Users UI. The following are details about actions for lgfapi Archive Level:
• NONE - No archiving
• ALL - Archive all request/response
• ERROR - Archive only on error
• EDIT_AND_ERROR - Archive when the HTTP method is not HEAD or GET, or on error
Note: This feature is enabled for all Rest APIs included in this REST API Guide. However, it is not enabled for the
legacy APIs.
Login and Authentication
Since each HTTP request is stateless, every request requires information to authenticate the user.
6

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 1
Overview
Lgfapi supports several types of user authentication:
• BasicAuth – Classic username and password.
• OAuth2 – A token based authorization framework.
Application Permissions
Making a request to lgfapi not only requires user authorization, but also one or more of the CRUD application-level
permission to access the supported HTTP methods. These are configurable in the user’s group-level permissions.
• “lgfapi_read_access” – GET, HEAD
• “lgfapi_create_access” – POST
Note: this access is also required in order to run resource operations.
• “lgfapi_update_access” – PATCH
• “lgfapi_delete_access” – DELETE
It’s recommended to create dedicated user(s) with appropriate lgfapi permissions and different facility/company
eligibility to protect the integrity of your data. For instance, it is safe to give users read access but may not be
appropriate to grant them permission to create or modify data.
The legacy API permission, “can_run_ws_stage_interface”, has been replaced by the new permission,
“lgfapi_update_access”. This permission now applies to both lgfapi and the legacy APIs. For legacy API’s, this is the
singular permission required to access all APIs. For lgfapi, this is one of several new permissions used to control user
access.
Data Input Methodology
Lgfapi allows for transmission of data in one of two ways, based on the HTTP method being used.
GET /HEAD
These read-only HTTP methods allow the user to pass additional information about the request in the URI. This data is
sent as key-value pairs and starts with a question mark (“?”) at the end of the main URI. This section of the URI is known
as the “query string”. Each key-value pair is known as a “parameter”. It is used to provide additional information to the
resource. Parameters are delimited by an equals sign (“=”), and multiple parameters are delimited by an ampersand
(“&”). The order of the parameters does not matter.
URL Encoding
In general, URIs only allow ASCII values, however there are specific cases like with internationalized domain names
(IDN) where non-ASCII characters may be used in the domain name. For the purposes of communicating data using
query string parameters in lgfapi, you cannot directly send non-ASCII (unsafe) characters. Also, some characters like
spaces, “=”, and “&” have a specific meaning when sent in the query string section of the URI and are reserved. In order
to handle unsafe characters and to distinguish between data and reserved characters that have special meaning in a
URI, the URI must be “URL Encoded”. This encoding replaces non-ACII and reserved characters parameter data with
7

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 1
Overview
ASCII equivalents. This is also known as “Percent Encoding” since each unsafe character is replaced with a value starting
with percent sign (“%”). All parameter values should be URL encoded to ensure correct transmission.
For example, the query string: “foo=Mañana” is URL encoded as “foo= %20Ma%C3%B1ana”. A URI cannot have a space
so that is encoded to the value “%20”. The Spanish letter “ñ” is not a valid ASCII value and is encoded as “%C3%B1”.
Once the data reaches the server, it is decoded back to the original characters. The key portion of each parameter is
determined by the application and therefore will never contain unsafe characters.
See <https://www.w3schools.com/tags/ref_urlencode.asp> for more information.
It is possible to repeat the same parameter within the query string. However, lgfapi will only observe the final occurrence
of the parameter in order to obtain a value. For example, given the query string “?code=A&code=B”, the interpreted
value of the “code” parameter will be “B”. The “A” value is discarded. There is no use case for transmitting repeated
parameters as the desired result is achieved through other module-specific query string mechanisms.
POST
A POST request is used to pass data to the server similar to pressing a “Submit” button on a web page to submit form
data to the server. In the context of lgfapi, when making a POST request, the user is passing data to either create a
resource or invoke a resource operation, such as cancelling an order. Unlike GET and HEAD requests, POST allows for
text data to be passed in the free-form body of the request. Request body data must be in a supported format (JSON or
XML) and follow the required structure of the API being invoked.
Content-Type HTTP Header
This HTTP header is required when using a method like POST, PATCH, and DELETE that allow transmitting data in the
body of the request. It describes the data format so it can be correctly parsed server-side. Lgfapi supports JSON and
XML input and therefore requires one of the two content-type values:
• application/json
• application/xml
The Content-Type “application/x-www-form-urlencoded” is not supported in lgfapi, but is still required for legacy
OCWMS APIs.
Content Encoding
By default, lgfapi will use UTF-8 to decode the request body as this handles the majority of characters for languages
supported in OCWMS. However, for situations where customers choose to use a different encoding, it can be specified
in the Content-Type header’s optional “charset” parameter:
Content-Type: application/json; charset=latin-1
Lgfapi will use the provided charset to decode the request body data. It is up to the customer to ensure that their data
is properly encoded using the desired charset before transmission to lgfapi. Failure to do so may result in incorrect
characters or an inability to process the request.
It is also important to note that this only applies to the encoding of the request body and does not apply to the encoding
used in any response body data from lgfapi.
8

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 1
Overview
Request Body Data – Repeated Keys
Lgfapi does not restrict users from repeating data in the request body for a single request. Rather, it will use only the
final occurrence in the body when processing the request.
For example, if one were to send a request with the key “code” multiple times in the same request body:
{
“code”: “A”,
“code”: “B”
}
The value used to process the request will be “B”. “A” is ignored and is never used. There is no lgfapi use case for
needing to pass repeating data in the same request.
Request Body List Formatting
JSON and XML data follow language standards except for the case of lists of items in XML. This is a unique concern for
XML since there is no standard methodology for how to handle lists whereas JSON supports lists by default.
XML Lists
A list of items in XML is represented by the wrapper tag, followed by a wrapper for each item’s value with the special
tag name “list-item”. For example, representing a list of serial numbers under the wrapper “serial_nbr_list”, in JSON is
represent as:
{
“serial_nbr_list”: [ “SN1”,
“SN2”
]
}
The equivalent XML list would be represented as the following. Note the use of “list-item” for each entry in the list to
allow for correct parsing.
<serial_nbr_list>
<list-item>SN1</list-item>
<list-item>SN2</list-item>
</serial_nbr_list>
Note: lgfapi is not intended to be directly called from a browser and users attempting it may run into CORS policy or
other security errors. That is intended behavior. Use a non-browser application to make the API calls.
9

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 1
Overview
10

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 2
HTTP Response
2 HTTP Response
Status Codes
Every valid HTTP request receives a response that is comprised of three main components:
• A 3-digit response status code that gives information about the success or failure of the request, the returned
content, and other information specific to the request.
(2) The response header(s), which vary by request. These headers contain metadata information about the request, the
response, the response data, and/or attributes of the server.
(3) The response body where free-form text information can be returned to the requester in either JSON (default)
or XML format and in a standard defined by the application. This is where application-specific data pertaining to
representation, success, and errors is returned to the requester.
Comprehensive list of HTTP status codes: <https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html>
Lgfapi uses many of the available HTTP response status codes to convey success or failure of the request back to the
user. All response status codes fall into 1 of 4 categories:
1xx – Informational
2xx – Success
3xx – Redirection
4xx – Failure
The following is a list of commonly used response status codes for lgfapi:
Status Code Status Message HTTP Method Description
200 Ok HEAD, GET, POST GET - The request was successful.

HEAD - The resource exists.

POST - Resource exists and/or has
been modified.

201 Created POST Resource successfully created.
204 No Content POST The request was successful, but
no content is being returned in the
response body.
304 Not Modified HEAD The resource has not been updated
since the target date-time.
400 Bad Request HEAD, GET, POST Invalid data or request structure.
401 Unauthorized HEAD, GET, POST Invalid login credentials.
403 Forbidden HEAD, GET, POST User lacks permission.
11

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 2
HTTP Response
Status Code Status Message HTTP Method Description
404 Not Found HEAD, GET, POST The resource does not exist.
405 Method Not Allowed - HTTP method is not supported for
the requested resource.
409 Conflict HEAD, GET, POST Record Changed - The resource
was modified by a concurrent
operation before the request could
be fulfilled. Try again.
500 Server Error HEAD, GET, POST An unhandled error occurred or
the application was unable to
formulate a valid response. Please
contact support and provide any
returned error information.
Response Formats
Lgfapi supports JSON (default) and XML formats for data returned in the body of the response. This applies to all HTTP
methods that return a response body.
The requester is able to specify the response format in several ways:

1. Making a request without specifying the response format will result in the default JSON format.
2. Using the reserved “format” query string parameter in the URI when making a request.
   You can set the format to XML by adding “format=xml” to the query string portion of the request (the key-value pair
   data after the “?”). This is in addition to any other query string parameters also in the URI:
   … /resource/?format=json
   … /resource/?format=xml
   Note – “format” is one of the few query string parameters you can use with HTTP methods like POST, which typically
   require all data to be in the body of the request.
   • Using the file-extension dot-notation in the URI when making a request.
   Very similar to the example above, you can also request the format using dot notation like you would when giving a file
   the extension “.xml” or “.json”:
   … /resource/.json
   … /resource.xml (optional trailing slash)
   This can also be combined with a query string:
   … /resource/.xml?key1=value1&key2=value2
   12

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 2
HTTP Response
Response Data Encoding
When a response body is returned, the raw JSON or XML data will always be encoded using UTF-8. There is no way
to configure or specify the response body’s encoding. This is done to ensure that the response content can always be
correctly rendered. A request body using a different encoding is allowed because the requester is able to control the
contents being sent to lgfapi. However, the output data may contain characters outside of the encoding used for the
request, if for example a consistent character set has not been used throughout the application. UTF-8 covers the full
change of characters supported by OCWMS and is therefore the default, and generally preferred, encoding.
Response Data Formats
In general, the HTTP response body can take on any number of different formats and styles. For lgfapi, several
dedicated conventions have been adopted to give uniformity and consistency to the handling of both successful and
erroneous requests.
Error Response
A standardized error format is returned in the body of the response whenever there is an error while fulfilling the
request. This is accompanied by the response status code, which provides additional insight.
The standard error response is comprised of 4 components:
• Reference – A unique string used as reference for the request and error. This should be provided in support
requests to help more quickly identify the information pertaining to the request in question.
• Code – A generic classification pertaining to the error message.
• Message – An error message related to the code.
• Details – Optional. Either a list or key-value map (dictionary) of more detailed information pertaining to the
error(s). For example, this may give a more detailed list of error messages or could be a map of field name(s) to
error(s).
Example JSON Error Response Body:
{
"reference": "25b414f0-7a1d-4f35-ac3c-0ec9886cf37a", "code":
"VALIDATION_ERROR",
"message": "Invalid input.", "details": {
"reason_code": "Invalid Reason code"
}
}
Example XML Error Response Body:
13

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 2
HTTP Response

<?xml version="1.0" encoding="utf-8"?>
<error>
<reference>25b414f0-7a1d-4f35-ac3c-0ec9886cf37a</reference>
<code>VALIDATION_ERROR</code>
<message>Invalid input.</message>
<details>
<reason_code>Invalid Reason code</reason_code>
</details>
</error>
Unhandled Errors
It is possible that the application is unable to convey the nature of the problem back to the requester. In these scenarios,
the server will respond with a 500 (“Server Error”) status code and an accompanying message.
Resource Representations
Representations are by default paginated unless a specific resource is being requested. Pagination allows the response
data to be served in chunks (pages) to keep payload sizes manageable.
Pagination
A paginated result set is returned when multiple representations may exist in the result set that exceed a preset size.
This breaks the result set into chunks (pages), each with its own page number. The default page size is determined by
the requesting user’s configuration of the field “Rows per Page”. This is the same field used to set the number of results
per UI page returned. It has an allowed range of 10 to 125 results per page.
If a larger page size is needed, or a programmatic method is needed, the page_size GET query parameter is supported.
This allows a value up to a maximum of 1250. For example, adding &page_size=275 will cause results to be returned
with up to 275 records per page. Increasing the page size can be useful when extracting data for non-interactive
applications such as for reporting purposes. However, please be aware that excessive use of large page size values for
a high number of concurrent queries may degrade performance, depending on various factors such as overall dataset
size, current loads on the environment and other factors.
Pagination Mode
Two modes of pagination are supported that offer different advantages and disadvantages depending on the user
requirements. The default mode is “paged”, but users may specify the type of pagination by using the “page_mode”
query string parameter in the URI. The two types are “paged” and “sequenced”.
Mode: Paged
This is the default mode for result sets (…/resource/?page_mode=paged ). This will break the data into chunks (pages)
and return one page per request. This will additionally return metadata such as the total count of results and the total
number of pages.
14

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 2
HTTP Response
Each page of the result set is given a pagination header:
• result_count – The total number of results across all pages.
• page_count – The total number of pages.
• page_nbr – The current page number.
• next_page – Hyperlink to the next page (if available).
• previous_page – Hyperlink to the previous page (if available).
• results – The result set list for the page.
A specific page number for a paginated result set is requested in the URI’s query string using the parameter “page”.
For example, to request the data for page 3 of a result set, one would add …/resource/?page=3 . You will also see these
automatically added in the hyperlinks generated for “next_page” and “previous_page”.
An example of a paginated JSON response:
{
"result_count": 1,
"page_count": 1,
"page_nbr": 1, "next_page": null, "previous_page": null, "results":
[
{
"id": 0,
…
},
]
}
An example of a paginated XML response:

<?xml version="1.0" encoding="utf-8"?>

<entity_name>
<result_count>1</result_count>
<page_count>1</page_count>
<page_nbr>1</page_nbr>
<next_page></next_page>
<previous_page></previous_page>
<results>
<list-item>
<id>0</id>
15

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 2
HTTP Response
…
</list-item>
</results>
</entity_name>
Mode: Sequenced
The sequenced mode (…/resource/?page_mode=sequenced ) is similar to the Paged mode, except for a few important
details. This mode is recommended for system to system integration where superfluous information and intuitive/
human-readable values are not necessary.
Each page of the result set is given a header that conveys extra information to the user and makes it easier to navigate
between pages:
• next_page – Hyperlink to the next page (if available).
• previous_page – Hyperlink to the previous page (if available).
• results – The result set list for the page.
First, you’ll notice that the pagination header does not have the total result count or total page count. This is because
sequenced pagination doesn’t know either of these values, and doesn’t want to. Instead, each page is generated on the
fly in an effort to improve performance, which means less work than paged mode where the total counts are fetched up
front. Determining total count can be expensive when you have a large result set.
With sequenced, you also sacrifice some human readability and functionality as the “page” query string parameter
is replaced by a system-generated “cursor” as well as the hyperlinks will not be as intuitive to understand. Since in
this mode the total result set is not known, only what’s rendered per page, there is no way to report the total number
of pages or label each with a specific page number. A cursor identifier is generated for each page instead of a page
number:
… /resource/?cursor=cD0xNDAw&page_mode=sequenced
Non-Paginated Responses
There are a few scenarios where a request will return data in the body of the response for a specific object, so
pagination is not needed.
The first is for a GET retrieve style request where the “id” value of the resource is known and is requested in the URI (…/
resource/{id}/).
The second is when creating a single resource using a POST request. The response will be a non-paginated
representation for only the new resource.
16

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
3 Entity Module
Supported Entities
The lgfapi entity module is used to access and modify OCWMS application data. It exposes specific methodologies for
identifying subsets of data and obtaining their representations as well as allowing for the creation of certain resources.
The entities supported and corresponding functionality will continue to be expanded through subsequent releases.
The entity module has a documenting feature that can be accessed via a GET request to the top-level (root) URL (… /
lgfapi/v10/entity/). This will return a sorted list of supported entities for the given lgfapi version and an accompanying
base URL.
Each entity represents an object or combination of objects within OCWMS that is accessible via lgfapi. However, not
all entities support all HTTP methods. Furthermore, these entities may share characteristics with their respective
counterparts in other areas of the OCWMS application, but as a whole should be considered independent of other
application functionality.
Entity Metadata
It is possible to obtain additional information for each entity by making a GET request to the “describe” entity
operation (… /lgfapi/v10/entity/{entity_name}/describe/). This will return metadata that can be used to further your
understanding of the entity. See “Entity Operations” section for more details.
Input Data Types
Lgfapi supports user input depending on the HTTP method:
• GET /HEAD
◦ Query string parameters
• POST
◦ Request body data

- The format must be JSON or XML
  ◦ The “format” query sting parameter alone is supported to specify the desired format for the response.
  Although the input formats may be type ambiguous, the input value is cast to the appropriate type as defined in
  the entity’s field metadata. Some fields have naming conventions that are outlined below. The following types are
  supported for user input:
  String/Text
  Query String: …/?field=abc123
  JSON: {“field”: “abc123”}
  17

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
XML: <field>abc1234</field>
Integer
Query String: …/?field=123
JSON: {“field”: 123}
XML: <field>123</field>
Numeric/Decimal
Query String: …/?field=1.234
JSON: {“field”: "1.234"}
XML: <field>1.234</field>
Note: Special Note about Numeric/Decimal Values: When sending decimal values in a JSON request, it is
recommended to send them wrapped in double quotes like a string value, as seen in the example above. This will
prevent against any loss of precision as part of the lgfapi request.
Boolean
Except for a few specific cases, all True/False Boolean field names end with “\_flg”.
The input value for all formats should be either “true” or “false”.
Query String: …/?field_flg=true
JSON: {“field_flg”: true}
XML: <field_flg>true</field_flg>
Temporal (Date/Time)
All date, time, and date-time fields require the iso-8601 format: YYYY-mm-ddTHH:MM:SS.ffffff
Note that the microsecond component “f” is optional. Using January 30th, 2018 at 6:30pm as an example:
Date
Field names for date-only fields typically end with “\_date”.
Query String: …/?field_date=2018-01-30
JSON: {“field_date”: “2018-01-30”}
XML: <field_date>2018-01-30</field_date>
Time
Field names for time-only fields typically end with “\_time”.
Query String: …/?field_time=18:30:00
JSON: {“field_time”: “18:30:00”}
XML: <field_time>18:30:00</field_time>
18

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Date-time
Field names for date-time fields typically end with “\_ts”.
All Date-time objects are assumed to be in the time zone of the user’s facility context. In other words, it should be the
date/time you would expect to see if viewed by the user in the UI.
Query String: …/?field_ts=2018-01-30T18:30:00
JSON: {“field_ts”: “2018-01-3030T18:30:00”}}
XML: <field_ts>2018-01-3030T18:30:00</field_ts>
Date/Time Values and Time Zones
It is a recommended best practice to always pass time zone aware date-time values that include the time zone offset
component so that there is no ambiguity. The following examples show the time zone specified as Indian Standard Time

- IST (+05:30):
  • Query String: field_ts=2024-08-07T00:00:00+05:30
  • JSON: {“field_ts”:“2024-08-07T00:00:00+05:30”}
  • XML: <field_ts>2024-08-07T00:00:00+05:30</field_ts>
  This data-time indicates 12:00 am on August 7th in India. The date is converted and stored in WMS appropriately using
  the offset provided on the field. When this date time is pulled up in a WMS UI screen, it would be displayed as per the
  time zone of the default facility of the user. For example, in an IST facility (Tz +05:30), the user would see this as 12:00
  am of August 7th. In a Singapore facility (Tz +08:00), the user would see this as 2:30 am on August 7th.
  • Query String: field_ts=2018-01-30T18:30:00
  • JSON: {“field_ts”: “2018-01-3030T18:30:00”}
  • XML: <field_ts>2018-01-3030T18:30:00</field_ts>
  Additional Note about Timezone
  If sending a time zone component, ensure that the API user's default facility time zone is same as the time zone of the
  facility in the payload, else the conversion may result in undesirable results
  Example 1:
  o API user's default facility time zone: +05:30
  o Time zone of the facility passed in the payload: +05:30
  o Timestamp sent with any time zone is converted appropriately.
  Example 2:
  o API user’s default facility time zone: +08:00
  o Time zone of the facility passed in the payload: +05:30
  o Timestamp sent with any time zone is NOT converted appropriately.
  If you are managing facilities in multiple time zones, ensure that you create as many API users as the number of time
  zones. Each user needs to have a default facility that represents a different time zone and used for posting API requests
  for the facilities in the respective time zones to avoid undesirable results as described in Example 2.
  19

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
The other option is to use time zone naïve data-time value as described below.
If a time zone naive date-time value is received by lgfapi, it is assumed to be in the time zone of the API user’s default
facility. In other words, it would be the date/time you expect to see if viewed by the user in the UI for their default
facility. These are date-time values that DO NOT include the time zone offset component as illustrated in the following
example.
• Query String: field_ts=2024-08-07T00:00:00
• JSON: {“field_ts”:“2024-08-07T00:00:00”}
• XML: <field_ts>2024-08-07T00:00:00</field_ts>
In this example, if the API user's default facility is Atlanta (Tz -04:00 EDT), the date-time value indicates 12:00 am on
August 7th in Atlanta. The date is converted and stored in WMS appropriately using the time zone of the API user’s
default facility. When this date time is pulled up in a WMS UI screen, it would be displayed as per the time zone of the
default facility of the user. For example, in an ATL facility (Tz -04:00 EDT), the user would see this as 12:00 am of August
7th. In a Singapore facility (Tz +08:00), the user would see this as 12:00 pm on August 7th.
Relational
Relational fields are when one resource has a link to another resource. These fields always end in “\_id” and by default,
are integer values. They are unique when filtering, in that you can use the double-underscore (“**”) notation to
reference a related resource’s fields, or even nested related resources. This is covered in more detail in the Resource
Result Set Filtering section.
Query String: …/?field_id=1
JSON: {“field_id”: 1}
XML: <field_id>1</field_id>
Resource Result Set Filtering
Lgfapi offers the ability to apply filters to GET and HEAD requests in order to narrow down the final result set. This is
done by adding query string filter parameters to the URI. Furthermore, lgfapi supports several built-in lookup functions
to assist in common filtering tasks.
It is important to note that all entity data is automatically filtered by the user’s eligible facilities and companies. This
prevents users from being able to access and/or change data outside of their assigned scope that same way that data is
isolated in the UI or RF features. The difference with lgfapi is that users may access data from multiple eligible facilities
and companies in a single request. In the UI and RF, this typically requires manually changing the user’s context.
The most basic format for a filter uses simply the exact operator (“=”): …/?field=value
This can be chained to apply multiple filters: …/?field1=value1&field2=value2
Lgfapi uses double underscore (“**”) notation in order to join multiple fields or functions in the query string filters.
The double underscore is used to distinguish the field names when filtering on a related resource’s attributes or when
applying a lookup function.
Applying a lookup function: …/?field**lookup=value
Filtering on a related resource: …/?relation_id**related_field=value
20

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Applying a lookup function on a related resource: …/?relation_id**related_field**lookup=value
Supported Lookup Functions
The following lookup functions are provided by lgfapi. Note that any match function with a corresponding “i” function
means that function is case-insensitive. For example, “exact” is used to match exactly on a value, as does “iexact”
except that the latter ignores upper/lower case.
Arithmetic Lookups
gt – Greater than
Example: Filtering sales order detail(s) for only those with an ordered quantity.
…/order_dtl/?ord_qty**gt=0
• gte – Greater than or equal to
Example: Filtering sales order detail(s) for only those with an ordered quantity.
…/order_dtl/?ord_qty**gte=1
• lt – Less than
Example: Filtering sales order detail(s) for only those with ordered quantity below 10.
…/order_dtl/?ord_qty**lt=10
• lte – Less than or equal to
Example: Filtering sales order detail(s) for those with ordered quantity at or below 10.
…/order_dtl/?ord_qty**lte=10
Text Match Lookups
• contains/icontains – Text contains substring
Example: Filtering sales order(s) for orders with “FOO” in the order_nbr field.
…/order_hdr/?order_nbr**contains=FOO
Example: Same as previous example, but ignore case.
…/order_hdr/?order_nbr**icontains=FOO
• exact/iexact – Text exactly matches
Example: Match sales order(s) exactly on the order number.
…/order_hdr/?order_nbr\_\_exact=ORDER001
Note: “Exact” is not typically needed. The above filter condition does not require the exact lookup since this is
automatically implied by the exact operator (“=”).
21

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
The query string can be simplified to:
…/order_hdr/?order_nbr=ORDER001
“iexact”, on the other hand, is a useful tool when you need to do an exact match, but ignore letter casing:
…/order_hdr/?order_nbr**iexact=OrDeR001
• startwith/istartswith – Text starts with
Example: Filtering sales order(s) for only those whose order_nbr starts with “ORD”:
…/order_hdr/?order_nbr**startswith=ORD
• endswith/iendswith – Text ends with
Example: Filtering sales order(s) for only those whose order_nbr ends with “001”:
…/order_hdr/?order_nbr**endswith=001
Temporal (Date/Time) Lookups
The following temporal functions may only be used on date, time, and/or date-time data. Consider the “order_hdr”
entity’s “order_shipped_ts” date-time field with a value “2018-09-17T20:30:59”:
• year – Match on a date’s year (date or date-time).
…/order_hdr/?order_shipped_ts**year=2018
• month – Match on a date’s month (date or date-time).
…/order_hdr/?order_shipped_ts**month=09
• week_day – Match on a date’s day of the week (date or date-time).
T akes an integer value representing the day of week from 1 (Sunday) to 7 (Saturday).
…/order_hdr/?order_shipped_ts**week_day=2
• day – Match on a date’s day (date or date-time).
…/order_hdr/?order_shipped_ts**day=17
• hour – Match on a date’s hour (time or date-time).
Assumes a 24-hour clock.
…/order_hdr/?order_shipped_ts**hour=20
• minute – Match on the time’s minutes (time or date-time).
…/order_hdr/?order_shipped_ts\_\_minute=30
You can also apply other lookup and arithmetic functions to temporal fields:
• Date Range
22

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
For example, if we have a date-time field where we want to search for resources that have a value within a range, it is
possible to chain two temporal filters together to search within a set date range:
…/order_hdr/?order_shipped_ts**gte=2018-09-01T00:00:00&order_shipped_ts**lt=2018-10-01T00:00:00
Or, it is possible to use the “range” lookup function:
…/order_hdr/?order_shipped_ts**range=2018-09-01T00:00:00,2018-10-01T00:00:00
However, since in this example we don’t have any specific time data, this could have also been accomplished more
easily using the “month” lookup:
…/order_hdr/?order_shipped_ts**month=09
There may be multiple different ways to arrive at the same result when filtering. It is always desirable to be as specific as
possible to minimize the result set and improve efficiency.
Additional Lookups
• isnull – Boolean; Is the field’s value null?
This lookup is used to test if a field is null. This is a useful lookup as it can be used on any type of field to test for null.
Example: Filtering sales order(s) for only those where the shipped timestamp is null:
…/order_hdr/?order_shipped_ts**isnull=true
This is important because it allows you to make this test for any field type. If, for example, you tried to filter on the field’s
value directly (…/order_hdr/?order_shipped_ts=null), you would receive an error that “null” is not a valid date. Since the
field is of type date-time, it is expecting a temporal value and is interpreting “null” as the input.
• in – Filter by values in a list
This lookup function allows for filtering by a group of values. These values may be a mix of different types, but the
type(s) should be consistent with the type of the field being filtered. The input is a comma-delimited list with no spaces
between entries in the list.
Example: Filter order_hdr by specific status id values:
…/order_hdr/?status_id**in=10,30,90
Or, it can be applied for filtering on a specific set of sales order numbers:
…/order_hdr/?order_nbr**in=ORDER001,ORDER002,ORDER003
It is also possible to use an “in” lookup with a single value to effectively function the same as an exact operator (“=”).
The two following examples are equivalent in that they will return the same result set:
…/order_hdr/?order_nbr=ORDER001
…/order_hdr/?order_nbr**in=ORDER001
The difference is that an “in” lookup in inherently slower because of the way the filter is built and applied when filtering
the data. If you have a single value to match on, it is recommended to use “=” instead of “in”.
• range – Filter for resources with value within an inclusive range.
Numeric range
23

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
…/order_hdr/?status_id**range=10,90
Date range
…/order_hdr/?order_shipped_ts**range=2018-09-01T00:00:00,2018-10-01T00:00:00
Relational Resource Filtering
It is possible to filter on any related field for the given entity. All related field names end with “\_id” and are integers by
default.
For example, the simplest and fastest performing related resource filter is to search directly on the resource’s id. An “id”
is the unique value assigned to every resource. Using the “order_hdr” field, “facility_id”, we could filter specifically for
order belong to the facility with id “1”:
…/order_hdr/?facility_id=1
Adding the “company_id” field is a very common thing to do, in order to filter resources by facility and company
(assuming the company’s id is also “1”):
…/order_hdr/?facility_id=1&company_id=1
But what if we wanted to filter by the value of a field belonging to the related resource. For example, what if we knew
the facility and company codes, but didn’t yet know their respective “id” values. It is possible to filter on the related
resource’s fields using double-underscore (“**”) notation.
Assuming facility with id=1 has a code “FAC1” and company with id=1 has a code “COM1”:
…/order_hdr/?facility_id**code=FAC1&company_id_code=COM1
This is not as efficient as using just the “id” of the related resources since lgfapi will need to do an additional lookup for
each related resource to filter on their respective “code” fields. It is recommended to cache client-side the “id” values of
commonly used, static entities (like facility and company) in order to improve performance in high-throughput systems.
It is also possible to filter multiple levels deep with related resources. For example, in order to filter on the order’s
facility’s parent company, we could further chain the facility field, “parent_company_id”, as it is a related resource of
“facility_id” and of entity type “company”:
…/order_hdr/?facility_id**parent_company_id=1
Again, you can also search on a related field:
…/order_hdr/?facility_id**parent_company_id_code=COM1
This is a handy and powerful tool for looking up resource sets based on related data. However, it is important to
remember that as the relational filter depth increases, the performance may decrease as well since there is more work to
be done to lookup related resource(s). Client-side caching and other performance methodologies are discussed in their
own section.
Chaining Multiple Filters
It is possible to chain multiple filters on the same field. Each condition is just another key-value pair where the field is
consistent. For example, if we wanted to filter the order_hdr entity to return those whose order_nbr starts with “ABC”
and additionally contains the word “TEST”, we would write it as:
…/order_hdr/?order_nbr**startswith=ABC&order_nbr**contains=TEST
24

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
It is possible to chain together any number of different field and lookup combinations to arrive at your desired result set.
However, it is important to note that the more filters applied, the more the performance may degrade. Therefore, it is
always preferred to be as specific as possible when using filtering.
Resource Representations (GET)
Within the lgfapi entity module, JSON or XML resource representation(s) of entity(s) may be obtained through a GET
request. A GET request is made for a specific entity in the format:
…/lgfapi/v10/entity/{entity_name}/
By default, each request is filtered by the requesting user’s eligible facility(s) and company(s). It is possible to add
additional filter conditions in the URI query string in order to arrive at the data required. If, after filtering, no data is
found, a 404 – Not Found error will be returned in the standard lgfapi response.
Furthermore, there are two conventions for how to request resource representation(s) – “list” and “retrieve”. For the
following examples, the “company” entity will be used.
List
A list request is used to fetch one or more object representations of an entity. The result set is based on the default
facility/company context filters and any optional filter parameters provided in the URI. The default results set is
comprised of all resources for the given entity that are eligible to the requesting user. Since the result set may be of an
arbitrarily size, a paginated data set is always returned.
The representation for all eligible objects can be requested by not providing the query string portion of the URI:
…/lgfapi/v10/company/
Query string filter parameters may optionally be used to further narrow down the data set. For example, to filter
additionally by company code “ABC”, we would add the following:
…/lgfapi/v10/company/?code=ABC
Retrieve
A retrieve request is used to fetch a single resource by its integer “id” value. This is the most performant way to get a
representation for a single resource where the “id” is known. The result set is not paginated. The “id” value is specified
in the URI after the entity name:
…/lgfapi/v10/company/{id}/
For example, if we had previously looked up the company with code “ABC” and found its “id” value to be 1, we could
retrieve its representation in the future by making a GET request to the URI:
…/lgfapi/v10/company/1/
Note that since the lookup is for a specific resource, no filters are allowed in the query string. It is permitted to pass
in allowed non-filter reserved parameters like “format” and “fields”. However, any pagination related query string
parameters like “page_mode” are not supported since the returned representation is not paginated.
25

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Note: …/lgfapi/v10/company/?id=1 is still considered a “list” style request and is paginated.
Last-Modified HTTP Header
If the requested resource exists and the data is temporally tracked, the Last-Modified HTTP header will be returned.
This is the date-time that the resource was last updated. It is in iso-8601 format in the requesting user’s time zone.
This can be cached client-side and used in conjunction with HEAD requests as an efficient way to check for resource
modification.
Resource Representation Data Conventions
For both list and retrieve GET requests, the “format” query string parameter can be passed in order to convey the
desired response format as “json” (default) or “xml”.
Hyperlink-Related Resource Representations
All resources use hyperlinked representations for related resource fields. These are the fields whose name ends
with “\_id”. They represent another entity resource that can generate its own representation using the hyperlink
provided. Lgfapi uses hyperlinked relationships to allow for users to crawl to the intended data sets. This allows for the
preservation of RESTful principals as well as to keep the data interchange sizes manageable.
All related field representations contain three pieces of information:

1. “id” – The integer id value of the related resource
2. “key” – A string identifier for the related resource
3. “url” – A crawl-able retrieve style hyperlink to the related resource
   ◦ Both “id” and “key” are always provided. However, the value for “url” may be blank if the related resource
   it not one of the supported entities. In this case, it is not possible to build a hyperlink to the resource as it
   does not support generating its own representations.
   For example, when getting a representation for the “company” entity where the company is of type Regular, the related
   field “company_type_id” would be represented like the following JSON string:
   {
   …
   “company_type_id”: {
   “id”: 1,
   “key”: “R”,
   “url”: “https://…/wms/lgfapi/v10/entity/company_type/1”
   },
   …
   }
   26

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Or, if the desired format is XML:
<company>
…
<company_type_id>
<id>1</id>
<key>R</key>
<url>https://.../wms/lgfapi/v10/entity/company_type/1</url>
</company_type_id>
…
</company>
The only exception for the related field representation format is for status_id related fields. These fields are always
represented as only the related resource’s integer “id” value. It is possible to get a representation for any status-based
entity by making a retrieve request. The only difference is that due to the volume of status fields on various entities, the
integer value is used to reduce payload size.
For example, the “order_hdr” entity has the related field “status_id” for the entity “order_status”. It is represented on the
“order_hdr” as just the “id” value:
{
…
“status_id”: 10,
…
}
However, it is possible to get a representation of the status by making the request:
GET https://.../wms/lgfapi/v10/order_status/10
Important
There are many related resource fields that are optional. If there is no linked resource, the field’s value will be “null” if
using JSON or an empty tag if using XML. For more information, reference the entity’s field metadata for the “required”
attribute.
Related Data Sets
The related resources previously discussed all link to a single resource. However, it is possible that the current resource
has a list many other linked resources of the same type. A good example is a sales order header that has one or more
child details. As a convenience and additionally for guidance/performance reasons, many entity representations have
additional hyperlinked relations to these data sets. These field names always end in “\_set”.
27

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Continuing the sales order header example, the order details set could be represented as the following in an order_hdr
retrieve representation. Assume there are two detail line items and the “id” value of the order_hdr entity is “123”.
GET https://.../wms/lgfapi/v10/entity/order_hdr/123
{
“id”: 123,
…
"order_dtl_set": {
"result_count": 2,
"url": "https://.../wms/lgfapi/v10/entity/order_dtl/?order_id=123"
},
…
}
It’s important to note that unlike the “\_id” related resources which have a retrieve style hyperlink to the specific resource,
“\_set” related representations use list style with query string filters in order to return a paginated list of 1 to n resource
representations. Also, instead of giving the “id” and “key”, the related count is returned.
If no related resources are found for the set, the value will be “null” for JSON representations and an empty tag for XML.
If you need to query an entity to return all entities with \_set value being null, then you can query it as follows:
Example: for purchase_order_hdr you can query as follows:
https//…<cloud WMS instance path>/wms/lgfapi/v10/entity/purchase_order_hdr?purchaseorderdtl**isnull=true
Example Output
The following is an example output that you will see for REST API GET operation for purchase order entity which have
no details on them.
{
"result_count": 138,
"page_count": 6,
"page_nbr": 1,
"next_page": “https//… intqa.wms.ocs.oraclecloud.com:443/lgf_22a_qa/wms/lgfapi/v10/entity/
purchase_order_hdr?page=2&purchaseorderdtl**isnull=true",
"previous_page": null,
"results": [
{
"id": 1176,
"url": "https//…intqa.wms.ocs.oraclecloud.com:443/lgf_22a_qa/wms/lgfapi/v10/entity/
purchase_order_hdr/1176",
"create_user": "",
"create_ts": "2014-04-10T12:01:48.391494+05:30",
"mod_user": "SMALL01",
"mod_ts": "2014-04-10T12:01:48.391494+05:30",
"facility_id": {
"id": 647,
"key": "QATRN01",
"url": "https//…intqa.wms.ocs.oraclecloud.com:443/lgf_22a_qa/wms/lgfapi/v10/entity/facility/647"
},
28

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
"company_id": {
"id": 369,
"key": "QATSTPC",
"url": "https://...intqa.wms.ocs.oraclecloud.com:443/lgf_22a_qa/wms/lgfapi/v10/entity/company/369"
},
"po_nbr": "POSMA001",
"status_id": 0,
"ord_date": "2014-04-10",
"ref_nbr": "1STPO",
"po_type_id": null,
"delivery_date": "2014-04-14",
"vendor_id": {
"id": 390,
"key": "VNDR048",
"url": "https://...intqa.wms.ocs.oraclecloud.com:443/lgf_22a_qa/wms/lgfapi/v10/entity/vendor/390"
},
"dept_code": "",
"ship_date": "2014-04-15",
"cancel_date": "2014-04-15",
"lock_id": null,
"cust_nbr": "",
"cust_name": "",
"cust_addr": "",
"cust_addr2": "",
"cust_addr3": "",
"rma_nbr": "",
"sold_to_legal_name": "",
"cust_field_1": "PO1",
"cust_field_2": "",
"cust_field_3": "",
"cust_field_4": "",
"cust_field_5": "",
"purchase_order_dtl_set": null
},
Similarly, some of the other entities which contain sets and how they can be queried are as follows:
IB_shipment (all inbound shipments which have no shipment details):
https://...<cloud WMS instance path>/wms/lgfapi/v10/entity/ib_shipment?ibshipmentdtl**isnull=true
Work_order_hdr (all work order headers which have not ktis on them):
https://...<cloud WMS instance path>/wms/lgfapi/v10/entity/work_order_hdr?workorderkit**isnull=true
Work_order_kit (all kits that have no components):
https://...<cloud wms instance path>/wms/lgfapi/v10/entity/work_order_kit?workordercomponent**isnull=true
Container (for all containers that have no inventory locks on them):
https://...<cloud wms instance path>/lgfapi/v10/entity/container?containerlockxref**isnull=true
Inventory (for all inventory that have no serials associated):
29

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
https://...<cloud wms instance path>/wms/lgfapi/v10/entity/inventory?inv_serial_nbr_id**isnull=true
Order_hdr (for all order hdrs what have no order details):
https://...<cloud wms instance path>/wms/lgfapi/v10/entity/order_hdr?orderdtl**isnull=true
Order_hdr (for all order hdrs that have no order locks):
https://...<cloud wms instance path>/wms/lgfapi/v10/entity/order_hdr?orderlockxref\_\_isnull=true
Field Selection
GET requests for the lgfapi entities support the “fields” query string parameters. It takes a comma-delimited list of field
names for the entity and returns only those fields in the representation.
For example, to return only the “id” and “code” for all eligible companies using a list style request with no filters:
GET https://.../wms/lgfapi/v10/entity/company?fields=id,code
The “fields” parameter can be combined with filter parameters and other parameters with special meaning, like
“format”. Here is a more complex example if one wanted to search for all eligible companies of type regular and return
only the “id” and “company” for each company entity found, in XML format:
GET https://.../wms/lgfapi/v10/entity/company?fields=id,code&format=xml&company_type_id=1
This can also be applied to retrieve style request for a specific resource:
GET https://.../wms/lgfapi/v10/entity/company/1?fields=id,code
This is an important tool when performance is of concern. If it is known ahead of time that only specific field values are
required, narrowing the returned data set using the “fields” parameter can greatly reduce the overall payload size and
remove the need for unnecessary field and/or relation lookups.
Ordering
By default, no ordering is applied to list style GET requests that can return 0 or more representations. This is done for
performance considerations as applying ordering to any request may degrade performance, especially in the case of
larger data sets.
It is possible to specify an order-by clause for list style requests using the “ordering” query string parameter. It accepts a
comma-delimited list of field names by ordering priority.
For example, one could request all eligible companies and order by the type and then the code:
GET https://.../wms/lgfapi/v10/entity/company/?ordering=company_type_id,code
By default, fields are ordering ascending. To order by descending value, add a dash (“-“) before the field name in the
ordering list. This can be applied to order first by company type ascending and then company code descending:
GET https://.../wms/lgfapi/v10/entity/company/?ordering=company_type_id,-code
30

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Just like any other query string parameter, it may be chained with other parameters and filters.
Querying Multiple Entities in one GET Request using “values_list”
Currently lgfapi GET queries can retrieve data related to one entity, whether it fetches objects (all the fields of the entity)
or a specific list of fields (using the fields parameter). With this new experimental feature called “values_list”, you can
now fetch data from other related entities also without the need to do multiple GET requests for each entity separately.
The benefits that you will get from this feature is that you can very easily query related data across multiple entities
which results in better performance as it fetches less data in the most efficient way possible. It is similar to running a
database SQL query by joining multiple tables instead of executing multiple separate queries, one per table.
Note: You need to know the relationships between various entities to use this feature effectively. The entity
relationships are described via the self-documenting nature of lgfapi as documented elsewhere in this guide. Another
resource is the list of entities (categories) that are listed in the web reports gen2 documentation, along with the
relationships.
Example 1: Order type code for a specific order
Let's say that you wanted to look up the company type code for a specific Order with id 1, using lgfapi. In order to get the
company type code you needed to make the following sequence of requests.
Step 1: Fetch the order_hdr to get the associated Company’s id.
GET .../entity/order_hdr/1
{
...
"company_id": {
"id": 48,
"key": "CM_COMP",
"url": ".../wms/lgfapi/v10/entity/company/48"
},
....
}
Step 2: Now that you have the company id, you can fetch the company entity to get company type
GET .../entity/company/48
{
...
"company_type_id": {
"id": 1,
"key": "R",
"url": ".../entity/company_type/1"
},
....
}
Now with value list feature, you only need one request.
GET .../entity/order_hdr/1?values_list=company_id**company_type_id**code
{
"company_id**company_type_id**code": "R"
31

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Note: The response field name will match the field names from the "values_list" parameter.
Let's break down the request:

1. Making a GET Request to the order_hdr entity
2. This is the order id value that we are filtering on
3. New feature values_list
4. Company_id is the foreign key between order hdr and company entities
5. Company_type_id is the foreign key between company and company_type entities
6. Code is what you are looking for ie. Order type code
   Example 2: Get the order number, ship via id and the ship via code for all orders of type ‘01’
   A query to lookup order hdr records with order type code of ‘01’ can already be represented in lgfapi as:
   GET .../lgfapi/v10/entity/order_hdr?type_id**code=01
   The ability to retrieve a values_list of field data for a filtered set of object and their related objects may now be used:
   GET .../lgfapi/v10/entity/order_hdr?
   type_id**code=01&values_list=order_nbr,ship_via_id,ship_via_id**code
   The ability to retrieve a values_list of field data for a filtered set of object(s) and their related objects may now be used:
   GET .../lgfapi/v10/entity/order_hdr?
   type_id**code**in=01,02,03&values_list=order_nbr,ship_via_id,ship_via_id**code
   Get All Information for a Load
   Example of a query to get all information for a load:
   <wms instance url>/wms/lgfapi/v10/entity/ob_stop_dtl?
   values_list=ob_stop_id**shipto_facility_id**code:facility,
   ob_stop_id**shipto_facility_id**name:Name,
   ob_stop_id**shipto_facility_id**address_1:Address,
   ob_stop_id**shipto_facility_id**zip:Zip,
   ob_stop_id**shipto_facility_id**state:State,
   ob_stop_id**load_id**load_nbr:load_nbr,
   container_id**container_nbr:container_nbr,
   container_id**cntr_inv**item_id**code:item_code,
   container_id**cntr_inv**to_from_inv**order_dtl_id**order_id**order_nbr:order_nbr,
   container_id**cntr_inv**to_from_inv**order_dtl_id**seq_nbr:order_seq_nbr,
   container_id**cntr_inv**batch_number_id:batch&ob_stop_id**load_id\_\_load_nbr=OBL0000003712
   32

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Paginated Response
When doing a GET request using filters and values_list, the response structure will still be paginated - the same as a
normal request of this type without "values_list":
{
"result_count": 20,
"page_count": 1,
"page_nbr": 1,
"next_page": null,
"previous_page": null,
"results": [
{
"order_nbr": "ORDER001",
"ship_via_id": 123,
"ship_via_id__code": "UPS1D"
},
{
"order_nbr": "ORDER002",
"ship_via_id": 456,
"ship_via_id__code": "FEDX2D"
},
...
]
}
Example 3: Do the same query as the previous example, but for a specific order using its id.
The same can also be done with the retrieve GET request using a specific object's ID in the URL:
GET .../lgfapi/v10/entity/order_hdr/123?
values_list=order_nbr,ship_via_id,ship_via_id**code
Non-Paginated Response
When doing a GET request using the ID in the URL with values_list, the response will not be paginated - the same as a
normal request of this type without "values_list".
{
"order_nbr": "ORDER001",
"ship_via_id": 123,
"ship_via_id**code": "UPS1D"
}
Differences in Response Structure
There are several differences between the data returned by a standard GET query (ie. One retrieving objects or fields of
one entity) versus one using values_list:
• Related objects (foreign keys) are represented in the normal flow as a nested object with the fields: id, url, key.
When using values_list, the result will only be the integer "id" value for the related object.
"company_id": {
"id": 48,
"key": "CM_COMP",
"url": ".../wms/lgfapi/v10/entity/company/48"
}
vs
{
"company_id": 48
33

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
}
• You will not get the enriched response structure like in the standard GET query. For example, when doing a
normal GET for the entity order_hdr, the response structure includes additional fields like "order_dtl_set",
"order_lock_set", and "order_instructions_set". These related/child references enrich the content by being
present in the representation, but are not actually fields directly defined on the "order_hdr" entity - they are
determined at runtime by the serializer. These types of fields will not work with "values_list" and will result in an
error.
Creating Aliases
You also have the option to "rename" the fields in the output to reduce the field name complexity and the overall size
of the response payload. It is important to have unique aliases. By default, fields names will match the value from the
values_list:
GET .../entity/allocation/1?values_list=id,order_dtl_id**order_id**order_nbr
{
"id": 1,
"order_dtl_id**order_id**order_nbr": "ORDER123"
}
You may override the default names by giving an alias delimited by a colon character ":" for the given field in the request
URL query string:
GET .../entity/allocation/1?values_list=id:foo,order_dtl_id**order_id**order_nbr:order_nbr
{
"foo": 1,
"order_nbr": "ORDER123"
}
Assumptions
• The output fields name(s) must be unique:
• You cannot repeat the same alias in a values_list
• You cannot use an alias that is the same name as another field in the values list
• An error like, "Values list alias names must be unique.", will be returned and will specify all of the name(s) in
violation.
Distinct Parameter
lgfapi will support the new "distinct" query parameter for GET requests when also doing a values_list style GET request.
Values list requests are used for making more direct calls to fetch targeted relational table data without the structure of
an entity serializer. Due to this, there may be instances where the resultant data is repeated. For example: An OBLPN
may have multiple allocation records pointing back to multiple order details for the same order. A values list request
for the order_nbr would have as many repeated results as allocation records. This follows the same principles as the
underlying DB query.
Assumptions

1. Only works for GET requests using the values_list query parameter
2. Only works for list-style (paginated) requests. Will not work when querying by id.
3. If used in unsupported situations, the parameter will be ignored (no error).
   34

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Example Usage - List (Paginated) Response
Example 1 - Fetch order_nbr without using distinct
GET .../entity/order_dtl/?order_id=123&values_list=order_id,order_id**order_nbr:order_nbr
{
"result_count": 2,
"page_count": 1,
"page_nbr": 1,
"next_page": null,
"previous_page": null,
"results": [
{
"order_id": 123,
"order_nbr": "ORDER123"
},
{
"order_id": 123,
"order_nbr": "ORDER123"
},
]
}
Example 1 - Fetch unique order_nbr using distinct
GET .../entity/order_dtl/?order_id=123&values_list=order_id,order_id**order_nbr:order_nbr&distinct=1
{
"result_count": 1,
"page_count": 1,
"page_nbr": 1,
"next_page": null,
"previous_page": null,
"results": [
{
"order_id": 123,
"order_nbr": "ORDER123"
}
]
}
Example 2 - Get unique container status for each of the first 100 containers selected.
GET .../entity/container/?limit=100&values_list=status_id\_\_description:container_status&distinct=true
{
"result_count": 4,
"page_count": 1,
"page_nbr": 1,
"next_page": null,
"previous_page": null,
"results": [
{
"container_status": "Allocated"
},
{
"container_status": "Cancelled"
},
{
"container_status": "Consumed"
},
{
"container_status": "Delivered"
}
35

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
]
}
Retrieve (Single-Object) Response
Flow where entity "id" is included as part of the URL.
This is not supported. Since this GET request style will always return a single object representation, there is no meaning
to "distinct" as values cannot be repeated. If the query parameter is included in this flow, it will be ignored.
Filter Entity Data using NOT Operator
You have the option to filter for entity data using the NOT operator, "!", in their URL querystring. The NOT operator ("!")
is added before the equals ("=") symbol in the key-value pair, and simply negates the statement to which it is added.
Note: This can be a useful tool for retrieving data, but be careful when using this functionality as this type of lookup
tends to be slower than an inclusive one.
Example 1:
Filter for a location barcode that contains the string "ABC":
• .../wms/lgfapi/v10/entity/location?barcode**contains=ABC
Filter for a location barcode that does NOT contain the string "ABC":
• .../wms/lgfapi/v10/entity/location?barcode**contains!=ABC
Example 2:
Filter for items where part A is in a list of explicit values:
• .../wms/lgfapi/v10/entity/item?part_a**in=ABC,DEF
Filter for items where part A is NOT in a list of explicit values:
• .../wms/lgfapi/v10/entity/item?part_a**in!=ABC,DEF
Resource Existence and Modification (HEAD)
HTTP requests for lgfapi entities using the HEAD method are an efficient way to determine if a resource or list of
resource(s) exists. Additionally, it is possible to determine if a specific resource has been modified since a target date-
time. The HEAD method does not return any data in the body of the response. The only data returned is the response
status code and any HTTP headers. Because HEAD requests do not have to know specifics about each resource and
36

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
build a representation (like in a GET request), minimum data is transmitted and the server-side determinations can be
optimized.
HEAD requests accept both retrieve and list style URI that same as a GET request. This can be used to check for the
existence of a specific resource or filter for the existence of potentially many resources in a list.
“If-Modified-Since” HTTP Request Header
Entity HEAD requests allow for the requester to optionally pass the “If-Modified-Since” HTTP header in the request.
This is only permitted for retrieve style requests when querying for a specific resource by id in the URL. The header’s
value is the target date-time in iso-8601 format in the appropriate time zone. When provided, the value will be
compared to the resource’s last modification time to determine if it has been modified since the header’s date-time. If
the resource exists, and it has been modified, a 200 - Ok status code is returned. If it exists but has not been modified, a
304 – Not Modified status code is returned.
Not that if the entity does not support mod time tracking, the header is ignored and a 200 – Ok response code is
returned meaning only that the resource exists.
The “If-Modified-Since” request header is typically used in conjunction with the “Last-Modified” response header that
is returned with every retrieve style GET request for those entities that track mod timestamps. For example, a common
scenario might start with a retrieve style GET request being made for a resource. The value of the “Last-Modified”
response header is saved client-side for that resource. Sometime later, the client wants to check if the resource has been
updated. A HEAD request can be made to determine if the resource has been modified since the original GET request
by passing the last mod timestamp in the “If-Modified-Since” request header.
In scenarios where the updated resource representation is not needed, a HEAD request is much more efficient than
a GET request. Or, it may be used to determine if a more expensive GET request is subsequently called to fetch the
updated resource representation. It is also common to use HEAD request modification checks as a trigger mechanism
for down-steam operations.
Response Statuses
The HTTP response status will be one of the following and vary depending on the outcome and if checking for existence
or existence and modification of one or more resources. Note that this is not the full list of all possible response
statuses. Rather, the following statuses are directly tied to this HTTP method’s functionality within lgfapi. For example,
one can still receive a 401 status code if not providing valid user authentication credentials.
• 200 - Ok
When checking for only existence, a 200 status code response means that the resource(s) exist. When additionally
checking for modification, this status code confirms that the specific resource exists and has been modified.
• 304 – Not Modified
Only applicable when checking for modification of a specific resource using the 'If-Modified-Since' header. This status
means that the resource exists but has not been modified since the input target date-time.
• 400 - Bad Request
For HEAD requests, it is possible to receive this status when using the 'If-Modified-Since' header with an invalid date-
time value or format. This may also be returned if other invalid data is found, such as invalid query sting filters.
• 404 - Not Found
37

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
No resource(s) were found based on the input provided. This may mean that either the resource(s) do not exist, or they
do exist but the requesting user is not eligible for any of the resources.
For example, use a retrieve style request to check for the existence of a company entity with id=1:
HEAD https://.../wms/lgfapi/v10/entity/company/1
Or, it can be applied to a list style request with filters:
HEAD https://.../wms/lgfapi/v10/entity/company?code=ABC
Creating a Resource (POST)
Lgfapi allows for the creating and linking of a limited number of entity resources using an HTTP POST request. The
new resource’s initial data set is passed in the body of the request, in the structure and formats outlined below. The
requesting user must have the “lgfapi_create_access” permission. Also, the requesting user must be eligible for the
facility/company context of the data being created.
Example request to create an IBLPN:
POST …/wms/lgfapi/v10/entity/iblpn/
Input Data
Data passed in the body of any POST request to the entity module requires the follow structure and data conventions.
Data Structure
Data is input in the request body in one of two sections:
• Fields – Initial field data. The “fields” section is used to pass in the initial field data required by the entity.
Optional fields have a default and should be omitted from the “fields” data if you with the default to be applied.
Lgfapi will attempt to use any data passed in the request body over the field default.
• Options – Additional/miscellaneous data. The “options” section is used to pass in extraneous data not directly
required by the entity. A common example is the need to pass in a reason code when creating certain entities
for the purposes of tracking against writing inventory history records.
JSON Example
{
“fields”: {
“string_field”: “ABC”,
“decimal_field”: 1.234
},
“options”: {
38

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
“reason_code: “RC”
},
}
XML Example
<request>
<fields>
<string_field>ABC</string_field>
<decimal_field>1.234</decimal_field>
</fields>
<options>
<reason_code>RC</reason_code>
</options>
</request>
Dates/Times
Temporal data must be iso-8601 format.
Related Resources
Relational fields (denoted by a field name ending in “\_id”) require the integer “id” value of the target resource. This can
be obtained by making a GET request to the corresponding entity with appropriate filters.
Assuming that you already know the corresponding fields each have an “id” value of 1; when creating a new resource
with the required related fields “facility_id” and “company_id”, the JSON POST request body is modeled as:
{
“fields”: {
“facility_id”: 1,
“company_id”: 1
}
}
If a related field is optional and not required as part of the initial resource creation, the field should be omitted to apply
the default value.
39

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Response Statuses
A non-paginated representation of the new resource will be returned in the body of the HTTP response in the desired
format.
200 – Ok
A lookup was done and it was determined that the resource already exists. No new resource was created. Instead, the
body of the response contains a representation of the existing resource. This is only applicable to certain entities.
• 201 - Created
The resource was successfully created.
• 400 - Bad Request
The request was invalid. This could be due to data validation failures, permission errors, or other missing requirements
of the operation.
Validations
Field and object-level validations are applied before the new resource is created. Any errors will be returned the
response body in the standard format. All related resources must be within the facility/company context of the resource
being created. Meaning, users cannot link the new resource to any resources outside of its facility and/or company.
For example, it is not possible to link an IBLPN to a pallet where the pallet is for a different facility or company than the
IBLPN.
Nested Related Objects
Some entities, such as “inventory”, allow for the creation and association of some related objects within the request
to create the inventory object. This allows for the creation of multiple related objects using a single API call instead of
multiple requests.
The currently supported related objects are “batch_number” and “inventory_attribute”. Instead of passing in the “id”
value of the related objects as the field definition’s value, you may alternatively insert a nested object representation.
If the nested object does not exist, it will be created. If it does exist, no creation for that object takes place but in both
cases it will be associated to the inventory object being created.
For example, when making a POST request to create an inventory object, it is valid to associate an existing batch using
its “id” value:
{
“batch_number_id”: 1,
…
}
40

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
It is also possible to send a nested representation of the batch object which will functionally act as “get or create”. The
nested object must still pass all of the same validations as if it were being created independently and its “id” value
passed in:
{
“batch_number_id”: {
“batch_nbr”: “BATCH001”,
“item_id”: 1,
“expiry_date”: “2019-01-01”
},
…
}
Supported Entities
• inventory_attribute
◦ Functions as get-or-create based on the provided attributes for the given facility and company
combination.
• batch_number
◦ Function as get-or-create based on the batch number for the given facility and company combination.
• iblpn
◦ Creates an inbound container with no inventory.
• inventory
◦ Creates inventory in either an iblpn or an active location.
◦ Requires “reason_code” option for inventory history tracking.
◦ Success results in inventory history adjustment(s) being generated.
◦ Supports nested “batch_number” and “inventory_attribute” object creation.
• inventory_lock
Create an inventory lock that can applied to containers and locations.
Updating a Resource (PATCH)
Lgfapi allows you to update specific fields on a limited number of entity resources using an HTTP PATCH request.
Only the desired changes are to be passed in the body of the request using the “fields” section (very similar to a create
resource (POST) request). The requesting user must have the “lgfapi_update_access” permission and must be eligible
for the facility/company context of the data being modified. Successful modification will additionally update the object’s
“mod_ts” and “mod_user” fields.
41

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
The entities and fields that may be modified are limited at this time, with a few exceptions, to custom (“cust”) fields,
where supported. These fields are for “pass through” data that generally has no functional significance.
Updates are restricted to a single object per request and the “id” of the target object is required as part of the resource
URL.
The following is an example URL to update a sales order:
PATCH …/wms/lgfapi/v10/entity/order_hdr/123/
Input Data
Data passed in the body of any PATCH request to the entity module requires the following structure and data
conventions.
• Fields –Field data with target value for update.
The “fields” section is used to pass in the fields to update and the desired value. Any omitted fields will be unchanged.
JSON example of updating the values of multiple “cust” fields:
{
“fields”: {
“cust_field_1”: “A”,
“cust_decimal_2: 1.234
}
}
Response Statuses
A non-paginated representation of the updated resource will be returned in the body of the HTTP response in the
desired format.
• 200 – Ok
The resource was successfully updated.
• 400 - Bad Request
The request was invalid. This could be due to data validation failures, permission errors, or other missing or incomplete
requirements.
Batch Number
The Batch Number PATCH API allows you to update the lock code/expiry date for an existing lot.
42

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
URL
PATCH .../wms/lgfapi/v10/entity/batch_number/(id).
Here is an example of a PATCH update request:
{
"fields": {
"expiry_date": "EXPIRY_DATE_VALUE",
"lock_id": "LOCK_ID_VALUE"
}
}
NOTE: If you would like to nullify a lock id for a specific batch, you can send a request with lock_id as " " (empty). You will
not be able to nullify the expiry date for a particular item that is expiry-tracked.
Field Type
lock_id Integer
expiry_date Date
IB Shipment
Field Type
cust_date_1 Date
cust_date_2 Date
cust_date_3 Date
cust_date_4 Date
cust_date_5 Date
cust_decimal_1 Decimal
cust_decimal_2 Decimal
cust_decimal_3 Decimal
cust_decimal_4 Decimal
cust_decimal_5 Decimal
cust_field_1 String
cust_field_2 String
cust_field_3 String
43

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Field Type
cust_field_4 String
cust_field_5 String
cust_long_text_1 String
cust_long_text_2 String
cust_long_text_3 String
cust_number_1 Integer
cust_number_2 Integer
cust_number_3 Integer
cust_number_4 Integer
cust_number_5 Integer
cust_short_text_1 String
cust_short_text_2 String
cust_short_text_3 String
cust_short_text_4 String
cust_short_text_5 String
cust_short_text_6 String
cust_short_text_7 String
cust_short_text_8 String
cust_short_text_9 String
cust_short_text_10 String
cust_short_text_11 String
cust_short_text_12 String
Make Changes During Different Shipment Statuses
PATCH API allows you to update shipment header fields for in transit, receiving started, and receiving complete status.
From 22D onwards, updating the fields is not supported for shipment statuses of locked for receiving, verification in
progress, verified, and cancelled. This change makes behavior consistent with the Web UI.
The following additional fields are allowed to be updated in different statuses.
44

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Field Type
vendor_info String
trailer_type String
manifest_nbr String
ref_nbr String
origin_info String
orig_shipped_lpns (only when ASN is in In-
Transit status)
String
orig_shipped_units ( nly when ASN is in In-
Transit status)
String
shipment_type_id Integer
load_id Integer
IB Shipment Detail
Field Type
cust_date_1 Date
cust_date_2 Date
cust_date_3 Date
cust_date_4 Date
cust_date_5 Date
cust_decimal_1 Decimal
cust_decimal_2 Decimal
cust_decimal_3 Decimal
cust_decimal_4 Decimal
cust_decimal_5 Decimal
cust_field_1 String
cust_field_2 String
cust_field_3 String
45

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Field Type
cust_field_4 String
cust_field_5 String
cust_long_text_1 String
cust_long_text_2 String
cust_long_text_3 String
cust_number_1 Integer
cust_number_2 Integer
cust_number_3 Integer
cust_number_4 Integer
cust_number_5 Integer
cust_short_text_1 String
cust_short_text_2 String
cust_short_text_3 String
cust_short_text_4 String
cust_short_text_5 String
cust_short_text_6 String
cust_short_text_7 String
cust_short_text_8 String
cust_short_text_9 String
cust_short_text_10 String
cust_short_text_11 String
cust_short_text_12 String
inv_attr_a String
inv_attr_b String
inv_attr_c String
inv_attr_d String
inv_attr_e String
inv_attr_f String
inv_attr_g String
inv_attr_h String
inv_attr_i String
46

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Field Type
inv_attr_j String
inv_attr_k String
inv_attr_l String
inv_attr_m String
inv_attr_n String
inv_attr_o String
Make Changes During Different Shipment Statuses
You can also make changes to IB Shipment Detail fields through PATCH API when the Shipment status is in "Receiving
Started" or "Receiving Complete" based on the status of the shipment.
Note: The Allow updating ASN after Receiving started flag needs to be enabled in the Shipment Type UI to allow
you to make changes to IB Shipment Detail via API. From 22D onwards, the PATCH API for Inbound Shipments allows
you to update relevant fields on the shipment header until the ASN status is in receiving complete.
The following are the fields which are allowed to be updated in different statuses:
Field Type
shipped_qty String
container_nbr String
item_id String
po_dtl_id String
pallet_nbr String
batch_nbr String
expiry_date String
priority_date String
invn_attr (a-o) String
lpn_weight String
lpn_volume String
lpn_length String
lpn_height String
lpn_width String
lpn_is_physical_pallet_flg String
47

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
dtl_recv_flag String
putawaytype_id String
receipt_advice_line String
marked_for_qc String
Inventory Attributes supported using IB Shipment Detail Patch API
Example Request:
PATCH .../wms/lgfapi/v10/entity/ib_shipment_dtl/123/
where 123 is the id of the IB Shipment Detail that needs to be updated.
JSON sample of the request body:
{
"fields": {
"invn_attr_id":
{ "invn_attr_a": "a", "invn_attr_b": "b", "invn_attr_c": "c" }
,
"cust_field_1": "cust1"
}
}
Validations
If invn_attr_id is provided, additional validations are needed.IB shipment header status should be less than Receiving-
Completed.the IB Shipment detail should not have started receiving. received_qty shouldbe 0.If the ib shipment detail
has po_dtl_id already populated, meaning it is linked to a PO, we will not support updating the invn attributes and the
validation will fail.
If these validations fail, the request should fail (so any other fields likecustom fields provided in this request will not
be updated even though theymay have more lenient validations).Validate that the invn-attribute record matches the
facility/company.If no invn_attr_id is provided then the current validations for custom fields should apply.
Item Characteristics
Field Type
cust_attr_1 String
cust_attr_2 String
48

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Load
Field Type
cust_field_1 String
cust_field_2 String
cust_field_3 String
cust_field_4 String
cust_field_5 String
cust_field_6 String
cust_field_7 String
cust_field_8 String
cust_field_9 String
cust_field_10 String
Location
Field Type Description
cust_field_1 String
cust_field_2 String
cust_field_3 String
cust_field_4 String
cust_field_5 String
to_be_counted_flg boolean • true
• false
to_be_counted_ts date and time All Date-time objects are assumed to be in the
time zone of the user's facility context.

JSON: {"field_ts": "2018-01-30T18:30:00"}}
49

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Field Type Description

XML: <field_ts>2018-01-30T18:30:00</
field_ts>

Order Header
Field Type Description
cust_date_1 Date
cust_date_2 Date
cust_date_3 Date
cust_date_4 Date
cust_date_5 Date
cust_decimal_1 Decimal
cust_decimal_2 Decimal
cust_decimal_3 Decimal
cust_decimal_4 Decimal
cust_decimal_5 Decimal
cust_field_1 String
cust_field_2 String
cust_field_3 String
cust_field_4 String
cust_field_5 String
cust_long_text_1 String
cust_long_text_2 String
cust_long_text_3 String
cust_number_1 Integer
cust_number_2 Integer
50

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Field Type Description
cust_number_3 Integer
cust_number_4 Integer
cust_number_5 Integer
cust_short_text_1 String
cust_short_text_2 String
cust_short_text_3 String
cust_short_text_4 String
cust_short_text_5 String
cust_short_text_6 String
cust_short_text_7 String
cust_short_text_8 String
cust_short_text_9 String
cust_short_text_10 String
cust_short_text_11 String
cust_short_text_12 String
externally_planned_load_flg Boolean • Only valid if the order is less than Shipped
status.
• When updating the flag to false, any
externally_planned_load_nbr values set
on the corresponding order details will be
removed.
gift_message String • User should be able to update Fields for
Order in status less than 'Shipped'.
priority String • User should be able to update Fields for
Order in status less than 'Shipped'.
reference_number String • User should be able to update Fields for
Order in status less than 'Shipped'.
required_ship_date String • User should be able to update Fields for
Order in status less than 'Shipped'.
special_instructions String • User should be able to update Fields for
Order in status less than 'Shipped'.
sales_channel String • User should be able to update Fields for
Order in status less than 'Shipped'.
51

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Field Type Description
start_ship_date String • User should be able to update Fields for
Order in status less than 'Shipped'.
stop_ship_date String • User should be able to update Fields for
Order in status less than 'Shipped'.
stop_ship_flag Boolean • Update the stop_ship_flag on the order
header if API call made is successful.
• Allowed order statuses for setting the
stop_ship_flag to true: Created, Partially
Allocated, Allocated, In-Picking, Picked, In-
Packing, Packed, Loaded. If order status is
shipped or cancelled, then respond with
error.
• If order status is shipped or cancelled,
then respond with error, other statuses
should be ok.
Order Detail
Field Type
cust_date_1 Date
cust_date_2 Date
cust_date_3 Date
cust_date_4 Date
cust_date_5 Date
cust_decimal_1 Decimal
cust_decimal_2 Decimal
cust_decimal_3 Decimal
cust_decimal_4 Decimal
cust_decimal_5 Decimal
cust_field_1 String
cust_field_2 String
cust_field_3 String
52

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Field Type
cust_field_4 String
cust_field_5 String
cust_long_text_1 String
cust_long_text_2 String
cust_long_text_3 String
cust_number_1 Integer
cust_number_2 Integer
cust_number_3 Integer
cust_number_4 Integer
cust_number_5 Integer
cust_short_text_1 String
cust_short_text_2 String
cust_short_text_3 String
cust_short_text_4 String
cust_short_text_5 String
cust_short_text_6 String
cust_short_text_7 String
cust_short_text_8 String
cust_short_text_9 String
cust_short_text_10 String
cust_short_text_11 String
cust_short_text_12 String
ord_qty Float
53

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Purchase Order Header
Field Type
cust_field_1 String
cust_field_2 String
cust_field_3 String
cust_field_4 String
cust_field_5 String
Purchase Order Detail
Field Type
cust_field_1 String
cust_field_2 String
cust_field_3 String
cust_field_4 String
cust_field_5 String
stop_recv_flg boolean
Work Order Header
Field Type
cust_field_1 String
cust_field_2 String
cust_field_3 String
54

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Field Type
cust_field_4 String
cust_field_5 String
Work Order Kit
Field Type
cust_field_1 String
cust_field_2 String
cust_field_3 String
cust_field_4 String
cust_field_5 String
Pallet
In order to provide the key to identify the Pallet and update the Weight and Volume fields. a PATCH verb for the Pallet
entity is available.
PATCH .../wms/lgfapi/entity/pallet/id/
where id = id of the pallet, which can be obtained using GET method
The following is a JSON sample of the request body:
{
"fields":
{
"lpn_type_id": "123",
"length": "45",
"width": "50.8",
"height": "70",
"actual_weight": "180"
55

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
}
}
You can update the following fields using the patch method:
Field Type
lpn_type_id String
length String
width String
height String
actual_weight String
Container, IBLPN, and OBLPN
The legacy API, “update_oblpn_dims”, has been deprecated in place of PATCH requests on three lgfapi entities:
container, iblpn, and oblpn. This functionality provides a mechanism to update the container’s dimensional and weight
fields. The functionality is the same for each entity. The only difference being that the “container” entity may be used to
update both IBLPN and OBLPN’s. The other two entities are restricted to acting on only their given container type.
URL examples:
PATCH .../entity/container/{id}
PATCH .../entity/iblpn/{id}
PATCH .../entity/oblpn/{id}

Supported Fields
• length
• width
• height
• weight
• volume
Supported Options
• calc_volume_flg
◦ Boolean (Default = False)
◦ When true, the container’s volume will be calculated from the length, width, and height.
◦ If the volume is explicitly provided in the “volume” field, this flag is ignored.
56

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Additional Functionality
Updating the container’s weight and dimension fields may trigger some additional updates:
• actual_weight_flg
◦ This container flag will be set to true if the weight is updated.
• lpn_type_id
◦ Container value will be removed if any of length, width, or height is updated.
Request Body Example 1
Explicitly update all dim and weight values.
{
"fields": {
"length": “1.23”,
"width": “2.24”,
"height": “3.40”,
"weight": “19.25”,
“volume”: “9.37”
}
}
Request Body Example 2
Update only some dim values and request container’s volume be recalculated.
{
"fields": {
"length": “1.23”,
"width": “2.24”
},
"options": {
"calc_volume_flg": true
}
}
Special Note about JSON Decimal Values
When sending decimal values in a JSON request, it is recommended to send them wrapped in double quotes like a
string value, as seen in the example above. This will prevent against any loss of precision as part of the lgfapi request.
57

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Movement Request Header
You can update movement requests after they are in a "Created" status, or update details in custom fields during the
life-cycle of a movement request, using the new Movement Request PATCH API.
Movement Request Header URL:
.../wms/lgfapi/v10/entity/movement_request_hdr/id
You can update the following fields using the PATCH method:
Movement Request Detail URL:
.../wms/lgfapi/v10/entity/movement_request_dtl/id
Field Type
cust_field_1 String
cust_field_2 String
cust_field_3 String
cust_field_4 String
cust_field_5 String
cust_date_1 String
cust_date_2 String
cust_date_3 String
cust_date_4 String
cust_date_5 String
cust_decimal_1 String
cust_decimal_2 String
cust_decimal_3 String
cust_decimal_4 String
cust_decimal_5 String
cust_short_text_1 String
cust_short_text_2 String
cust_short_text_3 String
cust_short_text_4 String
cust_short_text_5 String
58

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
Field Type
cust_short_text_6 String
cust_short_text_7 String
cust_short_text_8 String
cust_short_text_9 String
cust_short_text_10 String
cust_short_text_11 String
cust_short_text_12 String
Sample Patch API Body
"fields": {
"cust_field_1": "Example",
"cust_field_2": "Example",
"cust_field_3": "Example",
"cust_field_4": "Example",
"cust_field_5": "Example",
"cust_date_1": "Example",
"cust_date_2": "Example",
"cust_date_3": "Example",
"cust_date_4": "Example",
"cust_date_5": "Example",
"cust_decimal_1": "Example",
"cust_decimal_2": "Example",
"cust_decimal_3": "Example",
"cust_decimal_4": "Example",
"cust_decimal_5": "Example",
"cust_short_text_1": "Example",
"cust_short_text_2": "Example",
"cust_short_text_3": "Example",
"cust_short_text_4": "Example",
"cust_short_text_5": "Example",
"cust_short_text_6": "Example",
"cust_short_text_7": "Example",
"cust_short_text_8": "Example",
"cust_short_text_9": "Example",
"cust_short_text_10": "Example",
"cust_short_text_11": "Example",
"cust_short_text_12": "Example",
}
}
{
Entity Operations (GET /POST)
Many entities offer specialized operations in order to assist users in more complicated, or performance intensive
operations. These operations can act on one or more resources and may affect entities beyond the one(s) targeted in
the request. The URLs may follow a “list” or “retrieve” styles:
Format for an entity operation URL evocable for a specific resource by “id”:
59

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
…/wms/lgfapi/v10/entity/{entity_name}/{id}/{operation_name}/
Format for a “bulk” entity operation URL evocable for potentially multiple resources:
…/wms/lgfapi/v10/entity/{entity_name}/{operation_name}/
Entity operations are invoked in the same manner as previously discussed for GET and POST requests. Each operation
has its own URL tied to the entity. Entity operations that use a GET request are still for obtaining a representation in the
response body and do not modify data. Entity operations that use POST requests trigger an action or series of actions
on the entity that can change resource state.
Response Status
Entity operations follow the response statuses previously discussed for GET and POST request, with one addition:
• 204 – No Content
This HTTP response status is returned when the request was successfully fulfilled, but there is no additional content to
return to the requester. Users should interpret this as success and expect the response body to be empty.
Bulk Operations
Entities may also support “bulk” operation that allow the same operation to be run on one or more resources within a
single request. There are several key differences and additional options that apply to bulk operations.
Parameter Data Filtering
Since bulk operations are capable of acting on one or more objects in a single request, the request body’s “parameter”
data is required. This data is a series of one or more filter conditions that will be applied to identify the target list of
objects. Each operation may have its own allowed set of filter conditions that can be applied. This may include allowing
users to filter on related objects and using complex lookups such as “in” by the same double underscore (“**”) notation
as in a GET request’s filters.
Note: all data is still automatically filtered by the user’s eligible facilities and companies and that the user is not
permitted to run bulk operations on objects outside their allowed scope.
In general, all bulk operations allow for the filtering of objects by “id”. For example, a JSON request body’s parameters
section for filtering on multiple object id’s would be:
{
“paramters”: {
“id**in”: [1, 2, 3]
}
}
Filtering on facility code and company code could be achieved by doing the following (assuming the entity and
operation allow it):
{
60

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
“parameters”: {
“facility_id\_\_code”: “FAC1”,
“company_id_code”: “COM1”
}
}
The maximum number of objects that may be acted upon in a single request is dictated by the requesting user’s “Rows
per Page” attribute. This is configurable per user but also applies in other areas of the application such as how many
objects are returned per page in an lgfapi GET request, or in the UI when refreshing a page’s data grid.
Commit Frequency
All bulk operations are provided this additional “options” integer input parameter (default = 0). This parameter allows
the requester to dictate at what frequency the changes are applied to each resource or group of resources being
processed.
The default value of 0 specifies that no updates are committed unless all resources are processed successfully (all or
nothing). All changes are rolled back on the first error, and only the first error is reported back to the user using the
stand response.
A value of 1 indicates that the changes should be committed per resource successfully processed. Any error will only
cause a failure and roll back of changes for the specific resource that failed. All errors will be accumulated and returned
in the standardized bulk response format (see below).
Although a value > 1 is permitted, it is not advised that customers use this unless instructed to do so by support. This is
typically only used for more advanced or larger data processing scenarios and for certain performance considerations.
Response Status and Content
When the commit frequency is 0, the bulk operations will give the standard error response format as previously
documented, if any error is found. However, a different response status and standardized format is provided on total
success or when the commit frequency value is > 0:
A 200 – OK response is returned for bulk operations along with a standardized bulk response having the following
attributes:
• record_count – Total number of resources processed in the request.
• success_count – Number of successfully processed resources.
• failure_count – Number of unsuccessfully processed resources.
• details – A nested dictionary (key/value map) that provides additional details for any resources that failed
during the processing of the operation.
◦ The key to identify each resource and it’s failure is by default the resource’s unique “id” value. However, a
different identifying key may be returned per operation, as documented.
◦ If no details are provided, the value will be null.
The following is a JSON example where 2 objects were processed, but one (having id=123) failed:
{
“record_count”: 2,
61

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 3
Entity Module
“success_count”: 1,
“failure_count”: 1,
“details”: {
123: “Invalid status.”
}
}
62

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 4
Other API Modules
4 Other API Modules
Additional API Modules
Besides entity, there are several other modules that support mostly POST operations (along with a few GETs).
• cycle_count_info
• data_extract
• inventory
• pick_pack
• printing
• repack
• replenishment
• report
• sort_receive
• stage_track_record
• printing
• product
• report
Details of operations supported by these modules are in the next section, Supported Operations.
63

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 4
Other API Modules
64

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
5 Supported Operations
Batch Number
The Batch Number API allows you to create a batch by making a POST HTTP request.
URL
.../wms/lgfapi/entity/batch_number/
• If the matching record already exists, that will be returned and no record is created in the database. An HTTP
status of 200 - OK is returned.
• If a match is not found, a new record is created and an HTTP status 201 - Created is returned.
• Both scenarios will return a representation in the response body.
• We will attempt to match on facility, company, batch_nbr, and item.
• If a match is found, but the expiry date or lock do not match the existing record, an error is returned. This will
not update the existing record.
• The batch_nbr is validated against the barcode type configuration for "Batch Nbr".
Request Body Example
{
"fields": {
"facility_id": 269,
"company_id": 48,
"batch_nbr": "BATCH123",
"item_id": 1,
"lock_id": 123,
"expiry_date": "2018-01-01"
}
}
Bulk Change Eligible Group
The Bulk Change Eligible Group API allows you to add/remove the user eligible groups in bulk. You can update single or
multiple user eligible facility all at once. Once updates are made, they will reflect in the User UI --> Eligible Groups.
URL
POST ...../v10/entity/user/bulk_change_eligible_group
Example Body Request
{
65

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"parameters": {
"company_id": "222",
"auth_user_id**username**in": [
"user1",
"user2",
"user3"
]
},
"options": {
"action": "ADD",
"group_id_list": [10,20,21],
"group_name_list": ["GRP1","GRP2","GRP3"],
"commit_frequency": 1
}
Company
These topics give descriptions for APIs that complete actions related to companies for the Warehouse.
Bulk Change Eligible Company
The Bulk Change Eligible Group API allows you to add/remove the user eligible groups in bulk. You can update single or
multiple user eligible facility all at once. Once updates are made, they will reflect in the User UI --> Eligible Groups.
URL
POST ...../v10/entity/user/bulk_change_eligible_company
Example Body Request
{
"parameters": {
"company_id": "333",
"auth_user_id**username**in": [
"user1",
"user2",
"user3"
]
},
"options": {
"action": "ADD",
"company_id_list": [101,201,301],
"company_code_list": ["COMP1","COMP2","COMP3"],
"commit_frequency": 1
}
}

66

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Company Parameter
POST .../entity/company_parm
This operation is used to add single or multiple company parameters.
If you have a new facility and you want to copy the same Company Parameters from your current facility, you can first
GET the list by querying the company_parm entity, then POST the applicable data to this operation for the target facility.
Example Body Request
{
"fields": {
"company_id": 1,
"parm_key": "TEST_PARM_001",
"parm_value": "test"
}
}
Container
These topics give descriptions for APIs that complete actions related to containers in the Warehouse.
The “iblpn” and “oblpn” entities are derived from the “container” entity and have access to all of the following entity
operations, in addition to their own.
Get Sales Orders
GET …/wms/lgfapi/v10/entity/container/{id}/orders/
Returns a paginated representation of “order_hdr” entities for all sales order(s) allocated against the inbound or
outbound container.
Lock Container
POST …/wms/lgfapi/v10/entity/container/{id}/lock/
Apply one or more inventory locks to the target inbound or outbound container.
Category Parameter Type Required Default Description
options lock_code_list Array of Strings X Inventory lock code(s)
to be applied.
67

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Bulk Lock Container
POST …/wms/lgfapi/v10/entity/container/bulk_lock/
Apply one or more inventory locks to one or more inbound or outbound container(s).
The “parameters” section of the request body is required in addition to the “options” section outlined below. The “id”
parameter filter (for a single value) or the “id\_\_in” parameter (for an array of values) are valid and can be used.
Category Parameter Type Required Default Description
options lock_code_list Array of Strings X Inventory lock(s) to be
applied.
options commit_frequency Integer 1 0 = Roll back on first
error.

1 = Commit per object.

Unlock Container
POST …/wms/lgfapi/v10/entity/container/{id}/unlock/
Remove one or more inventory locks to the target inbound or outbound container.
Category Parameter Type Required Description
options lock_code_list Array of Strings X Inventory lock code(s) to be
removed.
Bulk Unlock Container
 POST …/wms/lgfapi/v10/entity/container/bulk_unlock/

Remove one or more inventory locks from one or more inbound or outbound container(s).
The “parameters” section of the request body is required in addition to the “options” section outlined below. The “id”
parameter filter (for a single value) or the “id\_\_in” parameter (for an array of values) are valid and can be used.
68

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Category Parameter Type Required Default Description
options lock_code_list Array of Strings X Inventory lock(s) to be
removed.
options commit_frequency Integer 1 0 = Roll back on first
error.

1 = Commit per object.

Palletize Container
POST .../entity/container/{id}/palletize/
Allows you to palletize an Inbound or Outbound LPN.
The “parameters” section of the request body is required in addition to the “options” section outlined below.
Category Name Required Type Description
parameters container_nbr X String IB or OB LPN to be linked.

“\_in” lookup is not
supported.

parameters facility_id Integer Container’s facility
parameters company_id Integer Container’s company
parameters type String Container’s type “I” or “O”.
Example
{
"parameters": {
"facility_id": 1,
"company_id": 1,
"container_nbr": "LPN-1"
}
}
• Both `facility_id` and `company_id` also support filtering on `code` as well.
Category Name Required Type Description
parameters facility_id string Container’s facility
parameters company_id string Container’s company
{
"parameters": {
"facility_id\_\_code": "FAC-1",
"company_id_code": "COM-1",
69

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"container*nbr": "OBLPN-1"
}
}
Functional Request Data
Category Name Required Type Default Description
options pallet_nbr X string Pallet number to be
used for palletizing IB
or OBLPN's.
options pallet_position string Position of Inbound
or OBLPN during
palletization.
options allow_mix_pa_types*
flg
boolean False whether to allow
mixing of LPN's with
different PA types on a
single pallet.
options allow_mix_dest_shipto string valid values to be
passed are

• Validate Ship To
• Validate
Destination
• Validate Ship To
and Destination
• Ignore Ship To
and Destination
{
"options": {
"pallet_nbr": "PLT001",
"pallet_position": "01",
"allow_mix_pa_types_flg": false
"allow_mix_dest_shipto": Ignore Ship To and Destination
}
}
Depalletize Inbound / Outbound LPN
Allows you to depalletize an Inbound or Outbound LPN so you do not have to use RF guns for performing
depalletization in automated guided facilities.
Identify container by ID:
POST .../entity/container/{id}/depalletize/
• The specific inbound or outbound LPN's id value is known and is provided in the URL.
• No additional `parameters` data in the request body is required.
70

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Identify container by Filters
POST .../entity/container/depalletize/
• lgfapi provides mechanism to determine the container entity to be dissociated with pallet.
• The `parameters` section of the request body will allow for the users to identify the specific OBLPN
Category Name Required Type Description
parameters container_nbr X String IB or OB LPN to be linked.

“\_in” lookup is not
supported.

parameters facility_id Integer Container’s facility
Parameters company_id Integer Container’s company
parameters type String Container’s type “I” or “O”.
{
"parameters": {
"facility_id": 1,
"company_id": 1,
"container_nbr":
"LPN001",
"type": "O"
}
}
• Both `facility_id` and `company_id` also support filtering on `code` as well.
Category Name Required Type Description
parameters facility_id_code string Container’s facility
Parameters company_id_code string Container’s company
{
"parameters": {
"facility_id\_\_code":
"FAC-1",
71

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"company_id\_\_code":
"COM-1",
"container_nbr":
"LPN001",
"type": "O"
}
}
Quality Check Approve
Quality Check Approv allows you to accept QC marked containers.
API URL: Lookup by ID:
POST.../entity/iblpn/{id}/qc_reject/

No additional `parameters` data in the request body is required.
API URL:Lookup by Filters:
POST.../entity/iblpn/qc_reject/
Category Name Required Type Description
parameters facility_id Integer Facility context by id
parameters facility_id**code string Facility context by code
parameters company_id Integer Company context by id
parameters company_id**code string Company context by code
parameters container_nbr X string IBLPN subjected to QC
Category Name Type Description
Options vendor_perf_code String Vendor performance code, users
want to pass for the QC transaction
Options lock_code string Unallocatable lock code bring the
QC rejected inventory within WMS
72

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
• If facility and/or company are provided, set login context accordingly.
• Only one of `facility_id` or `facility_id__code` may be provided.
• Only one of `company_id` or `company_id__code` may be provided.
• Lock code is an optional parameter. If users do not send the lock code, the rejected LPNs should get cancelled.
If the lock code parameter is populated with a unallocatable lock code, the system should mark the LPN as
received with QC status as QC Rejected. Users cannot provide allocatable lock codes to reject an IBLPN.
Bulk Reject URL
POST.../entity/iblpn/bulk_qc_reject/
Request Body:
The QC reject transaction is meant for the IBLPN entity. Hence, the users are required to send the following parameters
in the body.
{
"parameters": {
"id\_\_in": [1, 2, 3]
},
"options": {
"lock_code": "KHLOC01"
"vendor_perf_code": "KHVND001",
"commit_frequency": 1,
}
}
The commit frequency is by default set to 0. If it is set to 0, the system should roll back on first error/ If the commit
frequency is set to 1, the system should commit per object.
Additionally, users should be able to send either container ID or container number in the parameter body. Hence, if
users are sending container IDs, they can send as "id_in": [40129, 20138]. If users are sending container number, they
can send [KHLPN01, KHLPN02].
Updates
• Lock code is an optional parameter. If users do not send the lock code, the rejected LPNs should get cancelled.
If the lock code parameter is populated with a unallocatable lock code, the system should mark the LPN as
received with QC status as QC Rejected.
• The system should capture the following inventory histories;
◦ IHT-74- QC rejected
◦ IHT- 48- Shipment status changed
◦ IHT- 22- Lock container before shipment verification
• If the inventory in the QC marked IBLPN is serial tracked the IHT 74 should be broken based on the serial
number if the Enable split by serial nbr flag is turned on.
• Can perform the quality check from an external QC module without accessing the OCWMS platform.
API URL:Lookup by ID:
POST.../entity/iblpn/{id}/qc_approve/
73

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
No additional `parameters` data in the request body is required.
API URL: Lookup by Filters
POST.../entity/iblpn/qc_approve/
Category Name Required Type Description
parameters facility_id Integer Facility context by id
parameters facility_id**code string Facility context by code
parameters company_id Integer Company context by id
parameters company_id**code string Company context by code
parameters container_nbr X string IBLPN subjected to QC
Category Name Type Description
Options vendor_perf_code String Vendor performance code, users
want to pass for the QC transaction
• If facility and/or company are provided, set login context accordingly.
• Only one of `facility_id` or `facility_id__code` may be provided.
• Only one of `company_id` or `company_id__code` may be provided.
• If more than one object is found, an error should be returned.
Bulk Approve URL
POST.../entity/iblpn/bulk_qc_approve/
Request Body:
The QC accept transaction is meant for the IBLPN entity. Hence, the users are required to send the following parameters
in the body.
{
"parameters": {
"id\_\_in": [1, 2, 3]
},
"options": {
"vendor_perf_code": "KHVND001",
"commit_frequency": 0
}
}
The commit frequency is by default set to 0. If it is set to 0, the system should roll back on first error/ If the commit
frequency is set to 1, the system should commit per object.
74

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Additionally, users should be able to send either container ID or container number in the parameter body. Hence, if
users are sending container IDs, they can send as "id_in": [40129, 20138]. If users are sending container number, they
can send [KHLPN01, KHLPN02].
Updates
The system should proceed with the following updates after successful approval of the QC marked IBLPNS.
• The LPN status should be received with QC status as QC approved
• The system should capture the following inventory histories;
◦ IHT-73- QC approved
◦ IHT- 48- Shipment status changed\*\*
• If the inventory in the QC marked IBLPN is serial tracked the IHT 73 should be broken based on the serial
number if the Enable split by serial nbr flag is turned on.
• The Verification History view UI should create a record for the QC approval of the respective IBLPN-s.
Quality Check Reject
The Quality Check Reject API allows you to reject QC marked containers, so you can perform the quality check from an
external QC module without accessing the Oracle WMS Cloud platform.
Cycle Count
Cycle count LPN allows you to count the inventory available in a location. The following options are available:
• Confirm LPN Count
• Confirm Count LPN Scan
• Confirm Active Count
Confirm LPN Count
This API allows you to confirm the LPN count. This is if you need to confirm the number of LPNs available in a Reserve
Location, so you just need to specify the number of LPNs you see in the location.
URLs
POST .../wms/lgfapi/v10/entity/location/{id}/cc_confirm_lpn_count
Note: that with ID in the URL, there are no request parameters, just options.
OR
75

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
POST .../wms/lgfapi/v10/entity/location/cc_confirm_lpn_count
with parameters and options
Request Parameters
Parameters (filters)
• Only applicable when `id` is not present in the URL.
Name Required Type Default Description
facility_id C Integer Facility context by id.

one of id or code should be
provided

facility_id\_\_code C String Facility context by code.

one of id or code should be
provided

barcode Y String Location user is doing Cycle
Count. Must be a reserve
location.
• If facility is provided, set login context accordingly.
• Only one of `facility_id` or `facility_id__code` may be provided.
Options
Name Required Type Default Description
lpn_count Y integer Number of LPNs in the
location
validate_only_flg Y Boolean True or false
Example:
POST .../wms/lgfapi/v10/entity/location/cc_confirm_lpn_coun
{
"parameters": {
"facility_id\_\_code": "FAC",
"barcode": "Location001"
},
"options": {
"lpn_count": 5,
"validate_only_flg": "Y",
76

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
}
}
Request sent with an ID:
POST .../wms/lgfapi/v10/entity/location/{id}/confirm_lpn_coun
{
"options": {
"lpn_count": 5,
"validate_only_flg": "N",
}
}
Response
If validate only flag is set to true you will get a Response 200 - OK (No Pagination)
{
"current_lpn_count": 3
}
If validate only flag is True, you will get a Response 204 and a new record will be added to the module
SummaryAuditView.
If Validate only flag is set to true and there is no variance, the system will also write IHT- 38 - Reserve Location Cycle
Count Complete.
If validate only flag is set to False, a record is created - Response 204 and new record will be added to the module
SummaryAuditViewGroup Number.
Confirm Count LPN Scan
This API allows you to confirm the count of LPNs. This is if you to confirm the list of LPNs in the location.
URLs
POST .../wms/lgfapi/v10/entity/location/{id}/cc_confirm_count_lpn_scan
Note: With ID in the URL, there are no request parameters, just options.
OR
POST .../wms/lgfapi/v10/entity/location/cc_confirm_count_lpn_scan
with request parameters and options
Request Parameters
parameters(filters)
• Only applicable when `id` is not present in the URL.
77

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Required Type Default Description
facility_id C Integer Facility context by id.

one of id or code should be
provided

facility_id\_\_code C String Facility context by code.

one of id or code should be
provided

barcode Y String Location user is doing Cycle
Count
• Only one of `facility_id` or `facility_id__code` may be provided.
If after applying the parameters it matches more than one location, it is an error condition.
Options
Name Required Type Default Description
lpn_nbr_list Y String List of LPNs
validate_only_flg Y Boolean true or false
deferred_mode_flg Y Boolean
• If validate flag is set to true. We will return success message with details such as LPNs missing ( LPNs system
expected to be scanned, but were not send in the request)
• If validate flag is set to False, and user passes the same number of LPNs ( missing some lpns the system was
expecting to be sent) then the system will take as those LPNs are not in the location.
• If deferred_mode_flg is on. It would not matter the value in company parm INVN_ADJ_APPROVAL_REQUIRED.
If this flag is set to YES. Approval is required if there is an Inventory adjustment in the location.
Note: deferred_mode_flg value will be irrelevant when validate_flg is true. In other words validation is the same
regardless of the deferred_mode_flg.
Example:
POST .../wms/lgfapi/v10/entity/location/cc_confirm_count_lpn_scan
{
"parameters": {
"facility_id\_\_code": "FAC",
"barcode": "Location001"
},
"options": {
78

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"lpn_nbr_list": ["lpn1", "lpn2", "lpn3"],
"validate_only_flg": "Y",
"deferred_mode_flg": "Y"
}
}
Request sent with an ID:
POST .../wms/lgfapi/v10/entity/location/{id}/cc_confirm_count_lpn_scan
{
"options": {
"lpn_nbr_list": ["lpn1", "lpn2", "lpn3"],
"validate_only_flg": "Y",
"deferred_mode_flg": "Y"
}
}
Response
Response is not paginated as its only for one location whether the request uses parameters or ID
if validate is True and successful it will be a 200 response with the response JSON payload
if validate is False and successful, then response is 204, no payload
With 200 - OK (No Pagination) for validate True
{
"new_lpn_nbr_list": ["lpn1"]
"matching_lpn_nbr_list": ["lpn2", "lpn3"]
"missing_lpn_nbr_list": ["lpn4", "lpn5"]
}
Confirm Active Count
This API allows you to confirm the units available in an active location
URLs
POST .../wms/lgfapi/v10/entity/location/{id}/cc_confirm_active_count
Note: with ID in the URL, there are no request parameters, just options.
OR
POST .../wms/lgfapi/v10/entity/location/cc_confirm_active_count
with parameters and options
Request Parameters
parameters (filters)
• Only applicable when `id` is not present in the URL.
79

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Required Type Default Description
facility_id C Integer Facility context by id.

one of id or code should be
provided

facility_id\_\_code C String Facility context by code.

one of id or code should be
provided

barcode Y String Location user is doing Cycle
Count
• If facility is provided, set login context accordingly.
• Only one of `facility_id` or `facility_id__code` may be provided.
• Only one of item_barcode or item_alternate_code may be provided.
• Location type must be Active.
Options:
Name Required Type Default Description
count_all_items_flg Y Boolean If true all items in the
location must be provided.
If false only the items
provided will be counted.
validate_only_flg Y Boolean True or False
deferred_mode_flg Y Boolean
item_barcode C String Item identifier
item_alternate_code C String Item identifier
qty Y Integer Quantity of the item
• If facility and/or company are provided, set login context accordingly.
Note: This API does not track batch, expiry, srl numbers or inventory attributes. As this API does NOT track
those values, if you are trying to count a location with either batch, expiry, srl numbers or inventory attributes
you will get an error.
Example:
POST .../wms/lgfapi/v10/entity/location/cc_confirm_active_count
{
80

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"parameters": {
"facility_id\_\_code": "FAC",
"barcode": "Location001"
},
"options": {
"count_all_items_flg": true,
"item_quantity_list": [
{
"item_barcode": "Item001",
"qty": 5
},
{
"item_alternate_code": "itemx2",
"qty": 3
}
]
}
}
Example request by location ID:
POST .../wms/lgfapi/v10/entity/location/{id}/cc_confirm_active_count
{
"options": {
"count_all_items_flg": true,
"item_quantity_list": [
{
"item_barcode": "Item001",
"qty": 5
},
{
"item_alternate_code": "itemx2",
"qty": 3
}
]
}
}
Response
Response is not paginated as its only for one location whether the request uses parameters or ID
if validate is True and successful it will be a 200 response with the response JSON payload
if validate is False and successful, then response is 204, no payload
When validate is False and the request is successful a status of 204 - No Content is returned with no response payload.
When validate is True and the request is successful a status of 200 - OK is returned with a response payload:
If there is no mismatch, then an empty list is returned:
{
"mismatched_item_quantity_list": []
}
If there is a mismatch, the list of item(s) in error with the current quantity found is returned:
{
"mismatched_item_quantity_list": [
{
"item_barcode": "Item001",
"item_alternate_code": "itemx1",
"current_qty": 4
81

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
},
{
"item_barcode": "Item002",
"item_alternate_code": "itemx2",
"current_qty": 6
}
]
}
Cycle Count List
The Cycle Count List API allows you to input cycle count information from MHE to WMS.
URL
POST .../wms/lgfapi/v10/cycle_count_info/cycle_count_list/
This API is supported in JSON format. After processing the “Cycle Count List” API, the API honors the existing company
and facility parameters “INVN_ADJ_APPROVAL_REQUIRED” to update inventory.
Request Parameters
The `parameters` section of the request body will allow you to specify how the data needs to be loaded to the stage table
and how the Cycle Count List should be processed
Parameter Name Type Required Description
async_flg Boolean (True) The value will be considered as true. The API will always run
in async mode. This API is designed for asynchronous calls
(synchronous call is not supported).
only_load_flg Boolean (True/False) By default, the value will be considered as false. If the
value is false, then API executes the interface (process
corresponding records in stage tables). If the value is true,
then only the API loads the API records to the From MHE
Cycle Count Info stage table.
mhe_system String No MHE system used to perform the count.
task_nbr String Conditional (only
when MHE is
executing a task
generated in WMS)
WMS Cycle Count T ask number. For standalone counts
performed by the MHE, this field should be blank.
task_type String Conditional (only
when a task number
is populated)
WMS Cycle Count task type.
location_barcode String Yes Location where cycle count is performed.
82

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Parameter Name Type Required Description
lpn_scan_flg Boolean (True/False) No If this is set to “True”, then the count mode is reserve
location LPN Scan. If this is set to “False”, the count mode is
reserve location detailed count.

When the parameter is set to “True”, you can only send
the LPN barcodes to perform “Reserve Location LPN Scan”
mode. In this case, if you send the inventory details for the
LPNs, the API fails.

update_only_counted_inventory_flg Boolean (True/False) No This parameter allows the system to limit the count only for
the counted inventories. Uncounted inventories will not be
updated to 0. Default value is False. This is not applicable for
the item driven cycle counts.
allow_new_lpn_count_flg Boolean (True/False) No If this is set to “True”, then the API allows you to update
the inventory or create CC adjustment records with new or
cancelled LPNs. Default value is “FALSE”.

This field cannot be “True” for LPN scan mode.

container_nbr String Conditional (only
when the count is for
reserve location)
Any valid LPN Barcode in WMS. This is applicable only for
reserve locations.
item_alternate_code String Yes Item alternate code defined in WMS.
item_part_x (x varies from ‘a’ to ‘f’) String No SKU identification code parts a to f.
qty_counted Number Yes Quantity that is counted for the item.
inv_attr_x (x varies from ‘a’ to ‘o’) String No Value for inventory attributes a to o.
batch_nbr String No Lot Number (Batch number) of the counted item.
expiry_date Date No Expiry date of the counted item. Format is "YYYY-MM-DD"
example: 2010-11-01
cc_uom String No UOM in which cycle count is being performed. May be
different than the primary UOM of the item being counted.

This can be in any UOM, packs or cases. MHE needs to
define the UOM at the CC_UOM field. Otherwise, this will be
considered from the primary UOM of the item/item facility.

pack_qty Integer No Pack quantity. You must send the standard pack quantity if
you are counting the in terms of packs.

83

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Parameter Name Type Required Description
If you are counting in packs and passing a nonstandard pack
quantity, then the API will fail.

case_qty Integer No Case quantity. You must send the standard case quantity if
you are counting the in terms of cases.

If you are counting in cases and passing a nonstandard case
quantity, then the API will fail.

count_ts Datetime Yes This is the time stamp when MHE counted the inventory.
The format is “YYYY-MM-DDTHH:MM:SS”.
serial_nbr_list Array (String) No List of serial numbers scanned for the counted inventory.
You can send the serial numbers as comma separated
values.
Request Body - Active Location
{
"async_flg":true,
"only_load_flg":true,
"header": {
"document_version": "25A",
"origin_system": "ENV1",
"client_env_code": "ENV1",
"parent_company_code": "COMP01",
"entity": "stage_cc_adjustment",
"timestamp": "2024-06-04T12:12:12",
"facility_code": "FAC01",
"company_code": "COMP01",
"messageid": "MSGID_0306202401002"
},
"stage_cycle_count_list":
[
{
"mhe_system": "CONVEYOR-1",
"task_nbr": "",
"task_type": "",
"location_barcode": "SS1202",
"update_only_counted_inventory_flg": "FALSE",
"stage_cycle_count_dtl_list":
[
{
"stage_cycle_count_inventory_list":
[
{
"item_alternate_code":"SSITEM01",
"item_part_a": "",
"item_part_b": "",
"item_part_c": "",
"item_part_d": "",
"item_part_e": "",
"item_part_f": "",
"qty_counted": "5",
"invn_attr_a": "",
84

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"invn_attr_b": "",
"invn_attr_c": "",
"invn_attr_d": "",
"invn_attr_e": "",
"invn_attr_f": "",
"invn_attr_g": "",
"invn_attr_h": "",
"invn_attr_i": "",
"invn_attr_j": "",
"invn_attr_k": "",
"invn_attr_l": "",
"invn_attr_m": "",
"invn_attr_n": "",
"invn_attr_o": "",
"cc_uom":"",
"batch_nbr":"",
"expiry_date":null,
"pack_qty":"0",
"case_qty":"0",
"count_ts": "2025-01-21T12:05:45",
"stage_cycle_count_serial_nbr":
{
"serial_nbr_list": ["S01","S02","S03","S04","S05"]
}
},
{
"item_alternate_code":"SSITEM02",
"item_part_a": "",
"item_part_b": "",
"item_part_c": "",
"item_part_d": "",
"item_part_e": "",
"item_part_f": "",
"qty_counted": "3",
"invn_attr_a": "",
"invn_attr_b": "",
"invn_attr_c": "",
"invn_attr_d": "",
"invn_attr_e": "",
"invn_attr_f": "",
"invn_attr_g": "",
"invn_attr_h": "",
"invn_attr_i": "",
"invn_attr_j": "",
"invn_attr_k": "",
"invn_attr_l": "",
"invn_attr_m": "",
"invn_attr_n": "",
"invn_attr_o": "",
"cc_uom":"",
"batch_nbr":"",
"expiry_date":null,
"pack_qty":"0",
"case_qty":"0",
"count_ts": "2025-01-21T12:05:45",
"stage_cycle_count_serial_nbr":
{
"serial_nbr_list": ["S06","S07","S08"]
}
}
]
}
85

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
]
}
]
}
Request Body - Reserve Location Detailed Count
{
"async_flg": true,
"only_load_flg": false,
"header": {
"document_version": "25B",
"origin_system": "ENV1",
"client_env_code": "ENV1",
"parent_company_code": "COMP01",
"entity": "stage_cc_adjustment",
"timestamp": "2024-06-04T12:12:12",
"facility_code": "FAC01",
"company_code": "COMP01",
"messageid": "MSGID_0306202401002"
},
"stage_cycle_count_list": [
{
"mhe_system": "CONVEYOR-1",
"task_nbr": "",
"task_type": "",
"location_barcode": "SSRSV1101",
"lpn_scan_flg": "FALSE",
"update_only_counted_inventory_flg": "FALSE",
"allow_new_lpn_count_flg": "FALSE",
"stage_cycle_count_dtl_list": [
{
"container_nbr": "LPN001",
"stage_cycle_count_inventory_list": [
{
"item_alternate_code": "SSITEM01",
"item_part_a": "",
"item_part_b": "",
"item_part_c": "",
"item_part_d": "",
"item_part_e": "",
"item_part_f": "",
"qty_counted": "5",
"invn_attr_a": "",
"invn_attr_b": "",
"invn_attr_c": "",
"invn_attr_d": "",
"invn_attr_e": "",
"invn_attr_f": "",
"invn_attr_g": "",
"invn_attr_h": "",
"invn_attr_i": "",
"invn_attr_j": "",
"invn_attr_k": "",
"invn_attr_l": "",
"invn_attr_m": "",
"invn_attr_n": "",
"invn_attr_o": "",
"batch_nbr": "",
"expiry_date": "2025-11-01",
86

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"cc_uom": "",
"pack_qty": "0",
"case_qty": "0",
"count_ts": "2025-01-21T12:05:45",
"stage_cycle_count_serial_nbr": {
"serial_nbr_list": [
"SER01",
"SER02",
"SER03",
"SER04",
"SER05"
]
}
},
{
"item_alternate_code": "SSITEM02",
"item_part_a": "",
"item_part_b": "",
"item_part_c": "",
"item_part_d": "",
"item_part_e": "",
"item_part_f": "",
"qty_counted": "5",
"invn_attr_a": "",
"invn_attr_b": "",
"invn_attr_c": "",
"invn_attr_d": "",
"invn_attr_e": "",
"invn_attr_f": "",
"invn_attr_g": "",
"invn_attr_h": "",
"invn_attr_i": "",
"invn_attr_j": "",
"invn_attr_k": "",
"invn_attr_l": "",
"invn_attr_m": "",
"invn_attr_n": "",
"invn_attr_o": "",
"batch_nbr": "",
"expiry_date": "2025-11-01",
"cc_uom": "",
"pack_qty": "0",
"case_qty": "0",
"count_ts": "2025-01-21T12:05:45",
"stage_cycle_count_serial_nbr": {
"serial_nbr_list": [
"SER06",
"SER07",
"SER08",
"SER09",
"SER10"
]
}
}

]
}
]
}
]
}
87

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Request Body - Reserve Location LPN Scan Mode
{
"async_flg": true,
"only_load_flg": false,
"header": {
"document_version": "25B",
"origin_system": "ENV1",
"client_env_code": "ENV1",
"parent_company_code": "COMP01",
"entity": "stage_cc_adjustment",
"timestamp": "2024-06-04T12:12:12",
"facility_code": "FAC01",
"company_code": "COMP01",
"messageid": "MSGID_0306202401002"
},
"stage_cycle_count_list": [
{
"mhe_system": "CONVEYOR-1",
"task_nbr": "",
"task_type": "",
"location_barcode": "SSRSV1202",
"lpn_scan_flg": "TRUE",
"update_only_counted_inventory_flg": "FALSE",
"allow_new_lpn_count_flg": "FALSE",
"stage_cycle_count_dtl_list": [
{
"container_nbr": "LPN001"
},
{
"container_nbr": "LPN002"
}
]
}
]
}
Sample Response
{
"success": true,
"response": {
"message": "Data successfully processed"
}
}
Cycle Count Adjustment
The following APIs allow you to fetch paginated results for Cycle Count Header entries and Cycle Count details.
Cycle Count Adjustment Header URLs
Fetch paginated results when users use the following URL:
GET .../lgfapi/v10/entity/cc_adjustment_hdr/
Fetch non-paginated result by specific 'ID':
88

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
GET .../lgfapi/v10/entity/cc_adjustment_hdr/{id}
Cycle Count Adjustment Detail URLs
Fetch paginated results when users use the following URL:
GET .../lgfapi/v10/entity/cc_adjustment_dtl/
Fetch non-paginated result by specific 'ID':
GET .../lgfapi/v10/entity/cc_adjustment_dtl/{id}
Cycle Count Adjustment Approval Rule
This entity is used to get the list of the cycle count adjustment approval rules present in the system. These rules can
be utilized to feed an external system or referenced outside of WMS, providing flexibility and integration with other
platforms.
To fetch all results, use the following URL:
GET .../lgfapi/v10/entity/cc_adjustment_approval_rule/
To fetch only one result based on ‘ID’, search with a specific 'ID' in the following URL:
GET .../lgfapi/v10/entity/cc_adjustment_approval_rule/{id}
In the same way, the support is extended for HEAD Request Method using the following URL:
HEAD .../lgfapi/v10/entity/cc_adjustment_approval_rule/{id}
Cycle Count Summary Adjustment
The following APIs allow you to fetch paginated results for Cycle Count Summary Adjustment Header entries and Cycle
Count Summary Adjustment details.
Cycle Count Summary Adjustment Header URLs
Fetch paginated results using the following URL:
GET .../lgfapi/v10/entity/cc_summary_adjustment_hdr/
Fetch non-paginated result by specific 'ID':
GET .../lgfapi/v10/entity/cc_summary_adjustment_hdr/{id}
Cycle Count Summary Adjustment Detail URLs
Fetch paginated results using the following URL:
GET .../lgfapi/v10/entity/cc_summary_adjustment_dtl/
Fetch non-paginated result by specific 'ID'
GET .../lgfapi/v10/entity/cc_summary_adjustment_dtl/{id}
89

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Describe Entity
GET …/wms/lgfapi/v10/entity/{entity_name}/describe/
The describe operation is unique in that it is common and can be used on any entity. It returns a formatted
representation of the entity’s metadata including any filterable “parameters” and all field definitions. This is the primary
tool for obtaining details about a specific entity.
Response Components
• parameters – A list of fields that can be used for filtering of the entity.
• fields – Field definitions and metadata for the entity.
◦ type – The field data type
◦ allow_blank – String fields only. Is an empty string value permitted?
◦ max_length – String fields only. Max string length permitted.
◦ required – Does the field require data.
Note: Note about Required fields - X or Y indicates the field is required. N indicates the field is not
required. C indicates that the field is conditional.
◦ default – If the fields is not required, the default value when no value is provided.
Facility
These topics give descriptions for APIs that complete actions related to facilities for the Warehouse.
Bulk Change Eligible Facility
The Bulk Change Eligible Facility API allows you to add/remove the user eligible facility in bulk. You can update single or
multiple user eligible facility all at once. Once updates are made, they will reflect in the User UI --> Eligible Facility.
URL
POST ...../v10/entity/user/bulk_change_eligible_facility
Example Body Request
{
"parameters": {
"company_id": "222",
"auth_user_id**username**in": [
"user1",
"user2",
"user3"
]
},
"options": {
90

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"action": "ADD",
"facility_id_list": [10,20,21],
"facility_code_list": ["FAC1","FAC2","FAC3"],
"commit_frequency": 1
}
Facility Parameter
POST .../entity/facility_parm
This operation is used to add single or multiple facility parameters.
If you have a new facility and you want to copy the same facility parameters from your current facility, you can first GET
the list by querying the facility_parm entity, then POST the applicable data to this operation for the target facility.
Example Body Request
{
"fields": {
"facility_id": 1,
"prog_key": "FACILITY_PARM",
"parm_key": "TEST_PARM_001",
"parm_value": "test"
}
}
IBLPN
These topics give descriptions for APIs that complete actions related to IBLPNs in the Warehouse.
The “iblpn” entity is derived from the “container” entity and therefore also has access to all of its entity operations, in
addition to the following:
Direct Consume
POST …/wms/lgfapi/v10/entity/iblpn/{id}/direct_consume/
The direct consume API allows you to consume a Received or Located IBLPN and update its inventory to zero. This will
write IBLPN consumed inventory history records.
Note: The `options` parameters, `transaction_ref_nbr`, may now be passed in the request body. This parameters will
be added to any CNTR_CONSUMED inventory history records created as part of the API’s execution. The inventory
history field `ref_code_3` will now be set as “TRN”. The value of `ref_value_3` will be that of `transaction_ref_nbr` or an
empty string.
Sample Payload
{
91

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"options": {
"reason_code" : "DAM",
"transaction_ref_nbr" : "TX12345",
"num_days_iblpn_lost_for_consume": 1
}
}
Category Name Type Required Description
options reason_code String X Used for inventory
history tracking.
options transaction_ref_nbr String N Max length of 250
characters.
options num-days-iblpnlost-
for-consume
Integer N Blank or 0 Considers LPNs in
status Lost to be
consumed according
to the number of days
that it has been lost.
(Last mod date )
Modify Item Quantity
The IBLPN modify_item_qty API allows the caller to adjust item inventory in a “Received” or “Located” IBLPN. You can
only update a single IBLPN and item per request.
Regardless of the method used to identify the IBLPN, the following input is valid:
Category Name Type Required Description
options item_barcode String C Item identifier.
options item_alternate_code String C Item identifier.
options adjustment_qty Numeric Y Non-zero adjustment quantity.
options batch_nbr String N Batch tied to target inventory.
options expiry_date Date N Expiration date tied to target inventory.
options invn_attr_X String N Attributes A-O tied to the inventory.
options reason_code String Y Recorded on inventory history.
options transaction_ref_nbr String N Recorded on inventory history.
Parameters actual_qty Numeric Y Actual quantity of the LPN
options serial_nbr_list String N Serial Number list
• Only one of `item_barcode` or `item_alternate_code` is allowed.
92

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
• IBLPN inventory matching is restrictive and does not support wildcard searches:
◦ If no `batch_nbr` is provided, only match IBLPN inventory without a batch.
◦ If no `expriy_date` is provided, only match IBLPN inventory without expiration.
◦ If no `invn_attr_X` value is provided for A-O, it will be treated as blank.
◦ The user must send either adjusted quantity or actual quantity.
IBLPN Lookup by ID
POST .../entity/iblpn/{id}/modify_item_qty/
Caller knows the unique `id` value of the IBLPN, which is added to the request URL. No additional `parameters` data is
required from the request body.
IBLPN Lookup by Filters
POST .../entity/iblpn/modify_item_qty/

Category Name Type Required Description
parameters container_nbr String Y IBLPN to be adjusted.
parameters facility_id Integer N IBLPN’s facility.
parameters company_id Integer N IBLPN’s company.
• Only a single IBLPN may be moved per request.
◦ The `__in` lookup is not supported for `container_nbr`.
• `facility_id` and `company_id` both additionally support string lookup by `code` using the double-underscore
notation:
◦ facility_id\_\_code
◦ company_id_code
Example Request Body:
{
"options": {
"item_barcode": "ITEM1234",
"actual_qty": 13,
"batch_nbr": "BATCH1234",
"expiry_date": "2020-01-02",
"invn_attr_a": "A",
"reason_code": "C",
"transaction_ref_nbr": "TX123457890",
"serial_nbr_list": ["SN001", "SN002",...,"SN0013"]
}
}
93

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Track User Activity
If you have purchased WFM (Oracle Workforce Management), you can also send user activity data using the following
parameters in the Modify Item Quantity API.
• Screen_name: Name of the application or screen in the external system that was used by the user to modify
the LPN.
• Begin_ts: Time at which the user started modifying the LPN.
• End_ts: Time at which the user completed the modification of the LPN.
If all the three parameters are sent in the API, and if WFM is enabled, user activity is written to the WMS Activity view
and subsequently interfaced to WFM, enabling you to analyze user productivity through productivity reports in WFM.
Note:
• All three parameters must be sent for WMS Activity to be written.
• If WFM is not enabled, WMS Activity is not written even if the three parameters are sent.
• In order for WMS Activity data to interface successfully to WFM, screen_name that is sent in the API has to be
configured as a screen in WMS using an RF module and mapped to a work area activity in WFM.
• Screen_name sent on the API is also written on the corresponding IHTs that are written with this API.
• If only screen_name is sent without begin_ts and end_ts, the screen_name is written on the IHT, even if WFM is
not enabled.
• Begin_ts and End_ts cannot be greater than the current timestamp of the facility in the API.
Request Body with User Activity Data
{
"parameters": {
"facility_id": 268,
"company_id": 572,
"container_nbr": "LPN123"
},
"options": {
"item_barcode": "Item123",
"adjustment_qty": 10,
"reason_code": "DMG",
"begin_ts": "2024-05-27T18:30:00",
"end_ts": "2024-05-27T18:45:00",
"screen_name": "Modify IBLN Qty"
}
}
94

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Composite Create
POST …/wms/lgfapi/v10/entity/iblpn/composite_create/
This operation allows for the creation of a Received or Located IBLPN along with one or more inventory records in a
single request. Furthermore, it allows for the creating and/or association of the inventory’s corresponding batch and
inventory attribute, where applicable. This API follows all of the same validations and extended actions, such as writing
inventory history, as the standalone create (POST) APIs for each entity, but brings them together in a single API.
Furthermore, this API takes advantage of allowing for the input of nested data, such as batch and inventory attribute,
which will allow for those objects to be created or retrieved if they already exist. The use of the related objects “id” value
is still permitted as well. All objects must have the same facility and company context as the IBLPN being created, and
must still pass all standard user eligibility validations.
When the Composite Create API is called, an error will be returned if the appropriate serial number information is not
provided for any serial number tracked items:
This change avoids the requirement of making multiple API calls to complete the linking.
Note: Customers using composite_create for serial number tracked items should ensure that serial number
information is shared in the composite create itself.
The following is an example body for composite create:
{
"fields": {
"facility_id": 269, <== Will be inherited by objects
"company_id": 48, <== Will be inherited by objects
"iblpn": {
"container_nbr": "IBLPN000001",
"status_id": 30,
"curr_location_id": 28536,
"putawaytype_id":1020,
"length": 1.1234567,
"width": 2.34567890,
"height": 3.123
},
"inventory": [ <== List of dictionaries, one per inventory record.
{
"item_id": 1,
"expiry_date": "2019-01-01",
"curr_qty": 1.2345,
"batch_number_id": 1,
"invn_attr_id": 2,
"serial_nbr_list": [ <== Single Inventory can have multiple serial numbers.
"SN1",
"SN2",
"SN3"
]
}
]
},
"options": {
"reason_code": "IT",
"validate_serial_nbrs_flg": false
}
95

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
}
This API also has unique data structure requirements that mimic those of the individual entity’s create (POST) field
inputs. It also allows for the definition of a global context where “facility_id” and “company_id” may be defined at the
top level of the data and inherited by each object, if not defined on the object.
Category Parameter Type Required Default Description
fields facility_id Integer C “id” value of Facility.
Not required if defined
on the IBLPN or per
object.
fields company_id Integer C “id” value of Company.
Not required if defined
on the IBLPN or per
object.
fields iblpn Dictionary X Field value definitions
for the IBLPN being
created. These are
the same as if using
a standalone POST
request for creating an
IBLPN.
fields inventory Array X A list of one or more
inventory objects to be
created and associated
with the given IBLPN.
options reason_code String X Used for inventory
history tracking.
The following is an example of JSON request data where the facility/company context is defined at the top level and
using the “id” values of “batch_number_id” and “invn_attr_id” to associate those objects that already exist. The defined
top-level facility and company will be applied to the iblpn and inventory objects being created. The existing batch and
inventory attribute objects being associated to the inventory must be of the same context.
Note: even though “inventory” does not have a “company_id” field, the company is determined from the associated
item’s company and must also pass validations.
{
"fields": {
"facility_id": 1,
"company_id": 1,
"iblpn": {
"container_nbr": "IBLPN000001",
"status_id": 30,
"curr_location_id": 28536
},
"inventory": [
96

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
{
"item_id": 1,
"curr_qty": 1.2345,
"batch_number_id": 1,
"invn_attr_id": 1
}
]
},
"options": {
"reason_code": "IT"
}
}
The following is an example of JSON request data where the facility/company context is defined per object and using
the “id” values of “batch_number_id” and “invn_attr_id” to associate those objects that already exist. Also demonstrates
creating multiple inventory records for different item/batch/attribute combinations in a single IBLPN:
{
"fields": {
"iblpn": {
"facility_id": 1,
"company_id": 1,
"container_nbr": "IBLPN000002",
"status_id": 10
},
"inventory": [
{
"facility_id": 1,
"item_id": 1,
"curr_qty": 1.2345,
"batch_number_id": 1,
"invn_attr_id": 1
},
{
"facility_id": 1,
"item_id": 2,
"curr_qty": 10,
"batch_number_id": 2,
"invn_attr_id": 2
}
]
},
"options": {
"reason_code": "IT"
}
}
The following is an example of JSON request data where the facility/company context is defined at the top level and
the “id” values of “batch_number_id” and “invn_attr_id” have been replaced with nested objects to create and associate
those objects, which may or may not already exist:
{
"fields": {
"facility_id": 1,
"company_id": 1,
"iblpn": {
"container_nbr": "IBLPN000003",
"status_id": 10
},
"inventory": [
{
"item_id": 3,
"curr_qty": 1,
"batch_number_id": {
97

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
“batch_nbr”: “BATCH001”,
“item_id”: 3,
“expiry_date”: “2019-01-01”
},
"invn_attr_id": {
“invn_attr_a”: “A”,
“invn_attr_b”: “B”,
“invn_attr_c”: “C”
}
}
]
},
"options": {
"reason_code": "IT"
}
}
Track User Activity
If you have purchased WFM (Oracle Workforce Management), you can also send user activity data using the following
parameters in the Composite Create IBLPN API
• Screen_name: Name of the application or screen in the external system that was used by the user to create the
IBLPN.
• Begin_ts: Time at which the user started creating the IBLPN.
• End_ts: Time at which the user completed the creation of the IBLPN.
If all the three parameters are sent in the API, and if WFM is enabled, user activity is written to the WMS Activity view
and subsequently interfaced to WFM, enabling you to analyze user productivity through productivity reports in WFM.
Note:
• All three parameters must be sent for WMS Activity to be written.
• If WFM is not enabled, WMS Activity is not written even if the three parameters are sent.
• Begin_ts and end_ts are parameters at the inventory level and must be sent on all inventories.
• Activity tracking is currently not supported at the IBLPN level.
• In order for WMS Activity data to interface successfully to WFM, screen_name that is sent in the API has to be
configured as a screen in WMS using an RF module and mapped to a work area activity in WFM.
• Screen_name sent on the API is also written on the corresponding IHTs that are written with this API.
• If only screen_name is sent without begin_ts and end_ts, the screen_name is written on the IHT, even if WFM is
not enabled.
• Begin_ts and End_ts cannot be greater than the current timestamp of the facility in the API.
98

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Request Body with User Activity Data
{
"fields": {
"facility_id": 1,
"company_id": 1,
"iblpn": {
"container_nbr": "IBLPN000003",
"status_id": 10
},
"inventory": [{
"item_id": 2,
"curr_qty": 1,
"begin_ts": "2024-05-27T18:30:00",
"end_ts": "2024-05-27T18:45:00"
},
{
"item_id": 4,
"curr_qty": 2,
"begin_ts": "2024-05-27T18:50:00",
"end_ts": "2024-05-27T18:55:00"
}]
},
"options": {
"reason_code": "IT",
"screen_name": "Create IBLPN Screen"
}
}
Receive
The Receive API it allows you to receive LPNs. Currently, it supports attributes, batch, and expiry.
Note: Receipt can be done using the Purchase Order (PO) number or Inbound Shipment. If the PO number is
provided, then the Inbound Shipment is created automatically.
API Signature
POST .../entity/iblpn/receive
The following is an example body for receive API.
{ "facility_id_code": "FAC",
"company_id\_\_code": "COMP",
"shipment_nbr": "SHIPMTNBR",
"container_nbr": "CNTRNBR",
"recv_dock_nbr_or_location_barcode": "DOCK_NBR_OR_BARCODE",
"trailer_nbr": "TRLRNBR",
"lpn_type": "LPT",
"pallet_nbr": "PLTNBR",
"item_list": [{
"item_barcode": "ITEM1234",
"qty": 10,
"case_qty": 5,
"pack_qty": 5
}]
99

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
}
Request Parameters
Name Required Type Default Description
facility*id Integer Facility context by id.
facility_id**code String Facility context by code.
company_id Integer Company context by id.
company_id**code String Company context by code.
container_nbr X String IB container number
shipment_nbr C String IB shipment number
po_nbr C String Purchase order number
recv_dock_nbr_or_location*
barcode
String The dock number or dock
location barcode at which
the LPN is being received.
pallet_nbr String Pallet number
trailer_nbr String Trailer number
lpn_type String LPN type Code
item_list List SKU list
allow_inv_exp_override_flg Boolean False Any inbound SKUs with
an expiry date earlier than
the existing inventory of
available, the system will
not allow you to receive the
inventory and displays an
error message.
allow_rem_exp_override_flg Boolean False If the expiration date
entered does not pass the
“% acceptable” validation,
the system does not allow
you to receive the SKU and
displays an error message
“Rem prod life below accept
percent”.
Item List
Name Required Type Default Description
item_barcode X String Item Barcode
qty X Integer Quantity
100

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Required Type Default Description
case_qty Integer Case Quantity
pack_qty Integer Pack Quantity
po_nbr C String Purchase order number
po_seq_nbr C Integer Purchase order sequence
number
batch_nbr C String Batch number
batch_number C (If item is batch tracked,
then batch number is
mandatory.)
String Batch number
expiry_date C (If item is expiry tracked,
then expiry date is
mandatory. However, if
existing batch has expiry
date, then expiry date is not
mandatory.)
Date Expiry date for a batch
serial_nbr_list C (When the company is
configured for end-to-end
serial tracking, then serial
number is mandatory.)
String List of serial numbers in an
LPN
inv_attr_x (x varies from ‘a’
to ‘o’)
C (If item is tracking
corresponding inventory
attribute, then respective
inventory attribute is
mandatory.)
String Value provided for
inventory attributes a-o
qty C Number Value provided as a part of
cartonized receipt
manufacture_date C (If item is expiry tracked,
then either expiry date
or manufacture date is
mandatory to pass.)
Date Manufacture date
Cross Dock Receiving
The Receive REST API also allows Cross Docking of an LPN.
URL:
POST .../entity/iblpn/receive
101

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Request Parameter / Options
Name Required Type Default Options
xdock_mode N String None • 'lpn',
• 'lpn-and-one-sku',
• 'lpn-one-and-multi-
facility',
• 'lpn-one-and-multi'
• lpn-and-one-sku : It will first check the receiving LPN with orders that have arequired lpn number. If doesnt
match, it will try to do single sku xdock (as long as it is single sku lpn).
• lpn : It will first check the receiving LPN with orders that required lpn number.
• lpn-one-and-multi-facility: It will first try to match LPN with an order. If it doesnt match, then will try to cross
dock single sku. If it is a multi sku, it will try to xdock facility ( but it has to be a facility order).
• lpn-one-and-multi: It will first try to match LPN with an order. If it doesnt match, then will try to cross dock
single sku. If it is a multi sku, it will try to xdock.
Additional Notes
As of now we support only receiving of normal items. Support for attribute, batch, expiry and serial tracking items will
be added later.
Note: Receipt of cartonized LPNs is not supported for batch / expiry / inventory_attributes/ serial-tracking items,
even if underlining shipment details for the LPNs have batch / expiry / inventory_attributes/ serial information.
• We do not support LPN as a Physical Pallet.
• We do not support detail receiving for cartonized LPNs.
• We do not support handling over-receipt warning message.
• QC flow is not supported.
Note: If you are sending a case or pack quantity, it must be a multiple of standard case or standard pack quantity. For
a cartonized shipment, the REST API will only pass the LPN information and ignore the item list information.
If a PO number is passed in the API header, the PO is converted to a shipment for a PO based receiving.
Note: When the shipment is subjected for PO-based receiving, the PO sequence will not be considered.
Receive UOM
With the receive API, you can also receive inbound shipments with receiving UOM.
102

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Receiving UOM Sample Body
{ "facility_id_code": "QATST01",
"company_id_code": "QATSTPC",
"shipment_nbr": "APIBS25012302",
"container_nbr": "APCNTR27012301",
"recv_dock_nbr_or_location_barcode": "BH-DK-01-01",
"trailer_nbr": "APTRL2701",
"lpn_type": "PEP-BEV",
"pallet_nbr": "APPLT-27012301",
"item_list": [{
"item_barcode": "AP004",
"qty": 10,
"receiving_uom": "LB"
}]
}
Track User Activity
If you have purchased WFM (Oracle Workforce Management), you can also send user activity data using the following
parameters in the Receive API
• Screen_name: Name of the application or screen in the external system that was used by the user to perform
receiving.
• Begin_ts: Time at which the user started receiving the relevant item.
• End_ts: Time at which the user completed receiving the relevant item.
If all the three parameters are sent in the API, and if WFM is enabled, user activity is written to the WMS Activity view
and subsequently interfaced to WFM, enabling you to analyze user productivity through productivity reports in WFM.
103

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Note:
• All three parameters must be sent for WMS Activity to be written.
• If WFM is not enabled, WMS Activity is not written even if the three parameters are sent.
• Begin_ts and end_ts are parameters at the line level and must be sent on all lines.
• Activity tracking is currently not supported for cartonized receiving (payloads without lines)
• In order for WMS Activity data to interface successfully to WFM, screen_name that is sent in the API has to be
configured as a screen in WMS using an RF module and mapped to a work area activity in WFM.
• Screen_name sent on the API is also written on the corresponding IHTs that are written with this API.
• If only screen_name is sent without begin_ts and end_ts, the screen_name is written on the IHT, even if WFM is
not enabled.
• Begin_ts and End_ts cannot be greater than the current timestamp of the facility in the API.
Request Body with User Activity Data
{
"facility_id": "268",
"company_id": "572",
"container_nbr": "LPN123",
"screen_name": "Dtl Recv Screen",
"item_list": [
{
"item_barcode": "s1",
"qty": 10,
"begin_ts": "2024-05-21T18:30:00",
"end_ts": "2024-05-21T18:45:00"
},
{
"item_barcode": "s2",
"qty": 10,
"begin_ts": "2024-05-21T18:50:00",
"end_ts": "2024-05-21T18:55:00"
}
]
}
Split LPN
The Split LPN API allows you to split allocated Inbound LPNs into multiple LPNs. This will assist you in identifying
allocations during packing, and increase efficiency.
104

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
URL
POST /entity/iblpn/{id}/split*lpn/
Request Options
Name Required Type Default Description
company_id Y String Company ID
facility_id Y String
auto_generate_lpn N Boolean N If set to yes then do not
provide to_lpn
to_lpn_list Y Array List of LPN the inventory is
going to be split to. Refer to to*
lpn_list section for details
Sample Payload
"parameters": {
"iblpn_nbr": "LPN0"
},
"options": {
"company_id": "units",
"facility_id ": false,
"mhe_system_code": "",
"auto_generate_lpn": true,
"to_lpn_list": [
{
"to_lpn_nbr": "LPN1",
"inv_list": [
{
"item_code": "ABC",
"batch_nbr": "BAT1",
"expiry_date": "2024-12-31",
"invn_attr_a": "A1",
"invn_attr_b": "B1",
"invn_attr_c": "C1",
"qty": 10,
"uom_code": "pack",
"alloc_info": {
"facility_code": "bar"
}
},
{
"item_code": "ABC",
"batch_nbr": "BAT2",
"expiry_date": "2025-01-01",
"invn_attr_a": "A1",
"invn_attr_b": "B1",
"invn_attr_c": "C1",
"qty": 15,
"uom_code": "pack"
}
]
},
{
"to_lpn_nbr": "LPN2",
105

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"inv_list": [
{
"item_code": "DEF",
"invn_attr_a": "A1",
"invn_attr_b": "B1",
"invn_attr_c": "C1",
"qty": 20
}
]
}
]
}
}
to_lpn_list
Name Required Type Default Description
to_lpn C
item_code N String
expiry_date C
invn_attr_a - inv_attr_o C String T arget attribute value.
uom R String "units", "packs", "cases"
batch_nbr C String
qty Y number
alloc_info_list Y Array List of fields for identifying
allocation for the inventory
Note: if inventory has allocations, the alloc_info_list is required.
alloc_info_list
Name Required Type Default Description
facility_code C String Store number required for
allocation type distribution
wave_nbr N String default to empty. Will be used
for strict matching.
order_nbr C String If not store provided order
number is required
order_seq_nbr C If order number is sent this is
required
106

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
IBLPN Lookup by Filter
POST /entity/iblpn/split*lpn/
Options
Name Required Type Default Description
company_id Y String Company ID
facility_id Y String
mhe_system_code N String Code for MHE system
integration.
auto_generate_lpn N Boolean N If set to yes then do not
provide to_lpn
to_lpn_list Y Array List of LPN the inventory is
going to be split to. Refer to to*
lpn_list section for details
Split LPN for Replenishment
The new split LPN for Replenishment API allows third party integration systems or Product as a service (PAAS) to do
split an existing replenishment allocation of type “REPLEN_CS_PK_UNITS” into multiple smaller tasks as FULL LPN
replenishments. This would be most conducive if you have an LPN that contains more than one unit of an UOM, and it
does not fit for example on a conveyor belt.
You can split the LPN by it’s UOM, and it can fit on the conveyor and be used for allocations created during Mode 2
Replenishment. You can pass a fully or partly allocated container number in the API call. This container number is
considered your source LPN. In the request parameter, you can pass inventory information (such as item, batch, expiry
date, or inventory attributes a-o), quantities for the source LPN UOM that is being tracked, and more. This information
will be used to track the new LPN along the conveyor, and it will create a new task with task type “REPLEN_LPN.”Note:
The Split LPN for Replenishment API does not support serial number, and it will be added in a future release.
• POST .../wms/lgfapi/v10/entity/iblpn/<id>/split_lpn_for_replen
• POST .../wms/lgfapi/v10/entity/iblpn/split_lpn_for_replen
Name Type Required Description
facility_id Integer C Facility context by id.

one of id or code should be
provided

facility_id\_\_code String C Facility context by code.
107

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Type Required Description

one of id or code should be
provided

company_id String C Company context by id.

one of id or code should be
provided

company_id\_\_code String N Company context by code.

one of id or code should be
provided

container_nbr String Y Container/Source LPN pulled for
split

• If facility and/or company are provided, set login context accordingly.
• Only one of `facility_id` or `facility_id__code` may be provided.
• Only one of `company_id` or `company_id__code` may be provided.
Example:
{
"parameters": {
"facility_id\_\_code": "FAC",
"company_id": 1,
"container_nbr": "LPN123"
}
}
Request Parameters - Options
Name Required Type Default Description
item_barcode C String one of item_barcode

or item_alternate_code is
required

item_alternate_code C String one of item_barcode

108

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
or item_alternate_code is
required

batch_nbr String batch specified on the
inventory in the source LPN
expiry_date String expiry of inventory in the
source LPN
invn_attr_a to

invn_attr_o

String inventory attributes A to O
specified on the inventory
qty*in_uom X integer new parameter. Total Qty in
UOM.(2 units/2 cs/2pks)
new_container_nbr_list X list of Strings new parameter. List of new
LPN numbers
location_barcode Optional String must be of location type
DROP
task_type_description X String Description of REPLEN*
LPN task type
Example
{
"options": {
"item_barcode": "ITEM123"
"batch_nbr": "BTCH123"
"invn_attr_a": "AA123"
"qty_in_uom": 2
"new_container_nbr_list": ["lpn1","lpn2"],
"location_barcode": "LOC1",
"task_type_description": "Full LPN Replenishment - PM"
}
}
Full Request Body Examples
Request with `id` in URL
POST .../wms/lgfapi/v10/entity/iblpn/<id>/split_lpn_for_replen
{
"options": {
"item_barcode": "LOAD123",
"batch_nbr": "BTCH123",
"invn_attr_a": "AA123",
"qty_in_uom": 4,
"new_container_nbr_list": ["lpn1","lpn2","lpn3","lpn4"],
"location_barcode": "LOC1",
"task_type_description": "Full LPN Replenishment - PM"
}
}
109

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Request without ID in URL:
POST .../wms/lgfapi/v10/entity/iblpn/split_lpn_for_replen
{
"parameters": {
"facility_id\_\_code": "FAC",
"company_id": 1,
"container_nbr": "LPN123"
},
"options": {
"item_alternate_code": "ITEM123"
"qty_in_uom": 4,
"new_container_nbr_list": ["lpn1","lpn2","lpn3","lpn4"],
"location_barcode": "LOC1",
"task_type_description": "Full LPN Replenishment - PM"
}
}
Track User Activity
If you have purchased WFM (Oracle Workforce Management), you can also send user activity data using the following
parameters in the Split LPN for Replenishment API
• Screen_name: Name of the application or screen in the external system that was used by the user to split LPN.
• Begin_ts: Time at which the user started split LPN.
• End_ts: Time at which the user completed split LPN.
If all the three parameters are sent in the API, and if WFM is enabled, user activity is written to the WMS Activity view
and subsequently interfaced to WFM, enabling you to analyze user productivity through productivity reports in WFM.
Note:
• All three parameters must be sent for WMS Activity to be written.
• If WFM is not enabled, WMS Activity is not written even if the three parameters are sent.
• In order for WMS Activity data to interface successfully to WFM, screen_name that is sent in the API has to be
configured as a screen in WMS using an RF module and mapped to a work area activity in WFM.
• Screen_name sent on the API is also written on the corresponding IHTs that are written with this API.
• If only screen_name is sent without begin_ts and end_ts, the screen_name is written on the IHT, even if WFM is
not enabled.
• Begin_ts and End_ts cannot be greater than the current timestamp of the facility in the API.
Request Body with User Activity Data
{
"parameters": {
"facility_id": 101,
110

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"company_id": 102,
"container_nbr": "LPN123"
},
"options": {
"item_alternate_code": "ITEM123"
"qty_in_uom": 4,
"new_container_nbr_list": ["lpn1","lpn2","lpn3","lpn4"],
"location_barcode": "LOC1",
"task_type_description": "Full LPN Replenishment - PM",
"begin_ts": "2024-05-27T18:30:00",
"end_ts": "2024-05-27T18:45:00",
"screen_name": "Split LPN For Replen Screen"
}
}
Deallocate
The deallocate API allows you to de-allocate IBLPN which is in Partially Allocated/Allocated status through an API
API URL: Lookup by ID
POST.../entity/LPN/{id}/deallocate/
No additional `parameters` data in the request body is required.
API URL: Lookup by Filters
POST.../entity/iblpn/deallocate/
Category Name Required Type Description
parameters facility_id Integer Facility context by id
parameters facility_id**code string Facility context by code
parameters company_id Integer Company context by id
parameters company_id**code string Company context by code
parameters container_nbr X string IBLPN which needs to be
De-allocated
• If facility and/or company are provided, set login context accordingly.
• Only one of `facility_id` or `facility_id__code` may be provided.
• Only one of `company_id` or `company_id__code` may be provided.
Bulk_Cancel URL
POST.../entity/iblpn/bulk_deallocate/
111

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Request Body:
The transaction is meant for the task entity. The users are required to send the following parameters in the body.
POST.../entity/iblpn/bulk_deallocate/
{
"parameters": {
"id\_\_in": [01, 02, 03]
},
"options": {
"commit_frequency": "0",
}
}
The commit frequency is by default set to 0. If it is set to 0, the system should roll back on first error/ If the commit
frequency is set to 1, the system should commit per object. ID can be sent in bulk_deallocate or LPN numbers can also
be shared.
Vendor Performance Code
The Vendor Performance Code API allows you to to fetch the vendor performance code as an entity. Only the GET and
HEAD http methods are supported for this API.
The following are some ways for calling the Vendor Performance Code API:
• GET....../entity/vendor_perf_code/
Note: The system will display paginated results when users use the above URL.
Using the T ask ID
• GET....../entity/vendor_perf_code/{id}/
Note: The system will display non paginated results when users use the above URL
Quality Check Approve/Reject
The QC Approve API allows you to approve QC marked IBLPNs. You can perform quality check by using external quality
check modules with custom verification methods without accessing the UI or RF QC complete module in Oracle WMS
Cloud.
QC Approve
The following are some ways for calling the QC Approve API:
Using the Wave Template ID:
• POST.../entity/iblpn/{id}/qc_approve/
112

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Note: No additional `parameters` data in the request body is required.
Using the Container Number:
• POST.../entity/iblpn/qc_approve/
Note: The API body should include facility id/code, company id/code and container number. You can also send the
Vendor Performance code as an option in the API request body.
Using the Bulk QC Approve:
• POST.../entity/iblpn/bulk_qc_approve/
Note: The API body should have either the container IDs or container numbers in the. You can also send the Vendor
Performance code as an option in the API request body.
Once quality check is approved, the container status becomes Received with QC status as QC approved.
QC Reject
The following are some ways for calling the QC Reject API:
Using the Wave Template ID:
• POST.../entity/iblpn/{id}/qc_reject/
Note: You can send the Vendor Performance code and Lock code as options in the API request body.
Using the Container Number:
• POST.../entity/iblpn/qc_reject/
Note: The API body should include facility id/code, company id/code and container number. You can also send the
Vendor Performance code and Lock code as options in the API request body.
Using the Bulk QC Approve:
• POST.../entity/iblpn/bulk_qc_reject/
Note: The API body should have either the container IDs or container numbers in the. You can also send the Vendor
Performance code Lock code as options in the API request body.
113

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
If you do not send the unallocatable lock code, the rejected LPNs get cancelled. If the lock code parameter is populated
with a unallocatable lock code, the system marks the QC rejected LPNs as received with QC status as QC Rejected. You
cannot provide allocatable lock codes to reject an IBLPN.
Distribute
The Distribute API allows you to perform distribution on the selected LPN.
Request by ID
POST /entity/iblpn/{id}/distribute/
Parameters
Name Required Type Description
Alloc_uom N String Allocation UOM: Units, Packs,
Cases, Cases then Packs.
Req_host_oblpn_nbr N String When true, requires order details to
have a host OBLPN number.
allow_residuals N Boolean Option to allow distribution with
residuals.
mhe_system_code N String Code for MHE system integration.
Example Request Body
{{{}}
"options": {
"alloc_uom": "units",
"require_host_oblpn_nbr": false,
"allow_residuals": true,
"mhe_system_code": "system_code"
}
}
Request by Filter
POST /entity/iblpn/distribute/
114

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Parameters
Name Type Required Description
container_nbr String Y IBLPN to distribute
facility_id Integer N IBLPN's facility.
company_id Integer N IBLPN's company
Note: Only a single IBLPN may be distributed per request. The \_\_in lookup is not supported for container_nbr.
Example Request Body
{{{}}
"parameters": {
"container_nbr": "IBLPN00001",
},
"options": {
"alloc_uom": "units",
"require_host_oblpn_nbr": false,
"allow_residuals": true,
"mhe_system_code": "system_code"
}
}
Get All Distributions
The Get All Distributions API allows you to fetch all the current distributions available for the LPN.
Two options are available for you to filter the results. Item Barcode and Location Barcode. If you use the Item Barcode,
the system will filter only the results for that Item. If you use location barcode, the system will sort the results with that
location at the top, but it does not exclude other locations.
IBLPN Lookup by ID
POST /entity/iblpn/{id}/get_all_distributions/
Example Request Body
{{{}}
115

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"options": {
"item_barcode": "ITM0001",
"location_barcode": "location0001"
}
}
IBLPN Lookup by Filter
POST /entity/iblpn/get_all_distributions/
Parameters
Name Type Required Description
container_nbr String Y IBLPN to distribute
facility_id Integer N IBLPN's facility
company_id Integer N IBLPN's company
Example Request Body
{{{}}
"parameters": {
"container_nbr": "IBLPN00001",
},
"options": {
"item_barcode": "ITM0001",
"location_barcode": "location0001"
}
}
Distribution Response Structure
Name Type Description
alloc_id Integer Allocation ID
alloc_qty Number Allocation quantity
alloc_uom String Allocation UOM
116

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Type Description
alloc_uom_qty Number Allocation UOM quantity
extra_included_allocs Array This is used when a single pick is made of
multiple allocations

from_invn_id Integer From inventory ID
item_allow_decimal_qty Boolean Flag representing if we should allow decimals in
item quantity
item_alternate_code String Item alternate code
item_barcode String Item barcode
item_code String Item code
item_display String Item display
item_external_style String Item external style
item_id Integer Item ID
item_inner_pack_qty Number Item inner pack quantity
item_std_case_qty Number Item standard case quantity
location_barcode String Location barcode
location_display String Location display
location_id Integer Location ID
location_type String Location type
oblpn_nbr String OBLPN number
order_nbrs Array Order numbers
picked_qty Integer Picked quantity
skipped_alloc_id_list Array Array of skipped allocation IDs
style String Item style
Get Next Distribution
On performing distribution, you may want to anticipate the next pick information for the inventory. To get this
information, you can use the Get Next Distribution API. Its input parameters are the same and the response has similar
117

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
format as an individual record from Get All Distributions. Get Next Distribution is just giving the top result that you
would get from Get All Distributions rather than a list.
URL
POST /entity/iblpn/{id}/get_next_distribution/
Parameters
Name Required Type Description
item_barcode N String If populated, only includes
allocations for this item
Location_barcode N String If populated, gets next allocation
starting from this location. If no
matching is found for this barcode,
it will be ignored.
Example Request Body
{{{}}
"options": {
"item_barcode": "ITM0001",
"location_barcode": "location0001"
}
}
IBLPN Lookup by Filter
POST /entity/iblpn/get_next_distribution/
Parameters
Name Type Required Description
container_nbr String Y IBLPN to distribute.
facility_id Integer N IBLPN's facility.
company_id Integer N IBLPN's company.
Example Request Body
{{{}}
118

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"parameters": {
"container_nbr": "IBLPN00001",
},
"options": {
"item_barcode": "ITM0001",
"location_barcode": "location0001"
}
}
IB Shipment
These topics give descriptions for APIs that complete actions related to Inbound Shipments in the Warehouse.
Receive Entire Shipment
The Receive Entire Shipment allows you to receive the entire shipment if it is in cartonized and in transit status..
POST .../entity/ib_shipment/receive_entire_shipment
Sample JSON Request
{
"parameters": {
"facility_id**code": "FAC_CODE",
"company_id**code": "COMP_CODE",
"shipment_nbr": "SHIPMENT_NBR"
}
}
GET IB Shipment
You can query the IB Shipment entity to find out the LPN Count and Shipped Quantity for a specific shipment. The
LPN Count and Shipped Quantity fields are added in the response when you pass GET method (IB Shipment API) for
Cartonized Shipments.
GET … entity/ib_shipment?shipment_nbr=XXXXXXX&fields=lpn_count,shipped_qty
Example Request
{
"result_count": 1,
"page_count": 1,
"page_nbr": 1,
"next_page": null,
"previous_page": null,
119

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"results": [
{
"lpn_count": 4,
"shipped_qty": 40.0
}
]
}
Item
These topics give descriptions for APIs that complete actions related to items in the Warehouse.
Image Upload
The image_upload API allows you to update an image either by Item ID or Item by Filter.
Assumptions
• Only one item may be updated per request.
• An error will be returned if no items are found.
• An error will be returned if more than one item is found.
Item by ID
POST .../entity/item/{id}/image_upload/
Item by Filters
POST .../entity/item/image_upload/
Supported Item Filter Attributes
The "parameters" section of the request body supports item filters when using this URL style.
• company_id (Required)
◦ This additionally allows filtering on company code: "company_id_code"
• barcode
• part_a
• part_b
• part_c
• part_d
• part_e
• part_f
• item_alternate_code
120

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Example Request Body Parameters
{
"parameters": {
"company_id_code": "COM1",
"barcode": "ABC123"
}
}
Request Image Data
Regardless of which URL is used, the image data is passed in the request body's "options" section in the "image_data"
key. Data is required to be base64 encoded.
Example Request body options:
{
"options": {
"image_data": "ABC123"
}
}
Item Image
Currently the full representation of item GET does not include the item image ('image_data') since that can be large.
However if a request specifies the `fields` query string parameter and the 'image_data' field is specified, we will return
the field and value.
This will return the id and image data for one or more items.
GET .../entity/item/?fields=id,image_data
This will return the id and image data for a specific item.
GET .../entity/item/{id}/?fields=id,image_data
The 'fields` parameter may still be combined with other filters per normal functionality:
GET .../entity/item/?fields=id,image_data&barcode=ITEM123&...
Inventory
These topics give descriptions for APIs that complete actions related to inventory in the Warehouse.
Link Serial Numbers
POST …/wms/lgfapi/v10/entity/inventory/{id}/link_serial_nbrs/
This operation is used to link one or more serial numbers to a single inventory record. The “id” value of the target
inventory record is required in the URI.
121

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Category Parameter Type Required Default Description
options serial_nbr_list Array of Strings X A list of serial number
strings to be linked to
the target inventory
record.
Bulk Update Inventory Attributes
POST …/wms/lgfapi/v10/entity/inventory/bulk_update_inventory_attributes/
This operation is used to update the inventory attributes of one or more inventory objects. Inventory in a Received or
Located IBLPN and inventory in an active location may be modified. Inventory history adjustment records will be written
for each inventory record successfully modified.
The attributes individually are not necessarily required, but in total at least one attribute must be provided to indicate
a change. Additionally, an attribute value may or may not be required as dictated by other configuration such as the
corresponding item’s attribute requirements or the location allowing mixing of attributes. Furthermore, the inventory
cannot be or have been allocated.
An empty string is a valid value to indicate removing the value from the corresponding attribute. Any attribute that is
omitted from the request data will retain its current value.
The “parameters” section of the request body is required in addition to the “options” section outlined below. The “id”
parameter filter (for a single value) or the “id\_\_in” parameter (for an array of values) are valid and can be used.
Category Parameter Type Required Default Description
options invn_attr_a String C T arget attribute value.
options invn_attr_b String C T arget attribute value.
options invn_attr_c String C T arget attribute value.
options invn_attr_d String C T arget attribute value.
options invn_attr_e String C T arget attribute value.
options invn_attr_f String C T arget attribute value.
options invn_attr_g String C T arget attribute value.
options invn_attr_h String C T arget attribute value.
options invn_attr_i String C T arget attribute value.
options invn_attr_j String C T arget attribute value.
122

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Category Parameter Type Required Default Description
options invn_attr_k String C T arget attribute value.
options invn_attr_l String C T arget attribute value.
options invn_attr_m String C T arget attribute value.
options invn_attr_n String C T arget attribute value.
options invn_attr_o String C T arget attribute value.
options commit_frequency Integer 1 0 = Roll back on first
error.

1 = Commit per object.

Delink Serial Numbers
The Delink Serial Numbers API allows users to delink a list of serial numbers from an existing inventory in order for the
system to write appropriate serial number records.
Note: Every serial number that is delinked from the targeted inventory should have corresponding serial Number
History records. The Serial Number History UI should display the serial number with delinked action codes for IBLPN,
OBLPN, and Active inventories.
You can delink a serial number using the following POST request:
POST .../{version}/entity/inventory/{id}/delink_serial_nbrs/
Additional details for this API include:
• The delinking is successful for IBLPN and OBLPNs when the 'SERIAL_NUMBER_TRACKING_LEVEL' company
parameter is set to 2.
• The delinking is successful for only OBLPNs when the 'SERIAL_NUMBER_TRACKING_LEVEL' company
parameter is set to 1.
• The delink process is successful if the targeted inventory is non-decimal tracked.
• The system returns an error message if the targeted inventory is not linked with any serial number.
• The delink process is unsuccessful if the inventory associated with any LPN is either in Consumed, Shipped,
Delivered, Cancelled, or Lost status.
• The corresponding serial number history for delinking is recorded in the SerialNbrHistoryView UI screen for
serial numbers that are delinked from IBLPNs/OBLPNs/Active inventories.
Sample Data format JSON
{
"options" : {
"serial_nbr_list": [
"SN1",
"SN2",
"SN3"
]
}
123

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
}
XML
<request>
<options>
<serial_nbr_list>
<list-item>SN1</list-item>
<list-item>SN2</list-item>
<list-item>SN3</list-item>
</serial_nbr_list>
</options>
</request>
GET Inventory History
The Inventory History API allows you to query inventory histories for default Companies and Facilities configured for
the user. Previously, inventory history was not supported or exposed as an entity in lgfapi. Now, users can fetch the
inventory history as an entity since it has been exposed to the lgfapi.
You can get inventory history details with paginated results using the following GET request:
GET....../entity/inventory_history
To fetch non-paginated result by specific 'ID':
GET....../entity/inventory_history/{id}
To fetch paginated result by query string parameters:
GET....../entity/inventory_history?key1=value1&key2=value2
To check for object existence or modification:
HEAD .../entity/inventory_history?key1=value1&key2=value2
HEAD .../entity/inventory_history/{id}
Query String Parameters
Since inventory history is a large table, to avoid performance issues, certain combinations of query string fields are
required when querying using query parameters. One of the following combinations must be used (in addition to any
other field):
• company_id**code, facility_id**code, group_nbr
• company_id**code, facility_id**code, history_activity_id, status_id
• company_id**code, facility_id**code, history_activity_id, item_code
• company_id**code, facility_id**code, history_activity_id, item_alternate_code
• company_id**code, facility_id**code, history_activity_id, container_nbr
124

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Support for ISO-8601 Format Date/Time Values
Note: The company parameter ENABLE_ISO_8601_OUTPUT_DATE_TIME_FORMAT gives you the ability to control
the output format of date/time values in Inventory History and Shipped Load output. This will allow for all date/time
output to be in the widely accepted and used ISO-8601 standard. This standard will not only give date, time, and date/
time consistency across the output data, but it will provide the time zone offset from UTC as part of the date/time
format.
The addition of the time zone context into the date/time value will allow external systems to know the actual time zone
value and will remove any ambiguity. The ISO-8601 standard is a widely used and accepted format for exchanging date/
time information between systems.
Date/Time Format Example
Type Format Example
Date yyyy-mm-dd 2020-08-01
Time HH:MM:SS 15:01:30
Datetime yyyy-mm-ddTHH:MM:SSz 2020-08-0IT15:01:30-04:00
Format Definition
YYYY 4 digit year
MM 2 digit month
DD 2 digit day
T The literal letter "T" used as a delimeter between the date and time components.
HH 2 digit hour (24-hour clock)
MM 2 digit minute
SS 2 digit seconds
z Time zone offset from UTC in the format (+/-)HH:MM
GET Next Number
The GET Next Number API allows you to get a next up number from a given sequence counter.
This API is broken down into two lgfapi operations:

1. A detail operation where the sequence counter's id is already know and is provided in the URL.
   125

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations 2. A list operations where a series of filters are provided in the "parameters" section of the request body to find
the sequence
URL Signature
Detail lookup when id is already known:
POST /entity/seq_counter/{id}/get_next_number
List search by filters:
POST /entity/seq_counter/get_next_number
Request Body
• Both URLs support the "count" option.
Section Name Required Type Default Comments
options count integer 1 Count of next up
numbers to be
returned. Max value of 1000.
{
"options": {
"count": 2
}
}
Available Filters
When filtering is required, a combination of the following may be used to determine the sequence counter.
• facility_id
◦ Allows for filtering on fields like "code"
• company_id
◦ Allows for filtering on fields like "code"
• counter_code
• sub_code
• destination_company_id
◦ Allows for filtering on fields like "code"
• destination_facility_id
◦ Allows for filtering on fields like "code"
{
"parameters": {
"facility_id": 1,
"company_id\_\_code": "ABC",
"counter_code": "OBLPN"
}
126

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
}
Manufacturing Transaction
This API allows Manufacturing, Inventory Management or any other application to record Material Issues or Product
Completions and transaction reversals. This provides a common API which supports both material issues and product
completions.
Whatever inventory gets updated as part of work order transactions will be updated using this API.
URL
POST.../wms/lgfapi/v10/entity/inventory/manufacturing_transaction
The following data is passed in JSON format:
Column Mandatory Comments
manufacturing_transaction_list
mfg_transactionid yes Unique Identifier for the transaction shared by
fusion inventory.
location_barcode yes Location pass can correspond to active or
reserve location or drop location type.
lpn_nbr Will be required for product completions and
product returns.
transaction_type The following are the transaction types shared
from Inventory Management:

• Work in Process Material Issue
• Work in Process Negative Material Issue
• Work in Process Material Return
• Work in Process Negative Material Return
• Work in Process Product Completion
• Work in Process Product Return
mfg_work_order_nbr yes Work order number against which transaction is
recorded.
mfg_operation_seq_nbr Work order operation sequence against which
transaction is recorded.
external_transaction_date_time Holds the transaction date and time when it
was performed at the source system.
resend_flg By default the value will be No. If set to yes,
Inventory Managaement has an ability to
resend the transaction in case of any failures.
inventory_list
127

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Column Mandatory Comments
item_alternate_code Application expects either item alternate code
or combination of item_parts.
item_part_a
item_part_b
item_part_c
item_part_d
item_part_e
item_part_f
qty yes Corresponds to the quantity. Can be either + or

- depending upon the transaction type.
  uom_code uom_code in which the transaction quantity is
  recorded in. For Prebuilt integration
  batch_nbr Lot number for lot tracking item.
  expiry date Expiry date in case sku is only expiry tracked.
  invn_attr_a
  invn_attr_b
  invn_attr_c
  invn_attr_d
  invn_attr_e
  invn_attr_f
  invn_attr_g
  invn_attr_h
  invn_attr_i
  invn_attr_j
  invn_attr_k
  invn_attr_l
  invn_attr_m
  invn_attr_n
  invn_attr_o
  serial_number_list Corresponding serial numbers associated with
  the transaction.
  API callers should take care of sending quantity values in the appropriate positive or negative connotation by
  transaction type:
  128

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Transaction Type Comments for Quantity
Work in Process MaterialIssue Negative
Work in Process Negative Material Issue

Positive

Work in Process MaterialReturn Positive

Work in Process Negative Material Return

Negative
Work in Process ProductCompletion Positive

Work in Process ProductReturn Negative

Miscellaneous Receipt

Positive

Miscellaneous Issue Negative
Assumptions
• The OIC integration layer or the API caller will have to send + or - value for the quantity depending upon the
transaction performed
• It is assumed that Location information is set up in WMS as well, initial set up has to be done accordingly.
• Transaction is assumed to be primary UOM if uom code is not shared.
• API does not take in the actual date/time when the transaction was captured in manufacturing UI's and the
user will be the same API user.
• This API includes LPN for reserve inventory updates and Location for active inventory updates. So, the LPN and
active inventory location is not relevant in a single payload and errors out.
Example Payload
{
"async_flg":true,
"header":{
"entity":"stage_mfg_operation",
"company_code":"COMP",
"facility_code":"FAC",
"messageid":"KVORD",
"document_version":"24C",
"origin_system":"QA",
"client_env_code":"QA"
},
"manufacturing_transaction_list": [
{
"mfg_transactionid":1,
"lpn_nbr": "WOEMTEKEO300181",
"location_barcode":"KVR010103",
"mfg_work_order_nbr":"WOEMTEKEO300181",
129

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"mfg*operation_seq_nbr": 1,
"transaction_type": "Work in Process Material Issue",
"create_hdr_flg":true,
"resend_flg": false,
"ready_for_processing_flg": true,
"external_transaction_date_time":"2024-09-17T10:02:45.026Z",
"reason_code":"",
"inventory_list" : [
{
"item_alternate_code": "MS4-LCFACEPLT-SB",
"qty": -10,
}
]
}
]
}
Note: This API is designed for asynchronous calls (synchronous call is not supported) so the expected response on
success will be:
{
"success": true,
"response": {
"message": "Data successfully staged"
}
}
You can find the details of data processed or errored from the From Manufacturing Transaction Header View UI.Validations
The following table describes the validations at the header, detail, and serial number level:
Validation Description
Header Level Validations (mfg_work*
order_transaction_list)

• If there is a another instance of the transaction in "Not Ready", "Ready" or "In-Processing" or
"Processed", the record is updated to Failed status with error string as "Duplicate transaction
exists, cannot process the transaction".
• If the location passed is not valid for the passed in facility, the record is updated to Failed status
with error string as "Transaction (%tran_id%) has invalid location for the facility".
• If the location passed does not correspond to the location of type "Active"/"Reserve"/"Drop",
the record is updated to Failed status with error string as "Invalid Location type recorded for the
Transaction (%tran_id%)".
• If the LPN number passed is not in status "Allocated"/Partially Allocated/Reserved/"In-
Receiving/Lost/Quality Check", the record is updated to Failed status with error string as
"LPN(%lpn_number%) not in a valid status for transaction(%tran_id%)".
Detail Level Validations (inventory_list)

• If valid item is not returned for the company, the detail record is updated to Failed status with
error string as "Invalid Item".
• If the UoM_Code passed is not the same class as the item's primary UOM, the corresponding
detail record is updated to Failed status with error string as "UoM_Code passed for the
item(%item_alternate_code%) is of different UOM class"".
• If the Item passed, passes the dimension checks for the LPN, and the underlying LPN has LPN
type associated with it, The Unit Length/Width/Height of the item should be lesser than LPN
type's Length/Width/Height.
130

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Validation Description
• If the item/lot/attribute combination is not present on the active location passed, the
corresponding detail record is updated to Failed status with error string as "Inventory not found in
the location for the Item/Batch/Inventory attribute combination".
• If item/lot/attribute combination is not present on the LPN passed, the corresponding detail
record is updated to Failed status with error string as "Inventory not found in the LPN for the Item/
Batch/Inventory attribute combination".
• If the anticipated Item/Batch/Inventory attribute combination found for the sku in the location or
LPN, but the qty passed exceeds the inventory qty then the corresponding detail record is updated
to Failed status with error string as "Insufficient inventory for _Item/Batch/Inventory attribute
combination{_}".
• If the active location/reserve location passed has a Permanent Sku assignment and the qty
passed is a postive value where the item passed is not the same as the permanent dedicated
item, the corresponding detail record is updated to Failed status with error string as "Item passed
violates permanent sku assignment for the location".
• If the active/reserve location passed has allow*multi_sku flag set to Yes and the qty passed is
a positive value where the item/lot combination passed violates allow_multi_sku check, the
corresponding detail record is updated to Failed status with error string as "Item passed violates
allow multi sku check condition for the location".
• If the active/reserve location passed has the restrict_batch flag set to Yes and the qty passed
is a positive value where the item/lot combination passed violates restrict batch, then the
corresponding detail record is updated to Failed status with error string as "Item/batch number
passed violates restrict batch condition for the location".
• If the active/reserve location passed has restrict_inventory attribute flag set to Yes and the qty
passed is a positive value where the item/inventory_attribute combination passed violates restrict
inventory attribute, then the corresponding detail record is updated to Failed status with error
string as "Item/Inventory attribute combination passed violates restrict attribute check for the
location".
• if expiry date is passed for item that is tracking batch number and expiry, if e the expiration date
passed is not the same as what is associated with batch master record, the system returns an
error.
• If inventory attribute is passed, the system honors the column formatting rules associated with
each of the inventory attribute passed. This check happens irrespective of whether the item is
tracking inventory attributes or not
• If Company Parameter>>SERIAL_NUMBER_TRACKING_LEVEL is configured to 2 - Track serial
numbers for both Inbound and Outbound, then only serials are accepted, otherwise the system
returns an error "Serial Number not Supported for the company"
• If item passed is not serial tracked, and if serial number list is passed, the system returns an error
"Item does not track serial, serial number records are passed".
• If qty passed contains decimals and item is serial number tracked then the corresponding detail
record is updated to Failed status with error "Decimal Qty not supported for serial tracked sku's".
Serial Number Validations (serial_nbr*
list)

The following validations are applicable for the serial number passed pertaining to each inventory list:

• If ready_for_processing_flg is set to "yes" and there is a mismatch in serials passed. the
corresponding inventory detail record returns error "Number of serials not equal to the qty
passed".
• If passed in serial number does not match the barcode validations, the corresponding serial
number record returns error "Serial numbers provided do not match the barcode length
configured".
131

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Validation Description
• If passed in serial number is duplicated (another record for same serial number found in the
serial number list for the inventory), then the corresponding serial number record returns error
"Duplicate serial number passed in the serial number list"
If the quantity passed is positive, then the following are the validations for the serials:
◦ If the passed in serial number is valid but not present in the location passed from where inventory
is picked, the corresponding serial number record is failed and corresponding header and
inventory record fails with error "Serial Number not present in the LPN".
◦ If the passed in serial number is not present in the LPN number passed. then the corresponding
serial number record and the corresponding header and inventory record fails with error "Invalid
Serial Number passed for the LPN".
◦ If the passed in serial number is valid but not present in the current LPN passed for Product
Completion Returns or Undo Product Completion, the corresponding serial number record and
the corresponding header and inventory record fails with error “Invalid Serial Number passed for
the LPN”.
If the quantity passed is positive and the transaction does not involve LPN's then:
◦ If the passed in serial number is already present in another active location, the corresponding
serial number record and corresponding header and inventory record fails with error “Serial
Number is present in another active location (%target active location%)”.
◦ If the serial number passed is linked to an inventory in a different facility and the underlying
status of the LPN is < Shipped then an error is returned. If the underlying LPN associated to a
different facility for the passed in serial number is in status Consumed/Cancelled/Shipped/
Delivered then the system proceeds.
◦ If the serial number passed in is associated with an LPN in Lost Status for the current facility,
system returns an error.
• If the serial number passed is already present in the same active location passed, the system
returns an error.
• If the passed in serial number is already present in another LPN which is not in Consumed/
Cancelled Status, then the corresponding serial number record and corresponding header and
inventory record fails with error "Serial Number is present in another LPN(%target LPN%)".
From Manufacturing Transaction
The following APIs allow you to fetch paginated results for From Manufacturing Transaction Header, Detail, and Detail
Serial Number.
From Manufacturing Transaction Header URLs
Fetch paginated results when users use the following URL:
GET.../lgfapi/v10/entity/from_manufacturing_transaction_hdr/
Fetch non-paginated result by specific 'ID':
GET.../lgfapi/v10/entity/from_manufacturing_transaction_hdr/{id}
From Manufacturing Transaction Detail URLs
Fetch paginated results when users use the following URL:
132

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
GET.../lgfapi/v10/entity/from*manufacturing_transaction_dtl/
Fetch non-paginated result by specific 'ID':
GET.../lgfapi/v10/entity/from_manufacturing_transaction_dtl/{id}
From Manufacturing Transaction Detail Serial Number URLs
Fetch paginated results when users use the following URL:
GET.../lgfapi/v10/entity/from_manufacturing_transaction_dtl_serial_nbr/
Fetch non-paginated result by specific 'ID':
GET.../lgfapi/v10/entity/from_manufacturing_transaction_dtl_serial_nbr/{id}
Movement Request
The Movement Request API allows ERP and manufacturing applications the option to order specific serial numbers
against a particular movement request line. This API allows you to load the stage tables for the movement request
entity in JSON format with the required serial numbers.
API URL
POST .../wms/lgfapi/v10/stage/movement_request/
Parameters
Section Name Type Required Description
parameters json_data string yes Data to be shared will
be passed in the request
header as content type
parameters async boolean (yes/no) By default the value will be
considered as true or yes.
parameters only_load_flg boolean (yes/no) By default the value will be
considered false.
parameters load_all_errors boolean (yes/no) By default the value will be
no. If the value is passed as
yes, then do not stop the
movement request just on
first error.
parameters prevent_stage_hdr_record*
creation_flg
boolean (y/n) • Default value is "no"
to retain backward
compatibility.
• When the value is no,
WMS will create a
new header record for
133

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Section Name Type Required Description
the entity key in the
corresponding stage
tables.
• If the value is passed
as "yes" then the
new header record
will not be created in
stage tables and the
detail records will get
appended to the stage
header record with
the same file group
number.
parameters file*group_num_without*
timestamp*flg
boolean (y/n) • Default value is "no"
to retain backward
compatibility.
• If the value is set
to "no", then the
filegroup number is
generated (message*
id appended
with timestamp
(YYYYMMDDHHMMSS
format) as the file
group number.
• If the value is set to
"yes", then file group
number is the same
as the message id
passed in the XML
payload.
Select the relevant JSON format file from the Input Interface screen to upload and run the interface for movement
request. The API will pull data for the following fields:
• facility_code
• company_code
• movement_request_nbr
• Sequence_number
• item_code
• required_serial_number
• stage record status
• error_str
• create_ts
• create_user
• mod_ts
• mod_user
134

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Load
These topics give descriptions for APIs that complete actions related to Loads in the Warehouse.
Check_In
The check_in API allows the caller to check-in an inbound or outbound load to a dock door.
Regardless of the method used to identify the load, the following input is valid:
Category Name Type Required Description
options dock_nbr String Y Dock door for check-in.
Load Lookup by ID
POST .../entity/load/{id}/check_in/

The caller knows the unique `id` value of the trailer, which is added to the request URL. No additional `parameters` data is
required from the request body.
Example Request Body:
{
"options": {
"dock_nbr": "DOCK-1"
}
}
Load Lookup by Filters
POST .../entity/load/check_in/

Category Name Type Required Description
parameters load_nbr String Y Load for check-in.
parameters facility_id Integer N Load’s facility.
parameters company_id Integer N Load’s company.
• Only a single load may be moved per request.
◦ The `__in` lookup is not supported for `load_nbr`.
• `facility_id` and `company_id` both additionally support string lookup by `code` using the double-underscore
notation:
135

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
◦ facility_id**code
◦ company_id_code
Example Request Body:
{
"parameters": {
"facility_id**code": "FAC-1",
"company_id_code": "COM-1",
"load_nbr": "LOAD-1"
},
"options": {
"dock_nbr": "DOCK-1"
}
}
Check_Out
The check_out API allows the caller to check-out an inbound or outbound load from a dock door.
Load Lookup by ID
POST .../entity/load/{id}/check_out/

The caller knows the unique `id` value of the trailer, which is added to the request URL. No additional `parameters` data is
required from the request body.
Load Lookup by Filters
POST .../entity/load/check_out/

Category Name Type Required Description
parameters load_nbr String Y Load for check-in.
parameters facility_id Integer N Load’s facility.
parameters company_id Integer N Load’s company.
• Only a single load may be moved per request.
◦ The `__in` lookup is not supported for `load_nbr`.
• `facility_id` and `company_id` both additionally support string lookup by `code` using the double-underscore
notation:
◦ facility_id\_\_code
◦ company_id_code
136

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Example Request Body:
{
"parameters": {
"facility_id**code": "FAC-1",
"company_id_code": "COM-1",
"load_nbr": "LOAD-1"
}
}
Ship Load
The Ship Load API allows you to ship a load by uploading the load via ID or filter.
Category Name Required Type Description
parameters load_nbr X string Load for shipping
parameters facility_id Integer Facility context by id
parameters facility_id**code string Facility context by code
parameters company_id Integer Company context by id
parameters company_id_code string Company context by code
Load Lookup by ID
POST .../entity/load/{id}/ship/
• No additional `parameters` data in the request body is required.
Load Lookup by Filters
POST .../entity/load/ship/
Example Request Body:
{
"parameters": {
"facility_id\_\_code": "FAC-1",
"company_id_code": "COM-1",
"load_nbr": "LOAD-1"
}
}
This API includes the following features:
• Supports the ship load transaction for a load that is in the Loaded/ Loading Started /Checked Out status.
• An error is displayed if the load is in a "Cancelled", "Ship Load In Progress", or "Shipped" status.
• The shipload transaction can be performed either by providing the id or code for the company/facility along
with the load number.
137

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
• A Ship Load confirmation file is generated after the load is shipped.
Once a load is shipped via the Ship Load API, the following applies to Inventory
History Transaction (IHT) records:
• Inventory history IHT -3 '3 - Container Shipped' is written with respect to each container present on the load.
• For shipped loads with OBLPNs associated with asset inventory history, IHT- 58 '58 - Asset Shipped' is written
with respect to each OBLPN associated with an asset.
• Inventory history IHT- 60 '60 - Load Shipped File' is written for the outbound Load shipped.
The Ship Load API supports the following validations:
Ship Load API supports Order type with ''Single Order on multiple Loads':
• If "Single Order on multiple Loads" is set to "Do not Allow" in the order type, the system displays the error
message: "Load has Order/s marked to Prevent one order on different loads with Error."
• When an order is in Packed status but only some of the packed OBLPNs are loaded.
• When an order is in Packed status but some OBLPNs are loaded to different loads.
• For OBLPNs with pending audit if the Company parameter "ALLOW_LOAD_SHIP_WITH_AUDIT_PENDING" is set
to no.
Company Parameter REQD_FIELDS_FOR_SHIPPING is defined:
• When the required fields configured for the parameter 'REQD_FIELDS_FOR_SHIPPING ' are not defined for the
targeted load.
• When one of the container item on the load is serial number tracked and the number of serial numbers
allocated do not match with the count of serial numbers present in the container.
Serial Number Validations
• If company parameter ALLOW_LOAD_SHIP_WITH_AUDIT_PENDING = False and company parameter
SERIAL_NUMBER_TRACKING_LEVEL is 1 or 2
• If company parameter SERIAL_NUMBER_TRACKING_LEVEL is 0 or Non serial tracked items exist and company
parameter ALLOW_LOAD_SHIP_WITH_AUDIT_PENDING = False
• This API will not show you any warning message like the UI or RF, and it will proceed with the Ship Load
transaction.
• The Ship Load API does not generate multiple outbound files.
Location
These topics give descriptions for APIs that complete actions related to location in the Warehouse.
Update Active Inventory
The update_active_inventory API allows you to adjust the inventory quantity in an active location for a specific item.
Only a single location and item may be updated per request.
138

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Note: This is a new API meant to replace the existing legacy `update_active_inventory` API. The legacy API will
eventually be retired so no further enhancements will be made to it. New functionality will instead be added to this
API as part of the lgfapi suite.
Regardless of the method used to identify the location, the following input is valid:
Category Name Type Required Description
options item_barcode String C Item identifier.
options item_code String C Item identifier.
options item_alternate_code String C Item identifier.
options adjustment_qty Numeric C Non-zero adjustment
quantity.
options actual_qty Numeric C Non-negative final quantity.
options batch_nbr String N Batch tied to target
inventory.
options expiry_date Date N Expiration date tied to
target inventory.
options invn_attr_X String N Attributes A-O tied to the
inventory.
options reason_code String Y Recorded on inventory
history.
options transaction_ref_nbr String N Recorded on inventory
history.
options locn_capacity_check_flg Boolean N Validate locations max units
and volume?
options company_id Integer N Item’s company.
options company_code String N Item’s company’s code.
• Only one of `item_barcode`, `item_code`, or `item_alternate_code` is allowed.
• Only one of `actual_qty` or `adjustment_qty` is allowed.
• If positive change in quantity:
◦ The provided `batch_nbr` will be created if it does not exist.
• Only one of `company_id` or `company_code` is allowed.
◦ Although not required by the API, the company context may be necessary if there is ambiguity when
identifying the item to adjust. This is common in 3PL scenarios where the same identifying information
may be present for different items across companies for which the user is eligible.
Location Lookup by ID
POST .../entity/location/{id}/update_active_inventory/
139

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
The caller knows the unique `id` value of the active location, which is added to the request URL. No additional
`parameters` data is required from the request body.
Location Lookup by Filters
POST .../entity/location/update_active_inventory/

Category Name Type Required Description
parameters barcode String Y Location’s barcode.
parameters facility_id Integer N Location’s facility.
• Only a single location may be updated per request.
◦ The `__in` lookup is not supported for `barcode`.
• `facility_id` supports string lookup by `code` using the double-underscore notation:
◦ facility_id**code
Example Request Body:
{
"parameters": {
"facility_id**code": "FAC-1",
"barcode": "LOCN1"
},
"options": {
"item_barcode": "ITEM1234",
"adjustment_qty": -10,
"batch_nbr": "BATCH1234",
"expiry_date": "2020-01-02",
"invn_attr_a": "A",
"invn_attr_b": "B",
"reason_code": "RC",
"transaction_ref_nbr": "TX123457890",
"company_code": "COM-1"
}
}
Serial Number Tracked Items
This API also accepts serial numbers to cater to serial number tracked items or SKUs.
For positive adjustments, the serial numbers sent can be:
• New serial numbers (or)
• Serial numbers existing in the warehouse that are delinked and not associated with any other inventory
For negative adjustments, the serial numbers sent should be the ones that are already present in the location where
inventory is being updated.
The following is an example request for serial number adjustments:
{
140

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"parameters": {
"facility_id code": "FAC-1", "barcode": "LOCN1"
},
"options": {
"item_barcode": "ITEM1234", "adjustment_qty": -3, "batch_nbr": "BATCH1234",
"invn_attr_a": "A",
"invn_attr_b": "B",
"reason_code": "RC", "transaction_ref_nbr": "TX123457890", "serial_nbr_list":
[
"SrlNbr1", "SrlNbr2", "SrlNbr3"
]
}
}
Track User Activity
If you have purchased WFM (Oracle Workforce Management), you can also send user activity data using the following
parameters in the Update Active Inventory API
• Screen_name: Name of the application or screen in the external system that was used by the user to update
inventory.
• Begin_ts: Time at which the user started update inventory.
• End_ts: Time at which the user completed update inventory.
If all the three parameters are sent in the API, and if WFM is enabled, user activity is written to the WMS Activity view
and subsequently interfaced to WFM, enabling you to analyze user productivity through productivity reports in WFM.
141

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Note:
• All three parameters must be sent for WMS Activity to be written.
• If WFM is not enabled, WMS Activity is not written even if the three parameters are sent.
• In order for WMS Activity data to interface successfully to WFM, screen_name that is sent in the API has to be
configured as a screen in WMS using an RF module and mapped to a work area activity in WFM.
• Screen_name sent on the API is also written on the corresponding IHTs that are written with this API.
• If only screen_name is sent without begin_ts and end_ts, the screen_name is written on the IHT, even if WFM is
not enabled.
• Begin_ts and End_ts cannot be greater than the current timestamp of the facility in the API.
Request Body with User Activity Data
{
"parameters": {
"facility_id": 950,
"barcode": "RNA070204"
},
"options”: {
"adjustment_qty": 6,
"reason_code": "DR",
"item_barcode": "GDEAN13000003",
"transaction_ref_nbr": "TX11384-Issue1",
"company_code": "QATSTPC"
"begin_ts": "2024-05-27T18:30:00",
"end_ts": "2024-05-27T18:45:00",
"screen_name": "Update Active Inventory Screen"
}
}
Locate LPN or Pallet
The Locate LPN/Pallet API allows you to locate an LPN/ Pallet to its respective destination location.
You can locate an Inbound or Outbound LPN to its respective destination using the following POST requests:
Inbound LPN
POST .../entity/iblpn/{id}/locate/

                           POST .../entity/iblpn/bulk_locate/

Outbound LPN
142

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
POST .../entity/oblpn/{id}/locate/

                           POST .../entity/oblpn/bulk_locate/

Note: If you invoke the Locate LPN API by passing an LPN number that is part of the Pallet, the system locates the
whole pallet and does not locate the individual LPN (i.e. the remaining LPN’s that are part of the Pallet will also get
located.)
Example requests for Locate IBLPN and OBLPN:
POST .../entity/iblpn/bulk_locate/
{
"parameters": {
"id**in": [1, 2, 3]
},
"options": {
"location_barcode": "R1-R2-RB1-Rl1",
"depalletize_on_putaway_flg": false
}
}
POST .../entity/oblpn/bulk_locate/
{
"parameters": {
"container_nbr**in": ["LPNPTW0102"]
},
"options": {
"location_barcode": "R1-R2-RB1-Rl1",
"depalletize_on_putaway_flg": false
}
}
You can locate a Pallet to its respective destination using the following POST requests:
Pallet
POST .../entity/pallet/{id}/locate/

                              POST .../entity/pallet/bulk_locate/

Example Request for Locate Pallet:
POST .../entity/pallet/bulk_locate/
{
"parameters": {
"id\_\_in": [1, 2, 3]
},
"options": {
"location_barcode": "R1-R2-RB1-Rl1",
"depalletize_on_putaway_flg": false
}
}
143

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
The following validations should be performed while locating the LPN/ Pallet and the system should return an error
message.
Validations For LPN For Pallet Error Response
Inbound LPN is not present in the
System
Yes "LPN not found" .
IBLPN in "In Receiving",
"Consumed" & "Cancelled" Status
Yes "LPN is not in valid status"
IBLPN in Allocated Status &
Company Parameter "ALLOW\_
MOVING_OF_ALLOCATED_LPNS"
is set to No
Yes "Locating Allocated LPN is
restricted"
Inbound Pallet or Outbound Pallet
is not present in the System
Yes "Pallet not found".
Inbound/ Outbound Pallet with
status other than In facility
Yes "Pallet is not in valid status"
OBLPN in Status Other than In
Packing/ In Picking/ Packed/
Picked
Yes "OBLPN is not in valid status"
On Locating IBLPN/OBLPN which
is having lock code with "Prevent
Putaway " flag enabled.

Yes "Cannot locate LPN, having lock
code %Lock Code% which prevents
putaway"
Location Validation Error Response
Location passed in the API if location is not
present in the facility
"Location not in current facility"
When location doesn't have enough
capacity based on (Units/weight/Volume)
"Location doesn't have enough capacity for %Parameter due to which capacity check failed%"
When location is permanent not matching
with the SKU present in the LPN
"Cannot locate, Location is dedicated for SKU %SKU dedicated for location%"
When location with Multi SKU flag
disabled & Incoming LPN is Multi SKU LPN
"Cannot locate, Location is not allowed for multi SKU"
When location is marked with Restrict
Batch, If the incoming SKU with Batch
Number is not matching with the SKU
+Batch number combination present in
the location.
"Cannot locate, Location prevents different inventory Batch combination for a SKU. "
When location is marked with Restrict
Inventory Attribute, If the incoming
SKU with Inventory Attribute value is
not matching with the SKU +Inventory
Attribute value combination present in the
location.
"Cannot locate, Location prevents different inventory attribute combination for a SKU. "
144

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Location Validation Error Response
When location is marked with "Prevent
Putaway Flag"
"Cannot locate, Location is Locked"
When location passed is other than QC
location for IBLPN with "Quality Check"
Status
"Cannot locate to other than QC location"
When location passed is other than Drop
or staging location for an OBLPN or
Outbound pallet
"Cannot locate to %location type of given location%"
When drop location passed is configured
for IB sorting with criteria value defined,
if the Incoming LPN/Pallet breaks the
criteria value
"Cannot locate, Drop location criteria value is not matching"
When drop location passed is configured
for OB sorting with criteria value defined,
if the Incoming LPN/Pallet breaks the
criteria value
"Cannot locate, Drop location criteria value is not matching"
Parameters
Name Required Type Default Description
facility_id Integer Facility context by id.
facility_id**code String Facility context by code.
company_id Integer Company context by id.
company_id_code String Company context by code.
container_nbr String The allowed parameter
filter conditions are
"container_nbr" and
"container_nbr**in"
id Integer The allowed parameter
filter conditions are "id" and
"id\_\_in":
Request Options Parameters
Name Required Type Default Description
location_barcode X String
depalletize_on_putaway_flg Boolean False
145

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Location Size Type
POST .../entity/location_size_type
This operation is used to add single or multiple location size types.
If you have a new facility and you want to copy the same location size type from your current facility, you can first GET
the list by querying the location_size_type entity, then POST the applicable data to this operation for the target facility.
Example body request
{
"fields": {
"company_id": 1,
"size_type": "TEST_SIZE_001",
"description": "Test Size 001"
}
}
OBLPN
The “oblpn” entity is derived from the “container” entity and therefore also has access to all of its entity operations, in
addition to the following.
Mark Delivered
POST …/wms/lgfapi/v10/entity/oblpn/{id}/mark_delivered/
Updates a Shipped OBLPN to Delivered status and writes container delivered inventory history.
Create from IBLPN
The OBLPN create_from_iblpn API allows you to create an OBLPN in Outbound Ready status and allocate inventory
from a designated IBLPN in a single request. Additionally allows the caller to trigger packing of the OBLPN.
POST .../entity/oblpn/create_from_iblpn/

146

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Assumptions

1. All allocation data must have the same facility and company context as the OBLPN.
   ◦ Allocations may be for multiple sales orders from multiple IBLPNs for different items as long as the
   facility/company context is consistent with the created OBLPN.
2. Sales order status will be recalculated on success.
3. IBLPN status will be recalculated on success.
4. Inventory history is only written if the OBLPN is packed.
   Request Body Data
   The request body data utilizes the 3 categories in the following ways:
5. `fields` – The initial data required to create the OBLPN.
6. `parameters` – List of data defining allocations.
7. `options` – Additional functional data.
   OBLPN Fields Data
   The OBLPN’s initial data is defined in the `fields` section of the request under the `oblpn` key. This is similar to the
   request body data requirements when creating an LPN directly through the entity’s create mechanism.
   Supported fields:
   Name Type Required Description
   facility_id Integer Y OBLPN’s facility.
   company_id Integer Y OBLPN’s company.
   container_nbr String Y OBLPN’s container number.
   curr_location_id Integer N OBLPN’s location.
   lpn_type_id Integer N Associated LPN Type.
   length Numeric N OBLPN’s length dimension.
   width Numeric N OBLPN’s width dimension.
   height Numeric N OBLPN’s height dimension.
   • If providing `lpn_type_id` - `length`, `width`, and `height` are not valid.
   Example Request Body:
   "fields": {
   "oblpn": {
   "facility_id": 1,
   "company_id": 1,
   "container_nbr": "OBLPN-1",
   "lpn_type_id": 5
   }
   }
   147

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Allocation Parameters Data
Allocation data is defined in the `parameters` section of the request in the `allocations` key. The data is a list of objects,
each linking one sales order detail to one IBLPN for the given inventory and quantity. An order detail or IBLPN may be
referenced across multiple allocation definitions within the same request. Each of the following allocation scenarios is
supported:
• Single order detail from single IBLPN.
• Single order detail from multiple IBLPNs.
• Multiple order details from single IBLPN.
• Multiple order details from multiple IBLPNs.
Category Name Type Required Description
allocations order_nbr String Y Sales order identifier.
allocations iblpn_nbr String Y IBLPN identifier.
allocations qty Numeric Y Non-zero quantity to
allocate.
allocations order_dtl Object Y Nested object identifying
the sales order detail.
• Sales order status must be less than “Packed”.
• IBLPN status must be “Received”, “Located”, or “Partially Allocated” and have the necessary available
unallocated quantity.
The nested `order_dtl` object requires one of two definitions in order to identify the sales order detail.
Identify Sales Order Detail by Sequence Number
If the order detail’s unique sequence number is known to the user, this may be provided in the request and is the only
piece of data necessary to identify the correct detail for the given sales order number.
Category Name Type Required Description
order_dtl seq_nbr Integer C Sales order detail’s unique
sequence number.
Example Request Body:
"parameters": {
"allocations": [
{
"order_nbr": "ORDER-1",
"order_dtl": {
"seq_nbr": 1
},
"iblpn_nbr": "IBLPN-1",
"qty": 1
}
]
148

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
}
Identify Sales Order Detail by Attributes
The sales order detail may also be identified by its attributes. At least one of the following pieces of information is
required. If more than one order detail is identified, an error will be returned. Additionally, this is a restrictive search in
that any omitted data will not be treated as a wildcard.
• If no `batch_nbr` is provided, only match order detail(s) without a batch.
• If no `invn_attr_X` value is provided for A-O, it will be treated as blank.
Category Name Type Required Description
order_dtl item_barcode String C Item identifier.
order_dtl item_alternate_code String C Item identifier.
order_dtl batch_nbr String N Batch identifier.
order_dtl invn_attr_X String N Attributes A-O tied to the
order detail.
Example Request Body:
"parameters": {
"allocations": [
{
"order_nbr": "ORDER-2",
"order_dtl": {
"item_barcode": "ITEM2",
"batch_nbr": "BATCH-1",
"invn_attr_a": "A",
"invn_attr_b": "B"
},
"iblpn_nbr": "IBLPN-2",
"qty": 2
}
]
}
Additional Options Data
Functional request data in the `options` section:
Category Name Type Required Description
options pack_flg Boolean N Pack the OBLPN? (Default =
False)
• OBLPN will be routed regardless of the `pack_flg` value.
149

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
• If `pack_flg` = True:
◦ OBLPN will be updated to “Packed” status.
◦ The created allocations will be completed.
◦ The sales order detail(s) will be updated.
◦ OBLPN’s final weight and volume will be calculated.
◦ Inventory history will be written.
Example Request Body:
"options": {
"pack_flg": true
}
Full Request Body Example:
The following example would create a packed OBLPN allocated from two different IBLPNs for the same order.
{
"fields": {
"oblpn": {
"facility_id": 1,
"company_id": 1,
"container_nbr": "OBLPN-1"
}
},
"parameters": {
"allocations": [
{
"order_nbr": "ORDER-1",
"order_dtl": {
"seq_nbr": 1
},
"iblpn_nbr": "IBLPN-1",
"qty": 2
},
{
"order_nbr": "ORDER-1",
"order_dtl": {
"item_barcode": "ITEM-1",
"batch_nbr": "BATCH-1",
"invn_attr_a": "A",
"invn_attr_o": "O"
},
"iblpn_nbr": "IBLPN-2",
"qty": 5.52
}
]
},
"options": {
"pack_flg": true
}
}
150

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Track User Activity
If you have purchased WFM (Oracle Workforce Management), you can also send user activity data using the following
parameters in the Create From IBLPN API
• Screen_name: Name of the application or screen in the external system that was used by the user to create
OBLPN.
• Begin_ts: Time at which the user started the create OBLPN operation.
• End_ts: Time at which the user completed the create OBLPN operation.
If all the three parameters are sent in the API, and if WFM is enabled, user activity is written to the WMS Activity view
and subsequently interfaced to WFM, enabling you to analyze user productivity through productivity reports in WFM.
Note:
• All three parameters must be sent for WMS Activity to be written.
• If WFM is not enabled, WMS Activity is not written even if the three parameters are sent.
• Begin_ts and end_ts are parameters at the allocation level and must be sent on all allocations.
• Activity tracking is currently not supported at the OBLPN level.
• In order for WMS Activity data to interface successfully to WFM, screen_name that is sent in the API has to be
configured as a screen in WMS using an RF module and mapped to a work area activity in WFM.
• Screen_name sent on the API is also written on the corresponding IHTs that are written with this API.
• If only screen_name is sent without begin_ts and end_ts, the screen_name is written on the IHT, even if WFM is
not enabled.
• Begin_ts and End_ts cannot be greater than the current timestamp of the facility in the API.
Request Body with User Activity Data
{
"fields": {
"oblpn": {
"facility_id": 1,
"company_id": 1,
"container_nbr": "OBLPN-1"
}
},
"parameters": {
"allocations": [
{
"order_nbr": "ORDER-1",
"order_dtl": {
"seq_nbr": 1
151

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
},
"iblpn_nbr": "IBLPN-1",
"qty": 2,
"begin_ts": "2024-05-21T18:30:00",
"end_ts": "2024-05-21T18:45:00"
},
{
"order_nbr": "ORDER-1",
"order_dtl": {
"item_barcode": "ITEM-1",
"batch_nbr": "BATCH-1",
"invn_attr_a": "A",
"invn_attr_o": "O"
},
"iblpn_nbr": "IBLPN-2",
"qty": 5.52,
"begin_ts": "2024-05-21T18:50:00",
"end_ts": "2024-05-21T18:55:00"
}
]
},
"options": {
"pack_flg": true,
"screen_name": "Create OBLPN Screen"
}
}
Link OBLPN with Asset
POST …/wms/lgfapi/v10/entity/oblpn/{id}/link_asset
links asset (reusable tote) to oblpn.
Assumptions
• Only one OBLPN may be linked to one asset per request.
• OBLPN must be within user's eligible facilities/companies.
Request Body Data
The request body data utilizes the 3 categories in the following ways:

1. `parameters` – allows user to identify the specific oblpn
2. `options` – Additional functional data.
   Parameters
   Category Name Type Required Description
   Parameters container_nbr String Y OBLPN to be linked. "\_\_in"
   lookup is not supported
   Parameters facility_id Integer Container's facility.
   Parameters company_id Integer Container's company.
   152

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Example Request Body:
{
"parameters": {
"facility*id": 1,
"company_id": 1,
"container_nbr": "OBLPN-1"
}
}
Note: Both facility id and company id also support filtering on “code”.
Additional Options Data
Functional request data in the `options` section:
Category Name Type Required Description
options asset_nbr String Y Asset to be linked. May be
created as part of this API.
options asset_seal_nbr String Optionally tracked seal
number.
Options replace_container_nbr*
with_asset_flg
boolean Rename OBLPN to match
asset upon linking?
options validate_lpn_type_flg boolean Validate the LPN type of the
OBLPN with the LPN type
of the asset
{
"options": {
"asset_nbr": "ASSET-01",
"asset_seal_nbr": "SEAL-001",
"replace_container_nbr_with_asset_flg": true
"validate_lpn_type_flg": true
}
}
• If the Asset already exists in the system, then it will be made "In Use" status and update the Asset OBLPN field
with the corresponding OBLPN, Destination field with the OBLPN destination of the linked OBLPN and Seal Nbr
field with corresponding seal nbr passed in the API
• If Original OBLPN is renamed while interfacing (i.e. when "replace_container_nbr_with_asset"= true), system will
update the following:
◦ Populate OBLPN field with the Asset Nbr,
◦ Destination field with the OBLPN destination
◦ Seal Nbr field with corresponding seal nbr passed in the API
• OBLPN type in the Asset table will not get updated with the OBLPN type of the OBLPN
• If the Asset interfaced is new, then a new record is created in the Asset UI with the status "In Use" with
corresponding OBLPN, Seal and destination.
• If the Original OBLPN is renamed with Asset nbr while interfacing (i.e. when
"replace_container_nbr_with_asset"= true), system updates the OBLPN field with the Asset Nbr, Destination
153

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
field with the Original OBLPN's destination and Seal Nbr field with corresponding seal nbr passed in the
interface
• If the OBLPN is already linked to an asset and another Asset Nbr is passed in the interface for linking with
OBLPN, the original asset number needs to be updated back to status "In-warehouse" while the new asset
number is updated back to status "In-use".
• In case if the OBLPN is already linked to an asset/seal and another seal nbr is passed in the API, then update
the seal nbr field with the corresponding seal.
• If the Asset interfaced in the API is new to the system, then a new record is created in the Asset table
• The fields "asset*nbr" and "asset_seal_nbr" is updated with corresponding data in the oblpn.
• If Original OBLPN is replaced with Asset Nbr while interfacing (i.e. when "replace_container_nbr_with_asset"=
true), system should update the Container table as mentioned below:
◦ LPN Nbr is updated with the Asset Nbr
◦ Asset Nbr and Asset Seal Nbr is updated with the corresponding value passed in the API
◦ OBLPN Type field is not updated with the OBLPN type of the Asset
◦ "Ref OBLPN Nbr" field is updated with original OBLPN Nbr
• The following Inventory History records are created:
◦ IHT 57 - Asset Received – This record is not written if the Asset interfaced in the API is new to the system
◦ IHT 31- OB Container Modified is written if the OBLPN is renamed with Asset Nbr while linking.
Ship OBLPN
This API allows you to Ship a packed or loaded Outbound LPN.
POST entity/oblpn/{id}/ship/
Request Body
Section Name Required Type Default Comments
options locn_barcode X string Final shipping location
from the facility.
options output_file_to*
generate
string Output file to be
generated upon
success per OBLPN.
• "output_file_to_generate" supports:
◦ oblpn_shipping_info
◦ lpn_inventory
Note: The Ship OBLPN does not currently honor the Stop Ship flag.
154

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
{
"options": {
"locn*barcode": "LOCN123",
"output_file_to_generate": "oblpn_shipping_info"
}
}
Bulk Ship OBLPN
This API allows you to ship one or more OBLPN(s) in a single request.
Request Body
POST entity/oblpn/bulk_ship/
Section Name Required Type Default Comments
options commit_frequency integer 1 0=Roll back on first
error. 1=Commit per
OBLPN shipped.
options require_facility*
company_flg
boolean True When filtering on
fields other than `id`,
is the facility and
company context
required?
{
"parameters": {
"facility_id": "111",
"company_Id": "222",
"container_nbr\_\_in": ["OBLPN1", "OBLPN2", "OBLPN3"]
},
"options": {
"locn_barcode": "LOCN123",
"output_file_to_generate": "oblpn_shipping_info",
"commit_frequency": 0
}
}
Cancel OBLPN
The Cancel OBLPN REST API allows you to cancel an OBLPN. This enhancement work as a mirror to the functionality of
RF Cancel OBLPN.
API URL
POST .../entity/oblpn/cancel
155

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Request Parameters
Name Required Type Description
facility_id Not mandatory String Facility context by id
company_id Not mandatory String Company context by id
facility_id**code Not mandatory String Facility context by code
company_id**code Not mandatory String Company context by code
oblpn_nbr Mandatory String can be same as IBLPNs
iblpn_nbr Mandatory String can be same as OBLPNs
reason_code Not mandatory String Used for inventory history tracking.
Request Body Example
{
"parameters": {
"facility_id**code": "123RF",
"facility_id": "123",
"company_id**code": "456AR",
"company_id": "456",
"oblpn_nbr": "OBLPN1"
},
"options": {
"reason_code": "54",
"iblpn_nbr": "IBLPN1"
}
}
Bulk Cancel OBLPN
The Bulk Cancel OBLPN API allows you to bulk cancel OBLPNs. This enhancement work as a mirror to the functionality
of RF Bulk Cancel OBLPN.
API URL
POST .../entity/oblpn/bulk_cancel
Request Parameters
Name Required Type Description
facility_id Not mandatory String Facility context by id
156

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Required Type Description
company_id Not mandatory String Company context by id
facility_id**code Not mandatory String Facility context by code
company_id**code Not mandatory String Company context by code
container_nbr\_\_in Mandatory String List of container numbers
reason_code Not mandatory String Used for inventory history tracking
commit_frequency Not mandatory Integer 0=Roll back on first

error. 1=Commit per

OBLPN cancelled

Request Body Example
{
"parameters": {
"facility_id**code": "123RF",
"facility_id" : "123",
"company_id**code": "456AR",
"company_id" : "456",
"container_nbr\_\_in": [“CNTR1”, “CNTR2”, “CNTR3”]
},
"options": {
"reason_code": "54",
"commit_frequency": "1"
}
}
Order Detail Serial Number
GET …/wms/lgfapi/v10/entity/order_dtl_serial_nbr/{id}
On performing GET operation for "order_dtl_serial_nbr" with order detail, the API fetches the required serial numbers
(required_serial_nbr) for that particular order detail.
Response Components
• create_user
• create_ts
• mod_user
• mod_ts
• order_dtl_id
157

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
• required_serial_nbr
Pallet
These topics give descriptions for APIs that complete actions related to Pallets in the Warehouse.
Sort LPN
The Sort LPN API allows you to sort an LPN to a Pallet in a sort location mimicking what the RF Inbound Sorting process
does. The RF modules include: RF Sort LPN, and RF Inbound Sort Location.
You can sort an LPN to a pallet in a sort location with the following POST request:
POST .../entity/pallet/sort_lpn/

The following table provides details about the Input Parameters/Filters used to identify the target pallet:
Name Required Type Default Description
facility_id integer Facility context by id.
facility_id**code string Facility context by code.
company*id integer Company context by id.
company_id***code string Company context by code.
pallet_nbr X string T arget sort pallet.
• The pallet will be created if it doesn't exist.
• The requesting user's default facility/company context will be assumed if overrides are not provided.
Functional Options
Name Required Type Default Description
container_nbr X string LPN being sorted to pallet.
sort_zone X string Destination sort zone.
sort_location_barcode X string Destination sort location.
sort_to_inventory string "pallet-call-directed-
putaway"
Sort method.
allow_received_status_flg boolean False Allow sorting of IBLPN in
Received status.
allow_picked_status_flg boolean False Allow sorting of OBLPNs in
Picked status.
158

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
• Default valid LPN statuses:
• Located
• Allocated
• Packed
The following is an example body for Sort LPN to Pallet:
{
"parameters": {
"facility_id": 1,
"company_id_code": "FOO",
"pallet_nbr": "PALLET001"
},
"options": {
"container_nbr": "LPN001",
"sort_zone": "ZONE01",
"sort_location_barcode": "BRCD001",
"sort_to_inventory": "pallet-call-directed-putaway"
}
}
Response Status
• 204 - No content
• Operation successfully completed.
• 400 - Validation error
• 500 - Internal server error
Sort LPN Close Pallet
The Sort LPN/Close Pallet API is used as part of the inbound sorting process which groups LPNs to pallets in sort
locations. This API mimics the RF IB Sort LPN module which calls the Sort LPN Close IB Pallet back end entry point with
parameters.
You can Sort LPNs and Close Pallet with the following POST requests:
POST .../entity/pallet/close_inbound_sorting/

                        POST .../entity/pallet/{id}/close_inbound_sorting/

The following table provides details about the Input Parameters/Filters used to identify the target pallet:
Name Required Type Default Description
facility_id integer Facility context by id.
facility_id\_\_code string Facility context by code.
company_id integer Company context by id.
159

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Required Type Default Description
company_id*\_\_code string Company context by code.
pallet_nbr X string T arget sort pallet.
• The pallet will be created if it doesn't exist.
• The requesting user's default facility/company context will be assumed if overrides are not provided.
The following table details the functional options:
Name Required Type Default Description
create_replen_task_flg boolean True Generate a replenishment
task on close?
task_type_description string Required type description
for generated replen task.
Valid when create_replen*
task_flg = True.
Default valid LPN statuses:
• Located
• Allocated
• Packed
The following is an example body for Create Replenishment T ask Flag:
{
"parameters": {
"facility_id": 1,
"company_id_code": "FOO",
"pallet_nbr": "PALLET001"
},
"options": {
"create_replen_task_flg": true,
"task_type_description": "My Task Type"
}
}
Response
Response Status:
• 204 - No content
◦ Operation successfully completed.
• 400 - Validation error
• 500 - Internal server error
160

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Ship Pallet
This API allows you to ship a pallet and all associated OBLPN(s.)
entity/pallet/{id}/ship/
Request Parameters
Section Name Required Type Default Comments
options locn*barcode X string Final shipping location
from the facility.
options output_file_to*
generate
string Output file to be
generated upon
success per OBLPN.
• "output_file_to_generate" supports:
◦ oblpn_shipping_info
◦ lpn_inventory
{
"options": {
"locn_barcode": "LOCN123",
"output_file_to_generate": "oblpn_shipping_info"
}
}
Pick-Pack
These topics give descriptions for APIs that complete actions related to picking and packing in the Warehouse.
Pick Confirm
The Pick Confirm API allows you to perform cubed or non-cubed picking. Also:
• The Pick Confirm API supports picking of multiple allocations in a single payload.
• If one or more Pick updates fail we report an error only for the first failed Pick.
• If the First Pick fails, then the rest of the Picks in the payload does not get Picked.
161

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Note: This is a new API meant to replace the existing legacy `pick_confirm` API. The legacy API will eventually be
retired so no further enhancements will be made to it. New functionality will instead be added to this API as part of
the lgfapi suite.
This API supports features of the legacy API including the following new parameters:
• mhe_mode_flg - true/false; default true
• async_flg - true/false; default true
• short_flg - true/false; default false
• Replaces using the legacy "action_code" = "SHORT".
The Pick Confirm API can be called using the following POST request:
POST ..lgfapi/v10/pick_pack/pick_confirm/
Note About Distribution
This API has been updated so that it will not auto-close an OBLPN when there are cancelled allocations going into it.
Also note, for distribution, it is recommend that you use the Pack OBLPN Distribution API.
Note About T asks
If an allocation is completed using the pick_pack/pick_confirm API using one user, based on the modified user for the
T ask, the application restricts additional users from completing Picks through an API call.
Note: If you are not using the RF to complete Picks, it is not necessary to generate T asks and Picks based on T asks.
You can perform Pick Pack directly without generating the T asks using the Pick Pack API.
Allocation Unit of Measure
Note: If pick confirmation is called with a source location from active, and the allocation Unit of Measure (UOM) is
“Cases” or “Packs”, the UOM_Qty considered will always be in terms of the item’s standard pack or case quantity. This
is because allocation from active will always happen in terms of the underlying item’s standard pack or standard case
quantity. If the allocation is from reserve, then the UOM_Qty will be relevant if the allocation UOM passed is “Cases” or
“Packs”.
Allow Wave Number as Optional Field
We've made the Wave Number (wavenbr) field an optional (non-mandatory) in the pick_pack/pick confirm API, so you
can now pack allocations without needing a wave number.
To pack allocations without a wave number, send a pickpack/pickconfirm API request, without the 'wavenbr' field blank
in the body.
Request Parameters
Pick List
These represent the parameters required for a single pick/short:
162

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Required Type Default Description
facility_id Integer Facility context by id.
facility_id**code String Facility context by code.
company*id Integer Company context by id.
company_id***code String Company context by code.
wave*nbr X String Associated wave.
order_nbr X String Associated sales order.
item_alternate_code C String Item identifier.
item_barcode C String Item identifier.
qty X Number 0 Quantity to be acted upon.
batch_nbr String Inventory batch/lot.
uom_qty Number Filter on Case or Pack
quantity when searching
for allocations.
allocation_uom String "UNITS", "PACKS", or
"CASES".
reason_code String Reason for short.
pick_location C String From location.
from_container_nbr C String From container.
to_container_nbr C String LPN inventory is packed
into. Not required for short.
update_inventory_on*
short_flg
Boolean False Also short source inventory
on pick short?
close_container_status String "packed" Final OBLPN status:
"picked" or "packed".
short_on_close_flg Boolean False Should any remaining
unpacked quantity
shorted?
mhe_system_code C String MHE system.
short_flg Boolean False Is this a short?
serial_nbr_list C String List of Serial Numbers
separated by a comma.
invn_attr_a

C String Inventory attribute A
invn_attr_b

C String Inventory attribute B
invn_attr_c

C String Inventory attribute C
163

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Required Type Default Description
invn_attr_d

C String Inventory attribute D
invn_attr_e C String Inventory attribute E
invn_attr_f

C String Inventory attribute F
invn_attr_g

C String Inventory attribute G
invn_attr_h

C String Inventory attribute H
invn_attr_i C String Inventory attribute I
invn_attr_j C String Inventory attribute J
invn_attr_k C String Inventory attribute K
invn_attr_l C String Inventory attribute L
invn_attr_m

C String Inventory attribute M
invn_attr_n

C String Inventory attribute N
invn*attr_o C String Inventory attribute O
Expiry_date C Date Format YYYY-MM-DD
orig_iblpn_nbr C String If the original allocation
is from the LPN and
substitution is happening
from a different LPN.
orig_batch_nbr C String Batch Number associated
with the original allocation.
orig_expiry_date C String Expiry Date associated with
the original allocation.
orig_inventory_attribute*
a to orig*inventory*
attribute*o
C String Inventory attributes value
associated with the original
allocation.
cubed_oblpn_exact*
match_only_flg
Boolean False When passed as true, in
cubed scenarios (when the
OBLPN is created at wave
time), the system will be
enabled optimizations to
make processing faster.
Validations
• Facility must be in user's eligible facilities and not be ambiguous.
• Possible if there is a Store and a DC with the same code.
• Company must be in user's eligible companies.
164

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
• If facility or company context is not included in the input parameters, user defaults are used.
• User cannot pass both "facility_id" and "facility_id\_\_code" in the same request.
• User cannot pass both "company_id" and "company_id_code" in the same request.
• "mhe_system_code" is required if "mhe_mode_flg" is True.
• Only one of "item_alternate_code" or "item_barcode" is allowed.
• Only one of "pick_location" or "from_container_nbr" is allowed.
• "to_container_nbr" is required for "pick" operation, but is not required for "short".
• If the allocated inventory for the given order detail in the API request does not match with the inventory
attribute values passed in the API, then the system will return the error response "Inventory attribute
combination is not allocated for order %order number%."
Request-Level Flags
Name Required Type Default Description
mhe_mode_flg Boolean True When true, enforce that "mhe_system_code" is
provided.
async_flg Boolean True Run API asynchronously?
suppress_serial_warning_flg Boolean True If the suppress_serial_warning_flg" is set to "false":

• System should validate the validations pertaining
to serial numbers sent in the API, which are of
type Warning & Error .
• If user is not sending serial numbers in the API
request, then still user should be allowed to
process the API without serial number (Existing
behavior).
The following is an example JSON request:
{
"mhe_mode_flg": true,
"async_flg": true,
"suppress_serial_warning_flg":true,
"pick_list": [{ "facility_id**code": "QATST01",
"company_id**code": "QATSTPC",
"wave_nbr": "WVQATSTPC072935",
"order_nbr": "CPORD102720C1",
"item_barcode": "RUG99",
"qty":3,
"serial_nbr_list": [
"SLN1",
"SLN2",
"SLN3"],
"invn_attr_a" : "TESTA",
"invn_attr_b" : "TESTB",
"invn_attr_c" : "TESTC",
"invn_attr_d" : "TESTD",
"invn_attr_e" : "TESTE",
"invn_attr_f" : "TESTF",
"invn_attr_g" : "TESTG",
"invn_attr_h" : "TESTH",
"invn_attr_i" : "TESTI",
165

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"invn_attr_j" : "TESTJ",
"invn_attr_k" : "TESTK",
"invn_attr_l" : "TESTL",
"invn_attr_m" : "TESTM",
"invn_attr_n" : "TESTN",
"invn_attr_o" : "TESTO",
"from_container_nbr": "CNTST0100031583",
"to_container_nbr": "CPOBLPN0106,
"update_inventory_on_short_flg": true,
"close_container_status" : "packed",
"mhe_system_code": "CONVCP1",
"short_flg": false }]
}
The following is an example XML request:
<request>
<mhe_mode_flg>false</mhe_mode_flg>
<async_flg>false</async_flg>
<pick_list>
<list-item>
<facility_id_code>FAC</facility_id_code>
<company_id>1</company_id>
<wave_nbr>WAVE001</wave_nbr>
<order_nbr>ORDER001</order_nbr>
<item_barcode>ITEM1234</item_barcode>
<qty>10</qty>
<from_container_nbr>IBLPN0001</from_container_nbr>
<to_container_nbr>OBLPN0001</to_container_nbr>
<short_flg>false</short_flg>
</list-item>
</pick_list>
</request>
Currently, the Pick Confirm API (URL: pick_pack/pick_confirm/) sends the Batch Number that is used during picking.
If the batch number provided in the API is not the same as the original allocated inventory, or if the location where
the pick is happening contains inventory pointing to multiple batches for the same SKU, then substitution will happen
against one of the allocated inventory. (For example: If Location has Batch1 and Batch2 allocated for Order1, during
picking if the user sends Batch3 for Order1, the system will substitute against Batch1 or Batch2).
Note: To perform substitution by batch API, a new field called Original Batch Number for performing substitution will
be required in upcoming releases after 21B. The behavior of the inbuilt substitution by only sending the batch number
field will not be supported in the upcoming releases. Customers utilizing this API (pick_pack/pick_confirm/) please
keep note of this new change in upcoming releases.
Note: If some of the inventory attribute values are not passed in the Pick request, then system will assume it to
be wild card and matches with the allocated inventory. if the allocated inventory for the given order detail in the
API request is not matching with the inventory attribute values passed in the API, then system should return error
response "Inventory attribute combination is not allocated for order %order number%".
166

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Substitution
In scenarios when the original allocated inventory is not available, you can now substitute with another inventory. The
Pick Confirm API is enhanced to support substitutions where you can substitute or replace an inventory with another
available inventory via Pick Confirm API. As shown below, the following fields were added to the Pick List:
Parameters
Name Required Type Default Description
Orig*IBLPN_Nbr C String If original allocation is
from LPN & substitution is
happening from different
LPN.
Orig_Batch_nbr C String Batch Number associated
with the original allocation.
Orig_expiry_date C String Expiry Date associated with
the original allocation.
Orig_Inventory_Attribute*
A to Orig*Inventory*
Attribute_O
C String Inventory attributes value
associated with the original
allocation.
• Substitution will happen based on the value defined in the above fields, If the value is not defined in the above
fields (LPN ,Batch, Expiry date), then the system will consider it as normal picking flow (Without substitution).
• If original (Batch/Expiry/Attributes/LPN) values are not sent in the pick confirm API request, then after sending
a different batch number (other than the allocated batch number), the system will perform implicit substitution
which is an existing behavior.
• If any of the Original values (Attribute/Expiry date/LPN) are sent in the pick confirm API, and the user wants a
batch number to also be part of substitution, then the original batch number explicitly has to passed in the API.
In this case, implicit substitution of the batch number will not happen.
{
"mhe_mode_flg": false,
"async_flg": true,

"pick_list": [{
"facility_id**code": "QATST01",
"company_id**code": "QATSTPC",
"wave_nbr": "WVQATSTPC072935",
"order_nbr": "CPORD102720C1",
"item_barcode": "RUG99",
"qty":2,
"uom_qty":4,
"orig_iblpn_nbr": "CNTST0100031599",
"from_container_nbr": "CNTST0100031583",
"to_container_nbr": "CPOBLPN010621C1",
"orig_batch_nbr":"BAT2021",
"batch_nbr":"CPBAT0708C12",
"update_inventory_on_short_flg": true,
"close_container_status" : "packed",
167

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"mhe_system_code": "CONVCP1",
"short_flg": false
},
{
"facility_id**code": "QATST01",
"company_id**code": "QATSTPC",
"wave_nbr": "WVQATSTPC072935",
"order_nbr": "CPORD102720C1",
"item_barcode": "RUG99",
"qty":2,
"pick_location": "CPLOC2021AA",
"to_container_nbr": "CPOBLPN010621C1",
"orig_batch_nbr":"BAT2021",
"batch_nbr":"CPBAT0708C16",
"update_inventory_on_short_flg": true,
"close_container_status" : "packed",
"mhe_system_code": "CONVCP1",
"short_flg": false

}

]}
Track User Activity
If you have purchased WFM (Oracle Workforce Management), you can also send user activity data using the following
parameters in the Pick Confirm API
• Screen_name: Name of the application or screen in the external system that was used by the user to perform
picking.
• Begin_ts: Time at which the user started the relevant pick.
• End_ts: Time at which the user completed the relevant pick.
If all the three parameters are sent in the API, and if WFM is enabled, user activity is written to the WMS Activity view
and subsequently interfaced to WFM, enabling you to analyze user productivity through productivity reports in WFM.
168

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Note:
• All three parameters must be sent for WMS Activity to be written.
• If WFM is not enabled, WMS Activity is not written even if the three parameters are sent.
• Begin_ts and end_ts are parameters at the pick level and must be sent on all picks.
• In order for WMS Activity data to interface successfully to WFM, screen_name that is sent in the API has to be
configured as a screen in WMS using an RF module and mapped to a work area activity in WFM.
• Screen_name sent on the API is also written on the corresponding IHTs that are written with this API.
• If only screen_name is sent without begin_ts and end_ts, the screen_name is written on the IHT, even if WFM is
not enabled.
• Begin_ts and End_ts cannot be greater than the current timestamp of the facility in the API.
• WMS Activity is not written if short_flg is true.
Request Body with User Activity Data
{
"mhe_mode_flg": false,
"async_flg": true,
"screen_name": "Pick Confirm Screen",
"pick_list": [{
"facility_idcode": "QATST01",
"company_idcode": "QATSTPC",
"wave_nbr": "WVQATSTPC072935",
"order_nbr": "CPORD102720C1",
"item_barcode": "RUG99",
"qty":2,
"from_container_nbr": "CNTST0100031583",
"to_container_nbr": "CPOBLPN010621C1",
"begin_ts": "2024-05-27T18:30:00",
"end_ts": "2024-05-27T18:45:00"
},
{
"facility_idcode": "QATST01",
"company_idcode": "QATSTPC",
"wave_nbr": "WVQATSTPC072935",
"order_nbr": "CPORD102720C1",
"item_barcode": "RUG99",
"qty":2,
"pick_location": "CPLOC2021AA",
"to_container_nbr": "CPOBLPN010621C1",
"begin_ts": "2024-05-27T18:50:00",
"end_ts": "2024-05-27T18:55:00"
}
]
169

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
}
Close LPN
The close_lpn API allows you to close an LPN during picking/packing. This API replaces the legacy pick confirm API
when the action code is closed. While performing pick and pack operations (either non cubed active picking or cubed
picking), the Close action code indicates to WMS that the Outbound LPN being picked needs to be closed.
Note: This is a new API meant to replace the existing legacy `close_lpn` API. The legacy API will eventually be retired
so no further enhancements will be made to it. New functionality will instead be added to this API as part of the lgfapi
suite.
This API supports features of the legacy API including the following new parameter:
• async_flg - true/false; default true
Close LPN API can be called using the following POST request:
POST ..lgfapi/v10/pick_pack/close_lpn/

Request Parameters
The following table provides details about the query string parameters:
Name Required Type Default Description
facility*id Integer Facility context by id.
facility_id\_\_code String Facility context by code.
company_id Integer Company context by id.
company_id_code String Company context by code.
to_container_nbr X String To OBLPN.
close_container_status String "packed" Final OBLPN status:
"picked" or "packed".
short_on_close_flg Boolean False Should any remaining
unpacked quantity
shorted?
update_inventory_on*
short_flg
Boolean False Also short source inventory
on pick short?
reason_code String Reason for short.
async_flg Boolean True Run API asynchronously?
170

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
The following is an example JSON request:
{
"facility_idcode": "FAC",
"company_id": 1, "to_container_nbr": "OBLPN001", "close_container_status":
"picked", "short_on_close_flg": true, "async_flg": true
}
Wave Complete
The Wave Complete API replaces the legacy API when the action code is Complete. This is an indicator to inform WMS
that all picks are completed for that wave, and there are no more picks outstanding.
Note: This is a new API meant to replace the existing legacy `close_lpn` API. The legacy API will eventually be retired
so no further enhancements will be made to it. New functionality will instead be added to this API as part of the lgfapi
suite.
This API supports features of the legacy API including the following new parameter:
• async_flg - true/false; default true
◦ When false:

- Instead of submitting a celery task at the end for later processing, it should be immediately
  processed and a response returned.
- On success, return a 204 - "No Content" HTTP response status with no response body.
- When true: Return HTTP response status 202 - "Accepted" with no response body.
  ◦ Signals that we received the request and it was successfully submitted for processing.
  The Wave Complete API can be called using the following POST request:
  POST ..lgfapi/v10/pick_pack/wave_complete/

The following table provides details about the query string parameters:
Name Required Type Default Description
facility_id Integer Facility context by id.
facility_id**code String Facility context by code.
company*id Integer Company context by id.
company_id***code String Company context by code.
wave*nbr X String Associated wave.
update_inventory_on*
short_flg
Boolean False Also short source inventory
on pick short?
171

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Required Type Default Description
close_container_status String "packed" Final OBLPN status:
"picked" or "packed".
reason_code String Reason for short.
mhe_system_code String MHE system.
async_flg Boolean True Run API asynchronously?
The following is an example JSON request:
{
"facility_id\_\_code": "FAC",
"company_id": 1,
"wave_nbr": "WAVE001",
"update_inventory_on_short_flg": true,
"async_flg" true
}
GET Next Pick
The Get Next Pick REST API allows you to pick inventory based on the location pick sequence during picking from the
Oracle WMS Cloud Mobile App or an external system using WMS APIs. This API follows the same underlying logic used
in the text based Mobile RF picking transaction.
Note: The Oracle WMS Cloud Mobile App is one example of where this API will be leveraged. However, this API can be
used in other scenarios.
The Get Next Pick API should give one pick from allocation records based on the location pick sequence when there are
multiple allocation records that exist for a given Order/OBLPN.
The following is a sample GET request for Get Next Pick:
• GET .../entity/allocation/get_next_pick
Sample request for get next pick based on OBLPN:
• GET .../entity/allocation/get_next_pick?container_nbr=
Sample request for get next pick based on Order Number:
• GET .../entity/allocation/get_next_pick?order_nbr=
172

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Get Reponse:
• Get next pick should give information associated with the inventory that is getting picked including:
◦ Order Number : Order number against which the inventory is getting picked
◦ Destination Facility: For Store Order Destination facility associated with the order
◦ Customer Name: For Customer Order Customer name associated with the order
◦ IBLPN: IBLPN number from which the inventory that needs to picked
◦ OBLPN: OBLPN number in which the respective inventory is getting picked
◦ Location: Location from which the inventory is getting picked (Active/ Reserve)
◦ Item Code : Respective Item Code
◦ Item Alternate Code: Respective Alternate Item Code
◦ Inventory Attributes (A-O) : Attributes associated with the inventory.
◦ Batch Number: Batch number associated with the inventory.
◦ Expiry Date: Expiry date associated with the inventory.
◦ Quantity : Pending quantity that needs to be picked for respective allocation record (Allocated Qty -
Packed Qty)
Pack Full LPN
The Full LPN Packing API allows you to pack a full LPN. This API can be used for voice based picking, or invoked from
other systems likes MHE or AGV (Automated Guided Vehicle) to pack the full LPN's .
API URL: Lookup by Filters
POST.../lgfapi/v10/pick_pack/pack_full_lpn

Parameters for Full LPN API
Name Required Type Default Value Description
facility_id Integer Facility context by id
facility_id\_\_code string Facility context by code
company_id Integer Company context by id.
company_id_code string Company context by code.
oblpn_number C string OBLPN which needs to be packed.

If OBLPN is not sent, then system will pack
the OBLPN based on the IBLPN (Full LPN-
Allocated) sent in the API
173

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Required Type Default Value Description

iblpn_number C string If IBLPN is not sent, then system will consider
allocated IBLPN w.r.t given OBLPN for packing.

If IBLPN is sent, and IBLPN is allocated for Full
LPN then system will pack the corresponding
OBLPN against the given IBLPN.

If IBLPN is sent, and IBLPN is not matching
with allocated IBLPN then system will perform
substitution (substitution will be handled
through a seperate user story).

reason_code string Reason for short.
short_flg Boolean False short_flg = false; Allocated quantity against
OBLPN will be Packed.

short_flg= true; Allocated quantity against
OBLPN will be shorted.

update_inventory_on_short_flg Boolean False Short source allocated inventory
mhe_system_code string MHE system. MHE System is not mandatory as
the this API can be called from MHE systems or
through externally developed packing screens
or in future our VBCS option to perform full LPN
picking
Request Level Flags
Name Required Type Default Description
async_flg Boolean True Run API asynchronously
sub_validate_batch_number_flg Boolean False During substitution:

If True, batch number should be validated
against allocated inventories batch number.

If False, batch number of should not be
validated against allocated inventories batch
number.

sub_validate_expiry_date_flg Boolean False During substitution:
174

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Required Type Default Description

If True, expiry date should be validated
against allocated inventories expiry date.

If False, expiry date should not be validated
against allocated inventories expiry date.

sub_validate_po_number_flg Boolean False During substitution:

If True, PO number should be validated
against allocated LPN's PO number.

If False, PO number should be not validated
against allocated LPN's PO number.

sub_validate_shipment_number_flg Boolean False During substitution:

If True, shipment number should be validated
against allocated LPN's shipment number.

If False, shipment number should not be
validated against allocated LPN's shipment
number.

Sample Request JSON:
{

"async_flg": false,
"pick_list": [{
"facility_id__code": "FAC",
"company_id": 1,
"iblpn_number": "IBLPN0001",
"oblpn_number": "OBLPN0001",
"short_flg": false
}]
}
Substitution
Substitution Validation:
• API should allow to substitute given IBLPN only when respective IBLPN's quantity is an exact match for initial
allocated IBLPN.
• Do not allow to perform substitution if the allocated Inbound LPN being substituted is reserved against an
Order (Required LPN number populated).
175

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
• Do not allow to perform substitution if the substituted LPN is allocated against an order and original allocated
LPN is reserved for a different order.
• During substitution, based on the required validations (Batch/ PO etc..) mentioned in the API, system should
perform respective validations against the allocated LPN. Only when respective values are matching then only
system should perform substitution and pack the OBLPN, when values are not matching then API should return
error message "Substitution fails".
• If the substituting IBLPN is not present in the system for given facility, then API should return error message
"No Such IBLPN %IBLPN Number%".
Sample request JSON:
{

"async_flg": false,
"sub_validate_batch_number_flg": true,
"sub_validate_expiry_date_flg": true,
"sub_validate_po_number_flg": true,
"sub_validate_shipment_number_flg": true,

"pick_list": [{
"facility_id__code": "FAC",
"company_id": 1,
"iblpn_number": "IBLPN0001",
"oblpn_number": "OBLPN0001",
"short_flg": false
}]
}

Shorting
If Short flag is set to True, then it should allow:
• To short the inventory (Respective OBLPN).
• To update the allocated inventory on short.
• To send reason code for shorting.
Update Pack OBLPN to Picked Status
The Pack Full API now has an additional parameter (oblpn_status_post_picking) that allows you to move the LPN status
to Packed or Picked via API calls.
If the oblpn_status_post_picking parameter is set to:
• Packed/ Blank (Default): Created OBLPNs are updated to Packed Status.
• Picked: Created OBLPNs are updated to Picked Status.
The following table lists the fields in the parameter:
Name Description
facility_id Facility context by id
facility_id\_\_code Facility context by code
176

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Description
company_id Company context by id.
company_id_code Company context by code.
oblpn_number OBLPN which needs to be packed.
iblpn_number If IBLPN is not sent, then system will consider allocated IBLPN w.r.t given OBLPN for packing.
reason_code Reason for short.
short_flg short_flg = false; Allocated quantity against OBLPN will be Packed.
update_inventory_on_short_flg Short source allocated inventory
mhe_system_code MHE system. MHE System is not mandatory as this API can be called from MHE systems or through
externally developed packing screens or in future our VBCS option to perform full LPN picking.
oblpn_status_post_picking Supported values "Picked" or "Packed". If the parameter is not sent or the value is left blank, then
status "Packed" is displayed, as default.
Planned Parcel Shipment
The Planned Parcel Shipment API allows you to query data in the stage tables, status, and corresponding error
messages without the need to go through the Input Interface UI.
Stage Planned Parcel Shipment Header
This entity is used to get the list of the planned parcel shipment stage table records present in the system.
To fetch all results, use the following URL:
GET .../lgfapi/v10/entity/stage_planned_parcel_shipment_hdr/
To fetch only one result based on ‘ID’, search with a specific 'ID' in the following URL:
GET .../lgfapi/v10/entity/stage_planned_parcel_shipment_hdr/{id}
HEAD Request Method URL:
HEAD .../lgfapi/v10/entity/stage_planned_parcel_shipment_hdr/{id}
Stage Planned Parcel Shipment Detail
This entity is used to get the planned parcel shipment detail records of a parcel shipment stage table.
To fetch all results, use the following URL:
GET .../lgfapi/v10/entity/stage_planned_parcel_shipment_dtl/
To fetch only one result based on ‘ID’, search with a specific 'ID' in the following URL:
GET .../lgfapi/v10/entity/stage_planned_parcel_shipment_dtl/{id}
HEAD Request Method URL:
177

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
HEAD .../lgfapi/v10/entity/stage*planned_parcel_shipment_dtl/{id}
Print
These topics give descriptions for APIs that complete actions related to Printing in the Warehouse.
Print Shipping Label
GET.../wms/lgfapi/v10/print/label/shipping/?label_designer_code=foo
Returns the ZPL representation of the label
POST .../wms/lgfapi/v10/print/label/shipping
Submits the label for printing
Parameters
The “parameters” section of the request body is required in addition to the “options” section outlined below. One or
more parameters are used to determine the order(s) for which the operation will be applied.
Category Name Type Required GET Request POST Request Comments
options label_designer*
code
string X X X Label designer
template to be
printed
options printer*name string X Default's to
cwuser.default*
label_printer.
options label_count integer X Number of labels
to print. Must be
greater than 0.
Default = 1.
API Filters
Functions like a bulk operation for identifying one or more IBLPN(s) to be printed: id Including "in" lookup
• facility_id
• company_id
• container_nbr
• Including "in" lookup
Example Query String for GET
178

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
GET.../wms/lgfapi/v10/print/label/shipping/?
label_designer_code=foo&facility_id**code=FAC1&company_id_code=COM1&container_nbr=IBLPN1
Example Request Body for POST
{
"parameters": {
"facility_id**code": "FAC1",
"company_id\_\_code": "COM1",
"container_nbr": "IBLPN1"
},
"options": {
"label_designer_code": "label_1",
"printer_name": "PRINTER1",
"label_count": 1
}
}
Response Body Data
On success, a 200 - OK status is returned.
The standardized bulk response body is returned. This will have aggregate information for all IBLPN(s) processed as well
as the counts and any details.
For a GET request, the ZPL data bill be base64 encoded in the "data" section.
{
"record_count": 2,
"success_count": 1,
"failure_count": 1,
"data": {
"IBLPN_1": "VGhpcyBpcyBaUEwgY29kZQ=="
},
"details": {
"IBLPN_2": "Some error message."
}
}
Print Parcel Carrier Labels
You can easily print carrier labels using the Print Shipping Label API. When you are working with different carriers used
for shipping, you can easily print labels sent from these carriers without changing the design or format of the data sent.
• If thelabel_designer_code parameter is not sent or is blank, then the Print Shipping Label API looks at the
Label Rules Engine to determine the label template. The API now allows the label_designer_code to be optional
in the request.
• If no rule exists in the Label rules engine UI for Shipping Label type, then the API sends the error "Label Rule
not found."
To enable printing of carrier labels in the Print Shipping Label API:

1. Either, you can directly pass the label designer code of the label type ‘wsaddon’ for the API parameter
   label_designer_code.
2. Or, do not pass the label_designer_code in the request and set the configuration in the Label Rules Engine UI,
   set the Print Carrier Label Only flag to Yes, for the Shipping label type.
   179

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Print LPN Label
GET.../wms/lgfapi/v10/print/label/ib*container/?label_designer_code=foo
Returns the ZPL representation of the label.
POST .../wms/lgfapi/v10/print/label/ib_container
Submits the label for printing.The “parameters” section of the request body is required in addition to the “options”
section outlined below. One or more parameters are used to determine the order(s) for which the operation will be
applied.
Category Name Type Required GET Request POST Request Comments
options label_designer_code string X X X Label designer template to be
printed
options printer_name string X Default's to cwuser.default*
label_printer.
options label_count integer X Number of labels to print.
Must be greater than 0.
Default = 1.
API Filters
• Functions like a bulk operation for identifying one or more IBLPN(s) to be printed:
◦ id

- Including "in" lookup
  ◦ facility_id
  ◦ company_id
  ◦ container_nbr
- Including "in" lookup
  Example Query String for GET
  GET.../wms/lgfapi/v10/print/label/ib_container/?
  label_designer_code=foo&facility_id**code=FAC1&company_id_code=COM1&container_nbr=LPN1
  Example Request Body for POST
  {
  "parameters": {
  "facility_id**code": "FAC1",
  "company_id\_\_code": "COM1",
  "container_nbr": "OBLPN1"
  },
  "options": {
  "label_designer_code": "label_1",
  "printer_name": "PRINTER1"
  }
  }
  180

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Response Body Data
On success, a 200 - OK status is returned
For a GET request, the ZPL data bill be base64 encoded in the "data" section.
{
"record*count": 2,
"success_count": 1,
"failure_count": 1,
"data": {
"IBLPN_1": "VGhpcyBpcyBaUEwgY29kZQ=="
},
"details": {
"IBLPN_2": "Some error message."
}
}
Print Pallet Label
GET.../wms/lgfapi/v10/print/label/pallet/?label_designer_code=foo
Returns the ZPL representation of the label
POST .../wms/lgfapi/v10/print/label/pallet
Submits the label for printing
The “parameters” section of the request body is required in addition to the “options” section outlined below. One or
more parameters are used to determine the order(s) for which the operation will be applied.
Category Name Type Required GET Request POST Request Comments
options label_designer*
code
string X X X Label designer
template to be
printed
options printer*name string X Default's to
cwuser.default*
label_printer.
options label_count integer X Number of labels
to print. Must be
greater than 0.
Default = 1.
181

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
API Filters
• Functions like a bulk operation for identifying one or more IBLPN(s) to be printed:
◦ id

- Including "in" lookup
  ◦ facility_id
  ◦ company_id
  ◦ container_nbr
- Including "in" lookup
  Example Query String for GET
  GET.../wms/lgfapi/v10/print/label/pallet/?
  label_designer_code=foo&facility_id**code=FAC1&company_id_code=COM1&pallet_nbr=pallet1
  Example Request Body for POST
  {
  "parameters": {
  "facility_id**code": "FAC1",
  "company_id\_\_code": "COM1",
  "pallet_nbr": "pallet1"
  },
  "options": {
  "label_designer_code": "label_1",
  "printer_name": "PRINTER1"
  }
  }
  Response Body Data
  On success, a 200 - OK status is returned
  For a GET request, the ZPL data bill be base64 encoded in the "data" section.
  {
  "success_count": 1,
  "failure_count":0,
  "data": {
  "OBLPN_1": "VGhpcyBpcyBaUEwgY29kZQ=="
  }
  }
  Print OBLPN Packing Slip
  This API allows you to print packing slips for one or more OBLPNs to a specified printer from an external system (such
  as Material Handling Equipment (MHE.)
  URLs
  POST .../wms/lgfapi/v10/print/document/oblpn_packing_slip
  GET.../wms/lgfapi/v10/print/document/oblpn_packing_slip/doc_designer_code=foo
  182

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Parameters
Category Name Type Required Comments
options doc*designer_code string C Document template
to be printed.
options web_report_path string C This field is
mandatory. the path
for the web report
template.
options web_report_format string C This field is
mandatory. the file
format of the report
xls/csv/pdf
options printer_name string Defaults to
cwuser.default*
document_printer.
options document_count integer Number of
documents to print.
Must be greater
than 0. Default = 1.
Example Request Body - Web Reports
{
"parameters": {
"facility_id**code": "LW_FAC",
"company_id**code": "LW_COMP",
"container_nbr**in" : "OBLW_LWCOMP123"
},
"options": {
"web_report_path" : "ABC/OBLPNPackingList",
"web_report_format" : "pdf",
"printer_name": "ABCDOC",
"document_count": 1
}
}
Note: Web Reports will only work for PDF format.
Example Request Body - Label Designer
{
"parameters": {
"facility_id**code": "LW_FAC",
"company_id\_\_code": "LW_COMP",
"container_nbr": "OBLPN11212402"
183

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
},
"options": {
"doc*designer_code": "Packing_Slip_180_DPI_TOP_LW_COMP",
"printer_name": "ABCDOC",
"document_count": 1
}
}
Print Order Packing Slip
The Order Packing Slip API allows you to print pallet packing slips. Note that this API will not do any template
determination logic as seen in the UI. Doc designer code is required as part of the API parameters. Any determination
would need to be done in the outside system.
This API supports the following HTTP methods:
• GET - Returns the ZPL representation of the document.
• HEAD - only supports checking if the object exists since lookup models don't have create_ts.
• POST - Submits the document for printing.
URLs
POST.../wms/lgfapi/v10/print/document/order_packing_slip
GET.../wms/lgfapi/v10/print/document/order_packing_slip/?doc_designer_code=foo
Parameters
Category Name Type Required GET Request POST Request Comments
options doc_designer_code string X X X Document template
to be printed
options web_report_path string X X This field is
mandatory. the path
of the web report
template
options web_report_format string X X This field is
mandatory. the file
format of the report
xls/csv/pdf.
options printer_name string X Defaults to
cwuser.default*
document_printer.
options document_count integer X Number of
documents to print.
Must be greater
than 0. Default = 1.
184

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Print Pallet Packing Slip
The Pallet Packing Slip API allows you to print pallet packing slips. Note that this API will not do any template
determination logic as seen in the UI. Doc designer code is required as part of the API parameters. Any determination
would need to be done in the outside system.
This API supports the following HTTP methods:
• GET - Returns the ZPL representation of the document.
• HEAD - only supports checking if the object exists since lookup models don't have create*ts.
• POST - Submits the document for printing.
URLs
POST .../wms/lgfapi/v10/print/document/pallet_packing_slip
GET.../wms/lgfapi/v10/print/document/pallet_packing_slip/?doc_designer_code=foo
Parameters
Category Name Type Required POST Request Comments
options web_report_path string X X This field is
mandatory. This is
the path of the web
report template.
options web_report_format string X X This field is
mandatory. the file
format of the report
xls/csv/pdf
options printer_name string Defaults to
cwuser.default*
document_printer.
options document_count integer Number of
documents to print.
Must be greater
than 0. Default = 1.
Putaway
These topics give descriptions for APIs that complete actions related to putaway in the Warehouse.
185

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Putaway Priority
This operation allows you to determine the order in which Putaway Types are triggered for putaway.
POST .../entity/putaway_priority
If you have a new facility and you want to copy the same Putaway Priority rules from your current facility, you can first
GET the list by querying the putaway_priority entity, then POST the applicable data to this operation for the target
facility.
Name Required Type Default Description
facility_id Integer Facility context by id.
Priority Integer Priority
putaway_type_id Integer Putaway Type ID
putaway_method_id Integer Putaway Method ID
putaway_search_mode_id Integer Putaway Search Mode ID
locn_type_id Integer Location Type ID
locn_size_type_id Integer Location Size Type ID
replenishment_zone_id Integer Replenishment Zone ID
consider_fefo_flg boolean Yes enables consider fefo
flg
storage_priority_id

Integer • "1” indicates "Less
than or equal to
priority date" and
• "2” indicates "Greater
than or equal to
priority date"

radius Integer Radious
radial_increment Integer Radial Increment
Example body request:
{
"fields": {
"facility_id": 1,
"priority": 1,
"putaway_type_id": 256860,
"putaway_method_id": 1,
"putaway_search_mode_id": 0,
186

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"locn_type_id": 3,
"locn_size_type_id": 0,
"replenishment_zone_id": 35995,
"consider_fefo_flg”:false,
“storage_priority_id”
"radius": 1,
"radial_increment": 1
}
}
Directed Putaway Location
The Directed Putaway Location API now allows you to determine the putaway location for a given Inbound LPN or
Pallet via a POST request, so that you can locate the LPN/Pallet to its respective destination.
You can determine the putaway location for an IBLPN using the following POST request:
POST .../entity/iblpn/directed_putaway_location/

Parameters
Name Required Type Default Description
facility_id Integer Facility context by id.
facility_id\_\_code String Facility context by code.
company_id Integer Company context by id.
company_id_code String Company context by code.
container_nbr X String
You can determine the putaway location for a pallet using the following POST request:
POST .../entity/pallet/directed_putaway_location/

NOTE: Oracle WMS Cloud will check the putaway type associated with the IBLPN/ Pallet and check the respective
putaway method priority configured for the putaway type. The system then determines the putaway location honoring
the putaway method priority rule.
187

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Parameters
Name Required Type Default Description
facility*id Integer Facility context by id.
facility_id\_\_code String Facility context by code.
company_id Integer Company context by id.
company_id_code String Company context by code.
pallet_nbr X String
Request Options Parameters
Name Required Type Default Description
recalculate_putaway_type*
flg
Boolean False
validate*critical*
dimensions_flg
Boolean False
Example Request
POST .../entity/iblpn/directed_putaway_location/
{
"parameters": {
"container_nbr": "LPNPTW0102"
},
"options": {
"recalculate_putaway_type_flg": false,
"validate_critical_dimensions_flg": false
}
}
POST .../entity/pallet/directed_putaway_location/
{
"parameters": {
"pallet_nbr": "LPNPTW0102"
},
"options": {
"recalculate_putaway_type_flg": false
}
}
Putaway Type
POST .../entity/putaway_type
This operation is used to add single or multiple putaway type.
If you have a new facility and you want to copy the same putaway type from your current facility, you can first GET the
list by querying the putaway_type entity, then POST the applicable data to this operation for the target facility.
188

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Example body request:
{
"fields": {
"company_id": 1,
"pa_type": "TEST_PA_001",
"description": "Test PA 001",
"pallet_position_required_flg": false,
"depalletize_on_putaway_flg": false
}
}
Putaway Type Calculation Rule
POST .../entity/putaway_type_calc_rule
This operation is used to add single or multiple putaway type cal rules.
If you have a new facility and you want to copy the same putaway type cal rule from your current facility, you can first
GET the list by querying the putaway_type_cal entity, then POST the applicable data to this operation for the target
facility.
Example body request:
{
"fields": {
"facility_id": 1,
"company_id": 1,
"description": "TEST-001",
"priority": 1,
"final_putaway_type_id": 256860,
"sql_selection_id": 76886,
"enabled_flg": true
}
}
189

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Repack
The Repack APIs allow you to repack Outbound LPNs (or temporary totes) that are in Picked status to destination
OBLPNs and move them into Packed status using the Pack Inventory API follow by the Close LPN API.
Pack Inventory
The Pack Inventory API allows you to pack inventory based on the source OBLPN (from OBLPN), item, quantity and the
destination OBLPN (to OBLPN) information you send. In repack pack inventory, the system currently allows sending
only one packing detail per request.
URL
POST.../lgfapi/v10/repack/pack_inventory
Request Level Parameters
Name Required Type Default Description
facility_id Integer Facility context by id
facility_id**code String Facility context by code
company_id Integer Company context by id
company_id**code String Company context by code
restrict_multiorder_combine_flg Boolean False When 'False', destination
OBLPN can be repacked
from source OBLPNs
having different orders.

When 'True', destination
OBLPN can't be repacked
from source OBLPN
having different orders
and the destination
OBLPN will always have
inventory corresponding
to a single order

suppress_serial_warning_flg Boolean True When 'True', system will
not validate serial number
validations that are of
type warning

190

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Required Type Default Description
When 'False', both
validations of type
warning and error will be
treated as errors

from_oblpn_nbr X String OBLPN/temporary
tote that is going to be
repacked.

item_alternate_code C string Item identifier
item_barcode C string Item identifier
qty X number 0 If short_flg is false,
Quantity to be packed
into destination OBLPN
from source OBLPN

If short_flg is true,
Quantity to be shorted in
source OBLPN

allocation_uom string "UNITS", "PACKS",
"CASES", LPNS"
uom_qty number Provides the inventory/
standard pack qty or case
qty when allocation_uom
is 'PACKS' or 'CASES'
Gor FULL LPN type:
quantity can be <= to
the total quantity of the
source OBLPN, since
user may be packing into
multiple to OBLPNs.

batch_nbr C string Inventory batch/lot -
should be provided if the
inventory to be packed
has batch number
expiry_date C date Expiry date of inventory
present in the picked
OBLPN (From OBLPN).
Format - YYYY-MM-DD.
Should be provided if the
191

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Required Type Default Description
inventory to be packed
has expiry date
invn_attr_a to

invn_attr_o

C string Inventory attributes
A to O specified on
the inventory. Should
be provided if the
inventory to be packed
has inventory attributes
serial*nbr_list C list List of serial numbers
for the inventory packed
(single SKU can have
multiple serial numbers)
to_oblpn_nbr X string Destination OBLPN where
contents are going to
be packed into. The "to*
oblpn*nbr" will be the
new destination OBLPN
that will be substituted
in place of the "orig_to*
oblpn*nbr"
orig_to_oblpn_nbr string This field will be used
for substitution of
destination OBLPN (to
OBLPN.) The orig_to*
oblpn_nbr" will be the
final OBLPN number that
has been suggested by
the system and will be the
OBLPN that is going to be
substituted
to_oblpn_lpn_type string LPN Type for the
destination OBLPN (to
OBLPN)
packing_station_barcode string Packing station location
identifier, location
barcode to be provided.
short_flg Boolean False short_flg = false; quantity
provided will be Packed.

short_flg= true; quantity
provided will be shorted.

• Destination OBLPN (to OBLPN) is updated to status “In Packing”
192

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
• System reduces the packed quantity for the source LPN based on the quantity packed
• System increases the packed quantity for the destination OBLPN based on the quantity packed
• IHT 10 container detail packed is written for the destination OBLPNs being packed
• IHT 85 order detail status change and IHT 20 order status change is written for the orders associated with the
OBLPNs that are being packed
• If the complete source OBLPN is packed into destination OBLPN, the source OBLPN is moved into cancelled
status and IHT 32 OB container cancelled is written for the source OBLPN
• Based on the Expiry Date/inventory attribute/batch number values passed in the request, system packs the
respective inventory from the source OBLPN into destination OBLPN
• If OBLPN type is provided, destination OBLPN must be updated with that LPN type, volume for the OBLPN is
calculated based on the LPN type dimensions and the existing dimensions for the OBLPN are cleared
• WMS activity is written for the packing activity being done
Sample JSON Request
{
"facility_id\_\_code": "FAC",
"company_id": 1,
"restrict_multiorder_combine_flg": True,
"from_oblpn_nbr": "TMPOBLPN0001",
"item_alternate_code": "ITEM0001",
"qty": 5,
"batch_nbr":"B1",
"expiry_date": "2024-02-24",
"invn_attr_a" : "TESTA",
"invn_attr_b" : "TESTB",
"invn_attr_c" : "TESTC",
"invn_attr_d" : "TESTD",
"invn_attr_e" : "TESTE",
"invn_attr_f" : "TESTF",
"invn_attr_g" : "TESTG",
"invn_attr_h" : "TESTH",
"invn_attr_i" : "TESTI",
"invn_attr_j" : "TESTJ",
"invn_attr_k" : "TESTK",
"invn_attr_l" : "TESTL",
"invn_attr_m" : "TESTM",
"invn_attr_n" : "TESTN",
"invn_attr_o" : "TESTO",
"to_oblpn_nbr": "OBLPN0001",
"to_oblpn_type": "KNMEDBOX1",
"packing_station_barcode": "KNP0101",
"short_flg": false
}
Shorting
If Short flag is set to True, then it should allow:
• Source OBLPN provided by user is considered for shorting
• User must provide source OBLPN, item and quantity to be shorted in the request
• Currently, we are not planning to provide an option for shorting all remaining contents in the source OBLPN
(this is to avoid concurrency issues during multiple API requests).
• If the inventory to be shorted has inventory attributes/batch number/expiry date - the respective values should
also be provided during shorting, so that the system is aware of exact inventory to be shorted
193

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Sample JSON Request
{
"facility_id**code": "FAC",
"company_id": 1,
"from_oblpn_nbr": "TMPOBLPN0002",
"item_alternate_code": "ITEM0001",
"qty": 2,
"to_oblpn_nbr": "OBLPN0002",
"short_flg": true
}
• In the sample request above, once the request is successfully processed, "TMPOBLPN0002" OBLPN will be
shorted by 2 units for "ITEM0001."
Serial Number Support
Serial number is supported during packing through Repack API. This tells you which serial number inventory is packed
in the respective request sent. In your request you can send a serial number list. Sending serial numbers during repack
API is not mandatory.
"suppress_serial_warning_flg" - this flag helps users bypass warnings validations and improve speed of packing
validations. The default of this flag is True, but if you want to be strict about these validations, you can set flag as 'False'.
Note: New serial numbers are allowed irrespective of whether company parameter
SERIAL_NUMBER_TRACKING_LEVEL is set to '1' and '2'.
Sample Request with Serial Number:
{
"facility_id**code": "FAC",
"company_id": 1,
"from_oblpn_nbr": "TMPOBLPN0001",
"item_alternate_code": "ITEM0001S",
"qty":3,
"serial_nbr_list": [ <== Single Inventory can have multiple serial numbers.
"SLN1",
"SLN2",
"SLN3" ],
"to_oblpn_nbr": "OBLPN0001",
"short_flg": false
}
Track User Activity
If you have purchased WFM (Oracle Workforce Management), you can also send user activity data using the following
parameters in the Pack Inventory API
• Screen_name: Name of the application or screen in the external system that was used by the user to repack
OBLPN.
• Begin_ts: Time at which the user started repacking the OBLPN.
• End_ts: Time at which the user completed the repack.
If all the three parameters are sent in the API, and if WFM is enabled, user activity is written to the WMS Activity view
and subsequently interfaced to WFM, enabling you to analyze user productivity through productivity reports in WFM.
194

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Note:
• All three parameters must be sent for WMS Activity to be written.
• If WFM is not enabled, WMS Activity is not written even if the three parameters are sent.
• In order for WMS Activity data to interface successfully to WFM, screen_name that is sent in the API has to be
configured as a screen in WMS using an RF module and mapped to a work area activity in WFM.
• Screen_name sent on the API is also written on the corresponding IHTs that are written with this API.
• If only screen_name is sent without begin_ts and end_ts, the screen_name is written on the IHT, even if WFM is
not enabled.
• Begin_ts and End_ts cannot be greater than the current timestamp of the facility in the API.
• WMS Activity is not written if short_flg is true.
Request Body with User Activity Data
{
"facility_id": 101,
"company_id": 102,
"from_oblpn_nbr": "TMPOBLPN0001",
"item_alternate_code": "ITEM0001",
"qty": 5,
"to_oblpn_nbr": "OBLPN0001",
"begin_ts": "2024-05-27T18:30:00",
"end_ts": "2024-05-27T18:45:00",
"screen_name": "Repack OBLPN Screen"
}
Close LPN
The Repack Close LPN API allows you to close the destination OBLPN (to OBLPN), based on the OBLPN information you
send. This API is the second step to be done after you are done packing your inventory.
URL
POST.../lgfapi/v10/repack/close_lpn
The Repack Close LPN API allows you to:
• Close the destination OBLPN (to OBLPN) once packing is complete and move the OBLPN to 'Packed' status.
• Define an LPN type for destination OBLPN (to OBLPN), and update the volume based on the LPN type
• Define a delay for processing the request to end OBLPN.
195

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
• When you do a repack for OBLPNs as a part of mode 3 cubing flow, the final OBLPN numbers are already
decided by the system. But if you want to prematurely close the system suggested OBLPN, you can do so by
closing the current OBLPN but mention the new OBLPN to be considered in place of the current OBLPN in the
"new*to_oblpn_nbr" field.
Parameters
Name Required Type Default Value Description
facility_id Integer Facility context by id
facility_id**code string Facility context by code
company_id Integer Company context by id.
company_id**code string Company context by code.
to_oblpn_nbr X string Destination OBLPN where
contents were packed and
is about to be closed
new_to_oblpn_nbr string This field will be used for
substitution of destination
OBLPN (to OBLPN),
to_oblpn_lpn_type string LPN Type for the the
destination OBLPN (to
OBLPN)
The field "to_oblpn_lpn*
type" works together with
"new_oblpn_nbr". and this
oblpn_type is applicable
only for the new_oblpn_nbr
which is getting created as
part of Repack Close LPN
API. This is applicable only
during substitution.

Note: when the user
does a repack for
OBLPNs as a part of a
mode 3 cubing flow, the
final OBLPN numbers
are already decided by
the system.

If the user wants to
prematurely close the
system suggested
OBLPN, they need to
close the current OBLPN
and mention the new
OBLPN to be considered
in place of the current
OBLPN in the "new*to*
oblpn_nbr" field.

• Destination OBLPN (to OBLPN) is updated to status “Packed.”
196

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
• Respective order and order detail associated with the OBLPN is updated to status “Packed.”
• IHT 11 container packed is written for the destination OBLPNs being packed.
• IHT 85 order detail status change and IHT 20 order status change is written for the orders associated with the
OBLPN.
• If OBLPN type is provided, the destination OBLPN must be updated with that LPN type, the volume for the
OBLPN should be calculated based on the LPN type dimesions, and the existing dimensions for the OBLPN are
cleared.
Example Request Body
{
"facility_id\_\_code": "FAC",
"company_id": 1,
"to_oblpn_nbr": "OBLPN0001",
"to_oblpn_lpn_type": "KNMEDBOX1"
}
Replenishment
These topics give descriptions for APIs that complete actions related to Replenishment in the Warehouse.
Replenish to Active
The replenish_to_active API allows you to complete an open replenishment task for an active location.
You can replenish to active with the following POST request:
POST .../lgfapi/v10/replenishment/replenish_to_active/

Note: The Replenish to Active API is recommended only for Full LPN Resplenishment Task Types. . This API has
limited capabilities and may be deprecated in a future release. Consider using the Full LPN API.
Parameters
The following table provides details about the Input Parameters/Filters:
Name Required Type Default Description
facility_id integer Facility context by id.
facility_id**code string Facility context by code.
company*id integer Company context by id.
company_id***code string Company context by code.
197

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
• Used if the replenishment is in a context other than the requesting user's default.
• The requesting user's default facility/company context will be assumed if values are not provided.
• Either "facility_id" or "facility_id**code" may be used, but not both.
• Either "company*id" or "company_id***code" may be used, but not both.
The following table details the functional options:
Name Required Type Default Description
task_id C integer "id" of task to be
completed.
task_id**task_nbr C string Business key for task to be
completed.
replen_location_id C integer "id" of active location to be
replenished.
replen_location_id**
barcode
C string Barcode of active location
to be replenished
qty decimal Allocation Qty Quantity to replenish.
• Either "task_id" or "task_id**task_nbr" is required.
• Either "replen_location_id" or "replen_location_id**barcode" is required.
• If 'qty' is not provided, the full allocation quantity of the associated allocation will be used.
◦ If 'qty' is provided, it must be greater than 0.
The following is an example body for Replenish Location ID Barcode:
{
"facility_id": 1,
"company_id_code": "COMPANY",
"task_id": 1,
"replen_location_id\_\_barcode": "LOCN1"
}
Track User Activity
If you have purchased WFM (Oracle Workforce Management), you can also send user activity data using the following
parameters in the Replenish to Active API
• Screen_name: Name of the application or screen in the external system that was used by the user to complete
the open replenishment task.
• Begin_ts: Time at which the user started executing the task.
• End_ts: Time at which the user completed the task.
If all the three parameters are sent in the API, and if WFM is enabled, user activity is written to the WMS Activity view
and subsequently interfaced to WFM, enabling you to analyze user productivity through productivity reports in WFM.
198

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Note:
• All three parameters must be sent for WMS Activity to be written.
• If WFM is not enabled, WMS Activity is not written even if the three parameters are sent.
• In order for WMS Activity data to interface successfully to WFM, screen_name that is sent in the API has to be
configured as a screen in WMS using an RF module and mapped to a work area activity in WFM.
• Screen_name sent on the API is also written on the corresponding IHTs that are written with this API.
• If only screen_name is sent without begin_ts and end_ts, the screen_name is written on the IHT, even if WFM is
not enabled.
• Begin_ts and End_ts cannot be greater than the current timestamp of the facility in the API.
Request Body with User Activity Data
{
"facility_id": 1,
"company_id_code": "COMPANY",
"task_id": 1,
"replen_location_idbarcode": "LOCN1",
"begin_ts": "2024-05-27T18:30:00",
"end_ts": "2024-05-27T18:45:00",
"screen_name": "Replen To Active Screen"
}
Replenishment Zone
POST .../entity/replenishment_zone
This operation is used to add one or more replenishment zones.
If you have a new facility and you want to copy the same replenishment zones from your current facility, you can first
GET the list by querying the replenishment_zone entity, then POST the applicable data to this operation for the target
facility.
Example Body Request
{
"fields": {
"facility_id": 1,
"code": "TEST_RZ_001",
"description": "Test RZ 001"
}
}
199

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Move LPN
The Move LPN API allows you to facilitate the initial movement of the Replenishment process which will move the
LPN(s) from a source location to a drop location.
Note: This REST API will only support Full LPN replenishment allocations.
You can perform Move LPN with the following POST request:
Post Request : POST .../lgfapi/v10/replenishment/move_lpn

Request Body
{
"location": "AAAAA",
"move": [
{ --normal full LPN pick
"facility_id__code": "CM101",
"company_id__code": "CM_COMP",
"from_container_nbr": "CNTST0100031583",
"pallet_nbr": "IBLPN123",
"mhe_system_code": "AGV",
"short_flg": "False",
"update_invn_onshort": "No"
},
{-- full LPN shorting pick
"facility_id__code": "CM101",
"company_id__code": "CM_COMP",
"from_container_nbr": "CNTST0100031584",
"pallet_nbr": "IBLPN123",
"mhe_system_code": "AGV2",
"short_flg": "True",
"default_reason_code": "reason2",
"update_invn_onshort": "yes"
},
{ -- full LPN substitution
"facility_id__code": "CM101",
"company_id__code": "CM_COMP",
"from_container_nbr": "CNTST0100031583",
"sub_container_nbr": "CPOBLPN0106",
"pallet_nbr": "IBLPN123",
"mhe_system_code": "AGV",
"short_flg": "False",
"update_invn_onshort": "No"
}
]
}
Note: If shorting using the “short_flg” set to True, you have the option to provide a default reason code with a valid
reason code, and update_invn_on short to make sure the correct update happens to the inventory and the location in
the parameter must be a drop location.
200

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Full LPN
The Full LPN Replenishment API allows you to send Replenishment information for a Full LPN.
POST .../lgfapi/v10/replenishment/full_lpn
Request Parameters
Name Required Type Default Description
mhe_mode_flg Boolean Facility context by id.
async_flg Boolean Facility context by code.
Replenishment List
Name Required Type Default Description
facility_id**code String Facility context by code.
company*id***code String Company context by code.
replen_wave_nbr x String Associated replenishment
wave.
from_container_nbr x String From container number
sub_container_nbr Optional String Substitution container
number
mhe_system_code Optional String MHE system.
short_flg Boolean False is this a short?
Request JSON Example
"mhe_mode_flg": true,
"async_flg": true,
"replenishment_list": [{
"facility_id__code": "QATST01",
"company_id__code": "QATSTPC",
"replen_wave_nbr": "WVQATSTPC072935",
"from_container_nbr:"CNTST0100031583",
"sub_container_nbr": "CPOBLPN0106",
"mhe_system_code": "picktolight",
"short_flg": false },
{ "facility_id__code": "QATST01",
"company_id__code": "QATSTPC",
"replen_wave_nbr": "WVQATSTPC072935",
"from_container_nbr¿:"CNTST0100031584",
"sub_container_nbr": "CPOBLPN0126",
"mhe_system_code": "picktolight",
"short_flg": false }]
201

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
}
Report
These topics give descriptions for APIs that complete actions related to Reporting in the Warehouse.
Customer Inventory Summary
Allows you to execute the customer inventory summary report for only a single item per request. This request returns
the result set as a file attached to the response.
If output format is pipe-delimited, use the following:
GET.../report/custom_inventory_summary/?facility_id**code=FAC1&company_id_code=COM1&item_code=ITEM1
If the output format is XML use the following:
GET.../report/custom_inventory_summary.xml?
item_code=<item_code>&company_id=<company_id>&facility_id=<facility_id>
The following “parameters” are required:
Parameter Type Required Default Description
facility_id integer C Required facility context.
facility_id**code string C Required facility context.
company_id integer C Required company context.
company_id_code string C Required company context.
item_code string X Specific item for the report.
write_header_line_flg boolean False Include the header line with
field names?
• Either `facility_id` or `facility_id__code` is required
• Either `company_id` or company_id_code` is required
Dock to Stock Per Day
The Dock to Stock Per Day API provides valuable insights into your shipment processes. With this API, you can now
easily monitor and optimize the time it takes for your shipments to go from the receiving dock to the stock location.
This API will generate a report on the dock-to-stock time for shipments received and put away in the past seven days.
The report provides you a daily average, offering a general overview and valuable insights into your operations.
202

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
URL
GET /report/dock_to_stock_per_day/
Available Filters
Name Required Type Description
company_id C String Company ID
facility_id C String Facility ID
company_id**code C String Company Code
facility_id**code C String Facility Code
Dock to Stock Per Shipment
The Dock to Stock per Shipment API offers you detailed insights into your shipment processes. This API provides a
report with a view of the time taken for each shipment's journey from the receiving dock to the stock location.
With this API, you can easily access and analyze data for shipments received and put away within the past seven days.
The report generated will present the dock-to-stock time for each shipment, along with a daily average, giving you a
clear and concise overview.
URL
GET /report/dock_to_stock_per_shipment/
Available Filters
Name Required Type Description
company_id C String Company ID
facility_id C String Facility ID
company_id**code C String Company Code
facility_id**code C String Facility Code
Sales Order Header
These topics give descriptions for APIs that complete actions related to Sales Orders in the Warehouse.
203

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
GET IBLPN(s)
GET …/wms/lgfapi/v10/entity/order_hdr/{id}/iblpns/
Returns a paginated representation of all IBLPN(s) allocated to the sales order.
GET OBLPN(s)
GET …/wms/lgfapi/v10/entity/order_hdr/{id}/oblpns/
Returns a paginated representation of all OBLPN(s) allocated to the sales order.
Bulk Lock
POST …/wms/lgfapi/v10/entity/order_hdr/bulk_lock/
This operation is used to apply, and optionally create, an order lock to one or more orders.
The number of orders that can be modified by this operation in a single requests is configured by the value of the
requesting user’s “Rows per Page” attribute.
The “parameters” section of the request body is required in addition to the “options” section outlined below. One
or more parameters are used to determine the order(s) for which the operation will be applied. The allowed filter
parameters are:
• 'id'
• 'order_nbr'
• 'facility_id'
• 'company_id'
• 'erp_source_hdr_ref'
• 'erp_source_system_ref'
• 'orderdtl**erp_source_line_ref'
• 'orderdtl**erp_source_shipment_ref'
• 'orderdtl\_\_ship_request_line'
Category Parameter Type Required Default Value Description
options lock_code String X Order lock to be
applied.
options lock_description String Value of lock_code Description of order
lock. Only used when
creating a new order
lock.
options comments String “” Additional info for the
order’s applied lock.
204

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Category Parameter Type Required Default Value Description
options allow_allocate_flg Boolean False Order lock attribute.
Only used when
creating a new order
lock.
options autocreate_lock_flg Boolean False When true, the order
lock will be created in
addition to be applied,
if it does not already
exist.
options commit_frequency Integer 0 0 = Roll back on first
error.

1 = Commit per object.

Bulk Unlock
POST …/wms/lgfapi/v10/entity/order_hdr/bulk_unlock/
This operation is used to remove an order lock from one or more orders.
The “parameters” section of the request body is required in addition to the “options” section outlined below. One
or more parameters are used to determine the order(s) for which the operation will be applied. The allowed filter
parameters are:
• 'id'
• 'order_nbr'
• 'facility_id'
• 'company_id'
• 'erp_source_hdr_ref'
• 'erp_source_system_ref'
• 'orderdtl**erp_source_line_ref'
• 'orderdtl**erp_source_shipment_ref'
• 'orderdtl\_\_ship_request_line'
Category Parameter Type Required Default Value Description
options lock_code String X Order lock to be
removed.
options commit_frequency Integer 0 0 = Roll back on
first error.

1 = Commit per
object.

205

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Remove Personal Info
This operation is used to remove personal information on selected orders. This is the API form of the UI action button
“Remove Personal Info”
POST .../wms/lgfapi/v10/entity/order_hdr/remove_personal_info
POST .../wms/lgfapi/v10/entity/order_hdr/{id}/remove_personal_info
Request Parameters
Parameters (Filters)
Only applicable when `id` is not present in the URL.
Name Required Type Default Description
facility_id C Integer Facility context by id.

one of id or code should be
provided

facility_id\_\_code C String Facility context by code.

one of id or code should be
provided

company_id C Integer Company context by id.

one of id or code should be
provided

company_id\_\_code C String Company context by code.

one of id or code should be
provided

order_nbr

OR

order_nbr\_\_in

C String Order/Orders for which PI
needs to be removed.

one of id or order_nbr
should be provided.

206

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Required Type Default Description
id

OR

id\_\_in

C ID or IDs of Orders for
which PI needs to be
removed.

one of id or order_nbr
should be provided.

• If facility and/or company are provided, set login context accordingly.
• Only one of `facility_id` or `facility_id__code` may be provided.
• Only one of `company_id` or `company_id__code` may be provided.
Example:
URL: POST .../wms/lgfapi/v10/entity/order_hdr/remove_personal_info
{
"parameters": {
"facility_id**code": "FAC",
"company_id": 1,
"order_nbr": "ORD1"
}
}
Request sent with an ID:
{
"parameters": {
"facility_id**code": "FAC",
"company_id": 1,
"id": 123
}
}
Or for multiple orders:
{
"parameters": {
"facility_id**code": "FAC",
"company_id": 1,
"order_nbr**in": ["ORD1","ORD2","ORD3"]
}
}
Request sent with IDs:
{
"parameters": {
"facility_id**code": "FAC",
"company_id": 1,
"id**in": [123, 124, 126]
}
}
207

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Update Parcel Shipment Info
In order to support parcel shipments from Oracle Transportation Management (OTM) this API allows you to associate
WMS orders with the appropriate ship-via and OTM's planned shipment number.
POST ..lgfapi/v10/order_hdr/update_parcel_shipment_info/
Validations
• Order status must be < LOADED.
Parameters
These input field values may be updated by the user on the matching order_hdr.
• ship_via_code
◦ Lookup ship via using the ship_via_code.
• tms_parcel_shipment_nbr
• tms_order_hdr_ref
SQL Selection (Rule Tree)
POST .../entity/sql_selection
This entity is unique in that the API will allow the user to create the entire rule tree in a single request instead of needing
the create and link each parent/child object individually (it can still be done this way if the user chooses to do so). This
is accomplished using the `children` list field. This is an abstract field that does not exists on the object itself, but rather
defines the `parent_id` link, which will be handled by the API automatically.
To illustrate a complex example, the following request body could be used to create this rule structure as seen from the
UI:
Example Body Request
{
"fields": {
"facility_id": 1,
"sql_operator_id": 2,
208

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
"children": [
{
"column_name_id": 107,
"sql_operator_id": 5,
"column_value": "B"
},
{
"sql_operator_id": 1,
"children": [
{
"column_name_id": 1379,
"sql_operator_id": 7,
"column_value": "100"
},
{
"column_name_id": 35,
"sql_operator_id": 7,
"column_value": "50"
}
]
}
]
}
}
Sort and Receive
The topics in this section give descriptions for APIs that complete actions related to Sort and Receive transactions in the
Warehouse.
Validate Receiving Station
The Validate Receiving Station API allows you to validate if the location type is a Receiving Station or not.
URL
POST ..lgfapi/v10/sort_receive/validate_receiving_station
Example Response
POST ..lgfapi/v10/sort_receive/validate_receiving_station
{
"parameters": {
"receiving station" : location_barcode
}
209

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Validate Shipment
The Validate Shipment API allows you to validate the shipment number during the sort and receive transaction.
URL
POST ..lgfapi/v10/sort_receive/validate_shipment
Example Response
POST ..lgfapi/v10/sort_receive/validate_shipment
{
"shipment number" : "12345"
}
Note: On successfully response, the validate_shipment API returns Shipment Number, ASN type, Dock Number, and
Trailer Number.
Validate Load
The Validate Load API allows users to validate a load as required for the Sort and Receive transaction.
URL
POST ..lgfapi/v10/sort_recieve/validate_load
Example Response
POST ..lgfapi/v10/sort_recieve/validate_load
{
"load_nbr" : "12345"
}
Note: On successfully response, the validate_load API returns Dock Number, Trailer Number, Load Number.
Receive Sorted Item
The Receive Sorted Item API allows you to receive an item into a receiving station location during the Sort and Receive
transaction.
210

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
URL
POST ..lgfapi/v10/sort_recieve/receive_sorted_item
Example Payload
{
“location_barcode”:“LOC001”,
“ib_shipment_dtl_id”:1234,
“iblpn_nbr”:"LPN001”,
“qty”:1
}
End LPN
The End LPN API allows users to end a tote during the Sort and Receive transaction.
URL
POST ..lgfapi/v10/sort_recieve/end_lpn
Example Response
{
"container_nbr": "LPN0001",
"location_barcode": "LOCN0001",
"lock_code_list": [ "LOCK0001", "LOCK0002" ]
}
Parameters
Name Type Required Description
container_nbr String Y Container number
location_barcode String Y Location barcode for receiving
station
lock_code_list Array N Array of lock codes
Get Directed Tote
The Get Directed Tote API allows users to get directed tote for Sorting and Receiving.
211

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
URL
POST sort_receive/get_directed_tote
Example Request Body
{
"location_barcode": "LOCN0001",
"attributes_map": {"batch_nbr" : foo, "attr_a": bar, "attr_d": spam},
"ib_shipment_dtl_id": 255,
"qty": 10
}
Parameters
Name Type Required Default Description
location_barcode String Y Location barcode
attributes_map Object N Attribute values (including
batch & expiry)
ib_shipment_dtl_id Integer Y IbShipment detail ID
qty Integer or Number? N 1
Validate Expiry Date
The Validate Expiry Date API allows you to validate the expiry date during Sorting and Receiving.
URL
POST entity/ib_shipment_dtl/validate_expiry_date
Example Request Body
{
"container_nbr": {}"LPN0001"
} options:{
"shipment_nbr": {}"ASN0001",
"expiry_date": {}"2024-04-19"
}
212

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Parameters
Name Type Required Description
container_nbr String Y Container number
shipment_nbr String N Shipment number
load_nbr String N Load number
expiry_date Date C Expiry date
manufacture_date Date C Manufacture date
ib_shipment_dtl_id Integer N Inbound shipment detail ID
T ask
These topics give descriptions for APIs that complete actions related to tasks in the Warehouse.
Next T ask
The next_task API allows you to determine the next task via an API operation.
You can search for the next task using the following GET request:
GET .../entity/task/next_task

The following table provides details about the query string parameters:
Name Required Type Default Description
facility_id Integer Facility context by id.
facility_id\_\_code String Facility context by code.
location_barcode String User's current location.
task_type String Required task type.
ordering_rule String Order tasks by rule name.
Facility ID/Facility Code
• If a value isn't provided, the user's default facility context will be used.
• T ask look up is done relative to the user's facility and eligible company contexts.
213

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Location Barcode
• If provided, search for task within the same location area (if available) and/or pick sequence (if available).
Task Type
• If provided, search for task only of the given type.
Ordering Rule
• If provided, order the found tasks by the corresponding field(s) and return the top result.
• The value accepted by the API is that of the T ask Ordering Rule's description.
The following is an example GET request using location barcode:
GET .../entity/task/next_task?location_barcode=MY_LOCN_BRCD&task_type=MY_TASK_TYPE&ordering_rule=MY_RULE
Hold T ask
The Hold T ask API allows you to hold a task which is in ready status. With this api, external systemd can change one
or more task statuses to ‘Held’ from ‘Ready’. You can exclude tasks that are not currently required to be executed by
the assigned user without accessing the web UI. Users who have the T ask/ Can hold/release task permission enabled
should be able to put a task on ‘Held’ status.
The following are some ways for calling the Hold task API:
Using the Task ID:
• POST.../entity/task/{id}/hold/
Note: No additional parameters data in the request body is required.
Using the Task Number:
• POST.../entity/task/hold/
Note: The API body should include facility id/code, company id/code and task number.
Using the Bulk Task Hold:
• POST.../entity/task/bulk_hold/
Note: The API body should task number list. Users can also provide the commit frequency as an option. The commit
frequency is by default set to 0. If it is set to 0, the system should roll back on first error/ If the commit frequency is set
to 1, the system will commit per object.
Category Name Required Type Description
parameters facility_id Integer Facility context by id
214

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Category Name Required Type Description
parameters facility_id**code string Facility context by code
parameters company_id Integer Company context by id
parameters company_id**code string Company context by code
parameters task_nbr X string T ask which needs to be on hold
Using the Bulk Hold T ask
POST.../entity/task/bulk_hold/
{
"parameters": {
"id\_\_in": [01, 02, 03]
},
"options": {
"commit_frequency": "0",
}
}
Note: The API body should task number list. Users can also provide the commit frequency as an option. The commit
frequency is by default set to 0. If it is set to 0, the system should roll back on first error/ If the commit frequency is set
to 1, the system will commit per object.
Release T ask
The Release T ask API allowd you to release a task which is in 'Held’ status. With this API, external systems can change
one or more task statuses to ‘Ready’ from ‘Held’. These tasks can be executed by the assigned user without accessing
the web UI. Users who have the T ask/ Can hold/release task permission enabled should be able to put a task on ‘Held’
status.
The following are some ways for calling the Release T ask API:
Using the Task ID:
POST.../entity/task/{id}/release/
Note: No additional parameters data in the request body is required.
Using the Task Number:
POST.../entity/task/release/
215

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Category Name Required Type Description
parameters facility_id Integer Facility context by id
parameters facility_id**code string Facility context by code
parameters company_id Integer Company context by id
parameters company_id**code string Company context by code
parameters task_nbr X string T ask which needs to be
released
Note: The API body should include facility id/code, company id/code and task number.
Using the Bulk Task Release:
POST.../entity/task/bulk_release/
Note: The API body should have the task number list. Users can also provide the commit frequency as an option.
The commit frequency is by default set to 0. If it is set to 0, the system should roll back on first error/ If the commit
frequency is set to 1, the system will commit per object.
The bulk request API allows you to release task ids belonging to the same company in a given request. The API will not
support a request containing task ids belonging to multiple companies.
Print Labels
You can print labels during Release T ask using the task/release and task/bulk_release APIs.
• By printing LPN labels when the task is being released, you can target printing labels for picking to specific
printers
• When you perform Release T ask via the T ask/Release API for tasks in Held status, the system should print
labels configured in the Column Ordering Rule.
The following parameters are added in both task/release and task/bulk_release API:
Category Name Type Description
parameter label_printer_name string printer context by name
parameter document_printer_name string printer context by name
parameter column_ordering string column ordering context by
description
Note: The system should return a success message when labels/doc are printed after tasks are released.
216

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Using the Bulk Release T ask
POST.../entity/task/bulk_release/
Request Body:
The transaction is meant for the task entity. Hence, the users are required to send the following parameters in the body.
POST.../entity/task/bulk_release/
{
"parameters": {
"id\_\_in": [01, 02, 03]
},
"options": {
"commit_frequency": "0",
}
}
Note: The API body should have the task number list. Users can also provide the commit frequency as an option.
The commit frequency is by default set to 0. If it is set to 0, the system should roll back on first error/ If the commit
frequency is set to 1, the system will commit per object.
The bulk request API allows you to release task ids belonging to the same company in a given request. The API will not
support a request containing task ids belonging to multiple companies.
Assign T ask
The new Assign T ask API allows you to assign a task to another user. For example, a task may require equipment
handling like a forklift. The warehouse manager can assign the task to a specific user who can handle a forklift with this
API without accessing the Web UI. However, you can assign a task with this API only if the T ask/ Assign User Permission
is enabled.
The following are some ways for calling the Assign T ask API:
Using the Task ID:
• POST.../entity/task/{id}/assign_user/
Options
Category Name Type Required Description
Options assigned_user string X user who is being assigned to the task
Note: You need to provide the ‘assigned_user’ in the request body as this is a post operation of tasks to assign users.
Using the Task Number:
• POST .../entity/task/assign_user/
217

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Category Name Required Type Description
parameters facility_id Integer Facility context by id
parameters facility_id**code string Facility context by code
parameters company_id Integer Company context by id
parameters company_id**code string Company context by code
parameters task_nbr X string T ask which needs to be updated
Options
Category Name Type Required Description
Options assigned_user string X user who is being assigned to the task
Note: The API body should include facility id/code, company id/code and task number. You are also required to
provide the ‘assigned_user’ in the request body as this is a post operation of tasks to assign users.
Using the Bulk Task Release:
• POST.../entity/task/bulk_assign_user/
POST.../entity/task/bulk_assign_user/
{
"parameters": {
"id\_\_in": [01, 02, 03]
},
"options": {
"assigned_user": "KHALL01",
"commit_frequency": "0",
}
}
Note: The API body should have the task number list. You are also required to provide the ‘assigned_user’ in the
request body. You can send the commit frequency as an option as well. The commit frequency is by default set to 0. If
it is set to 0, the system should roll back on first error/ If the commit frequency is set to 1, the system will commit per
object.
• If the status of one or more of the selected tasks goes to Processing Started, completed, In Drop between
Zones, Cancelled the return error and will not assign any user to the task.
• If task equipment and user equipment eligibility check fails for the assigned user, the API will return an error.
218

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Change Priority
The Change T ask Priority API allows you to change the priority of a task which is in Ready, Held or Created s status.
External systems can also change the task priority of one or more tasks based on the urgency of other tasks which
need to be executed on a priority. However, you can change the task priority with this API only if the T ask/ Change task
priority Permission is enabled.
The following are some ways for calling the Change task Priority API:
Using the Task ID:
• POST.../entity/task/{id}/change_priority/
Options
Category Name Type Required Description
Options priority integer X Priority code of the task (3, 20 etc)
Note: You need to provide the task priority in the request body as this is a post operation of tasks to change the task
priority.
Using the Task Number:
• POST .../entity/task/change_priority/
Category Name Required Type Description
parameters facility_id Integer Facility context by id
parameters facility_id**code string Facility context by code
parameters company_id Integer Company context by id
parameters company_id**code string Company context by code
parameters task_nbr X string T ask which needs to be updated
Options
Category Name Type Required Description
Options priority integer X Priority code of the task (3, 20 etc)
219

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Note: The API body should include facility id/code, company id/code and task number. You are also required to
provide the task priority in the request body as this is a post operation of tasks to change the task priority.
Using the Bulk Task Release:
• POST.../entity/task/bulk_change_priority/
{
"parameters": {
"id**in": [01, 02, 03]
},
"options": {
"priority": "3",
"commit_frequency": "0"
}
}
Note: The API body should have the task number list. You are also required to provide the task priority in the request
body. You can send the commit frequency as an option as well. The commit frequency is by default set to 0. If it is set
to 0, the system should roll back on first error/ If the commit frequency is set to 1, the system will commit per object.
Cancel T ask
The Cancel T ask API allows you to cancel a task which is in ready/held status through an API so that the tasks not yet
picked up can be cancelled/or supervisor would want to cancel a task part of the wave.
API URL: Lookup by ID
POST.../entity/task/{id}/cancel/
No additional `parameters` data in the request body is required.
API URL: Lookup by Filters
POST.../entity/task/cancel/
Category Name Required Type Description
parameters facility_id Integer Facility context by id
parameters facility_id**code string Facility context by code
parameters company_id Integer Company context by id
parameters company_id\_\_code string Company context by code
parameters task_nbr X string T ask which needs to be on
hold
220

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
• If the facility and/or company are provided, set login context accordingly.
• Only one of `facility_id` or `facility_id__code` may be provided.
• Only one of `company_id` or `company_id__code` may be provided.
Bulk Cancel URL
POST.../entity/task/bulk_cancel/
Request Body:
The transaction is meant for the task entity. So, the users are required to send the following parameters in the body.
POST.../entity/task/bulk_hold/
{
"parameters": {
"id\_\_in": [01, 02, 03]
},
"options": {
"commit_frequency": "0",
}
}
The commit frequency is by default set to 0. If it is set to 0, the system should roll back on first error/ If the commit
frequency is set to 1, the system should commit per object.
Trailer
These topics give descriptions for APIs that complete actions related to trailers and the Warehouse.
First Available
The first_available API allows you to identify yard locations with available capacity. After fetching this API, you will
get the first yard location with capacity based on the yard location putaway sequence. If the putaway sequence is not
configured, the fetch will display according to the yard location pick sequence. After you get the location, you can use
the locate to yard API to update the trailer location to the yard.
Identify yard location by capacity:
GET
.../entity/location/yard/first_available
Request
The following are the Query String Filters for this API:
Name Required Type Default Description
facility_id String Facility context by id.
221

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Name Required Type Default Description
facility_id**code String Facility context by code.
• Only one of "facility_id" or "facility_id**code" is allowed per request.
• If no additional context is provided, the user's default facility/company will be used.
Example Requests
GET .../entity/location/yard/first_available?facility_id=1
The following is an example GET request for facility ID:
GET .../entity/location/yard/first_available?facility_id=1
The following is an example GET request for facility ID code:
GET .../entity/location/yard/first_available?facility_id_code=STRAJB01
Locate to Yard
The locate_to_yard API allows the caller to update a trailer’s location within the yard.
Input Parameters
Common Parameter (Applicable to All Requests)
Category Name Type Required Description
options location_barcode String Yes Barcode of the yard
location.
Trailer Lookup by ID
This method requires the unique id of the trailer in the request URL. No additional parameters are required in the
request body.
URL
POST… /entity/trailer/{id}/locate_to_yard/
Example Request Body
{
"options": {
"location_barcode":
"YARDAJ0101"
}
}
222

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Trailer Lookup by Filters
URL: POST… /entity/trailer/locate_to_yard/ Input Parameters
Category Name Type Required Description
parameters trailer_nbr String Yes Trailer number to be
moved.
parameters company_id Integer No Trailer’s company identifier.
Additional Notes
• Only a single trailer may be moved per request.
• The **in lookup is not supported for trailer_nbr.
• company_id also supports string lookup by code using double-underscore notation:
• company_id**code
Example Request Body
{
"options": {
"location_barcode":
"YARDAJ0101"
},
"parameters": {
"company_id\_\_code": "QATSTPC",
"trailer_nbr": "JPTRL280225-1"
}
}
Response Codes
Status Code Description
200 OK Trailer location updated successfully.
Remove from Yard
The remove_from_yard API allows the caller to release a trailer from its current yard location.
Trailer Lookup by ID
POST .../entity/trailer/{id}/remove_from_yard/

The caller knows the unique `id` value of the trailer, which is added to the request URL. No additional `parameters` data is
required from the request body.
223

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Trailer Lookup by Filters
POST .../entity/trailer/remove_from_yard/

Category Name Type Required Description
parameters trailer_nbr String Y Trailer number to be
removed.
parameters facility_id Integer N Trailer’s facility.
parameters company_id Integer N Trailer’s company.
• Only a single trailer may be moved per request.
◦ The `__in` lookup is not supported for `trailer_nbr`.
• `facility_id` and `company_id` both additionally support string lookup by `code` using the double-underscore
notation:
◦ facility_id\_\_code
◦ company_id_code
Example Request Body:
{
"parameters": {
"facility_id": 1,
"company_id_code": "COM-1",
"trailer_nbr": "TRLR-1"
}
}
Waves
These topics give descriptions for APIs that complete actions related to waves in the Warehouse.
224

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Run Manual Wave
The Run Manual API allows you to invoke a manual wave. The following are some potential scenarios and reasons for
running the wave using a Rest API:
• External systems or PaaS Solutions can be built with the option to run a manual wave screen. These systems
may have their own order entry or display screen and running an API will allow them to invoke waves.
The following are some ways for calling the Manual Wave:
Using the Wave Template ID:
POST .../entity/wave_template/{id}/run_manual/
Note: ID corresponds to a valid Wave template ID. The API body should contain the list of corresponding
Order detail IDs for which the wave is run.
Using the Wave Template Name:
POST .../entity/wave_template/run_manual/
Note: The API body should include facility id/code, company id/code, wave template name, and corresponding Order
Detail ID's, or Order Number and Sequence number combination.
Example Request Body Parameters to Identify Wave Template
{
"parameters": {
"facility_id": 1,
"template_name": "Wave Template"
}
}
{
"parameters": {
"facility_id\_\_code": "FAC1",
"template_name": "Wave Template"
}
}
Identifying the Order Details
• User can provide either a list of specific order detail id(s), or a list of order number / sequence number pairs.
◦ Only one of the two inputs may be provided in a single request.
• The data is provided in the "options" section of the request body.
Identifying Order Details by ID
{
...
"options": {
"order_dtl_id_list": [1, 2, 3, 4]
}
225

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
}
• "order_dtl_id_list" is always a list, even if a single id is provided.
◦ The list may not be empty.
Identifying Order Details by Order Number - Sequence Number Pairs
{
...
"options": {
"order_seq_nbr_list": [
{
"order_nbr": "ORD1",
"seq_nbr_list": [1]
},
{
"order_nbr": "ORD2",
"seq_nbr_list": [3, 4, 5]
}
]
}
}
• order_seq_nbr_list is a list of objects grouping the different order number and sequence number combinations.
◦ "seq_nbr_list" is always a list, even if a single sequence number is provided.

- The list may not be empty.
  Setting the Company Context
  • Users may optionally specify the company context by including either the "company_id" or "company_code" in
  the "options" section of the request required to:
  a. Specify a valid facility/company combination when changing the user's context from the default.
  b. Ensure any company parameters used in the functionality are of the correct company.
  {
  ...
  "options": {
  ...
  "company_id": 1
  }
  }
  {
  ...
  "options": {
  ...
  "company_code": "COM1"
  }
  }
  Run Template
  The Run Template API allows you to invoke the wave template.
  226

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
The following are some ways for calling the Wave Template API:
Using the Wave Template ID
• POST .../entity/wave_template/{id}/run_template/
Note: No additional `parameters` data in the request body is required.
Using the Wave Template Name
• POST .../entity/wave_template/run_template/
Note: The API body should include facility id/code and the wave template name.
• The wave template name provided in the body should correspond to the default facility code or to your eligible
facility.
• If the company parameter "ONL Y_ONE_WAVE_PER_FACCO" is configured to ‘No’ and if there is already a wave
running for the same wave template, the system will not allow you to invoke the wave to send in the API
request.
Category Name Required Type Description
parameters facility_id Integer Facility context by id
parameters facility_id**code string Facility context by code
parameters template_name X string Wave Template Name that
users intend to run
• Only one of `facility_id` or `facility_id**code` may be provided.
• If more than one object is found, an error should be returned.
Options
Category Name Type Description
options company_id Integer Company context by id
options company_code string Company context by code
227

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
• This is used to set the user's company context corresponding to the wave template's facility.
◦ This also ensures the correct company parameters are referenced.
◦ If not provided, the user's default company is assumed.
Sample Request Body Data Format JSON
{
"parameters": {
"facility_id": "1",
"template_name": "KHWAVE001"
},
"options": {
"company_code": "CO1"
}
}
Response Body
• Upon successful invocation of the wave return response code HTTP 202 - Accepted.
◦ API will run in asynchronous mode only, once API is invoked basic validations will be done and
corresponding wave number generated will be shared in the response. Users will need to poll the "wave"
entity using this information to know when the wave is complete.
Sample Response Body Data Format JSON
{
"run_nbr": "WAVE001"
}
Undo Wave
The Undo Wave API allows you to invoke the wave template. With the introduction of this API, external systems or PaaS
solutions can be integrated which will allow you to undo a wave without accessing the web UI screen.
The following are some ways for calling the Undo Wave API:
Using the Wave Template ID
• POST .../entity/wave/{id}/undo
Note: No additional `parameters` data in the request body is required.
Using the Wave Run Number
• POST .../entity/wave/undo/
228

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Note: The API body should include facility id/code and the wave run number.
When the parameter UNDO_WAVE_EVEN_AFTER_PICKING is set to 'No,' the system will not undo a Wave if picking is
started. If the parameter is set to 'Yes,' the application allows undo wave even after picking has started.
Category Name Required Type Description
parameters run_nbr X string Wave Number
parameters facility_id Integer Facility context by id
parameters facility_id**code string Facility context by code
• User should be able to provide either wave run_nbr or id.
• Login context will be set up based on the facility id/facility_id**code provided.
• Only one of `facility_id` or `facility_id__code` may be provided.
• The above mentioned URL should undo the wave template ( Allocation should be cancelled for the order
defined in the wave search set up in the wave template)
Sample Data Format JSON
{
"parameters": {
"facility_id\_\_code": "FAC-1",
"run_nbr": "128935"
}
}
Attachments
The topics in this section describe the APIs that can be used to upload, get, and delete attachments from WMS.
Attachments related to the following entities are supported through these APIs:
• Inbound LPN
• Outbound LPN
• Inbound Shipment
• Outbound Load
• LPN Type
• Pallet
229

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Attachment Upload
The Attachment Upload API allows you to upload attachments to WMS. The attachment name along with the base 64
encoded attachment data needs to be sent in the options section of the request body. The API supports both entity by
ID and entity by filters.
API
POST.../attachment/upload/
Parameters
Name Required Description
company_id X This is required for all entities
facility_id C This is required only for facility level entities –
Inbound LPN, Inbound Shipment, Outbound
LPN, Outbound Load and Pallet. Not required
for LPN Type
entity X Represents the entity - IBLPN, IBSHIPMENT,
OBLPN, LPNTYPE, OBLOAD, PALLET for which
the request is being made.
entity_id O Represents the unique ID of the entity, such as
Container ID, IB Shipment ID. If entity_key is not
populated, this field has to be populated
entity_key O Represents the nbr or code of the entity such
Container Nbr, Shipment Nbr, LPN Type Code.
If entity_id is not populated, this field has to be
populated
Where X = Required; C = Conditional and O = Optional
Options:
• attachment_name (Required)
• attachment_data (Required) – Base 64 encoded. If using an online tool to encode your attachments to base 64,
use output format as “Data URI”
Example Requests
Entity by ID
POST .../attachment/upload/
{
"parameters": {
"company_id": "369",
"facility_id": "648",
"entity": "IBLPN",
"entity_id": 12345 (container_id)
230

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
},
"options": {
"attachment_name": "file123.png",
"attachment_data": "data:@file/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/…" (base64 encoded)
}
}
Entity by Filters
POST .../attachment/upload/
{
"parameters": {
"company_id": "369",
"facility_id": "648",
"entity": "IBLPN",
"entity_key": "LPN123" (container_nbr)
},
"options": {
"attachment_name": "file123.docx",
"attachment_data": "data:@file/vnd.openxmlformats-
officedocument.wordprocessingml.document;base64,UEsDBBQABgAIAGCnNFWaPJ7…" (base64 encoded)
}
}
Response
If the attachment is uploaded successfully, a 200 OK is returned with the following field in the response body.
{
"nbr_attachments": <Nbr of Attachments>
}
This field indicates the total number of attachments in WMS for the entity ID or entity key passed in the request.
231

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Note:
• Attachment upload through this API is only allowed if the requesting user belongs to the group with upload
permission for the requested entity and the entity is in a valid status:
◦ If entity is IBLPN, the requesting user should have “container / Upload Files” permission AND the LPN
should not be cancelled, consumed or lost.
◦ If entity is OBLPN, the requesting user should have “container / Upload Files” permission AND the LPN
should not be cancelled, shipped or delivered.
◦ If entity is LPNTYPE, the requesting user should have “LPN Type / Upload Files” permission.
◦ If entity is IBSHIPMENT, the requesting user should have “ib shipment / Upload Files” permission AND
the IB Shipment should not be cancelled.
◦ If entity is OBLOAD, the requesting user should have “load / Upload Files” permission AND the OB Load
should not be cancelled.
◦ If entity is PALLET, the requesting user should have “Pallet / Upload Files” permission AND the Pallet
should not be cancelled.
• Only one attachment can be uploaded per request.
• The size of attachment is limited to 10 MB.
• Attachments are subjected to virus scanning.
• Attachments of the following file types are supported: jpg, jpeg, png, doc, docx, xls, xlsx, pdf.
Each attachment uploaded to WMS is tagged with relevant keys that can be used as a search criterion in the
Attachments UI in WMS.
Depending on the entity for which the attachment has been uploaded, the keys would be different as depicted in the
table below:
Entity Key Note
Inbound LPN number Mandatory – Every attachment will be tagged with this key
Inbound shipment number
Purchase order number
Trailer number
IBLPN
Pallet number
Optional – Attachments will be tagged with these keys only if available at the time
of uploading
Outbound LPN number
Outbound order number
Mandatory – Every attachment will be tagged with these keys
Outbound load number
OBLPN
Pallet number
Optional – Attachments will be tagged with these keys only if available at the time
of uploading
LPNTYPE LPN Type Mandatory – Every attachment will be tagged with this key
232

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Entity Key Note
Inbound shipment number Mandatory – Every attachment will be tagged with this key
Purchase order number
Trailer number
Optional – Attachments will be tagged with these keys only if available at the time
of uploading
IBSHIPMENT
Inbound load number Optional – Although optional, attachments will always be tagged with this key,
since this data is always available
Outbound load number Mandatory – Every attachment will be tagged with this keyOBLOAD
Trailer number Optional – Attachments will be tagged with this key only if available at the time of
uploading
PALLET Pallet number Mandatory – Every attachment will be tagged with this key
Attachment GET
The Attachment Get API allows you to get the list of attachments for the requested entity from WMS. The API supports
both entity by ID and entity by filters.
API
POST.../attachment/get/
Query String Parameters
Name Required Description
company_id X This is required for all entities
facility_id C This is required only for facility level entities –
Inbound LPN, Inbound Shipment, Outbound
LPN, Outbound Load and Pallet. Not required
for LPN Type
entity X Represents the entity - IBLPN, IBSHIPMENT,
OBLPN, LPNTYPE, OBLOAD, PALLET for which
the request is being made.
entity_id O Represents the unique ID of the entity, such as
Container ID, IB Shipment ID. If entity_key is not
populated, this field has to be populated
entity_key O Represents the nbr or code of the entity such
Container Nbr, Shipment Nbr, LPN Type Code.
If entity_id is not populated, this field has to be
populated
233

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
Where X = Required; C = Conditional and O = Optional
Response
The response contains paginated results with the following fields:
• attachment_id - Unique ID of the attachment
• attachment_name - Name of the attachment
• attachment_data – Based 64 encoded attachment data
• delete_permission - A boolean value (True or False) that indicates if the requesting user has delete permission
for the requested entity
◦ If entity is IBLPN or OBLPN, the value of "container / Delete Files" permission is returned for the
requesting user
◦ If entity is LPNTYPE, the value of "LPN Type / Delete Files" permission is returned for the requesting user
◦ If entity is IBSHIPMENT, the value of "ib shipment / Delete Files" permission is returned for the
requesting user
◦ If entity is OBLOAD, the value of "load / Delete Files" permission is returned for the requesting user
◦ If entity is PALLET, the value of "Pallet / Delete Files" permission is returned for the requesting user
Example Requests
Entity by ID
GET.../attachment/get?company_id=354&facility_id=572&entity=IBLPN&entity_id=12345
(where entity id is the ID of the container)
Entity by Filters
GET.../attachment/get?company_id=354&facility_id=572&entity=IBLPN&entity_key=LPN123
(where entity key is the container nbr)
Example Response
{
"result_count": 2,
"page_count": 1,
"page_nbr": 1,
"next_page": null,
"previous_page": null,
"results": [
{
"attachment_id": "1234567890",
"attachment_name": "IBLPN_LPN123_01242024090005.jpg",
"attachment_data": "data:@file/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/…", (base64 encoded)
"delete_permission": "true"
},
{
"attachment_id": "5723497522",
"attachment_name": " IBLPN_LPN123_01242024091017.docx",
"attachment_data": "data:@file/vnd.openxmlformats-
officedocument.wordprocessingml.document;base64,UEsDBBQABgAIAGCnNFWaPJ7…", (base64 encoded)
"delete_permission": "true"
}
]
234

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
}
Attachment Delete
The Attachment Delete API allows you to delete attachments from WMS. The list of attachment IDs needs to be
sent in the options section of the request body. The attachment ID is internal to WMS and can be retrieved using the
“attachment/get” API described in the Attachment Get section. The API supports both entity by ID and entity by filters.
API
POST.../attachment/delete/
Parameters
Name Required Description
company_id X This is required for all entities
facility_id C This is required only for facility level entities –
Inbound LPN, Inbound Shipment, Outbound
LPN, Outbound Load and Pallet. Not required
for LPN Type
entity X Represents the entity - IBLPN, IBSHIPMENT,
OBLPN, LPNTYPE, OBLOAD, PALLET for which
the request is being made.
entity_id O Represents the unique ID of the entity, such as
Container ID, IB Shipment ID. If entity_key is not
populated, this field has to be populated
entity_key O Represents the nbr or code of the entity such
Container Nbr, Shipment Nbr, LPN Type Code.
If entity_id is not populated, this field has to be
populated
Where X = Required; C = Conditional and O = Optional
Options:
• Attachment ID list (Required)
Example Requests
Entity by ID
POST .../attachment/delete/
{
"parameters": {
"company_id": "369",
"facility_id": "648",
"entity": "IBLPN",
"entity_id": 12345 (container_id)
},
"options": {
"attachment_id_list": [
235

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 5
Supported Operations
1230,
2457,
7299
]
}
}
Entity by Filters
POST .../attachment/delete/
{
"parameters": {
"company_id": "369",
"facility_id": "648",
"entity": "IBLPN",
"entity_key": "LPN123" (container_nbr)
},
"options": {
"attachment_id_list": [
1230,
2457,
7299
]
}
}
Response
Depending on how many attachments are deleted successfully, a 200 OK is returned with the following field in the
response body.
{
"nbr_deleted": <Nbr of attachments deleted successfully>,
"nbr_failed": <Nbr of attachments that could not be deleted>,
"nbr_attachments": <Nbr of Attachments>
}
Where nbr_deleted indicates the number of attachments that were successfully deleted from WMS.
• nbr_failed indicates the number of attachments that could not be deleted from WMS.
• nbr_attachments indicate the remaining number of attachments in WMS for the entity ID or entity key passed
in the request.
Note:
• Attachment delete through this API is only allowed if the requesting user belongs to the group with delete
permission for the requested entity:
• ◦ If entity is IBLPN or OBLPN, the requesting user should have "container / Delete Files" permission.
◦ If entity is LPNTYPE, the requesting user should have "LPN Type / Delete Files" permission.
◦ If entity is IBSHIPMENT, the requesting user should have "ib shipment / Delete Files" permission.
◦ If entity is OBLOAD, the requesting user should have "load / Delete Files" permission.
◦ If entity is PALLET, the requesting user should have "Pallet / Delete Files" permission.
236

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 6
Data Extract
6 Data Extract
Data Extract
Oracle WMS now supports the use of a REST API to extract data to your preferred object store by configuring the
Endpoints UI.
To use the REST API for Object Store, we’ve introduced a new Endpoints Interface Protocol called “Objectstore for Data
Extract”. The same service providers that are supported in Endpoint for Output Interfaces are supported here as well.
You can configure your selected service provider’s specific set of fields/parameters to setup the Endpoints for Data
Extract. The following table lists the fields/parameters you can configure for each of the supported cloud storage
service providers:
CLOUD STORAGE SERVICE PROVIDER REQUIRED OR CONFIGURABLE FIELDS/PARAMETERS
Object Storage (OCI) • Namespace
• Bucket Name
• Region
Cloud Storage (GCS) Bucket URL
Simple Storage Service (AWS S3) • User Role ARN
• Bucket URL
Binary Large Object Storage (Azure BLOB) • Tenant ID
• Bucket URL
You can click the “Provider Configuration” button on the Endpoints UI and the system displays a set of service provider-
specific information. This can be used by the cloud storage service provider to allow WMS target access for data
extraction.
Note: Refer to this link for more information on configuration policies for your respective cloud object store service
provider.
After you click the Provider Configuration button, the system displays the relevant configuration info for the selected
service provider as follows:
CLOUD STORAGE SERVICE PROVIDER SERVICE PROVIDER CONFIGURATION INFO
Object Storage (OCI) • Tenancy OCID
• Dynamic Group OCID
Cloud Storage (GCS) Service Account
237

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 6
Data Extract
CLOUD STORAGE SERVICE PROVIDER SERVICE PROVIDER CONFIGURATION INFO
Simple Storage Service (AWS S3) • Database OCID
NOTE: The External ID needs to be configured as the Database OCID in the Trust Relationship.

• Oracle User ARN
Binary Large Object Storage (Azure BLOB) • Consent URL
• App Name
Note:
• Refer to your respective cloud storage service provider’s guidelines and requirements for the credentials/
parameters.
• You can set the data extract file size ranging from 10 MB to 1 GB using the API. By default, the file size is 10 MB.
• If any object store credentials are inputted incorrectly, the system will display an error dialog box: “Invalid data
configured for: %FIELDS%".
• If any mandatory fields are not configured, the system will display an error dialog box: "The following
mandatory fields cannot be left blank: "%s List of mandatory parameters not configured %s".
Using the new API, you can extract entity-level data and push it to the configured Object Store via files in CSV, JSON or
parquet formats.
Push to Object Store API URL
POST .../wms/lgfapi/v10/data_extract/push_to_object_store
Example Body
{
"options": {
"endpoint": {
"name": "dummy_endpoint",
"object_store_path": "Folder1/Folder2"
},
"file_format": "CSV",
"file_size_in_mb": 10,
"compressed": "true",
"unique_identifier": "uniqueidentifier_01"
},
"parameters": {
"entities": [
{
"entity": "inventory",
"fields": "item_id",
"filter": {
"create_ts**gt": "2024-10-01T00:00:00.000",
"status_id**lt": 90
}
},
{
"entity": "container",
"fields": "container_nbr,rcvd_ts,curr_location_id",
"filter": {
238

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 6
Data Extract
"mod_ts**gt": "2024-10-01T00:00:00.000",
"status_id**lt": 90
}
}
]
}
}
Sample Response
{
"response_check_url": ".../wms/lgfapi/v10/data_extract/export_async_status?
unique_identifier=uniqueidentifier_01",
"inventory": {
"task_id": "b3cae633-b893-4e40-aefe-c037b79c2b81",
"entity_status_url": ".../wms/lgfapi/v10/entity/lgf_async_task?backend_taskid**taskid=b3cae633-b893-4e40-
aefe-c037b79c2b81"
},
"container": {
"task_id": "b897ee89-2346-4d10-92a5-48572b0771c4",
"entity_status_url": ".../wms/lgfapi/v10/entity/lgf_async_task?
backend_taskid**taskid=b897ee89-2346-4d10-92a5-48572b0771c4"
}
}
Note:
• The Unique Identifier is required to group the set of entities in the payload. So, it is mandatory to specify a
unique identifier for each API call.
• The REST API supports only three filters, namely "create_ts**gt", "mod_ts**gt" and "status_id**lt". Entries for
"create_ts**gt" and "mod_ts\_\_gt" filters cannot be given simultaneously per entity. However, specifying atleast
one of them is mandatory.
• The timestamps in the API call should be specified only in UTC since the API is agnostic of the facility time
zone.
Async Data Extract Flag
The “async data extract” flag allows select users to perform data extract using the API. By default, this is set as False
(unchecked) in the Users UI. For data extraction, the checkbox for the async data extract flag needs to be enabled.
You can apply facility/company filtering in the query (if required), since the API is targeted towards a table-level data
extract.
Note: Only the original ADMIN role user(s) who are provisioned as a part of the WMS Cloud service activation (who
also have access to the RF Device Connection details button on the Users page) will be able to set or unset the new
“async data extract” flag. This can be set for any user, so that such users could be given the access to use this API,
which will extract data, regardless of facility company restrictions.
239

Oracle Warehouse Management Cloud
WMS REST API Guide
Chapter 6
Data Extract
Export Async Status API
You can use the Export Async Status API call to check the status of the aggregated task and the system will return status
results like “PENDING”, “RUNNING”, “SUCCEEDED” and “FAILED”.
URL
GET .../wms/lgfapi/v10/data_extract/export_async_status?unique_identifier=uniqueidentifier_01
Sample Response
{
"unique_identifier": "uniqueidentifier_01",
"cummulative_status": "SUCCESS",
"total_duration": 2.550852,
"entities": [
{
"inventory": {
"task_id": "b3cae633-b893-4e40-aefe-c037b79c2b81",
"file_prefix": "data_ocwms_uniqueidentifier_01_inventory_b3cae633-b893-4e40-aefe-c037b79c2b81",
"status": "SUCCESS",
"message": null,
"total_duration": 1.120942
}
},
{
"container": {
"task_id": "b897ee89-2346-4d10-92a5-48572b0771c4",
"file_prefix": "data_ocwms_uniqueidentifier_01_container_b897ee89-2346-4d10-92a5-48572b0771c4",
"status": "SUCCESS",
"message": null,
"total_duration": 1.165918
}
}
]
}
Async T ask Status - Entity Level
You can use this API call to check the async task status at the entity-level.
HEAD .../lgfapi/v10/entity/lgf_async_task/{id}
You can also GET APIs to fetch results ordered by the following criteria:
For paginated results:
GET .../lgfapi/v10/entity/lgf_async_task/
For non-paginated results, filtered by specific 'ID':
GET .../lgfapi/v10/entity/lgf_async_task/{id}

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Oracle Integration Hub](./index.md) - Understanding Oracle integration patterns
- [HTTP Client Adapter](../../api-reference/adapters/flx-adapters-comprehensive-reference.md) - FLX HTTP adapter for Oracle WMS calls

### **Next Steps**

- [WMS Comprehensive Guide](./oracle-wms-comprehensive-guide.md) - Complete WMS integration guide
- [Oracle Authentication](./oracle-sso-authentication-setup.md) - Setting up Oracle authentication
- [WMS CLI Guide](./oracle-wms-cli-guide.md) - Command-line tools for WMS

### **Related Topics**

- [HTTP Integration Patterns](../../architecture/patterns/advanced-patterns-hub.md) - Advanced HTTP integration patterns
- [Testing Oracle Integrations](../../development/testing/integration-testing.md) - Testing Oracle WMS integrations
- [Performance Optimization](../../optimization/performance/index.md) - Optimizing Oracle API calls

---

**📂 Hub**: [Oracle Guides](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
