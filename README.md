# X20 LAN Hook

Integração personalizada para o Home Assistant que preserva o valor bruto da
propriedade MIoT `siid=2`, `piid=2` recebida pela LAN do `xiaomi_home`.

O projeto nasceu de um Xiaomi Robot Vacuum X20 Max
(`xiaomi.vacuum.d109gl`). Nesse modelo, a propriedade é o estado operacional do
robô. O `xiaomi_home` converte vários valores para as atividades genéricas do
Home Assistant; por exemplo, os códigos de retorno para carregar e de retorno
para lavar o pano podem aparecer apenas como `returning`. O sensor bruto torna
possível distinguir esses casos em automações.

## Como funciona

O componente envolve `MIoTLan.__message_handler` e mantém o processamento
original intacto. Depois do handler original, ele examina mensagens
`properties_changed` e, para cada propriedade `siid=2`, `piid=2`, atualiza:

```text
sensor.xiaomi_<did>_p_2_2
```

O estado é o valor inteiro recebido, representado como texto pelo state machine
do Home Assistant. A entidade recebe também os atributos `did`, `siid` e
`piid`.

```text
X20 Max ──LAN──> xiaomi_home / MIoTLan
                         │
                         ├──> vacuum.xiaomi_...  (atividade normalizada)
                         │
                         └──> x20_lan_hook
                                  └──> sensor.xiaomi_<did>_p_2_2
                                         (estado MIoT bruto)
```

## Caso de uso principal

No X20 Max, o código `7` significa `gowash` — retorno/atividade de lavagem do
pano. Uma automação pode reagir especificamente a esse valor:

```yaml
automation:
  - alias: X20 - Parar lavagem automática do pano
    triggers:
      - trigger: state
        entity_id: sensor.xiaomi_SEU_DID_p_2_2
        to: "7"
    conditions:
      - condition: state
        entity_id: binary_sensor.SEU_X20_mop_status
        state: "on"
    actions:
      - delay: "00:00:02"
      - action: button.press
        target:
          entity_id: button.SEU_X20_stop_mop_wash
```

Os nomes de entidade variam conforme a conta, o dispositivo e a versão do
`xiaomi_home`. Substitua os exemplos pelas entidades da sua instalação.

## Instalação manual

1. Instale e configure a integração `xiaomi_home`.
2. Copie `custom_components/x20_lan_hook` para o diretório
   `custom_components` da sua configuração do Home Assistant.
3. Adicione ao `configuration.yaml`:

   ```yaml
   x20_lan_hook:
   ```

4. Reinicie o Home Assistant.
5. Aguarde uma atualização LAN do aspirador e confirme o aparecimento de
   `sensor.xiaomi_<did>_p_2_2` em **Ferramentas do desenvolvedor > Estados**.

## Compatibilidade verificada

| Componente | Versão/identificação validada |
| --- | --- |
| Home Assistant | 2026.9.3, instalação Supervised |
| `xiaomi_home` | 0.4.7 |
| Aspirador | Xiaomi Robot Vacuum X20 Max |
| Modelo MIoT | `xiaomi.vacuum.d109gl` |
| `x20_lan_hook` | 0.0.1 |

Essa tabela registra o ambiente em que o comportamento foi observado; não é
uma restrição intencional de versão.

## Códigos de estado do X20 Max

Os códigos de `siid=2`, `piid=2` e as observações da instalação de origem estão
documentados em [docs/x20-max-status-codes.md](docs/x20-max-status-codes.md).

## Limitações atuais

- O componente usa um método privado de `xiaomi_home`; mudanças internas nessa
  integração podem quebrar o hook.
- A entidade é criada diretamente no state machine. Ela não é registrada no
  Entity Registry, não pertence a um dispositivo e não é restaurada pelo
  `core.restore_state`.
- Após reiniciar o Home Assistant, o sensor só reaparece quando chega a primeira
  notificação LAN correspondente.
- O par `siid=2`, `piid=2` está fixo no código. Em outro modelo, esse par pode
  ter outro significado.
- O DID faz parte do `entity_id`. Trocas de conta ou dispositivo podem mudar o
  nome da entidade usada pelas automações.
- Ainda não há `config_flow`, opções, descarregamento do hook nem testes
  automatizados.

Veja a [auditoria sanitizada do uso real](docs/live-ha-findings.md) para o
contexto que orientou esta documentação e os pontos de evolução identificados.

## Operação e desenvolvimento

- [Operação sem internet](docs/offline-operation.md): o que continua local, o
  que depende da Xiaomi Cloud e quais cenários ainda precisam de prova física.
- [Branches em andamento](docs/development-branches.md): escopo e próximos
  passos das linhas de desenvolvimento abertas.
- [Como contribuir](CONTRIBUTING.md): convenção de branches, critérios para PR
  e cuidados com dados reais do Home Assistant.

## Licença

MIT.
