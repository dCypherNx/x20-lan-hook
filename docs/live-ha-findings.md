# Auditoria sanitizada do uso real

Esta página resume a inspeção somente leitura realizada em 25 de setembro de
2026 na instalação que originou o componente. Identificadores específicos da
conta e do aparelho foram omitidos porque este repositório é público.

## Implantação confirmada

- `x20_lan_hook:` está habilitado no `configuration.yaml` ativo.
- O Home Assistant carregado era o 2026.9.3, em instalação Supervised.
- O componente aparecia carregado como integração personalizada `0.0.1`.
- A dependência ativa era `xiaomi_home 0.4.7`.
- O dispositivo associado era um Xiaomi Robot Vacuum X20 Max, modelo
  `xiaomi.vacuum.d109gl`.
- O código do componente no host correspondia à importação inicial deste
  repositório.

## Entidade produzida

O hook produzia uma entidade no formato:

```text
sensor.xiaomi_<did>_p_2_2
```

A inspeção confirmou que ela:

- recebia estados e era persistida pelo Recorder;
- continha os atributos `friendly_name`, `did`, `siid=2` e `piid=2`;
- não aparecia no Entity Registry;
- não aparecia em `core.restore_state`;
- estava explicitamente marcada para não ser exposta ao assistente de conversa
  local.

Na janela disponível do Recorder havia 174 alterações entre 19 e 25 de
setembro de 2026. Foram observados os códigos `1`, `2`, `4`, `5`, `6`, `7`,
`10`, `14`, `18`, `20` e `21`. Isso confirma recepção contínua de estados LAN,
inclusive quatro ocorrências do código `7`.

## Consumidor confirmado

Um pacote ativo de limpeza referenciava o sensor em uma automação com este
fluxo:

1. aguardar a transição do estado bruto para `"7"`;
2. confirmar que o pano estava instalado por um `binary_sensor` do
   `xiaomi_home`;
3. aguardar dois segundos;
4. pressionar a entidade de botão que interrompe a lavagem do pano.

O dashboard oferecia controle para ligar ou desligar essa automação. Scripts de
limpeza por andar/cômodo também a desligavam e religavam em pontos específicos
da sequência, evitando que ela interferisse durante a preparação do robô e
reativando-a depois.

Durante a janela auditada, a automação estava desligada e não havia
`last_triggered` registrado. Portanto, a auditoria confirma a produção do
sensor e sua integração na configuração, mas não afirma que a ação de parada
foi executada com sucesso nesse período.

## Conclusões para a evolução

1. O contrato realmente necessário é expor o estado MIoT bruto sem substituir
   a entidade `vacuum` normalizada.
2. O código `7` é o caso de uso imediato, mas os demais códigos também podem ser
   úteis para diagnóstico e automações avançadas.
3. A entidade dinâmica atual tem limitações de ciclo de vida e descoberta. Uma
   evolução deve preferir uma entidade registrada, associada ao dispositivo e
   disponível de forma previsível após a inicialização.
4. O DID não deveria precisar ser codificado manualmente em automações; uma
   entidade estável e configurável reduziria acoplamento.
5. A dependência de `MIoTLan.__message_handler` precisa de proteção contra
   mudanças de assinatura, aplicação duplicada do hook e descarregamento da
   integração.
6. Suporte a outros modelos deve ser orientado pela especificação de cada
   aparelho, não pela suposição de que `2/2` sempre significa estado.

## Fontes locais examinadas

- configuração e pacote YAML ativos;
- implementação instalada de `x20_lan_hook`;
- implementação de `MIoTLan` e da plataforma `vacuum` do `xiaomi_home`;
- especificação MIoT em cache para `xiaomi.vacuum.d109gl`;
- Entity Registry, Device Registry, estado restaurado e configuração de
  exposição;
- histórico somente leitura do Recorder;
- dashboard Lovelace ativo.
