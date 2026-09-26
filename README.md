# X20 LAN Hook

Integração personalizada para o Home Assistant que intercepta notificações LAN
da integração `xiaomi_home` e publica o valor MIoT `siid=2`, `piid=2` como uma
entidade `sensor.xiaomi_<did>_p_2_2`.

## Estado atual

Esta é a versão inicial extraída de uma instalação ativa do Home Assistant. O
componente aplica um *hook* em `MIoTLan.__message_handler`, um método privado da
integração `xiaomi_home`. Mudanças internas nessa integração podem exigir
ajustes futuros neste projeto.

## Instalação manual

1. Copie `custom_components/x20_lan_hook` para o diretório
   `custom_components` da sua configuração do Home Assistant.
2. Adicione ao `configuration.yaml`:

   ```yaml
   x20_lan_hook:
   ```

3. Reinicie o Home Assistant.

## Comportamento

Ao receber uma mensagem `properties_changed`, o componente procura a
propriedade `siid=2`, `piid=2` e atualiza dinamicamente uma entidade com:

- estado igual ao valor recebido;
- `did`, `siid` e `piid` como atributos;
- nome amigável no formato `Xiaomi <did> MIoT status`.

## Licença

MIT.
