# Branches em andamento

Estado observado em 25 de setembro de 2026, no fuso America/Sao_Paulo. Esta é
uma fotografia do trabalho em curso; os Pull Requests são a fonte atual para o
estado de revisão.

## `feat/hacs-realtime-map-room`

Pull Request: [#1 — Make X20 LAN Hook HACS-ready and add map/room discovery](https://github.com/dCypherNx/x20-lan-hook/pull/1)

Objetivo atual:

- preparar instalação pelo HACS;
- adicionar `config_flow`;
- substituir o sensor criado diretamente no state machine por entidades do HA;
- separar runtime, decodificação e entidade;
- descobrir mapa, cômodo atual e propriedades MIoT em tempo real.

Situação auditada:

- PR em modo draft;
- 11 commits à frente e 1 commit atrás da `main` na data da inspeção;
- altera 11 arquivos e reorganiza a arquitetura do componente;
- usa heurísticas para localizar campos de mapa/cômodo em payloads ainda não
  confirmados no aparelho real;
- não possui testes automatizados no estado observado.

Orientação:

1. Tratar esta branch como a linha principal da evolução arquitetural.
2. Atualizá-la com a `main` antes de ampliar o trabalho.
3. Manter mapa/cômodo como experimental até capturas reais identificarem os
   campos autoritativos.
4. Adicionar testes do decoder, do filtro por DID, da criação de entidades e da
   aplicação/remoção do hook.
5. Preservar compatibilidade com o sensor bruto `2/2` usado pela automação real.
6. Não publicar release HACS antes de validar instalação limpa, atualização e
   remoção em uma instância de teste.

## `feat/lan-property-discovery`

Pull Request: [#2 — Add opt-in LAN property discovery capture](https://github.com/dCypherNx/x20-lan-hook/pull/2)

Objetivo atual:

- oferecer captura opt-in das propriedades `properties_changed`;
- permitir filtro por DID;
- preservar o sensor bruto `2/2` existente;
- coletar evidência para descobrir propriedades de mapa e cômodo.

Situação auditada:

- PR em modo draft;
- 1 commit à frente da `main`;
- mudança pequena e concentrada em `__init__.py`;
- registra os payloads capturados em nível `warning`;
- sobrepõe uma área também modificada pela branch HACS.

Orientação:

1. Tratar esta branch como um *spike* temporário de coleta, não como uma segunda
   arquitetura permanente.
2. Nunca habilitar captura sem filtro por DID em uma instalação com vários
   dispositivos Xiaomi.
3. Preferir nível `debug`, limitar volume e documentar explicitamente que
   valores podem conter dados particulares.
4. Sanitizar qualquer amostra antes de anexá-la a issue, PR ou documentação.
5. Transferir as descobertas confirmadas para decoder e testes da branch HACS.
6. Evitar mesclar os dois PRs de forma independente: decidir qual implementação
   de captura será mantida e integrar somente essa versão.

## Relação entre as branches

As duas branches atacam partes do mesmo problema e modificam o hook central.
Elas não devem evoluir indefinidamente em paralelo.

Fluxo recomendado:

```text
feat/lan-property-discovery (spike e captura controlada)
                         │
                         └── evidências sanitizadas + testes
                                      │
                                      ▼
feat/hacs-realtime-map-room (arquitetura candidata)
                                      │
                                      └── PR revisado e validado
                                                   │
                                                   ▼
                                                 main
```

A branch de descoberta pode ser encerrada sem merge depois que seu aprendizado
for incorporado à branch arquitetural. Isso evita carregar código temporário de
logging para a versão distribuída.
