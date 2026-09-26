# Códigos de estado do X20 Max

Para o modelo `xiaomi.vacuum.d109gl`, `siid=2` é o serviço principal do robô e
`piid=2` é a propriedade `status`. A especificação MIoT em cache na instalação
validada define os valores abaixo.

| Código | Nome MIoT | Descrição da especificação |
| ---: | --- | --- |
| 1 | `idle` | Standby |
| 2 | `charging` | Charging |
| 3 | `breakcharging_2` | Charging_2 |
| 4 | `sweeping` | Working |
| 5 | `paused` | Pausing |
| 6 | `go_charging` | Returning |
| 7 | `gowash` | Cleaning the mop |
| 8 | `remote` | Remote controlling |
| 9 | `charged` | Fully charged |
| 10 | `buildingmap` | Mapping |
| 11 | `updating` | Updating |
| 12 | `multitaskstationworking` | The station is working |
| 13 | `multitaskrecharge_2` | Returning_2 |
| 14 | `stationworking_2` | The station is working_2 |
| 15 | `error` | Error |
| 16 | `sweeping_and_mopping` | Vacuuming & mopping |
| 17 | `mopping` | Mopping |
| 18 | `mappingpause_2` | Pausing_2 |
| 19 | `gochargebreak_3` | Returning_3 |
| 20 | `washbreak_4` | Returning_4 |
| 21 | `gochargebuildingmap_5` | Returning_5 |

## Por que o valor bruto é útil

O `xiaomi_home 0.4.7` agrupa os estados específicos do fabricante nas
atividades suportadas pelo Home Assistant. Na implementação auditada,
`gocharging` e `gowash`, entre outros, são mapeados para
`VacuumActivity.RETURNING`.

Essa normalização é apropriada para a entidade `vacuum`, mas elimina a diferença
necessária para uma automação que deve agir somente quando o robô vai lavar o
pano. O estado bruto `7` conserva essa informação.

## Escopo

Esses valores pertencem à especificação do `xiaomi.vacuum.d109gl`. Não presuma
que `siid=2`, `piid=2` ou seus códigos tenham a mesma semântica em outros
modelos. Antes de ampliar o suporte, consulte a especificação MIoT do modelo e
valide notificações reais.
