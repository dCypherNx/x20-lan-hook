# Operação sem internet

Esta análise descreve a instalação que originou o projeto. O dashboard do Home
Assistant é resolvido internamente pelo OpenWrt; portanto, a perda da internet
não impede, por si só, o acesso ao painel dentro da rede local.

## Resumo

| Função | Integração/caminho | Sem internet |
| --- | --- | --- |
| Botões de limpeza por cômodo | scripts do HA → `xiaomi_home` | Esperado: funciona pela LAN |
| Iniciar, pausar, parar e retornar | entidade `vacuum` do `xiaomi_miot` | Esperado: funciona pela LAN |
| Automação de interromper lavagem | automação do HA + `x20_lan_hook` | Esperado: funciona pela LAN |
| Estado bruto `siid=2`, `piid=2` | push LAN interceptado pelo hook | Funciona pela LAN |
| Imagem atualizada do mapa | `xiaomi_cloud_map_extractor` | Não funciona |

Os comandos locais e a atualização do mapa usam caminhos independentes. A
indisponibilidade do mapa não significa, por si só, perda do controle do robô.

## Botões de limpeza por cômodo

Os botões superiores do dashboard iniciam scripts do Home Assistant. Esses
scripts usam entidades do `xiaomi_home` para:

- selecionar o mapa/piso;
- selecionar tipo e potência de limpeza;
- iniciar limpeza por cômodo;
- pausar o robô quando necessário;
- ligar e desligar a automação de lavagem do pano.

Na instalação auditada, o `xiaomi_home 0.4.7` está em `ctrl_mode: auto`. Para
propriedades e ações, essa versão tenta primeiro um gateway local, depois o
controle MIoT LAN e usa a nuvem somente quando não há rota local considerada
online.

O componente carrega do armazenamento local a lista de dispositivos antes de
tentar atualizar dados pela nuvem. Quando o monitor de rede detecta ausência de
internet, ele desconecta o cliente de nuvem e cancela atualizações remotas, mas
mantém a inicialização e as assinaturas LAN. Isso indica que um reinício do HA
durante a indisponibilidade também deve preservar o controle, desde que o cache
e as credenciais locais continuem válidos.

## Controles do cartão do aspirador

O cartão de mapa aponta para uma entidade `vacuum` fornecida pelo
`xiaomi_miot`. Na instalação auditada, essa integração possui endereço e token
locais e está configurada com `miot_cloud: false`. O modelo
`xiaomi.vacuum.d109gl` também consta na lista de modelos com controle local da
integração.

Assim, serviços como `vacuum.start`, `vacuum.pause`, `vacuum.stop` e
`vacuum.return_to_base` são encaminhados diretamente ao aparelho na LAN.

O endereço local do robô é parte dessa configuração. Uma reserva DHCP no
OpenWrt é recomendada para impedir que uma troca de IP quebre esse caminho.

## Dependência do mapa

A imagem usada pelo cartão vem do `xiaomi_cloud_map_extractor`, configurado com
a API Xiaomi. Essa integração consulta os servidores Xiaomi para obter a URL e
baixar o arquivo do mapa. Sem internet ou durante uma indisponibilidade desses
servidores:

- o mapa deixa de atualizar;
- a imagem pode ficar indisponível ou manter apenas o último conteúdo;
- o cartão visual pode ficar degradado, mesmo que a entidade `vacuum` continue
  controlável.

Por robustez, comandos essenciais não devem existir somente dentro de um cartão
que dependa da imagem de nuvem. Os botões superiores atuais já oferecem um
caminho independente para as rotinas por cômodo. Uma evolução pode acrescentar
botões locais explícitos para iniciar, pausar, parar e retornar à base.

## Matriz de falhas

| Cenário | Controle esperado | Mapa esperado |
| --- | --- | --- |
| Servidores Xiaomi indisponíveis | Local disponível | Indisponível/desatualizado |
| Internet residencial indisponível, HA já iniciado | Local disponível | Indisponível/desatualizado |
| HA reiniciado enquanto a internet está fora | Local esperado a partir do cache | Indisponível |
| Primeira instalação ou reautenticação sem internet | Não disponível | Não disponível |
| Cache/credenciais locais removidos | Pode não inicializar corretamente | Não disponível |
| LAN ou Wi-Fi do robô indisponível | Não disponível | Pode mostrar apenas conteúdo antigo |
| IP local do robô alterado | `xiaomi_miot` pode falhar | Situação independente |

## Nível de comprovação

Estão confirmados pela configuração e pelo código instalado:

- prioridade LAN do `xiaomi_home` em modo automático;
- recepção recente de notificações LAN pelo `x20_lan_hook`;
- modo local, sem nuvem, da entidade `xiaomi_miot` usada no cartão;
- dependência de nuvem da imagem do mapa;
- carregamento do cache pelo `xiaomi_home` antes das atualizações de nuvem.

Ainda falta uma prova física controlada com a saída para a internet bloqueada.
Até esse teste, o comportamento após perda de internet e após reinício offline
deve ser tratado como fortemente sustentado pelo código, mas não como validado
de ponta a ponta.

## Roteiro de validação futura

1. Confirmar que o HA e o X20 estão disponíveis na LAN.
2. Bloquear temporariamente apenas a saída para a internet, preservando o
   tráfego local e a resolução interna do dashboard.
3. Confirmar que o mapa deixa de atualizar, como esperado.
4. Executar um comando local de baixo risco e observar a resposta do aparelho.
5. Executar uma limpeza curta e supervisionada por um dos scripts de cômodo.
6. Reiniciar o HA ainda sem internet e repetir o comando de baixo risco.
7. Restaurar a internet e confirmar a recuperação do mapa e das integrações.

O teste deve ser supervisionado e registrado sem publicar DID, token, endereço
local, credenciais ou payloads brutos.
