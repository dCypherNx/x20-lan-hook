# Como contribuir

## Branch principal

`main` representa o código documentado e considerado estável. Trabalhos ainda
não validados devem permanecer em branches e Pull Requests em modo draft.

Não faça desenvolvimento experimental diretamente em `main`.

## Convenção de nomes

- `feat/<objetivo>`: funcionalidade destinada a uma versão futura;
- `fix/<problema>`: correção de comportamento conhecido;
- `docs/<tema>`: documentação sem mudança funcional;
- `test/<tema>`: cobertura ou infraestrutura de testes;
- `spike/<hipotese>`: experimento descartável para produzir evidência.

Use nomes curtos, em minúsculas e separados por hífen. Uma branch deve ter um
objetivo principal claramente descrito no Pull Request.

## Fluxo recomendado

1. Atualize a `main` local a partir de `origin/main`.
2. Crie uma branch com o prefixo apropriado.
3. Faça commits pequenos e coerentes.
4. Abra um Pull Request draft cedo, registrando objetivo, riscos e evidências
   ainda ausentes.
5. Mantenha a branch atualizada com `main` e resolva divergências antes da
   revisão final.
6. Remova o estado draft somente depois de cumprir os critérios de validação.
7. Exclua a branch remota após o merge ou encerramento do experimento.

Branches que modificam a mesma área devem ter uma relação explícita: uma pode
depender da outra, substituir a outra ou ser apenas um *spike*. Evite manter
duas implementações concorrentes sem uma decisão registrada.

## Critérios mínimos para integração

- código Python compila sem erros;
- JSON e manifestos são válidos;
- testes automatizados cobrem parsers, decoders e regras semânticas novas;
- o hook não é aplicado duas vezes e pode ser removido com segurança;
- falhas no `xiaomi_home` não impedem a inicialização do Home Assistant;
- comportamento existente do sensor `siid=2`, `piid=2` permanece coberto;
- instalação, atualização e remoção são testadas antes de uma release HACS;
- afirmações sobre hardware real indicam modelo, versões e tipo de validação;
- mudanças no HA ativo são reversíveis e verificadas no resultado publicado.

## Dados particulares

Este projeto nasceu de uma instalação residencial real. Não publique:

- DID, MAC, IP ou token do aparelho;
- nomes de pessoas, cômodos ou redes Wi-Fi;
- credenciais, IDs de conta ou conteúdo de arquivos `.storage`;
- payloads brutos sem revisão;
- logs completos do Home Assistant.

Use placeholders como `<did>`, `<robot_entity>` e `<room_id>`. Capturas usadas
para engenharia reversa devem ser limitadas ao necessário, sanitizadas e
removidas quando deixarem de ser úteis.

## Evidência e documentação

Separe sempre:

- comportamento confirmado em hardware;
- comportamento deduzido do código/configuração;
- hipótese ainda não testada.

Descobertas reutilizáveis devem ser incorporadas à documentação ou aos testes.
Resultados temporários e decisões em aberto devem permanecer no Pull Request ou
em uma issue vinculada.
