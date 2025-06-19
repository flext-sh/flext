# sso-and-alternate-authentication-setup.pdf

**Caminho:** `reference/sso-and-alternate-authentication-setup.pdf` \n**Data de conversão:** 2025-05-15T14:33:08.273768 \n**Tipo:** .pdf \n**[Download original](reference/sso-and-alternate-authentication-setup.pdf)**

---

## Sumário

## Resumo automático

Este guia do Oracle Warehouse Management Cloud (Release 25B) apresenta os mecanismos de autenticação disponíveis e os passos necessários para configurá-los em seu ambiente:

1. Visão geral dos métodos de autenticação

   - Autenticação nativa (usuário/senha) para acesso Web, App móvel e RF.
   - OAuth2 (fluxo ROPC) para Web, App móvel e RF, delegando a validação de credenciais a um Identity Provider (IDP).
   - SAML2 Single Sign-On (SSO) para acesso Web, redirecionando ao IDP e retornando um token SAML.

2. Identity Providers suportados

   - Oracle Identity Cloud Service (IDCS)
   - Azure Active Directory (Azure AD)
     (Outros provedores compatíveis com OAuth2 ou SAML2 podem funcionar.)

3. Configuração no WMS Cloud

   - Associar cada usuário local a um “alternate username” no formato <usuário>@<domínio>.
   - Possibilidade de manter usuários com autenticação local enquanto outros usam OAuth2 e/ou SSO.

4. Detalhes técnicos para OAuth2

   - Fluxo suportado: Resource Owner Password Credentials (ROPC).
   - Parâmetros exigidos em um Service Request:
     • Nome do IDP, endpoint de token, client ID e client secret
     • Recurso/escopo
     • X-USER-IDENTITY-DOMAIN-NAME (domínio para mapear o alternate username)

5. Detalhes técnicos para SAML2 SSO

   - Troca de metadados entre cliente e Oracle (arquivo XML ou URL).
   - Itens fornecidos pelo cliente:
     • Metadata SAML2.0 (incluindo certificado de assinatura em PEM)
     • Issuer ID, URLs de Single Sign-On e Assertion Consumer Service
     • Domínio para mapeamento do alternate username
   - Itens fornecidos pela Oracle:
     • Service Provider ID, resposta de binding, certificados públicos
   - Instruções específicas para IDCS e Azure AD (NameID na asserção, URLs, certificados X.509).

6. Observações finais
   - Não suportam federations nem MFA no fluxo OAuth2.
   - O mesmo usuário pode usar SSO na interface Web e OAuth2 em App/RF, desde que o IDP seja o mesmo.
   - Para ativar qualquer mecanismo, é preciso abrir um Service Request e preencher os dados técnicos solicitados.

## Conteúdo extraído

Oracle Warehouse
Management Cloud
SSO and Alternate Authentication
Setup
Release 25B

Oracle Warehouse Management Cloud
SSO and Alternate Authentication Setup
Release 25B
G27182-02
Copyright © 2025, Oracle and/or its affiliates.
Author: Oracle WMS Cloud Product Team

Oracle Warehouse Management Cloud
SSO and Alternate Authentication Setup
Contents
Get Help ................................................................................................................................ i
2 Oracle WMS Cloud Alternate Authentication Mechanisms 3
Oracle WMS Cloud Alternate Authentication Mechanisms ................................................................................................... 3
Identity Providers ........................................................................................................................................................................... 3
WMS Configuration for Alternate Authentication ................................................................................................................... 3
Built-in Authentication .................................................................................................................................................................. 4
OAuth2 Authentication ................................................................................................................................................................. 4
3 SSO Authentication 7
SSO Authentication ........................................................................................................................................................................ 7
Technical Configuration for SSO ................................................................................................................................................. 7
IDCS SSO Information ................................................................................................................................................................... 8
Azure AD SSO Authentication ..................................................................................................................................................... 9

Oracle Warehouse Management Cloud
SSO and Alternate Authentication Setup

Oracle Warehouse Management Cloud
SSO and Alternate Authentication Setup
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
SSO and Alternate Authentication Setup
Get Help
ii

Oracle Warehouse Management Cloud
SSO and Alternate Authentication Setup
Chapter 2
Oracle WMS Cloud Alternate Authentication Mechanisms
2 Oracle WMS Cloud Alternate Authentication
Mechanisms
Oracle WMS Cloud Alternate Authentication Mechanisms

Oracle® Fusion Cloud Warehouse Management includes a built-in authentication mechanism using with users can
be setup with their own user-id and passwords to access the Oracle Warehouse Management (WMS) Web UI, WMS
Cloud Mobile App and Mobile RF applications. In addition, it also supports authenticating users against external identity
providers (IDP). It supports multiple authentication mechanisms:
• SAML2 Single Sign On, or SSO in short
◦ A web-based authentication standard that can be used only to login to the WMS Web UI
• OAuth2
◦ Another authentication standard that can be used for the WMS Web UI, the WMS Cloud Mobile App and
Mobile RF.
Identity Providers
Oracle Identity Cloud Service (IDCS) and Azure AD/ADFS are Identity Providers that have been tested with Oracle WMS
Cloud. Other providers that support these standards may also work. Customers can request their environments to
be configured to use SSO and/or Oauth2 by raising a Service Request (SR). Oracle will provide a template via the SR
for customers to fill out certain technical pieces of information which will be used by our Cloud operations team to
configure the customers environment.
WMS Configuration for Alternate Authentication
Once the WMS Cloud environment has been setup for SSO or OAuth2 authentication, usernames in WMS Cloud have to
be associated with a corresponding username in the external Identity Provider. This is the “Alternate username” field in
WMS Cloud and must be of the format:
<username>@<domain>
WMS Cloud users can be created/configured from the Users screen or by uploading a User Excel file from the Input
Interface screen.
It is possible to have some WMS users be locally authenticated (add note about temp users) and others externally
authenticated. It’s possible to have both SSO and OAuth2 backends configured for one customer.
3

Oracle Warehouse Management Cloud
SSO and Alternate Authentication Setup
Chapter 2
Oracle WMS Cloud Alternate Authentication Mechanisms
Built-in Authentication
The user types in the username and password on the WMS Cloud login page, whether the Web, Mobile App, or Mobile
RF device. The encrypted credentials are validated against the WMS Cloud Service.
OAuth2 Authentication
The user types in the username and password on the WMS Cloud login page, whether the Web, Mobile App or Mobile
RF device. The encrypted credentials are sent to the WMS Cloud Service. If the username has an associated “alternate
username”, WMS Cloud will delegate the authentication to the external identity provider and validate against that
service. If the authentication succeeds, the user is logged into the WMS.
OAuth2 backends that have been validated with WMS Cloud are Oracle IDCS and Azure AD.
If users WMS instance was activated via My Services Portal for OCWMS after February 2021, as part of the activation,
users are automatically provisioned with OAuth2 Authentication enabled. It is enabled with the domain of the WMS
administrator who activated the account.
Note: You can include additional domains.
Technical Configuration for OAuth2
Note: Federation and MFA (Multi Factor Authentication) are not supported. The OAuth2 flow only supports the ROPC
(Resource Owner Password Credentials) grant type, as defined here:
4

Oracle Warehouse Management Cloud
SSO and Alternate Authentication Setup
Chapter 2
Oracle WMS Cloud Alternate Authentication Mechanisms
<https://tools.ietf.org/html/rfc6749#section-4.3>
When submitting an SR to My Oracle Support to setup OAuth2 authentication, you need to provide the data per the
table below. The technical details are explained in the reference links below.
Oracle IDCS Reference
<https://docs.oracle.com/en/cloud/get-started/subscriptions-cloud/csimg/obtaining-access-token-using-user->
credentials-client-assertion.html
Azure AD Reference
<https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth-ropc>
Item Description
Identity Provider Name Name of IDP such as Azure AD or Oracle IDCS.
Endpoint URL Used by the WMS to authenticate
Client ID Needed for Oracle IDCS and Azure AD
Client Secret Needed for Oracle IDCS and Azure AD
Resource/Scope Needed for Oracle IDCS and Azure AD
X-USER-IDENTITY-DOMAIN-NAME Needed for Oracle IDCS
Domain name Used to link WMS username with the OAuth2 username, using "Alternate username"

For example if the username is "jdoe"@somedomain.com, then the domain name is somedomain.com.

NOTE: Customers need to provide ALL domains that they need for WMS. We don’t support generic
consumer domains (for example: @yahoo.com @gmail.com)

5

Oracle Warehouse Management Cloud
SSO and Alternate Authentication Setup
Chapter 2
Oracle WMS Cloud Alternate Authentication Mechanisms
6

Oracle Warehouse Management Cloud
SSO and Alternate Authentication Setup
Chapter 3
SSO Authentication
3 SSO Authentication
SSO Authentication
SAML2 SSO works a bit differently. The username and password are not entered in the WMS Cloud login page. The
user instead clicks the “Login using SSO” button (which will be available after the SSO configuration has been setup by
following SR process mentioned earlier). The page gets redirected to the Identity Provider’s login page where the user
will login using their username linked to the IDP (this is stored in the “Alternate username” field in WMS Cloud). If the
authentication succeeds, a token is returned back to the WMS Cloud and the user is logged in to the application.
Note: SAML2 being a web-based standard, this mechanism can be used only to login to the WMS Cloud web UI. RF
or App login will have to use either local authentication or OAuth2 authentication. It is possible for the same user to be
linked to both SAML2 SSO and OAuth2 backends (the IDP has to be the same in this case), so the same user can login
via SSO to the Web UI and via OAuth2 on the RF.SAML2 SSO backends that have been validated against WMS Cloud
are Oracle IDCS and Azure AD.
Technical Configuration for SSO
For SAML2 SSO setup, the customer and Oracle exchange certain technical information needed to configure both
systems.
Customer Provides Oracle provides
• SAML2.0 Metadata including signing
certificate.
• For some IDPs customer may
also need to provide additional
information (details below).
• Application Service Provide ID
• The public key for request signing
• SAML assertion URL
• Other IDP configuration

7

Oracle Warehouse Management Cloud
SSO and Alternate Authentication Setup
Chapter 3
SSO Authentication
Customer Provides Oracle provides

Customer provided information:
The customer configures their IDP for Cloud WMS authentication, generates the SAML2 Metadata file, and sends it to
Oracle. IDPs that support SAML2 SSO will have a mechanism to generate this file, including Oracle IDCS and Azure AD.
SAML2.0 MetaData - Customer must provide IDP metadata for SAML2.0, it can be provided in a metadata.xml file or a
URL allowing Oracle to download the IDP metadata from customer site.
The specific fields that are used by Oracle are explained below. In addition, for IDCS, the MyApp URL is also needed
(details below) and has to be sent separately as its not part of the metadata file.
IDCS SSO Information
Item Description
Issuer ID Unique identifier of the IDP
MyApp URL The binding that is used to send the response to the Identity provider.

NOTE: IDCS also has an SSO_URL which is different. The Metadata does not include the MyApp URL

Response signature certificate

(X509 Certificate) – PEM format

Will verify tokens signed by IDCS
Domain name Used to link WMS username with the SSO username, using "Alternate username"

For example if the username is "jdoe"@somedomain.com, then the domain name is somedomain.com.

NOTE: Customers need to provide ALL domains that they need for WMS. We don’t support generic
consumer domains (for example: @yahoo.com @gmail.com)

Note: An app has to be created in IDCS using the ROPC grant type. This is required for WMS to authenticate using
IDCS.If you have separate accounts for IDCS with Fusion, WMS and/or other, the backend IDCS setup for WMS will be
used and if you want to use both, you can federate with assistance from the IDCS team.
8

Oracle Warehouse Management Cloud
SSO and Alternate Authentication Setup
Chapter 3
SSO Authentication
Azure AD SSO Authentication
Item Description
Issuer ID Unique identifier of the IDP

Single Sign-On URL The binding that is used to send the response to the Identity provider.
Response signature certificate

(X509 Certificate) – PEM format

Will verify tokens signed by the IDP
Domain name Used to link WMS username with the SSO username, using "Alternate username"

For example: if the username is jdoe @somedomain.com, then the domain name is somedomain.com.

NOTE: Customers need to provide ALL domains that they need for WMS. We don’t support generic
consumer domains (for example: @yahoo.com @gmail.com)

Note: The SSO assertion returned by the IDP must contain NameID tag with the alternate username configured in our
application as the value. We will use that to look up a user and create a session. Example assertion with NameID:
<saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ...>
...
<saml:Subject>
<saml:NameID>username@domain</saml:NameID> ...
</saml:Subject>
...
</saml:Assertion>
9

Oracle Warehouse Management Cloud
SSO and Alternate Authentication Setup
Chapter 3
SSO Authentication
10
