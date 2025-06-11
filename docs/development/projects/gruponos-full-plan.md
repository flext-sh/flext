Perfeito. Iniciarei agora a criação do plano técnico detalhado e completo para a integração entre Oracle WMS Cloud e Autonomous Database via OIC, validado com base em documentação oficial da Oracle e todos os pontos já discutidos. Assim que estiver pronto, trarei aqui o conteúdo final completo para seu uso.

# Plano de Integração Técnica – Oracle WMS Cloud e Autonomous Database

## 1\. Visão Geral do Projeto e Objetivos

Este plano detalha a integração entre o **Oracle Warehouse Management Cloud (WMS Cloud)** – versão 25A/25B – e o **Oracle Autonomous Database (Autonomous DB)**, utilizando o **Oracle Integration Cloud (OIC) versão 3** como plataforma de orquestração. O objetivo é estabelecer um fluxo de dados confiável e em tempo quase real entre o sistema de gerenciamento de armazém e o banco de dados autônomo, garantindo que informações críticas de pedidos e alocações de estoque estejam disponíveis para análises, relatórios e outros sistemas corporativos.

Serão abordados todos os aspectos técnicos da integração, baseando-se em **documentação oficial da Oracle** para assegurar aderência a boas práticas e aos padrões recomendados. Entre os objetivos principais estão:

* **Sincronia de Pedidos:** Integrar pedidos de venda (ordens) entre o WMS e o Autonomous DB, contemplando cabeçalhos e detalhes (tabelas `order_hdr` e `order_dtl` no contexto do WMS), desde cargas iniciais até processamento contínuo.  
* **Rastreamento de Alocações:** Capturar e armazenar no Autonomous DB os eventos de **alocação de estoque** gerados no WMS (reservas de itens para pedidos), possibilitando visibilidade do atendimento de pedidos.  
* **Orquestração via OIC:** Utilizar o Oracle Integration Cloud para receber, transformar e transmitir os dados entre os sistemas, aplicando validações, tratamento de erros e garantindo segurança nas conexões.  
* **Atualização em Tempo Real:** Configurar **Webhooks** (interfaces de saída) no WMS Cloud para acionar fluxos do OIC em tempo real quando eventos-chave ocorrerem (por exemplo, criação de pedido ou alocação efetuada), reduzindo latência e evitando integrações puramente batch.  
* **Persistência e Auditoria:** Modelar tabelas de **stage** no Autonomous DB que armazenem os dados integrados com campos de auditoria (usuário, timestamps, status de processamento), servindo como histórico e ponto de recuperação em caso de falhas.  
* **Conformidade e Boas Práticas:** Garantir que a solução siga padrões de segurança (autenticação, criptografia), escalabilidade (suportando volumes grandes de dados) e observabilidade (monitoramento e logging adequados), conforme as recomendações da Oracle e experiências práticas.

Ao final, este projeto entregará uma integração completa, validada e pronta para produção, facilitando a **visibilidade ponta a ponta** dos processos de warehouse no banco de dados autônomo, com mínima intervenção manual e máxima confiabilidade.

## 2\. Arquitetura de Integração

**Visão Geral da Arquitetura:** A solução segue uma arquitetura híbrida de integração, combinando **cargas batch iniciais** via arquivos CSV e **integrações event-driven** via webhooks/REST. O Oracle Integration Cloud (OIC) atua como mediador central. Em alto nível, a arquitetura contempla os seguintes fluxos e componentes:

* **Oracle WMS Cloud 25A/25B:** Sistema fonte e destino de dados de operações de armazém. Ele fornecerá eventos (como alocações realizadas) e receberá dados de entrada (como novos pedidos). O WMS Cloud suporta dois formatos de dados principais – **XML** e **dados delimitados (CSV)** – e dois protocolos de integração – **serviços REST (HTTPS)** e **SFTP seguro**. Nesta integração, usaremos ambos conforme o caso: arquivos CSV para carga inicial via SFTP e chamadas REST (com payload XML) para integrações em tempo real.  

* **Oracle Integration Cloud (OIC) v3:** Plataforma iPaaS que hospedará os fluxos de integração (*integrations*). No OIC serão configuradas conexões adaptadoras para cada endpoint: **REST** (para receber chamadas do WMS via webhook e para invocar APIs REST do WMS), **FTP** (para ler arquivos CSV de um SFTP externo na carga inicial) e **Oracle DB** (para inserir/consultar dados no Autonomous DB). O OIC orquestra as chamadas, realizando transformações de payload (XML ↔︎ JSON ↔︎ tabela), tratamento de exceções e chamadas de procedimentos SQL quando necessário.  

* **Oracle Autonomous Database:** Repositório central dos dados integrados. Será utilizado um **Autonomous Transaction Processing (ATP)** (ou **Autonomous Data Warehouse**, conforme o caso de uso) para armazenar tabelas de estágio e fornecer *views* e *procedures* para transformação. A conexão do OIC ao Autonomous DB usará o adaptador nativo de Oracle Autonomous DB, com conexão JDBC segura via wallet (arquivo de credenciais). O Autonomous DB armazenará tanto os dados transacionais recebidos do WMS (pedidos, alocações, etc.) quanto dados de auditoria de integração. Ele também será responsável por consolidar e fornecer dados para relatórios ou outras aplicações de consumo, possivelmente através de *materialized views* ou procedimentos.  

* **Fluxos de Dados:**  

  * *Fluxo 1:* **Carga Inicial** – Em fase inicial ou em grandes sincronizações, o WMS Cloud exportará dados (por exemplo, todos os pedidos abertos existentes) em arquivos CSV para um servidor SFTP. O OIC (via conexão FTP) fará polling ou será agendado para ler esses arquivos, transformá-los em formato adequado (por exemplo, em objetos JSON/XML) e gravar nas tabelas de stage do Autonomous DB. Esse processo garante que o banco autônomo comece populado com os registros atuais do WMS.  

  * *Fluxo 2:* **Pedidos (Order)** – Integração de novos pedidos de venda. Dependendo do cenário, este fluxo pode operar de duas formas:  

    1. **Inbound para WMS:** se os pedidos tiverem origem em sistemas externos (por exemplo, ERP ou outro repositório consolidado no Autonomous DB), o OIC atuará pegando esses pedidos do banco (ou recebendo via outro trigger, não descrito aqui) e os enviará para o WMS Cloud através da API REST de criação de ordens. Nesse caso, o WMS Cloud atuaria como destino e o Autonomous DB como fonte.  
    2. **Outbound do WMS:** alternativamente, se o WMS for o sistema de origem dos pedidos (ex: pedidos inseridos manualmente ou provenientes de outra interface já carregados no WMS), o WMS enviará esses pedidos para o OIC via webhook tão logo forem criados, e o OIC os persistirá no Autonomous DB.

    Este plano cobre a infraestrutura necessária para **ambos os cenários**, garantindo que exista um mecanismo confiável de ida e volta. Por simplicidade, assumiremos que após a fase inicial, os pedidos novos entrarão no WMS via sistemas externos (ERP) *e* serão registrados no DB, enquanto atualizações ou eventos importantes no ciclo do pedido gerados dentro do WMS (como alocação ou expedição) serão repassados ao DB via eventos.

  * *Fluxo 3:* **Alocações de Estoque (Allocations)** – Quando o WMS realizar uma alocação de estoque a um pedido (reserva de itens para separação/picking), ele acionará um webhook (interface de saída) para notificar o OIC. O payload conterá detalhes da alocação (pedido, item, quantidade alocada, etc.). O OIC, ao receber o evento, fará a inserção desses dados nas tabelas de stage do Autonomous DB. Esse fluxo é **unidirecional (WMS \-\> DB)** e **em tempo real**, permitindo que o banco de dados autônomo espelhe imediatamente o status de atendimento dos pedidos.  

  * *Fluxo 4:* **Confirmações e outros** – Embora o escopo principal sejam pedidos e alocações, a arquitetura é expansível para outros fluxos, como confirmação de embarque/expedição, recebimento de mercadorias, ajustes de inventário, etc. O padrão seria similar: o WMS Cloud enviando eventos via webhook e/ou o OIC buscando dados periodicamente, com persistência no Autonomous DB. Esses fluxos adicionais podem ser implementados conforme a necessidade, reutilizando a infraestrutura aqui definida.

* **Segurança e Conectividade:** Todos os componentes comunicam-se de forma segura. As chamadas REST utilizam **HTTPS** e autenticação (Basic Auth ou OAuth2, conforme configurado) e as transferências SFTP usam canais cifrados. O OIC, por ser um serviço cloud, acessará o WMS Cloud (outro serviço SaaS da Oracle) pela internet pública usando credenciais seguras, e acessará o Autonomous DB preferencialmente via **conexão direta com wallet e SSL** (evitando a necessidade de agent on-premises). O Autonomous DB poderá estar configurado com **endereço público (com whitelisting de IPs do OIC)** ou via **Private Endpoint em VCN** – se for privado, será necessário usar o **Connectivity Agent** do OIC em uma rede que acesse o ADB. Neste plano, consideramos o caso comum de **ADB Shared com endpoint público**, usando wallet para comunicação direta.  

* **Componentes de Integração no OIC:** Serão criadas integrações separadas para cada fluxo (ex.: integração “CargaInicialPedidos”, “Integ\_Pedido”, “Integ\_Alocacao”). Cada uma delas será documentada na seção de Desenvolvimento (seção 7). O OIC também fornecerá painéis de monitoramento e logs de atividade para rastreamento das execuções e erros, detalhados posteriormente.

Em resumo, a arquitetura combina o melhor de dois mundos: **batch** (para sincronismo de grande volume inicial) e **event-driven** (para delta em tempo real), usando padrões nativos suportados pelo WMS Cloud e garantindo persistência confiável no Autonomous DB. A figura a seguir ilustra os componentes e fluxos (descrição textual caso a imagem não esteja disponível):

 *Arquitetura de Integração entre WMS Cloud, OIC e Autonomous DB (fluxos inbound e outbound)*

*(Figura: O WMS Cloud aciona OIC via webhook REST em eventos de pedido/alocação; OIC grava no Autonomous DB. Em paralelo, OIC carrega pedidos no WMS via API REST, obtendo-os de arquivos CSV ou da própria base autônoma. Conexões seguras (HTTPS, SFTP, JDBC SSL) destacadas.)*

## 3\. Configuração de Ambiente

Nesta fase, preparamos todos os ambientes e conexões necessários antes do desenvolvimento das integrações em si. São três pilares principais: **Oracle Integration Cloud**, **Autonomous Database** e configurações no **WMS Cloud** para permitir a comunicação.

### 3.1 Configurações no Oracle Integration Cloud (Conexões)

No OIC, criaremos conexões para cada endpoint envolvido, fornecendo as credenciais e parâmetros de segurança adequados:

* **Conexão REST (WMS Cloud API/Webhook):** Usada tanto para *triggers* (receber chamadas do WMS via webhook) quanto para *invokes* (chamadas do OIC para as APIs REST do WMS). Para configurar:  

  * **Adapter:** Selecionar "REST Adapter" ao criar a conexão.  

  * **Role (Papel):** Definir como **Trigger and Invoke** (ambos), já que esta conexão será utilizada como ponto de entrada (no caso de um webhook do WMS) e também como saída (para chamar o WMS). No OIC Gen3, o adaptador REST suporta as duas direções.  

  * **Connection URL:** Configurar a URL base do serviço do WMS Cloud. Por exemplo: `https://<tenant>.wms.ocs.oraclecloud.com/<env>/wms/api` (até o path comum das APIs). Isso permite que nas integrações usemos caminhos relativos para endpoints específicos (como `/init_stage_interface/` ou outros).  

  * **Segurança (Security Policy):** Selecionar **Basic Auth** para autenticação, já que o WMS Cloud por padrão exige usuário e senha nas chamadas REST. Informar as credenciais de um usuário dedicado de integração criado no WMS (detalhes abaixo em 3.3).  

    * *Nota:* O WMS Cloud também suportaria OAuth2 em webhooks de saída, mas para simplificar, usaremos Basic Auth nas duas vias. Certifique-se que a política de segurança escolhida corresponda com o que for configurado do lado do WMS (i.e., se o WMS for chamar o OIC, ele usará Basic Auth com um usuário do OIC).

  * **Teste de Conexão:** Após salvar, usar o botão “Test” para verificar se o OIC consegue alcançar o endpoint do WMS. Isso requer que o IP do OIC esteja liberado no WMS (caso haja lista de permissão) ou que não haja restrição de firewall do lado do WMS Cloud (sendo SaaS, geralmente não há bloqueio de saída).

* **Conexão FTP (SFTP Externo):** Usada para a **carga inicial via arquivos**. O WMS Cloud não hospeda seu próprio SFTP, então utilizaremos ou um SFTP público do próprio OIC (Integration Cloud File Server) ou configuraremos um SFTP server à parte.  

  * **Adapter:** FTP Adapter.  
  * **Role:** Invoke (a conexão FTP será utilizada pelo OIC para ler arquivos, portanto é um “invoke” no fluxo).  
  * **URL/Host:** Informar o host SFTP onde os arquivos CSV estarão disponíveis. Se for o File Server interno do OIC, o host é algo como `<id>.integration.files.oraclecloud.com` com porta 22\. Caso seja um SFTP custom, usar o endereço adequado.  
  * **Credenciais:** Configurar usuário e senha ou chave privada para acesso SFTP. Garantir que essas credenciais tenham permissão de leitura/apagamento nos diretórios de entrada.  
  * **Diretório de Trabalho:** Pode ser especificado nas configurações da conexão ou diretamente no fluxo. Ex: `/WMSInitialLoad` ou conforme estrutura definida.  
  * Após configurar, **testar a conexão** para validar acesso. Subir um arquivo de teste no diretório e verificar se o OIC consegue listá-lo pode ser útil.

  179.191.87.110

  22022

  sftp

* **Conexão Oracle Autonomous DB:** Utilizada para inserir, atualizar e consultar dados no banco autônomo.  

  * **Adapter:** Oracle Database Adapter (ou especificamente o *Oracle Autonomous Transaction Processing Adapter* se listado).  

  * **Role:** Invoke (iremos utilizar o adaptador apenas para operações de saída do OIC – inserções de dados, chamadas de procedures – não faremos polling de DB como trigger).  

  * **Connection Properties:** Fornecer detalhes de conexão:  

    * *Host:* Hostname do Autonomous Database. Pode ser encontrado no string de conexão dentro do wallet (`tnsnames.ora`). Exemplo: `adb.sa-saopaulo-1.oraclecloud.com` (caso público).  
    * *Service Name:* Nome do serviço do banco. Para Autonomous DB, é recomendado usar o serviço **`<dbname>_low`** para workloads de aplicação comuns. Ex: `myadb_low` (o perfil "`low`" geralmente oferece menor consumo de recursos por sessão, adequado para integrações).  
    * *Port:* 1522 (padrão ATP/ADW).  
    * *Wallet:* Marcar a opção de usar wallet (JDBC over SSL). Fazer o upload do arquivo *wallet ZIP* do Autonomous DB e fornecer a senha do wallet. Esse wallet é baixado do console do Autonomous DB ( opção "DB Connection" \> "Download Wallet" ).  
    * *JDBC URL:* Alternativamente, em OIC Gen3, pode-se optar por inserir manualmente a URL JDBC do wallet (string longa contendo `(description= ...)`). Porém, fornecer host/serviço e wallet costuma ser suficiente.

  * **Security:** Selecionar a política **JDBC over SSL** (ou “Oracle Autonomous DB” se houver) para indicar uso de wallet. Em seguida, fornecer:  

    * Nome de usuário do esquema do banco (p. ex., `WMSSTAGE`) e senha. Esse usuário deve ter sido criado previamente no ADB (ver seção 3.2).  
    * Confirmar a senha.  
    * Caso vá se utilizar o recurso de **Bulk Import** do adaptador (carregamento massivo via Object Storage), seria necessário selecionar a opção de segurança **JDBC With OCI Signature** e preencher os campos de OCI (OCID de tenancy, user, etc.). *Para nosso escopo, isso não é obrigatório*, mas deixamos apontado como possibilidade de otimização.

  * **Agent Group:** Deixar em branco se estivermos conectando diretamente (rede pública). Se o ADB estivesse apenas via VCN privada, aqui apontaríamos para um Connectivity Agent configurado no mesmo VCN.  

  * Testar a conexão ao final. Um teste bem-sucedido indica que a rede está ok (considerar que talvez seja preciso liberar o IP do OIC na lista de ACL do ADB se aplicável).

Após essas configurações, o OIC terá as **3 conexões principais** prontas: `WMS_REST_CONN`, `SFTP_CONN` e `ADB_CONN` (nomes sugestivos). Durante o desenvolvimento das integrações, iremos usá-las conforme cada fluxo exigir.

### 3.2 Configuração do Oracle Autonomous Database

No Autonomous Database, as principais configurações envolvem a **preparação do esquema de dados** para receber as informações do WMS e garantir segurança e auditoria.

Os passos incluem:

* **Criação de Usuário e Esquema:** Em vez de usar o usuário ADMIN padrão, é recomendável criar um usuário dedicado, com privilégios limitados apenas ao necessário. Por exemplo, criar um usuário `WMSSTAGE`:  

  CREATE USER OIC IDENTIFIED BY "\<senha\_forte\>" DEFAULT TABLESPACE DATA QUOTA UNLIMITED ON DATA;  

  GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE PROCEDURE, CREATE SEQUENCE TO WMSSTAGE;  

  Aqui usamos o tablespace padrão `DATA` do ADB, com quota ilimitada para simplicidade. Caso deseje, pode-se criar tablespaces específicos (por exemplo, `OIC_DATA` para separar o armazenamento), mas no Autonomous isso não é obrigatório – ele gerencia automaticamente armazenamento e compressão. As permissões concedidas permitem ao usuário criar objetos necessários (tabelas de stage, views, etc.). Não concedemos privilégios desnecessários (como DBA).  

* **Parâmetros e Configurações Adicionais:** O Autonomous Database já vem otimizado e seguro por padrão (criptografia TDE ativada, autoscale opcional, etc.). É importante verificar:  

  * Se necessário, habilitar **Auto Scaling** para lidar com picos de carga (no console do Autonomous DB).  
  * Opcionalmente, ajustar **níveis de serviço** (ex: alterar entre `low`, `medium`, etc. nas conexões do OIC, dependendo do volume – mas em geral `low` é suficiente).  
  * **Auditoria:** O Autonomous Database possui auditoria unificada habilitada. Podemos criar políticas de auditoria custom se quisermos rastrear, por exemplo, cada INSERT nas tabelas de stage. Contudo, isso pode ser custoso. Uma abordagem prática é usar as próprias colunas de auditoria nas tabelas (como *created\_by*, *created\_at*) para rastrear origem e tempo de cada registro. De qualquer forma, garantir que a retenção de auditoria padrão do ADB (baseada em políticas Oracle Cloud) está adequada às necessidades de compliance da empresa.

* **Rede e Acesso:** Se o Autonomous DB for usado via internet pública, assegurar que:  

  * A opção "Permitir conexões seguras com IPs de qualquer lugar" esteja habilitada **OU** que a lista de redes permitidas inclua o intervalo de IPs do OIC. Para ambiente de teste, pode-se liberar geral; em produção, é recomendável restringir.  
  * Caso use Private Endpoint (dentro de VCN), o OIC não conseguirá acessar diretamente sem um agente. Neste caso, seria necessário configurar um **Connectivity Agent** dentro da VCN. Como mencionado, assumiremos acesso público com wallet para simplificar.

* **Schema de Destino:** Confirmar que o usuário `WMSSTAGE` (ou nome escolhido) será o mesmo configurado na conexão OIC (Security \-\> username). O adaptador do OIC irá se autenticar como esse usuário e todas as operações (inserir, selecionar) ocorrerão nesse esquema. Logo, todo objeto de stage deve ser criado sob esse usuário.  

* **Tabelas e Objetos de Stage:** Ainda na configuração de ambiente, planejar a criação das tabelas de stage. Embora o detalhe de modelagem seja discutido na seção 4, vale executar os scripts de DDL neste momento no Autonomous DB. Por exemplo:  

  \-- tabela de cabeçalho de pedidos (stage)  

  CREATE TABLE WMSSTAGE.ORDER\_HDR\_STAGE (  
      BATCH\_ID     VARCHAR2(50),  
      ORDER\_NBR    VARCHAR2(50),  
      ORDER\_TYPE   VARCHAR2(30),  
      COMPANY\_CODE VARCHAR2(20),  
      FACILITY\_CODE VARCHAR2(20),  
      ORDER\_DATE   DATE,  
      DESTINATION  VARCHAR2(100),  
      \-- ... outros campos relevantes do pedido ...  
      STATUS       VARCHAR2(20),  
      CREATED\_BY   VARCHAR2(30),  
      CREATED\_AT   TIMESTAMP DEFAULT SYSTIMESTAMP,  
      PROCESSED\_FLAG CHAR(1) DEFAULT 'N',  
      PROCESSED\_AT TIMESTAMP  
  );  

  ALTER TABLE WMSSTAGE.ORDER\_HDR\_STAGE ADD CONSTRAINT PK\_ORDER\_HDR\_STAGE PRIMARY KEY (ORDER\_NBR);  

  A tabela acima (exemplo) contém campos típicos de um pedido: número, tipo, empresa, data, etc., mais colunas de auditoria. O campo `BATCH_ID` pode agrupar registros de uma mesma carga (útil se inserirmos vários pedidos juntos) e `PROCESSED_FLAG`/`PROCESSED_AT` indicam se o registro já foi transformado/movido para tabela definitiva ou consumido por outro processo.  

  **Obs:** Não executar ainda – esta é apenas uma ilustração de DDL; a modelagem completa vem adiante em seção 4 e 5\. Porém, deixar o script preparado faz parte da configuração inicial.  

* **Testes de Acesso:** Do lado do Autonomous DB, após criar o usuário e objetos, testar conectividade a partir de uma máquina cliente usando o wallet, para confirmar que o serviço está acessível. Isso pode ser feito localmente via SQL\*Plus ou SQL Developer usando o wallet, ou até via o utilitário `curl` com TLS para testar se porta está aberta. Contudo, o teste definitivo virá do OIC (já realizado ao configurar a conexão, conforme acima).

Resumindo, ao fim da configuração do Autonomous DB, teremos:

* Usuário de banco dedicado (e credenciais seguras guardadas no OIC).  
* Tabelas de stage criadas (mesmo que inicialmente vazias).  
* Medidas de segurança ativas (wallet para conexão criptografada, IPs autorizados, etc.).  
* Ambiente de banco pronto para receber os scripts de transformação mais adiante.

### 3.3 Configuração no Oracle WMS Cloud (Webhooks e Usuários)

Para que o WMS Cloud participe da integração, precisamos garantir dois pontos: **acesso via API** (para o OIC chamar o WMS) e **configuração de webhooks (interfaces de saída)** para o WMS chamar o OIC nos eventos desejados.

* **Usuário de Integração no WMS:** No Console/UI do WMS Cloud, criar ou identificar um usuário específico para integrações (por exemplo, usuário `INT_OIC`). Esse usuário deve ter as permissões adequadas para uso das APIs REST. Conforme a documentação, é necessário habilitar a permissão global **“can\_run\_ws\_stage\_interface”** para que o usuário possa invocar os web services de integração no WMS. Além disso, atribuir ao usuário acesso (eligibilidade) às empresas/facilidades necessárias, pois o WMS valida isso em cada chamada. Definir uma senha forte para este usuário. Esse usuário e senha serão usados na conexão REST no OIC (Basic Auth) para chamadas do OIC \-\> WMS.  

* **Configuração de Webhook (Output Interface) para Pedidos:** O WMS Cloud possui um framework de **“Output Interface”** onde podemos configurar interfaces de saída para diversos eventos. Para capturar novos pedidos ou atualizações de pedidos:  

  * Acesse o menu de **Endpoint** no WMS (possivelmente "Output Interface Configuration").  

  * Localize o **interface type** relacionado a **Orders**. No WMS Cloud, pedidos de venda (Sales Orders) normalmente correspondem ao objeto "Orders" ou "Order Header". Pode existir uma interface padrão chamada "Orders" (conforme visto em documentação de touchpoints).  

  * Crie (ou edite) uma configuração de saída para Orders:  

    * **Protocolo:** selecionar **REST Web Service** como destino.  

    * **URL de Destino:** informar a URL do endpoint exposto pelo OIC que irá receber os pedidos. Esse endpoint será gerado quando desenvolvermos a integração de pedidos no OIC (ex: algo como `https://<OIC-instance>/ic/api/integration/v1/flows/rest/ORDER_INBOUND/v01/newOrder`). Neste momento, pode ser um placeholder até termos o fluxo criado; posteriormente atualizaremos com a URL real do OIC.  

    * **Autenticação:** escolher o método. O OIC, ao expor um endpoint REST, por padrão requer Basic Auth (usuário/senha do OIC) a não ser que configuremos para não exigir. Recomenda-se proteger, então:  

      * No WMS, em *Interface Authentication Type*, escolher **Basic Auth**.  
      * Informar o **usuário e senha do OIC** que devem ser usados. Podemos criar um usuário de integração no OIC (ou usar um já existente) exclusivamente para que o WMS se autentique. Ex: usuário `OIC_INT` com senha gerada. **Atenção:** Armazenar essa senha no WMS significa que o WMS irá enviá-la a cada chamada – verifique se o canal HTTPS está ativo (estará, pois WMS só chama via HTTPS).

    * Campos OAuth2 (Client ID, Secret, etc.) não são necessários se Basic Auth for escolhido (são opcionais e ficam escondidos nesse caso).  

    * **Headers/Payload:** configurar se necessário algum header específico. Geralmente, o WMS envia conteúdo XML ou JSON no corpo. Podemos forçar um header `Content-Type: application/json` se quisermos JSON, ou deixar padrão para XML. Decidiremos o formato de payload de pedidos – para facilitar no OIC, podemos preferir JSON. Se o WMS suportar JSON na saída (o que é provável, visto que as APIs REST costumam aceitar/enviar JSON ou XML), podemos configurá-lo. Caso contrário, receberemos XML e o OIC converterá.  

    * **Teste:** Se a interface do WMS permite um teste manual (por ex., “retransmitir último registro”), usar após configurar o fluxo OIC para validar que a chamada chega.

  * **Trigger de Evento:** Ainda na config da interface de Orders, garantir que ela seja acionada nos eventos desejados. Provavelmente, há um checkbox ou sub-configuração indicando que sempre que um pedido for **criado ou atualizado** no WMS, deve-se gerar a saída. Podemos optar por apenas criação inicialmente (para não enviar múltiplas vezes). Configurar filtros se aplicável (por ex, somente pedidos de certo tipo ou companhia).

* **Configuração de Webhook para Alocações:** Similar ao acima, configurar uma Output Interface para eventos de **Allocation**. Precisamos identificar no WMS qual interface corresponde às alocações de estoque. Possibilidades:  

  * O WMS pode não ter “allocation” como entidade direta de interface. A alocação é parte da atividade de um pedido ou de inventário. Contudo, muitos WMS geram **Inventory History** records quando há alocação. Outra saída possível: “Wave Pick Info” ou “Order Allocation” se existir.  

  * Verificando a documentação de touchpoints, vemos "Inventory History – All WMS activities". Uma estratégia: configurar uma interface de *Inventory History* para sair quando ocorrerem eventos do tipo "ALLOCATE". No WMS, Inventory History registra transações como alocação (commit), deallocação, consumo, etc., e cada uma tem um código de transação.  

  * Assim, criar uma interface de saída para **Inventory History** ou similar, com REST/BasicAuth apontando para um endpoint do OIC (ex: `.../flows/rest/ALLOC_INBOUND/v01/newAlloc`). Adicionar um filtro se possível para incluir apenas transações de tipo "Alloc" (pode ser por código de transaction\_type ou descrição).  

  * Se o WMS Cloud tiver nativamente um objeto “Allocation” para interface (menos provável), utilizar diretamente. De qualquer forma, configurar similarmente a autenticação e formato como feito para Orders.  

  * **Formato do Payload:** Para allocations, provavelmente o WMS enviará dados como: Order number, Item, Quantity allocated, maybe allocation ID or location. Podemos confirmar via documentação ou testes. Supondo que venha em formato JSON:  

    `{`  

      `"company_code": "YOURCO",`  
      `"facility_code": "WH1",`  
      `"order_nbr": "ORD12345",`  
      `"item_alternate_code": "PROD001",`  
      `"allocated_qty": 100,`  
      `"allocation_ts": "2025-05-08T15:30:00Z"`  
    `}`  

    (Exemplo ilustrativo de um payload JSON de alocação.)  

  * Salvar a configuração.

* **Outras Configurações WMS:** Certificar que o WMS Cloud tenha as **Interface Specifications (XSDs/CSVs)** atualizadas para referência. Embora não necessário para execução, obter os XSDs de *Orders* e *Inventory History* pode ajudar a validar campos. Isso está disponível no Oracle Support, conforme nota, mas não detalharemos aqui. Apenas nos asseguramos de alinhar os campos do payload com os das tabelas de stage.  

* **Calendário de Execução:** Configurar no WMS, se aplicável, janelas de execução das interfaces. Muitas integrações podem ser contínuas (event-driven), mas se houver alguma dependência (ex: só liberar dados após um cut-off diário), ajustar no WMS ou OIC.

Com isso, o ambiente WMS Cloud estará preparado para: **aceitar chamadas do OIC** (via usuário de integração e API) e **enviar chamadas ao OIC** (via webhooks configurados para Orders e Allocations).

## 4\. Modelagem das Tabelas de Stage

A modelagem das tabelas de stage no Autonomous Database é crucial para acomodar os dados vindos do WMS Cloud de forma organizada e permitir transformações eficientes. As tabelas de stage atuarão como “área de pouso” dos dados brutos da integração, antes de serem transformados ou consumidos por outros componentes (relatórios, views, etc.). A seguir, detalhamos a estrutura física sugerida para as principais entidades:

### 4.1 Princípios de Modelagem

* **Espelhamento dos Dados do WMS:** As tabelas de stage conterão colunas correspondentes a praticamente todos os campos relevantes enviados pelo WMS nas interfaces. Por exemplo, se o WMS envia 10 campos no payload de pedido (order\_nbr, order\_type, data, etc.), a tabela stage de pedido terá colunas para esses 10 campos. Isso evita perda de informação e facilita auditoria.  

* **Colunas de Auditoria Padrão:** Incluir colunas adicionais em cada tabela para rastrear a integração:  

  * `BATCH_ID` – identifica o lote ou transação de carga (pode ser preenchido, por exemplo, com um identificador de arquivo CSV ou um UUID gerado a cada chamada do OIC).  
  * `CREATED_AT` / `CREATED_BY` – timestamp e usuário do banco que inseriu o registro. No caso, o OIC ao inserir pode definir o usuário (será WMSSTAGE) e podemos usar default `SYSTIMESTAMP` para data.  
  * `PROCESSED_FLAG` / `PROCESSED_AT` – para indicar se aquele registro já foi processado posteriormente pelas transformações no DB. Por exemplo, podemos marcar ‘N’ quando insere e depois, ao aplicar uma procedure que consolida dados, marcar ‘Y’ e timestamp. Isso evita retrabalho em caso de reprocessamento ou duplicidade.  
  * `ERROR_MSG` – opcional, para registrar mensagem de erro de validação se algum dado estiver inconsistente.

* **Chaves Primárias e Índices:** Definir chaves primárias adequadas. Por exemplo, para Order Header Stage, a PK pode ser `ORDER_NBR` (assumindo que dentro de uma mesma empresa não haja duplicidade). Se compõem chave (company\_code \+ order\_nbr), incluir ambas. Para Order Detail Stage, a PK pode ser composta por `ORDER_NBR + LINE_NBR` (ou `seq_nbr`). Definir índices em colunas de junção (por ex, index em order\_nbr em detalhe para join com header).  

* **Nomenclatura:** Usar um sufixo ou prefixo consistente para diferenciar stage tables. Exemplo: suffix `_STAGE` (ORDER\_HDR\_STAGE, ORDER\_DTL\_STAGE, ALLOC\_STAGE). Ou prefixo like `STG_`. No exemplo aqui adotamos `_STAGE` para clareza.  

* **Normalização vs Desnormalização:** Como se trata de estágio, podemos desnormalizar alguns campos para facilitar consultas rápidas. Mas de modo geral seguiremos o modelo fonte: Order header separado do detail, já que teremos possivelmente múltiplas linhas por pedido e queremos refletir isso.

### 4.2 Estrutura das Tabelas

**Tabela 1: ORDER\_HDR\_STAGE** – Representa o cabeçalho do pedido de venda integrado do WMS.

* `ORDER_NBR` (PK): Número do pedido (identificador único no contexto da empresa WMS).  

* `COMPANY_CODE`: Código da companhia no WMS (multi-empresa).  

* `FACILITY_CODE`: Código da instalação (armazém) onde o pedido será atendido.  

* `ORDER_TYPE`: Tipo do pedido (e.g. "SO" para Sales Order, "TR" transferência, etc., conforme codificação do WMS).  

* `ORDER_DATE`: Data de criação do pedido (pode ser data de pedido ou data de chegada prevista, dependendo do contexto).  

* `DESTINATION`: Destino do pedido (pode ser código de loja, cliente ou endereço).  

* `STATUS`: Status inicial do pedido (ex: "CREATED", "ALLOCATED", etc.).  

* Campos adicionais conforme necessário: por exemplo `PRIORITY`, `ROUTE`, etc., se existirem no WMS.  

* Auditoria:  

  * `CREATED_AT` (timestamp, default SYSTIMESTAMP).  
  * `CREATED_BY` (usuário, default ‘OIC’ ou podemos preencher com OIC instance id).  
  * `PROCESSED_FLAG` (char(1), default 'N').  
  * `PROCESSED_AT` (timestamp).

Chave primária: (`ORDER_NBR`, `COMPANY_CODE`, `FACILITY_CODE`) – assumindo combinação única. Se `COMPANY_CODE` e `FACILITY_CODE` forem sempre iguais (muitos casos têm uma empresa e um warehouse), poderíamos simplificar a PK para `ORDER_NBR` apenas.

**Tabela 2: ORDER\_DTL\_STAGE** – Itens detalhados do pedido.

* `ORDER_NBR` (PK parte 1, FK para ORDER\_HDR\_STAGE.ORDER\_NBR).  

* `LINE_NBR` ou `SEQ_NBR` (PK parte 2): número de linha do pedido.  

* `ITEM_CODE` ou `ITEM_ALT_CODE`: Código do item (SKU) conforme enviado pelo WMS. Usar o mesmo campo que o WMS envia, muitas vezes `item_alternate_code` é usado para SKU externo.  

* `ORDERED_QTY`: Quantidade solicitada.  

* `ALLOCATED_QTY`: Quantidade alocada (inicialmente pode ser 0 se nada alocado ainda, ou WMS pode já mandar se alocou simultâneo).  

* `UOM`: Unidade de medida (ex: EA, CS).  

* Possíveis campos adicionais: `UNIT_PRICE`, `LOT_NUMBER` (se relevante), etc., dependendo se WMS repassa ao integrar.  

* Auditoria: mesclar campos audit também:  

  * `CREATED_AT`, `CREATED_BY`, `PROCESSED_FLAG`, `PROCESSED_AT` – todos similares à tabela de header.

Chave primária: (`ORDER_NBR`, `LINE_NBR`) – garantindo unicidade por linha.

Índice sugerido: Em `ORDER_NBR` para facilitar junção e busca de todas linhas de um pedido.

**Tabela 3: ALLOC\_STAGE** – Representa uma alocação de estoque realizada. Cada alocação tipicamente refere-se a um item de um pedido reservado em certa quantidade.

* `ALLOC_ID`: Identificador da alocação (se o WMS fornece; talvez combine order+item+timestamp se não houver id).  
* `ORDER_NBR`: Referência ao pedido relacionado (pode não ser PK porque um pedido terá várias alocações).  
* `LINE_NBR`: Linha do pedido relacionada (se for possível identificar qual linha foi alocada; útil se mesmo item aparece em duas linhas).  
* `ITEM_CODE`: Item alocado.  
* `ALLOC_QTY`: Quantidade alocada.  
* `ALLOC_TS`: Timestamp da alocação (quando ocorreu).  
* `SOURCE_LOC`: Local de estoque de onde foi alocado (por ex., código de localização ou LPN, se o WMS mandar).  
* `BATCH_NBR` / `LOT` / `SERIAL`: Se controlado por lote ou serial, incluir campos para guardar essa informação vinda do WMS.  
* Auditoria: `CREATED_AT`, `CREATED_BY` (quando inserido no stage – possivelmente coincide com ALLOC\_TS), etc., e `PROCESSED_FLAG/AT`.

Chave primária: pode ser um surrogate key (gerar um sequence e usar em ALLOC\_ID), ou usar combinação de campos naturais (order+item+ts). Preferível criar uma sequence no DB para ALLOC\_ID (usando `GENERATED BY DEFAULT AS IDENTITY` no Oracle 19c+). Ex:

ALLOC\_ID NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY

Assim cada registro tem um identificador único.

Índices: index em `ORDER_NBR` (para buscar todas alocações de um pedido) e possivelmente em `ITEM_CODE` se consultas por item forem necessárias.

**Outras tabelas de stage (menções breves):**

* Se eventualmente integrarmos **Inventory History** completo, poderíamos ter `INV_HISTORY_STAGE` com colunas para qualquer evento de inventário.  
* Se integrarmos **Shipments (expedições)**, uma tabela `SHIPMENT_STAGE` com cabeçalho e detalhe (itens embarcados).  
* Se integrarmos **Recebimentos** (ASN/Receipt), tabelas `RECEIPT_STAGE`, etc.  
* O padrão de modelagem seria similar: replicar campos do WMS, acrescentar audit.

### 4.3 Relacionamentos e Integridade

Para garantir integridade referencial básica no stage:

* Definir **foreign keys** como mencionado (ORDER\_DTL\_STAGE.order\_nbr referenciando ORDER\_HDR\_STAGE.order\_nbr). Assim, não teremos linhas órfãs de pedido.  
* A tabela ALLOC\_STAGE referenciando ORDER\_HDR\_STAGE (e possivelmente DTL). Se a alocação vier relacionada a uma linha específica, podemos referenciar order\_nbr+line\_nbr. Se não, pelo menos order\_nbr.  
* Essas FKs podem ser definidas como *DEFERRABLE INITIALLY DEFERRED* se quisermos carregar em qualquer ordem e validar ao final da transação, mas como OIC insere por fluxo (provavelmente insere header depois detalhes numa mesma integração), podemos manter standard.

Exemplo FK:

ALTER TABLE WMSSTAGE.ORDER\_DTL\_STAGE

ADD CONSTRAINT FK\_ODTL\_ORDER

FOREIGN KEY (ORDER\_NBR) REFERENCES WMSSTAGE.ORDER\_HDR\_STAGE(ORDER\_NBR);

* **Chaves de Negócio vs Técnicas:** Lembrar que as PKs aqui são mais para integridade interna. As chaves naturais (como ORDER\_NBR) vêm do sistema externo; colisões só ocorreriam se WMS mandasse o mesmo pedido duas vezes. Podemos permitir duplicatas se precisarmos registrar várias versões (ex: reprocessamento), mas nesse caso usaríamos uma PK técnica e um campo version. Contudo, para simplificar, assumimos que o WMS não enviará duplicado de um pedido (a menos que seja atualização, que iremos tratar com UPSERT logic no OIC, discutido em seção 7).

Em suma, as tabelas de stage devem capturar fielmente os dados do WMS e adicionar o mínimo necessário para controle de processamento e integridade. A modelagem aqui proposta garante isso, seguindo padrões de auditoria comuns em integrações.

## 5\. Carga Inicial via FTP/CSV

Antes de ativarmos os webhooks e integrações em tempo real, realizaremos uma **carga inicial** dos dados existentes do WMS Cloud para o Autonomous DB. O objetivo é popular o banco autônomo com o estado atual (baseline) – por exemplo, todos os pedidos pendentes e suas linhas, e possivelmente status de alocação até o momento – garantindo que, a partir daí, apenas incrementos sejam aplicados. Esta carga inicial será feita via arquivos CSV pelo seguinte motivo: possibilita transferir volumes grandes de forma eficiente e com controle, e o WMS já fornece mecanismos de import/export flat file.

**Estratégia de Extração do WMS:**

* Utilizar o recurso de **relatórios ou interfaces batch** do WMS Cloud para gerar arquivos dos dados atuais. O WMS Cloud oferece templates de Excel/CSV para diversas entidades. Em especial, podemos usar:  

  * **Input Interface Screen (UI):** Via tela do WMS, exportar a lista de pedidos em formato CSV (seguindo o layout de interface "Orders"). Como alternativa, se o WMS tiver um **job de export** (por exemplo, “Download Interface Data”), agendá-lo.  
  * **Formato:** Idealmente gerar dois arquivos: um para Order Header (ex: `Orders_Header.csv`) e outro para Order Detail (`Orders_Detail.csv`), já que as interfaces muitas vezes separam. Se o WMS fornecer um único arquivo hierárquico, também é possível (mas o OIC consegue processar separado igualmente).  
  * **Conteúdo:** Incluir todos os pedidos relevantes. Podemos filtrar por status (ex: só pedidos não entregues) para não trazer históricos fechados, a menos que necessário para data warehouse completo. Confirmar que o delimitador é consistente (padrão Oracle é pipe `|` ou vírgula, conforme config).  
  * **Local de Armazenamento:** Configurar o WMS Cloud para **enviar o arquivo para um SFTP externo**. Isso pode ser feito criando uma **Output Interface** do tipo SFTP. Por exemplo, configurar uma interface "Outbound Load shipment" ou uma custom para Orders, mas em vez de REST, selecionar protocolo SFTP e informar host/credenciais (as do nosso servidor SFTP definido). Alternativamente, fazer download manual via UI e depois upload para o SFTP, se volume for manejável.

**Processo no OIC para carga inicial:**

* Criar uma integração agendada (Scheduled Orchestration) chamada *“InitialLoadOrders”*. Essa integração será do tipo **Schedule** (no OIC Gen3, podemos configurar para rodar uma vez ou sob demanda).  

* **Trigger (Schedule):** Início manual ou imediato.  

* **Leia Arquivo de Header:** Usando a conexão FTP, configuramos um leitor de arquivo:  

  * Diretório e nome: ex: `/initial_load/Orders_Header.csv` (poderíamos também usar mascará tipo `Orders_Header*.csv` se quisermos pegar com timestamp).  
  * Formato: delimited. O FTP adapter do OIC permite definir o esquema de um CSV. Podemos definir os campos de acordo com as colunas esperadas (empresa, pedido, data, etc.). Esse mapeamento pode ser facilitado se tivermos um arquivo de exemplo e usar a opção de *Generated Schema* a partir do CSV no OIC.  
  * O OIC lerá e produzirá uma coleção de registros (cada linha \-\> um objeto de dados no integration).

* **Leia Arquivo de Detalhe:** Similar ao header, pegar `Orders_Detail.csv`. Este passo poderá ser aninhado: ou lemos todos detalhes em memória ou, melhor, para evitar consumo, podemos processar streaming. Por simplicidade, podemos primeiro ler todos headers e armazenar, depois ler detalhes.  

* **Mapeamento e Inserção:** Para cada registro de header lido, invocar a conexão Database (ADB) para inserir na tabela ORDER\_HDR\_STAGE. Podemos usar a operação **“Run a SQL Statement”** com um SQL parametrizado:  

  INSERT /\*+ APPEND \*/ INTO WMSSTAGE.ORDER\_HDR\_STAGE

  (ORDER\_NBR, COMPANY\_CODE, FACILITY\_CODE, ORDER\_TYPE, ORDER\_DATE, DESTINATION, STATUS, CREATED\_BY)  

  VALUES (:order\_nbr, :company, :facility, :order\_type, :order\_date, :dest, :status, 'INITIAL\_LOAD');  

  Os bind `:order_nbr` etc. vêm dos campos lidos. Usamos um hint `APPEND` para performance (inserção direta) dado volume, e marcamos CREATED\_BY como 'INITIAL\_LOAD' para diferenciar.  

  * Em OIC, podemos optar pelo modo **Batch** do adapter de banco, que suporta inserir múltiplos registros em lote. Nesse caso, passar a lista de registros lidos diretamente para a inserção em batch, o que é eficiente.  
  * Repetir o processo para cada registro de detalhe: inserir em ORDER\_DTL\_STAGE. Garantir que cabeçalhos sejam inseridos primeiro para obedecer FK (ou desativar FK até terminar carga).

* **Validação e Logging:** Após inserções, podemos contar quantos registros inseridos e logar no OIC (Log ação). Comparar com contagem de linhas no arquivo para consistência.  

* **Marcar processado ou mover arquivos:** Uma boa prática é, após sucesso, mover os arquivos para um diretório de *archive* no SFTP (ex: `/archive/Orders_Header_20250508.csv`). O OIC via FTP adapter pode renomear/mover. Assim evitamos releitura acidental.  

* **Carga de Alocações (se aplicável):** Se quisermos também carregar histórico de alocações já existentes, poderíamos repetir o processo para um arquivo de Inventory History ou Allocation. Contudo, se os pedidos estavam pendentes, provavelmente todas alocações serão reprocessadas de qualquer forma no evento. Poderíamos omitir para simplificar a carga inicial e deixar que as alocações se populassem apenas via eventos daqui em diante.

**Desempenho na carga inicial:** Caso os arquivos sejam muito grandes (ex: dezenas de milhares de linhas), considere:

* O adaptador de DB do OIC suporta **Bulk Import** nativamente, que usa o recurso de copiar CSV direto para o Autonomous DB. Isso exige usar o security *OCI Signature* e fornecer detalhes de Object Storage. Uma implementação possível seria: OIC lê o CSV e o salva em um bucket de Object Storage, então aciona a operação **Import Bulk Data** do adaptador. Dado o tempo e complexidade, essa otimização pode ser feita se o volume exigir (digamos \> 100k registros). Para volumes menores, o batch insert dentro do OIC é suficiente.  
* Paralelismo: Podemos paralelizar leitura de header e detail se necessário usando stage files ou independent integrations, mas depois precisamos juntar. Talvez não valha a pena – a simplicidade de fazer sequencial e transacionalmente consistente é preferível.

**Execução:** Rodar a integração de carga inicial e monitorar no OIC. Esperar completar e então, no Autonomous DB, realizar queries de validação, por exemplo:

SELECT COUNT(\*) FROM WMSSTAGE.ORDER\_HDR\_STAGE;

SELECT COUNT(\*) FROM WMSSTAGE.ORDER\_DTL\_STAGE;

Comparar com o esperado. Conferir alguns registros amostrais para ver se dados fazem sentido.

Após essa etapa, o Autonomous DB terá o espelho inicial. Podemos agora prosseguir para configurar integrações contínuas sabendo que a base histórica está pronta.

## 6\. Configuração de Webhooks no WMS Cloud

*(Nota: Parte desse tópico já foi endereçada na seção 3.3, mas aqui recapitulamos e aprofundamos especificamente no funcionamento dos webhooks no WMS Cloud.)*

**Webhooks**, no contexto do WMS Cloud, são implementados via o mecanismo de **Output Interfaces** configuráveis. Cada Output Interface define: um tipo de dado a ser enviado (Orders, Shipments, etc.), um meio de transporte (REST, SFTP, etc.), e credenciais. Já configuramos os alvos (endpoints do OIC) na seção de ambiente. Agora, detalhamos considerações de funcionamento e finalização da configuração:

* **Ativação e Teste das Interfaces de Saída:**  

  * Apos criar as interfaces de saída para *Orders* e *Allocations*, é preciso garantir que elas estejam **ativas**. Verifique na tela do WMS Cloud se há um campo "Enabled/Disabled". Marque como Enabled.  
  * **Teste de Orders:** Uma forma controlada de testar é criar um pedido dummy no WMS (via UI ou via upload Excel) e verificar se o OIC recebe. Se o OIC já tiver a integração de recebimento publicada (ver próxima seção 7.1), você verá a instância disparar. Alternativamente, se a integração do OIC não estiver pronta, usar uma ferramenta como Postman para captar a chamada – substituindo a URL por um webhook.site temporário, por exemplo – só para checar se WMS consegue enviar.  
  * **Teste de Allocations:** Similarmente, realizar uma ação no WMS que gere alocação (por ex: alocar manualmente um pedido, ou criar um wave de picking) e ver se a chamada de saída ocorre. Pode ser útil habilitar logs no WMS: geralmente há uma tela de **Interface Transmissions** onde é possível ver registros de envio (sucesso/erro, timestamp, mensagem). Checar nessa tela se após os testes há registros.

* **Estrutura dos Payloads de Webhook:**  

  * **Orders:** Quando configurado para REST, o WMS Cloud deverá enviar o conteúdo do pedido recém criado em formato JSON ou XML. A documentação Oracle sugere que as APIs retornam dados em XML por padrão, porém, ao fazer um POST via Output Interface, o WMS pode enviar uma representação JSON (especialmente se Content-Type JSON for especificado). Precisamos estar preparados para ambos no OIC.  

    * Um exemplo de payload (XML) de pedido que poderíamos receber:  

      \<Order\>  
        \<order\_hdr\>  
          \<company\_code\>YOURCO\</company\_code\>  
          \<facility\_code\>WH1\</facility\_code\>  
          \<order\_nbr\>ORD0001\</order\_nbr\>  
          \<order\_type\>SO\</order\_type\>  
          \<order\_date\>2025-05-08T12:00:00Z\</order\_date\>  
          \<destination\>DROGARIA A\</destination\>  
          \<status\>Created\</status\>  
          ... outros campos ...  
        \</order\_hdr\>  
        \<order\_dtl\>  
          \<order\_nbr\>ORD0001\</order\_nbr\>  
          \<seq\_nbr\>1\</seq\_nbr\>  
          \<item\_alternate\_code\>ITEM123\</item\_alternate\_code\>  
          \<orig\_qty\>5\</orig\_qty\>  
          \<uom\>EA\</uom\>  
          ...
        \</order\_dtl\>  
        \<order\_dtl\>  
          \<order\_nbr\>ORD0001\</order\_nbr\>  
          \<seq\_nbr\>2\</seq\_nbr\>  
          \<item\_alternate\_code\>ITEM124\</item\_alternate\_code\>  
          \<orig\_qty\>2\</orig\_qty\>  
          \<uom\>EA\</uom\>  
        \</order\_dtl\>  
      \</Order\>  

      Este XML hierárquico traz um `<order_hdr>` seguido de um ou mais `<order_dtl>`. No caso JSON, seria análogo com um objeto contendo um array de linhas. O OIC integrará esse payload (ver 7.1).

  * **Allocations:** O payload de alocação possivelmente virá como parte de um objeto de histórico de inventário. Pode ser simples (como o JSON exemplo dado anteriormente) ou conter muitos campos irrelevantes. Precisaremos filtrar no OIC. Por exemplo, se vier um XML `<inventory_history>` contendo `<transaction_type>ALLOCATE</transaction_type>` e detalhes do item, usaremos apenas os campos necessários para nossa tabela ALLOC\_STAGE.

* **Autenticação do Webhook:** Como configurado, o WMS incluirá a autenticação Basic no header da requisição. O OIC, ao publicar o endpoint REST, deverá ter segurança Basic. Garantir que as credenciais batem. Uma dica: criar no OIC uma conta de acesso específica e usar essa no WMS, para segregar permissões.  

* **Retries e Garantia de Entrega:** É importante entender como o WMS lida com falhas ao chamar o webhook:  

  * Se o OIC estiver indisponível (por exemplo, fora do ar ou retornou erro 500), o WMS vai registrar uma falha na interface. Por padrão, o WMS **não re-tenta automaticamente indefinidamente**. Ele marca o status como erro. No entanto, a Oracle oferece a API **update\_output\_interface** para que sistemas externos sinalizem status de processamento – por exemplo, o OIC poderia chamá-la em caso de erro para informar falha. Essa mesma API permite solicitar reenvio definindo `run_output_interface_flg=true` e status adequado.  
  * Estratégia de retry: Podemos implementar no OIC, em caso de falha ao inserir no DB, uma lógica de reprocessamento (ver seção 7.3 sobre tratamento de erros). Mas se o OIC estiver totalmente indisponível, precisaríamos reprocessar do lado WMS. Nesse caso, teremos que **manualmente reativar** via UI do WMS (há opção "Reprocess/Resend" no registro da interface) ou automatizar via *update\_output\_interface*.  
  * Para robustez, documentaremos um procedimento operacional: verificar diariamente interfaces de saída com erro no WMS (pela UI), e reprocessar se necessário. Em paralelo, planeja-se configurar alertas (seção 10\) para notificar tais ocorrências.

* **Segurança dos Dados:** Os webhooks trafegam via HTTPS, então em trânsito os dados estão cifrados. O WMS Cloud valida o certificado do OIC (que é válido por ser serviço Oracle Cloud). Não usar endpoints HTTP inseguros. Além disso, garantir que nenhuma informação sensível além do necessário esteja no payload – pedidos e alocações geralmente não têm PII sensível, mas de toda forma, os canais são seguros.

Em resumo, a configuração de webhooks no WMS Cloud estabelece a **conexão reativa** do WMS para o OIC. Com as interfaces de saída de Orders e Allocations devidamente configuradas e testadas, o WMS atuará como um **emissor de eventos** que disparará as integrações do OIC sempre que um novo pedido for criado ou uma alocação de estoque ocorrer, completando assim o elo de integração em tempo real.

## 7\. Desenvolvimento das Integrações no OIC

Com ambiente e modelagem prontos, passamos ao desenvolvimento dos fluxos de integração no Oracle Integration Cloud. Serão construídas principalmente duas integrações orquestradas: uma para **Processamento de Pedidos** (pedido e suas linhas) e outra para **Processamento de Alocações**, além de implementar mecanismos transversais de **segurança e tratamento de erros**. A seguir, cada integração é detalhada, incluindo lógica de mapeamento, transformações e chamadas.

### 7.1 Integração de Processamento de Pedidos (Order\_HDR e Order\_DTL)

**Nome da Integração:** `WMS_Order_Inbound_Int` (por exemplo). Essa integração terá a responsabilidade de receber os dados de um pedido (cabeçalho \+ detalhes) do WMS Cloud via webhook e gravá-los nas tabelas de stage correspondentes no Autonomous DB. Também deverá lidar com pedidos duplicados ou atualizações.

**Gatilho (Trigger):** REST endpoint exposto no OIC, vinculado à conexão REST configurada para WMS.

* Método: provavelmente **POST**.  

* Caminho: definir algo como `/order` ou `/orders/new` dependendo de convenção.  

* Segurança: Basic Auth (conforme configurado).  

* Request Payload: configurar o esquema de entrada. Aqui podemos simplificar definindo o tipo como JSON genérico e depois ajustando no mapeamento. Alternativamente, podemos fornecer um exemplo de payload ou XSD para gerar o modelo. Como definimos no WMS usar JSON, vamos supor um JSON:  

  {  

    "order\_hdr": { ... campos ... },  

    "order\_dtl": \[ { ... campos ... }, { ... } \]  

  }  

  O OIC então terá um objeto com `order_hdr` e uma lista `order_dtl`. Se vier XML, o adaptador REST do OIC pode ser configurado para aceitar XML também (ele fará conversão automática para um tree).  

* Response: Podemos retornar um simples 200 OK com um status message ao WMS. O WMS não necessariamente usa essa resposta, mas se configurado, ele pode registrar a resposta. Um JSON de confirmação do tipo `{ "received": true, "order_nbr": "ORD123" }` pode ser enviado.

**Fluxo de Lógica:**

1. **Recepção:** O OIC recebe o pedido via trigger. Imediatamente, podemos registrar (no Tracking) algum identificador – por exemplo, o número do pedido – usando a funcionalidade de *business identifiers* do OIC, para facilitar busca posterior de instâncias.  

2. **Mapeamento do Cabeçalho:** Extrair do payload os campos do cabeçalho. O OIC mapeia esses campos para os parâmetros da instrução de banco ou para um objeto representando a tabela. Exemplo de transformação:  

   * `order_hdr.order_nbr` \-\> DB column `ORDER_NBR`  
   * `order_hdr.company_code` \-\> `COMPANY_CODE`  
   * etc., conforme definidas na tabela ORDER\_HDR\_STAGE.  
   * Adicionar campos adicionais: `CREATED_BY = 'WMS_WEBHOOK'` (indicando origem) e possivelmente `BATCH_ID`. O BATCH\_ID podemos gerar como um GUID ou usar algum identificador do WMS se disponível (p.ex., WMS às vezes fornece um `message_id`).

3. **Inserção do Cabeçalho no DB:** Usar conexão `ADB_CONN`:  

   * Escolher operação **“Run a SQL Statement”** (simples) ou **“Perform an Operation on Table”** (que pode diretamente mapear ao insert).  

   * Se usar SQL custom, exemplo:  

     MERGE INTO WMSSTAGE.ORDER\_HDR\_STAGE tgt  

     USING (SELECT :order\_nbr as ORDER\_NBR, :comp as COMPANY\_CODE, :fac as FACILITY\_CODE, ... FROM DUAL) src  

     ON (tgt.ORDER\_NBR \= src.ORDER\_NBR AND tgt.COMPANY\_CODE \= src.COMPANY\_CODE)  

     WHEN MATCHED THEN

       UPDATE SET ... \-- poderíamos atualizar status se quisermos suportar update  

     WHEN NOT MATCHED THEN

       INSERT (...) VALUES (...);  

     Optamos por MERGE para suportar cenários em que o pedido já exista (evitar PK violation). Isso cobre caso de WMS reenviar o mesmo pedido (ou se formos usar esse fluxo também para updates). Se assumirmos que não haverá update, um simples INSERT serve, com try-catch de erro duplicado.  

   * Mapear variáveis `:order_nbr` etc. dos campos extraídos.

4. **Mapeamento e Inserção dos Detalhes:** Iterar pela lista de `order_dtl` no payload:  

   * OIC permite um loop For Each sobre a array de linhas.  
   * Dentro do loop, para cada item, mapeamos campos: `order_nbr` (herdado do header ou presente em cada detail), `seq_nbr` \-\> LINE\_NBR, `item_alternate_code` \-\> ITEM\_CODE, `orig_qty` \-\> ORDERED\_QTY, etc.  
   * Executar inserção no DB. Podemos otimizar acumulando e inserindo via batch, mas como o número de linhas por pedido costuma não ser tão alto, inserir individual dentro do loop é aceitável. Contudo, OIC v3 suporta **batch insert**: podemos coletar as linhas e usar um single invoke de DB. Alternativa: usar a operação *“Perform an Operation on a Table”* \-\> *Insert* com opção de processar array, o que insere todos de uma vez.  
   * Similarmente, utilizar MERGE or INSERT. Provavelmente, se reprocessarmos, queremos evitar duplicar linhas. Chave natural: (order\_nbr, seq\_nbr). Podemos incluir no MERGE MATCH condition.

5. **Confirmação e Fim:** Após inserir header e detalhes, considerar qualquer pós-processamento:  

   * Poderíamos chamar um procedimento no DB para validações adicionais ou calculos (mas isso deixaremos para seção 8).  

   * Montar a resposta ao WMS. Se tudo OK: retornar sucesso. Caso algum erro aconteceu durante inserção (ex: violação de integridade), cairá no bloco de erro tratado abaixo.  

   * Responder com código 200 e eventualmente body JSON confirmando recepção do pedido. O WMS possivelmente registra a resposta. Um exemplo:  

     {  

       "status": "SUCCESS",  

       "order\_nbr": "ORD123",  

       "message": "Order received by integration at 2025-05-08T15:45:00Z"  

     }  

     Essa mensagem não é mandatória, mas útil para debug.

**Considerações de Implementação:**

* **Idempotência:** Para evitar duplicar registros caso o mesmo pedido venha mais de uma vez, usamos MERGE (UPSERT). Isso atualizará o registro existente. Poderíamos também optar por rejeitar duplicatas – mas como pode haver cenários de update de pedido (ex: aumento de qty), é melhor processar.  
* **Transação:** Cada chamada do webhook trata um pedido. Envolver header e detail inserts numa mesma transação é desejável. Como estamos no OIC, cada invoke DB por padrão faz autocommit. No entanto, podemos utilizar o **transaction scope** do OIC (define scope “Transactional”) para garantir que vários invokes DB dentro dele sejam commitados juntos ou revertidos juntos. Isso requer que o adaptador DB esteja configurado para participar de XA (no OIC Gen3 não tenho certeza se suporta XA). Alternativamente, podemos designar o header insert e detail inserts como independentes – em caso de falha no meio, ficaria possivelmente um header sem detalhes ou vice-versa. Para mitigar, implementamos lógica de limpeza em erro (ver Tratamento de Erros).  
* **Logging no OIC:** adicionar **notas de log** (no nível debug) contendo o payload recebido (talvez truncado se muito grande) e confirmando a inserção. Isso ajuda suporte mas cuidado para não logar dados sensíveis.  
* **Performance:** Inserir um pedido com, digamos, 5 linhas, é trivial e rápido (\<1s). O overhead maior é a chamada em si. O volume de pedidos por hora esperado definirá se o OIC dá conta linearmente. Por exemplo, 100 pedidos/hora é fácil. Se fosse 1000/hora, ainda ok. Caso haja picos muito altos, poderíamos dimensionar OIC (cluster) ou optar por agrupar envios (mas WMS manda um a um, então provavelmente fine).

### 7.2 Integração de Processamento de Alocações

**Nome da Integração:** `WMS_Allocation_Inbound_Int`. Essa integração recebe os eventos de alocação do WMS e os insere na tabela ALLOC\_STAGE.

**Gatilho:** REST endpoint (outro recurso) na conexão REST, caminho talvez `/allocation` ou `/inventoryHistory`. Dependendo do payload exato:

* Se configuramos o WMS para enviar somente alocações (filtradas), podemos fazer endpoint específico `/allocation`.  

* Se não conseguimos filtrar e WMS envia todos eventos de inventário, teremos que filtrar no OIC internamente (pode cair no mesmo endpoint para todos InventoryHistory, e só tratar quando `transaction_type == "ALLOCATE"`).  

* Supondo que fizemos específico para allocations:  

  * Método: POST.  

  * Payload: JSON simples por evento. Poderia ser uma lista de alocações, mas provavelmente é um evento por vez. Então estrutura:  

    {  

       "company\_code": "YOURCO",  

       "facility\_code": "WH1",  

       "order\_nbr": "ORD0001",  

       "item\_alternate\_code": "ITEM123",  

       "allocated\_qty": 5,  

       "allocation\_time": "2025-05-08T15:30:00Z",  

       "source\_loc": "RESERVE-A1"  

    }  

    (Novamente, isso depende do que WMS manda; se for XML, adaptamos similarmente.)

* Response: um 200 OK simples ou mensagem de sucesso.

**Fluxo de Lógica:**

1. **Recepção:** Gatilho acionado via webhook do WMS. Podemos configurar o tracking identifier como o order\_nbr ou um allocation id se houver.  

2. **Filtro (se necessário):** Se o endpoint receber múltiplos tipos de eventos, checar um campo discriminador. Ex: `if transaction_type != 'ALLOCATE' then return 200 (ignorar)`. Mas se já segmentamos no WMS, não precisa.  

3. **Mapeamento:** Extrair campos: empresa, pedido, item, qty, etc., e montar para tabela.  

4. **Inserção no DB:** Usar `ADB_CONN` para inserir em `ALLOC_STAGE`. Exemplo SQL:  

   INSERT INTO WMSSTAGE.ALLOC\_STAGE

   (ORDER\_NBR, LINE\_NBR, ITEM\_CODE, ALLOC\_QTY, ALLOC\_TS, SOURCE\_LOC, CREATED\_BY)  

   VALUES (:order, :line, :item, :qty, :alloc\_ts, :loc, 'WMS\_ALLOC\_EVENT');  

   Aqui, `LINE_NBR` talvez não venha do WMS, pois a alocação pode não referenciar explicitamente a linha do pedido (só o item). Se não tivermos line, podemos preencher null ou derivar buscando nas tables de stage (mas evitar lógica complexa aqui).  

   * Use `MERGE` ou `INSERT`? Provavelmente `INSERT` simples, porque alocações tendem a ser eventos únicos (se WMS mandar duas vezes o mesmo evento, seria duplicado… poderíamos proteger com PK unique constraint).  
   * Se definimos `ALLOC_ID` como identity PK, não precisamos do value; DB gera.  
   * Mapear binds com payload.

5. **Resposta:** Retornar sucesso/erro. Se inserção ok, 200 OK. Se falha (ex: DB down ou constraint), lançar erro (que será tratado no bloco de erro).  

6. **Considerações Adicionais:**  

   * Poderíamos enriquecer o evento: por exemplo, consultar a tabela ORDER\_HDR\_STAGE para pegar alguma info contextual (como status ou verificar se pedido existe). Não é essencial, mas poderíamos marcar o pedido como “allocated” no stage. Isso envolveria executar um UPDATE em ORDER\_HDR\_STAGE setting status \= 'ALLOCATED' where order\_nbr. Isso pode ser feito dentro do mesmo integration, após inserir alloc.  
   * No entanto, como vamos ter transformações e views no DB, podemos lá determinar o status consolidado (um view que verifica: se existe alguma alloc para aquele pedido, status \= Allocated).  
   * Portanto, a integração de Allocation pode limitar-se a inserir o registro de alocação.

**Volume e Performance:** Alocações podem ser bem mais frequentes que pedidos, pois um único pedido pode gerar várias alocações (um pedido de 100 linhas poderia alocar 100 itens em possivelmente centenas de LPNs). Mas o WMS geralmente aloca por onda, não item a item manual, então poderia enviar múltiplos eventos próximos. Precisamos garantir que o OIC suporta bursts. Tipicamente, OIC consegue processar muitos webhooks paralelamente (escala horizontal), mas se esperarmos milhares por minuto, poderíamos adotar lotes. Provavelmente não chega a tanto no contexto comum. De qualquer forma, por ser insert simples, deve ser leve.

### 7.3 Segurança e Tratamento de Erros

**Segurança em Execução:**

* Já garantimos que as conexões usam credenciais seguras. Dentro das integrações, devemos também **sanitizar dados** se necessário. Por exemplo, verificar que campos numéricos realmente são numéricos (OIC tipagem já cuida em parte).  
* **Controle de Acesso:** Os endpoints REST expostos no OIC (para pedidos e alocações) requerem Basic Auth. Somente o WMS Cloud tem essas credenciais, portanto somente ele deve conseguir invocar. Isso impede acessos não autorizados externos.  
* Adicionalmente, podemos configurar no OIC uma verificação de IP (ex: obter o IP do request e verificar se pertence ao range Oracle Cloud do WMS) – mas isso não é trivial de implementar no OIC, então confiaremos na Basic Auth.

**Tratamento de Erros:**

* Implementar blocos de exceção (*fault handlers*) em cada integração. Possíveis pontos de falha:  

  * Conexão com DB falhou (transient network, ou DB down).  
  * Violação de integridade no insert (por exemplo, PK duplicada não tratada, ou valor truncado).  
  * Erro inesperado no OIC (null pointer se payload não conforme).

* Para cada caso, definiremos:  

  * **Retry lógico:** se for erro transitório de DB (pouco provável no Autonomous, mas rede pode falhar), podemos encapsular o DB invoke numa ação de *Scope* com propriedade *“Continue on Error”* false e depois um *Repeat* em fault handler para tentar novamente X vezes com delay. O OIC não tem recurso nativo de auto-retry em triggers, então se falhar e não tratado, aquela mensagem fica como erro a ser resubmetida manualmente.  

  * **Error Hospital:** O OIC Integration 3 possui a página de Errors onde podemos resubmeter instâncias. Vamos utilizar isso: ou seja, deixar a instância falhar e depois alguém ir lá e dar resubmit após corrigir a causa. Mas podemos melhorar a automação.  

  * **Compensação:** Se inserimos header mas falha nos detalhes, temos meio inserido. Podemos no fault handler executar uma limpeza: deletar o header inserido para não ficar órfão. Isso usando outro invoke DB no handler (cuidado para não apagar se o erro foi apenas duplicata).  

  * **Comunicação de Erro ao WMS:** Importante \- se não conseguimos processar o webhook, devemos retornar um erro adequado para que o WMS saiba. Por exemplo, retornar HTTP 500 ou 400 com mensagem. Assim o WMS marcará aquele envio como failed. Como visto, WMS output interface espera status \!= 2xx para marcar erro. Faremos isso: no fault handler do trigger, definiremos a resposta com erro. Ex:  

    * Código 500 e body `{"status":"ERROR","message":"DB unreachable"}`.  
    * O WMS registrará e não tentará novamente automaticamente. Caberá ação manual ou uso da API de update\_output\_interface para retentativa. Não implementaremos a chamada de update\_output\_interface do OIC automaticamente, pois se OIC estava down, não teria como rodar. Isso fica para operação manual (ver seção 10/11).

  * **Notificação:** Podemos incluir no fault handler lógica de notificação: enviar um email ou chamar um outro fluxo de alerta se um erro ocorrer. O OIC v3 permite configurar **Global Fault** ou instanciar um fluxo para tratar faults. Simplesmente, enviaremos um email para o suporte de TI com detalhes (pedido tal falhou, motivo X). Isso usando o Notification Service ou um adapter de Email (OIC tem adapter SMTP configurável).  

  * **Resubmit Manual:** Documentar o procedimento: se erro X ocorreu, ajustar causa (ex: se foi dado inválido no WMS, corrigir no WMS ou DB) e então do OIC Integration \-\> Errors \-\> Resubmit a instância. Ao reexecutar, ele vai tentar inserir de novo (cuidar para duplicatas). Como usamos MERGE, reexecutar não causa erro (atualiza registro já inserido e re-tenta detalhes).

**Testes de Erro:** Durante desenvolvimento, forçar algumas condições:

* Mandar um pedido duplicado e ver se MERGE lida sem erro.  
* Desligar a conexão DB (simular inacessível) e mandar pedido, ver se OIC responde 500 e WMS loga erro.  
* Mandar dados malformados (ex: string muito longa para campo) e ver erro tratado.

**Logging e Monitoramento no OIC:** Além do console de erros, podemos configurar **Tracking custom**. Por exemplo, definir Business Identifiers nas integrações (Order Integration: OrderNumber; Allocation Integration: OrderNumber+Item). Assim, no painel do OIC podemos facilmente encontrar instâncias por esses IDs (ex: buscar pelo número do pedido). Isso é muito útil em suporte.

**Segregação de Ambientes:** Garantir que em dev/test, as credenciais e endpoints usados apontem aos ambientes certos. Ao promover para produção, atualizar conexões do OIC para usar cred de prod (ex: usuário WMS prod) e endpoint do WMS prod, e DB prod, etc.

Com segurança e erros bem tratados, as integrações serão resilientes. Em resumo, qualquer falha resultará em:

* O WMS saber que aquele evento não foi aplicado (porque recebeu um erro HTTP) – podendo assim o pessoal de suporte identificar e atuar.  
* O OIC registrar o erro e permitir reprocessamento.  
* Nenhuma transação ficar meia-completa sem detecção (ou serão limpas, ou marcadas com flag, dependendo da estratégia).  
* Notificações proativas avisarão quando necessário para não depender de inspeção manual frequente.

Isso conclui a construção das integrações de pedidos e alocações no OIC, cobrindo os cenários normais e excepcionais.

## 8\. Estratégia de Transformação no DB (Views, Procedures, Materialized Views)

Após os dados serem inseridos nas tabelas de stage no Autonomous DB, muitas vezes é necessário transformá-los ou agregá-los para uso prático – seja para relatórios de negócio, para alimentar APIs de consulta ou até para transferir a outro sistema. Em vez de sobrecarregar o OIC com lógicas complexas, adotaremos a estratégia de realizar **transformações dentro do Autonomous Database**, aproveitando seu poder de processamento SQL e PL/SQL.

Os principais componentes dessa estratégia são: **Views (visões)** para representar dados consolidados, **Stored Procedures** para atualizações e regras de negócio, e possivelmente **Materialized Views** para ganho de performance em consultas analíticas.

### 8.1 Visões Consolidadas

Criaremos *views* no esquema `WMSSTAGE` (ou outro esquema de relatório) que combinem os dados das tabelas de stage para formar informações completas de negócio:

* **VIEW `VW_ORDER_COMPLETE`:** Visão que junta cabeçalho e detalhes do pedido, mostrando uma linha por item do pedido com informações do cabeçalho.  

  CREATE OR REPLACE VIEW VW\_ORDER\_COMPLETE AS  

  SELECT h.ORDER\_NBR,  

         h.COMPANY\_CODE,  
    
         h.FACILITY\_CODE,  
    
         h.ORDER\_TYPE,  
    
         h.ORDER\_DATE,  
    
         h.DESTINATION,  
    
         h.STATUS AS ORDER\_STATUS,  
    
         d.LINE\_NBR,  
    
         d.ITEM\_CODE,  
    
         d.ORDERED\_QTY,  
    
         d.ALLOCATED\_QTY,  
    
         d.UOM,  
    
         COALESCE(d.ALLOCATED\_QTY, 0\) as ALLOCATED\_QTY,   
    
         CASE   
    
           WHEN COALESCE(d.ALLOCATED\_QTY,0) \>= d.ORDERED\_QTY THEN 'ALLOCATED'  
    
           WHEN COALESCE(d.ALLOCATED\_QTY,0) \> 0 THEN 'PARTIALLY\_ALLOCATED'  
    
           ELSE 'NOT\_ALLOCATED'  
    
         END as LINE\_ALLOC\_STATUS,  
    
         h.CREATED\_AT,  
    
         h.PROCESSED\_FLAG  

  FROM ORDER\_HDR\_STAGE h

  JOIN ORDER\_DTL\_STAGE d ON d.ORDER\_NBR \= h.ORDER\_NBR

       AND d.COMPANY\_CODE \= h.COMPANY\_CODE;  

  Explicação: esta view lista todos os itens de todos pedidos. Inclui uma coluna derivada `LINE_ALLOC_STATUS` que checa se a quantidade alocada (caso o OIC populasse essa coluna no stage ou via subsequent updates) atinge a total. No nosso fluxo atual, a alocação chega separada, não atualizamos `ALLOCATED_QTY` em ORDER\_DTL\_STAGE diretamente. Poderíamos fazer isso via procedimento (ver adiante). Em alternativa, poderíamos mudar a view para calcular alocação somando ALLOC\_STAGE:  

  (SELECT SUM(alloc\_qty) FROM ALLOC\_STAGE al

   WHERE al.ORDER\_NBR \= d.ORDER\_NBR AND al.ITEM\_CODE \= d.ITEM\_CODE) as ALLOCATED\_QTY  

  Mas isso pode gerar duplicidade se o item repetido. Talvez melhor via procedure.  

* **VIEW `VW_ORDER_HEADER_STATUS`:** Visão resumida por pedido, indicando se o pedido está totalmente alocado, parcialmente ou não. Poderia basear-se nos detalhes:  

  CREATE OR REPLACE VIEW VW\_ORDER\_HEADER\_STATUS AS  

  SELECT h.ORDER\_NBR,  

         h.COMPANY\_CODE,  
    
         h.FACILITY\_CODE,  
    
         h.ORDER\_DATE,  
    
         CASE   
    
           WHEN MIN(CASE WHEN COALESCE(d.ALLOCATED\_QTY,0) \>= d.ORDERED\_QTY THEN 1 ELSE 0 END) \= 1 THEN 'FULLY\_ALLOCATED'  
    
           WHEN MAX(CASE WHEN COALESCE(d.ALLOCATED\_QTY,0) \> 0 THEN 1 ELSE 0 END) \= 1 THEN 'PARTIALLY\_ALLOCATED'  
    
           ELSE 'NOT\_ALLOCATED'  
    
         END as ALLOCATION\_STATUS,  
    
         COUNT(d.LINE\_NBR) as TOTAL\_LINES,  
    
         SUM(d.ORDERED\_QTY) as TOTAL\_QTY,  
    
         SUM(COALESCE(d.ALLOCATED\_QTY,0)) as TOTAL\_ALLOCATED\_QTY  

  FROM ORDER\_HDR\_STAGE h  

  JOIN ORDER\_DTL\_STAGE d ON d.ORDER\_NBR \= h.ORDER\_NBR  

  GROUP BY h.ORDER\_NBR, h.COMPANY\_CODE, h.FACILITY\_CODE, h.ORDER\_DATE;  

  Isso nos dá uma ideia do status geral do pedido. Entretanto, observe que ainda dependemos de atualizar `ALLOCATED_QTY` em ORDER\_DTL\_STAGE para refletir as alocações. Se isso não estiver ocorrendo automaticamente, podemos optar por preencher via procedure.  

* **VIEW `VW_ALLOCATIONS_RECENT`:** Uma visão ou consulta para listar alocações recentes com join nos detalhes do pedido:  

  CREATE OR REPLACE VIEW VW\_ALLOCATIONS\_RECENT AS  

  SELECT al.ALLOC\_ID,  

         al.ORDER\_NBR,  
    
         al.ITEM\_CODE,  
    
         al.ALLOC\_QTY,  
    
         al.SOURCE\_LOC,  
    
         al.ALLOC\_TS,  
    
         h.DESTINATION,  
    
         d.LINE\_NBR  

  FROM ALLOC\_STAGE al  

  LEFT JOIN ORDER\_HDR\_STAGE h ON h.ORDER\_NBR \= al.ORDER\_NBR  

  LEFT JOIN ORDER\_DTL\_STAGE d ON d.ORDER\_NBR \= al.ORDER\_NBR AND d.ITEM\_CODE \= al.ITEM\_CODE  

  WHERE al.ALLOC\_TS \>= TRUNC(SYSDATE)  \-- por exemplo, alocações do dia  

  ;  

  Essa view facilita ver o que foi alocado hoje, unindo com informações do pedido.

As views acima servem para consultas e relatórios rápidos. Colocando-as no Autonomous DB, podemos acessá-las via Analytics tools ou mesmo expor via OIC se precisarmos de uma API de consulta.

### 8.2 Procedimentos e Atualizações de Stage

Para manter os dados de stage atualizados e eventualmente mover para estruturas finais, podemos usar **Stored Procedures (PL/SQL)** agendadas ou acionadas:

* **Procedure de Consolidação de Alocação:** Uma procedure `PRC_UPDATE_ALLOCATIONS` que:  

  * Agregue as quantidades alocadas de `ALLOC_STAGE` por pedido e item.  

  * Atualize a tabela `ORDER_DTL_STAGE` definindo `ALLOCATED_QTY` em cada linha conforme o somatório recebido.  

  * Eventualmente atualize `ORDER_HDR_STAGE.STATUS` para 'ALLOCATED' se todas as linhas foram completamente alocadas.  

  * Marque as entradas de ALLOC\_STAGE como processadas (um flag) para não recontar no futuro.  

  * Essa procedure pode ser agendada para rodar periodicamente (ex: a cada 5 minutos) ou disparada via um call do OIC após inserir alocação. Poderíamos até chamá-la no final da integração de alocação (após inserir, chamar procedure via adaptador DB).  

  * Em PL/SQL, algo como:  

    CREATE OR REPLACE PROCEDURE PRC\_UPDATE\_ALLOCATIONS IS  

    BEGIN  

      FOR rec IN (  

         SELECT order\_nbr, item\_code, SUM(alloc\_qty) as total\_alloc   
      
         FROM ALLOC\_STAGE   
      
         WHERE processed\_flag \= 'N'  
      
         GROUP BY order\_nbr, item\_code  

      ) LOOP  

         UPDATE ORDER\_DTL\_STAGE   
      
         SET ALLOCATED\_QTY \= COALESCE(ALLOCATED\_QTY,0) \+ rec.total\_alloc  
      
         WHERE ORDER\_NBR \= rec.order\_nbr AND ITEM\_CODE \= rec.item\_code;  

      END LOOP;  

      \-- update statuses if needed  

      UPDATE ORDER\_HDR\_STAGE h  

      SET STATUS \= 'FULLY\_ALLOCATED', PROCESSED\_FLAG \= 'Y'  

      WHERE STATUS \= 'Created'  

        AND NOT EXISTS (  
      
           SELECT 1 FROM ORDER\_DTL\_STAGE d   
      
           WHERE d.ORDER\_NBR \= h.ORDER\_NBR   
      
             AND COALESCE(d.ALLOCATED\_QTY,0) \< d.ORDERED\_QTY  
      
        );  

      \-- mark processed  

      UPDATE ALLOC\_STAGE SET PROCESSED\_FLAG \= 'Y', PROCESSED\_AT \= SYSTIMESTAMP  

      WHERE PROCESSED\_FLAG \= 'N';  

    END;  

    (Código ilustrativo. Em produção, considerar fazer batido com SQLs únicos em vez de loop, e incluir tratamento de concorrência.)

* Decidir se chamamos essa procedure via OIC ou agendamento no DB:  

  * O Autonomous DB não permite DBMS\_SCHEDULER (no ATP-S it might, but historically it era restrito). Contudo, Database Actions do Autonomous tem Aplication Express etc., mas preferível agendar via OIC ou Exadata scheduler.  
  * Podemos configurar um integration scheduler no OIC para chamar essa procedure periodicamente. Porém, isso reintroduz OIC no circuito para algo que o DB pode fazer. Como ABO (Always Free / Cloud) nem sempre permite scheduler DB, usar OIC scheduler a cada X min para chamar `CALL WMSSTAGE.PRC_UPDATE_ALLOCATIONS` via adaptador DB.  
  * Alternativamente, criar uma **Materialized View** que já traga allocated\_qty somado (ver próxima seção) e nem atualizar a tabela detail. Depende do uso.

* **Procedure de Limpeza/Archiving:** Com o tempo, as tabelas de stage podem crescer (embora se marque processed). Podemos criar um job para mover registros antigos (por ex, pedidos já completados há \> 30 dias) para tabelas de histórico ou deletar se não precisa mais. Isso manterá performance. Essa procedure poderia rodar 1x por mês.

### 8.3 Materialized Views e Performance

Se houver demanda por relatórios pesados ou integração com BI, as *materialized views* podem acelerar consultas agregadas:

* **MV\_ORDER\_ALLOC\_SUM**: materialized view que pré-calcula por pedido quantidades alocadas e pedidos atendidos, para quick reporting. A refresh pode ser on-demand ou nightly. Dado o volume não ser enorme a princípio, talvez desnecessário.  
* **MV\_INVENTORY\_SNAPSHOT**: se integrássemos mais coisas (estoque total), faríamos snapshots. Fora do escopo atual.

No contexto atual (pedidos e alocações), consultas diretas nas views base serão rápidas, pois as tabelas não são gigantes inicialmente, e o Autonomous DB tem recurso de **Auto-Indexação e Query Optimization**. Podemos contar também com **result cache** de queries.

**Consideração Final:** Manter as transformações no DB significa que caso no futuro deseje-se levar esses dados a outro sistema (ex: Oracle Analytics Cloud ou Data Warehouse), já estarão prontos num formato consolidado. Por exemplo, apontar OAC diretamente para a view `VW_ORDER_COMPLETE` para dashboards de atendimento de pedidos.

Resumindo a estratégia:

* Dados brutos ficam nas stage tables.  
* Lógica de negócio (como cálculo de status de alocação) implementada via SQL no DB, seja em views ou procedures que atualizam campos.  
* O OIC permanece simples (inserindo dados), e o DB faz o trabalho pesado de combinação e resumo, tirando proveito da performance do Oracle Database.

## 9\. Testes e Validação (Funcional, Volumétrico e Performance)

Uma vez desenvolvidas as integrações e implementadas as transformações no banco, é fundamental realizar uma bateria abrangente de testes para validar que a solução atende aos requisitos funcionais e de desempenho. A seguir detalhamos o plano de testes:

### 9.1 Testes Funcionais (Happy Path e Casos de Borda)

* **Teste de Pedido Completo (Happy Path):** Criar manualmente um pedido no WMS Cloud (via UI ou import) com, por exemplo, 2 linhas. Verificar:  

  * Se o OIC recebe o webhook do pedido e a instância conclui com sucesso.  
  * Conferir no Autonomous DB que as tabelas ORDER\_HDR\_STAGE e ORDER\_DTL\_STAGE foram populadas corretamente (campos batendo com o WMS).  
  * Consultar a view `VW_ORDER_COMPLETE` para garantir que o pedido aparece lá corretamente.

* **Teste de Alocação Completa:** No WMS, alocar estoque para o pedido acima (pode ser via função "Allocate" ou confirmando um picking). Ver se:  

  * O OIC recebe o evento de alocação e insere em ALLOC\_STAGE.  
  * A tabela ALLOC\_STAGE tem o registro com quantidade, item, etc.  
  * Se implementamos procedure de atualização imediata, verificar se ORDER\_DTL\_STAGE.ALLOCATED\_QTY foi atualizado ou se a view de status reflete a alocação.

* **Teste de Pedido com Atualização:** Criar um pedido, depois fazer uma modificação nele (por ex, adicionar uma linha, ou alterar qty via WMS if possible). O WMS pode ou não emitir outro webhook. Caso emita:  

  * Verificar se o OIC trata como upsert: o header MERGE atualizou algo? a nova linha foi inserida?  
  * Confirmar no DB que não há duplicatas: apenas a nova linha adicional presente.

* **Teste de Pedido Duplicado (Reenvio):** Simular que o WMS reenvie o mesmo pedido (por exemplo, usando a função reprocessar interface no WMS).  

  * Espera-se que o OIC ao tentar inserir encontre já existente. Como lidamos? Se MERGE, atualizará timestamp mas nada de errado. Se era insert e cair em erro PK, nosso tratamento de erro deve lidar. Ajustar se necessário.

* **Teste de Erro no DB:** Provocar um erro deliberado. Exemplo: modificar temporariamente a tabela para causar erro (como colocar uma constraint NOT NULL e mandar valor null). Ou desligar a conexão DB (difícil em cloud, mas talvez alterar credencial para forçar falha).  

  * Confirmar que o OIC retorna erro 500 ao WMS.  
  * Ver no WMS Cloud UI que a interface de saída ficou com status de erro, e mensagem se capturou (às vezes aparece).  
  * Ver no OIC monitoring que a instância está em erro e foi logada.

* **Teste de Arquivo CSV (Carga Inicial):** Se possível em ambiente de teste, pegar um extrato de vários pedidos (talvez 20\) do WMS, colocar no SFTP e rodar a integração de carga inicial.  

  * Conferir que todos foram inseridos.  
  * Comparar total de pedidos e linhas entre arquivo e DB.  
  * Repetir a carga inicial com um arquivo ligeiramente modificado para ver se lida com duplicates adequadamente (talvez a integration inicial não era idempotente e insira duplicado – mas carga inicial é única, então não crítico).

* **Testes de Campos Especiais:** Verificar comportamento com:  

  * Caracteres especiais (acentos, &, \<) em campos – garantir que JSON/XML encoding não quebre. OIC lida bem com UTF-8 normalmente.  
  * Campos opcionais faltando – ex: destino vazio, verificar se integração não falha e DB aceita null.  
  * Pedido com muitos itens (para ver loop).  
  * Alocação parcial (alocar apenas parte do pedido, verificar status).  
  * Alocação múltipla do mesmo item (ex: item em 2 locais, WMS pode gerar 2 eventos – no DB teremos duas linhas ALLOC\_STAGE; verificar se view ou calc soma ambas).

### 9.2 Testes Volumétricos (Carga de Volume)

Mesmo que a carga normal seja moderada, devemos testar escalabilidade:

* **Volume de Pedidos:** Simular (se possível) a inserção de, por exemplo, 500 pedidos em curto intervalo. Se não der via UI, podemos usar a API do WMS para criar em massa ou duplicar um payload de webhook via uma ferramenta para chamar o OIC repetidamente.  

  * Por exemplo, usar JMeter ou uma collection do Postman para enviar 100 pedidos fictícios para o endpoint do OIC, em paralelo.  
  * Monitorar se o OIC processa todos sem gargalos significativos. Observando no console, quantas instâncias ativas simultâneas, se alguma fila se forma.  
  * Verificar uso de CPU no Autonomous DB via **Performance Hub** ou métricas (CPU should handle easily 500 inserts).  
  * Ajustar se necessário: se OIC ficar lento, considerar aumentar threads (OIC auto-scales to some extent, or if not, consider asynchronous patterns).

* **Volume de Alocações:** Similar, enviar muitos allocation events. Ver se OIC consegue consumir. Alocações são leves, mas volume pode ser maior que pedidos.  

  * Ex: 1000 allocation events in a burst. OIC deveria enfileirar e inserir.  
  * Testar se alguma falha ou backlog: OIC Integration 3 possivelmente pode ter um limite de throughput \~50 TPS por node, mas precisaríamos ver.

* **Tamanho de Payload:** Testar um pedido com, digamos, 100 linhas. O payload JSON seria grande (\~100k?). Ver se OIC consegue parsear e inserir sem problemas. Isso testa limites de tamanho (OIC suporta payloads bem grandes, mas acima de 10MB seria problema, nosso caso talvez \< 1MB).  

* **Carga Inicial Pesada:** Se possível, colocar um arquivo CSV com milhares de linhas e rodar. Medir tempo.  

  * Ex: 10k pedidos, 50k linhas – será que finaliza em tempo hábil? OIC might take minutes. Checar se isso é aceitável ou se precisaríamos usar Bulk API do DB.

### 9.3 Testes de Performance e Tuning

Avaliar a performance end-to-end:

* **Latency de Webhook:** Medir o tempo entre um evento no WMS e o dado aparecer no DB.  

  * Pode-se registrar timestamp no WMS (e.g. WMS might log time event sent) e comparar com CREATED\_AT no DB.  
  * Esperado que seja poucos segundos (\<5s). Confirmar.

* **Consulta no DB:** Executar queries típicas nas views, especialmente se muitas linhas, para ver se respondem rápido. Ex: selecionar todos pedidos, filtrar por status. O Autonomous DB deve responder bem até certo ponto; se notar lentidão, avaliar plano de execução e adicionar índice ou usar auto-index. O ADB tem auto-tuning, então deixar ele rodar um tempo e sugerir indexes.  

* **Comportamento Sob Carga Contínua:** Simular uma hora de operação normal: enviar pedidos e allocations de forma intercalada aleatória para ver se algum recurso saturado.  

  * Ver no OIC console se CPU usage (if accessible) ou memory ficam ok. O OIC cloud não expõe facilmente, mas podemos ver se há filas.  
  * No Autonomous DB, monitorar *Active Sessions* via Performance Hub – verificar se há algum spike indicando gargalo no SQL.  
  * Monitorar rede: OIC calls to DB should be minimal overhead.

* **Tuning Identificado:** Se durante testes volumétricos percebermos pontos fracos:  

  * Exemplo: inserir 1000 lines individually foi lento. Solução: usar batch insert no OIC integration (refatorar).  
  * Ou procedure de update de alloc demorando muito para lotes enormes: otimizar SQL (indices em ALLOC\_STAGE por order maybe).  
  * Ou muitas instâncias OIC em paralelo causando thrashing: talvez introduzir um **queue** (OIC has concept of Streaming/Parallel options, or use an OCI Queue service) – mas isso raramente é preciso se dimensionado adequadamente.

* **Testes de Failover:** Embora não controlamos, é bom saber:  

  * OIC cloud tem alta disponibilidade, mas teste rápido: reiniciar (disable/enable) a integration no meio de eventos e ver se retoma bem.  
  * Autonomous DB: simular que fique indisponível (difícil simular, mas imaginar) e ver se quando volta as mensagens que falharam podem ser reprocessadas adequadamente.

### 9.4 Critérios de Aceite

Estabelecer que:

* 100% dos casos de teste funcionais passaram (ou com desvios documentados e aceitos).  
* A solução aguenta pelo menos 2x o volume de pico esperado sem degradação severa.  
* Latência de integração atende aos requisitos (por ex, pedido aparece no DB em \<10s do evento).  
* Nenhum dado se perde ou é duplicado erroneamente em cenários de retry.  
* Operações de resubmissão funcionam (testado reprocessar manualmente um erro e ver que insere sem duplicar).  
* Segurança: tentar acesso não autorizado ao endpoint (simular com cred inválida) retorna 401 – testado via Postman usando cred errada.  
* Sistema de monitoramento (próxima seção) mostra claramente os fluxos.

Após atingido isso, podemos proceder ao UAT (User Acceptance Testing) se houver e, em seguida, planejar a produção.

## 10\. Monitoramento e Governança

Uma vez em operação, a integração precisa ser acompanhada de perto para garantir continuidade e identificar problemas rapidamente. Dividiremos o monitoramento em três frentes – no OIC, no Autonomous DB e no WMS Cloud – além de abordar governança (processos e responsabilidades).

### 10.1 Monitoramento no Oracle Integration Cloud

O OIC provê ferramentas integradas de monitoramento de integrações:

* **Dashboards e Métricas:** A interface do OIC (Integrations \> Monitoring) oferece um painel com estatísticas de execução: número de mensagens processadas, sucesso vs erro, tempo médio, etc. Utilize isso para acompanhar volume diário e tendências. Por exemplo, ver se hoje teve mais mensagens que o normal, ou se aumentou taxa de erros.  

* **Logs de Atividade:** Cada instância de integração possui um log detalhado (activity stream). Em caso de erros, esses logs podem ser baixados para análise. Configurar retenção adequada (OIC normalmente retém 30 dias de tracking).  

* **Alerts/Notifications:** OIC v3 permite configurar **Alertas** via *Integrations \> Monitoring \> Integrations \> Enable Callback Notifications*. Podemos definir notificações para falhas, integrando com email ou pager:  

  * Por exemplo, criar um integração simples que seja acionada pelo evento de erro (via ICS Callback) e envie um email ao administrador com o ID da integração falha e causa.  
  * Alternativamente, usar o OCI Logging Analytics: configurar o OIC para enviar logs de erro a um serviço OCI Log, e dali configurar Alarms (um pouco avançado).

* **Erro e Reprocessamento:** A equipe de suporte deve checar regularmente a tela de **Errors** no OIC. Essa tela permite filtrar por integração e ver falhas. Itens nessa fila devem ser tratados:  

  * Se for um erro transitório já resolvido, clicar “Resubmit” (pode reprocessar vários juntos se selecionar).  
  * Se for erro de dados, corrigir dados primeiro (ex: via correção no WMS ou DB) e então resubmit.  
  * Definir um SLA: por exemplo, nenhum erro deve ficar sem atendimento por mais de 2 horas.

* **Atualizações do OIC:** Oracle Integration Cloud recebe atualizações periódicas. Monitorar anúncios de update e realizar smoke tests após updates para garantir que as integrações continuam funcionando. Normalmente, as atualizações não quebram fluxos existentes, mas é parte da governança acompanhar.

### 10.2 Monitoramento no Oracle Autonomous Database

O Autonomous Database oferece **ferramentas de monitoramento robustas**:

* **Service Console (Web):** Acesse o Service Console do ADB e navegue até **Performance**. Use o **Performance Hub** para observar estatísticas de consultas, uso de CPU, espera de I/O, etc., em vários intervalos de tempo. Isso ajuda a identificar se alguma query do nosso lado está lenta ou consumindo demais.  

* **Metrics e Alarms:** No OCI console, habilitar métricas para o Autonomous DB – por exemplo, CPU Utilization, Storage Utilization, Sessions – e configurar **Alarms** (via serviço Monitoring):  

  * Ex: disparar um alarme se CPU passar de 80% por mais de 15 minutos (indicaria talvez carga pesada ou problemas).  
  * Alarme de erro de conexão: não disponível diretamente, mas se ADB ficar inacessível, possivelmente CPU=0 repentino \+ alertas do lado OIC.

* **AWR e Auto-tuning:** O Autonomous gera automaticamente relatórios AWR e pode sugerir índices via Auto Indexing (se habilitado). Revisar periodicamente se índices foram criados automaticamente para nossas tabelas (por ex, index em ORDER\_NBR se consultas frequentes). Auto-Index em ATP é geralmente disponível e pode melhorar performance sem intervenção manual.  

* **Monitoring de espaço:** Embora o Autonomous seja elástico, acompanhar o uso de armazenamento. Se crescer muito rápido (p.ex., logs ou stage retendo muitos registros), avaliar purga ou aumento de storage. Por padrão, o Autonomous autoscale storage up to 128TB, então provavelmente não será problema, mas governança inclui evitar guardar dado inútil eternamente. Implementar a limpeza histórica citada (procedures).  

* **Backup e Recovery:** Autonomous DB faz backup automáticos diários com retenção (normalmente 7 ou 30 dias dependendo do config). Verificar que backups estão ocorrendo (console mostra) e anotar o período de retenção. Para governança, planejar drills de recuperação: testar restaurar num ambiente de teste um backup para ver se processo funciona e quanto tempo leva, garantindo que em desastre real estamos prontos.  

* **Auditoria de Segurança:** Se a empresa exige auditoria de acesso, consultar os logs de auditoria do ADB:  

  * Comando: `SELECT * FROM UNIFIED_AUDIT_TRAIL WHERE DBUSER='WMSSTAGE';` para ver ações do usuário de stage. Normalmente, cada insert via OIC apareceria, mas unified audit por padrão loga pouca coisa. Ativar políticas se necessário (ex: LOGON, DML on certain tables).

### 10.3 Monitoramento no Oracle WMS Cloud

O WMS Cloud, como sistema SaaS, tem limitações de acesso a logs internos, mas oferece algumas ferramentas:

* **Interface Transmission Log:** Conforme mencionado, na UI do WMS há telas para acompanhar as interfaces de entrada e saída. Em particular, para nossas integrações:  

  * **Output Interface (Orders, Allocations):** Monitorar nessa tela se há registros com status "Error" ou pendentes (unprocessed). Idealmente, todos devem estar como "Transmitted" ou similar. Se vir erros, investigar detalhe (coluna message). Por exemplo, pode mostrar "HTTP 500 returned" ou "Authentication failed".  
  * **Input Interface (if using for inbound orders):** Se em algum momento usamos a API init\_stage\_interface (inbound para WMS), o WMS também registra os processamentos de interface. Seria útil verificar se todos pedidos enviados do OIC para WMS entraram. Essa tela mostraria sucesso ou erro (ex: erro de validação no WMS).

* **Fila de Eventos:** O WMS não expõe uma fila persistente tipo JMS, mas internamente as output interfaces funcionam quase como fila (registros numa tabela). Saber disso implica que se por algum motivo quisermos *pausar* envios, poderíamos desativar a interface temporariamente – os eventos ficariam enfileirados no WMS e poderíamos escoar depois. Parte da governança pode ser: em manutenção do OIC ou DB, desligar as interfaces no WMS para segurar eventos, depois ligar e reprocessar.  

* **Alertas no WMS:** O WMS Cloud permite configurar **notify users on interface error** via email. Verificar se há tal config. Ou simplesmente, incumbir o admin do WMS de checar diariamente se alguma interface falhou. Frequência de falha deve ser baixa se tudo estiver bem.  

* **Relatórios de Integração:** Em WMS, possivelmente extrair relatórios mensais de volume de transações integradas, para ver utilização e planejar capacidade. Se não disponível out-of-box, pode ser manual a partir dos logs.

### 10.4 Governança e Processo

Definir claramente papéis e procedimentos:

* **Equipe de Suporte de Integração (TI):** Responsável por monitorar o OIC e ADB, tratar erros de integração, coordenar com equipe WMS.  

* **Equipe de Suporte de WMS (Consultores ou Key-user):** Responsável por monitorar as interfaces do lado WMS e tratar erros de dados (por exemplo, se um pedido falhou porque dado obrigatório faltou, corrigir no WMS e pedir reenvio).  

* **Reuniões de Revisão:** Durante o período inicial pós go-live, fazer reuniões semanais para revisar logs de integração, identificar padrões de falha, ajustar configurações de performance se necessário.  

* **Documentação Viva:** Manter a documentação da integração atualizada (por exemplo, se novos campos forem adicionados futuramente ou novas interfaces – incluir no documento). Isso ajuda onboarding de novos membros na equipe e facilita auditorias.  

* **Gestão de Mudanças:** Qualquer alteração em fluxos de integração (OIC) ou em estrutura de DB deve passar por testes em ambiente de stage antes. Oracle Integration Cloud permite exportar integracões e importar em outro ambiente (ou usar OIC's CICD features) – usar isso para ter pelo menos um ambiente de teste além da prod.  

* **Escala e Crescimento:** Se o volume transacional crescer significativamente (por exemplo, WMS onboarding mais unidades ou aumento de pedidos sazonal), planejar com antecedência:  

  * OIC pode precisar de upgrade de capacidade (ex: pedir instância de OIC com mais throughput).  
  * Autonomous DB pode precisar aumentar CPUs (pode ser feito online com slider de OCPUs).  
  * Testes de carga adicionais devem ser feitos preemptivamente.

* **Custos:** Monitorar uso para evitar surpresas de custo:  

  * OIC é faturado por mensagens e activos. Saber quantas integrações ativas e volume de msgs. OIC Gen3 possivelmente tem modelo diferente (consumo).  
  * Autonomous DB é faturado por OCPU/hora e storage. A autoscale e autopause (se configurado) podem otimizar custo. Verificar se autopause está off para Prod (para não pausar durante inatividade, a menos que aceitável).

* **Compliance:** Garantir conformidade com LGPD/GDPR se dados pessoais trafegassem (nesse caso não muito). Se sim, pseudonimizar ou proteger.  

  * Talvez irrelevante aqui, mas governança requer pensar nisso.

Em termos de governança, a ideia é que a integração seja **visível** (com monitoramento) e **ajustável** ao longo do tempo. Oracle oferece muitas ferramentas integradas, então a chave é configurar alertas e rotinas para não depender de esforço manual intensivo contínuo.

## 11\. Plano de Suporte e Operação Contínua

A fase de operação contínua requer um plano de suporte definido para garantir que a integração permaneça confiável e atenda a SLAs de negócio. Este plano cobre desde suporte nível 1 (monitoramento e resposta inicial) até melhorias contínuas.

**Suporte Nível 1 (NOC/Monitoramento):**

* Ter pessoal ou serviços dedicados a acompanhar os **dashboards do OIC e alarmes OCI** configurados. Esses operadores de primeiro nível não precisam entender todo o código, mas devem saber reiniciar uma integração ou notificar responsáveis.  

* Documentar procedimentos de verificação diária:  

  * Checar fila de erros do OIC.  
  * Verificar se nenhuma integração está desativada inesperadamente.  
  * Conferir alertas de DB (como space usage).  
  * Checar WMS interface logs.

* Fornecer contato 24/7 (se a operação do warehouse for 24h) ou durante horário comercial ampliado para caso de falhas críticas (ex: integração parada impedindo expedição de pedidos).

**Suporte Nível 2 (Equipe de Integração Especializada):**

* Esta equipe (talvez a mesma que desenvolveu) deve ser acionada se o Nível 1 não resolver. São responsáveis por:  

  * Analisar logs de erros complexos no OIC.  
  * Ajustar configurações ou código do OIC se bug for encontrado.  
  * Interagir com DBAs do Autonomous DB se algum tuning de banco for necessário.  
  * Contatar Oracle Support se houver problemas na plataforma (ex: incidente no OIC cloud ou bug de produto).

* Manter um **runbook** de incidentes conhecidos e soluções. Por exemplo: "Erro X: acontece quando WMS manda um item não cadastrado. Solução: cadastrar item e resubmit."

**Acordos de Nível de Serviço (SLA):**

* Definir SLAs para tempos de resposta e resolução:  

  * Ex: Critico (integração completamente parada): resposta em 15 min, resolver em 4h.  
  * Médio (alguns registros falhando, mas maioria ok): resposta 1h, resolver 1 dia.  
  * Baixo (questões cosméticas ou de relatório): agendar em backlog de melhorias.

* Acompanhamento de SLA via ferramenta de ITSM (ServiceNow, Jira etc.), onde tickets de incidentes são registrados quando ocorrem falhas e fechados quando resolvidos.

**Operação Contínua e Melhoria:**

* **Registro de Métricas:** Além de monitorar erros, acompanhar métricas de sucesso:  

  * Quantidade de pedidos integrados por dia, e alocações por dia.  
  * Taxa de sucesso (ideal 100% ou muito próxima).  
  * Se começam a surgir erros similares repetidos, isso indica necessidade de melhoria (ex: se muitos pedidos falham por dados faltantes \-\> ajustar validação upstream).

* **Reuniões de Revisão Mensal:** Reunir stakeholders (TI integração, gestor do warehouse, etc.) para revisar se a integração está atendendo bem. Discutir possíveis otimizações ou novas funcionalidades desejadas.  

* **Atualizações de Versão:**  

  * O WMS Cloud sendo SaaS terá atualização (25C, 25D, etc. futuramente). Ler as notas de release para ver se algo muda nas APIs ou integrações. Testar integrações no ambiente de estágio do WMS antes de cada upgrade. Oracle normalmente mantém compatibilidade, mas é... prudente realizar testes de regressão integrados.

**Escalonamento para Suporte Oracle:** Se algum problema parecer ser bug da plataforma (OIC ou WMS Cloud) e não de configuração, acionar o suporte Oracle via SR (Service Request) com alta prioridade, fornecendo os logs e detalhes reproduzidos. Enquanto isso, ter plano de contingência (por ex., inserção manual de um pedido urgente no DB) se necessário até resolução.

Em suma, o plano de suporte prevê **monitoramento proativo**, **ação rápida em incidentes** e **melhoria contínua**. Assim, a integração se mantém saudável ao longo do tempo, acompanhando evoluções do ambiente de negócio e de sistemas (novas versões Oracle, aumento de volume, etc.), com mínimo impacto ao funcionamento do armazém.

## 12\. Fase de Entrega e Transição para Produção

A transição final para o ambiente de produção requer um planejamento cuidadoso para minimizar riscos e interrupções. A seguir, delineamos os passos para implantar a solução e fazer a virada (“cutover”) para operação produtiva.

**12.1 Preparação do Ambiente de Produção:**

* **Replicação de Configurações:** Reproduzir no ambiente de produção todas as configurações realizadas em desenvolvimento/teste:  

  * No **Oracle Integration Cloud Prod**, importar os pacotes de integração (exportados do OIC test) ou recriar as integrações manualmente seguindo documentação. Atualizar as **conexões** com as credenciais e URLs de produção:  

    * Conexão REST (WMS): apontar para a URL do WMS Cloud de produção e usuário de integração de prod.  
    * Conexão DB: apontar para o Autonomous DB de produção (ou esquema de prod). Importar o wallet de prod e testar.  
    * Conexão FTP: usar o SFTP de produção (pode ser o mesmo se não sensível, ou um segregado).

  * No **Autonomous DB Prod**, criar o usuário esquema (ex: WMSSTAGE) e executar os scripts DDL para criar tabelas de stage, views e procedures conforme modelado. Idealmente, utilizar um script versão final que já inclua todos objetos validados em QA.  

  * No **WMS Cloud Prod**, configurar os webhooks (Output Interfaces) para Orders e Allocations conforme feito em teste:  

    * Isso provavelmente envolve repetir a configuração na instância SaaS de produção. Atenção para usar a URL final do endpoint OIC prod (que pode ser diferente da de teste).  
    * Confirmar credenciais (Basic Auth) corretas do usuário OIC prod.  
    * Deixar desabilitado inicialmente, até o momento exato do cutover, para evitar envio antecipado.

* **Carga Inicial Pré-Produção:** Planejar a execução da carga inicial de dados pouco antes do go-live:  

  * Extrair do WMS prod os pedidos existentes (provavelmente os mesmos que estavam no WMS test se era clone, ou se WMS já está em uso, extrair dados atualizados).  
  * Carregar via OIC no DB prod e validar. Isso pode ser feito algumas horas antes do go-live, enquanto a integração de eventos ainda está desativada (para não ter duplicidade).  
  * Se não for possível extrair de antemão (por dados mudando até último minuto), considerar um pequeno downtime do WMS para extrair dados consistentes.

* **Teste de Fumaça (Smoke Test) em Prod:** Com tudo configurado mas ainda não em uso real, fazer um teste controlado:  

  * Acionar manualmente um webhook (por ex., usar a função de *test endpoint* do WMS, se disponível, ou criar um pedido de teste e ver no OIC monitor).  
  * Inserir um registro de teste via OIC no DB para ver conectividade.  
  * Esses testes garantem que quando abrir a torneira de dados real, nada impede a comunicação.

**12.2 Plano de Cutover:**

* Definir uma **janela de transição** (por exemplo, fora do horário de pico do armazém). Pode ser durante a noite ou fim de semana se operações permitirem.  

* **Congelamento de Atividades Relacionadas:** Se possível, durante a janela:  

  * Evitar criação de pedidos novos no sistema de origem (ou no WMS, dependendo do fluxo) para ter um ponto estável para sincronização final.  
  * Pausar quaisquer integrações antigas que estão sendo substituídas por esta (se aplicável).

* **Execução do Cutover:**  

  1. Executar a **carga inicial final** de pedidos/alocações no DB prod, garantindo que todas informações até o momento zero estão no DB. Conferir contagem.  
  2. **Ativar Webhooks no WMS Prod:** Habilitar as Output Interfaces de Orders e Allocations. A partir deste momento, eventos novos do WMS começarão a ir para o OIC/DB.  
  3. **Iniciar Integrações no OIC Prod:** Garantir que as integrações de Order e Allocation estão ativas (Activated) e no estado Running. O OIC começará a processar quaisquer requisições recebidas.  
  4. **Verificação Imediata:** Criar um ou dois pedidos de teste/produção no WMS e confirmar que aparecem no DB. Realizar uma alocação e conferir. Assim validamos rapidamente que tudo está funcionando em produção.  
  5. Comunicar "Go Live" aos usuários-chave (por ex, time do armazém, TI) indicando que a nova integração está operante.

* **Período de Estabilização (Hypercare):** Nas primeiras semanas pós-go-live, intensificar o monitoramento:  

  * Equipe de suporte de prontidão para qualquer erro.  
  * Reuniões diárias rápidas para revisar se houve incidentes.  
  * Garantir que todos estejam cientes de como voltar atrás se algo sério ocorrer (plano de contingência).

**12.3 Treinamento e Transição Operacional:**

* **Treinamento da Equipe de Operação:** Capacitar o pessoal de TI Operações e de negócio relevante em:  

  * Uso das telas de monitoramento do OIC (como identificar erros e notificar TI).  
  * Uso das telas do WMS para reprocessar interfaces caso necessário.  
  * Leitura de relatórios ou views no Autonomous DB (se, por exemplo, analistas irão consultar diretamente os dados lá).

* **Documentação de Execução:** Fornecer manuais de procedimentos, como:  

  * "O que fazer se integração de pedidos parar" – passo a passo.  
  * "Como adicionar um novo campo na integração" – se no futuro precisar estender (no âmbito de entrega, talvez não agora, mas deixar indicado).

* **Entrega Formal:** Realizar a passagem de conhecimento final do time de projeto para o time de operações, formalizando que a solução está em produção e sob gerenciamento do suporte. Isso inclui entrega de todos artefatos: código OIC exportado, scripts SQL, credenciais (guardadas em cofre seguro), diagrama de arquitetura, etc.

**12.4 Considerações Finais de Produção:**

* Manter um ambiente de **homologação/QA** sincronizado sempre que possível para testar patches ou novas funcionalidades antes de aplicar em produção.  
* Avaliar rodar testes de recuperação de desastre: por exemplo, simular perda do Autonomous DB (no caso, promover um clone backup) ou queda do OIC (raro, mas existe fallback?). O WMS Cloud possui alta disponibilidade intrínseca.  
* Planejar **crescimento futuro:** O design atual foca em pedidos e alocações, mas a arquitetura suporta adicionar novos fluxos (recebimento, expedição, inventário, etc.). Em produção, quando surgir demanda de integrar novas entidades, seguir padrões semelhantes e usar a base existente.

Ao concluir a transição, a integração estará oficialmente **em produção**, com dados fluindo do WMS Cloud para o Autonomous Database via OIC de forma contínua e confiável. A partir daí, a atenção volta-se à operação assistida (suporte) e a futuras otimizações ou ampliações conforme necessidades do negócio. A coordenação estreita entre as equipes de aplicações (WMS), integrações (OIC) e banco de dados garantirá que essa ponte digital do armazém funcione de forma robusta e sustentável ao longo do tempo.

**\[*Fim do Plano Técnico*\]**  
