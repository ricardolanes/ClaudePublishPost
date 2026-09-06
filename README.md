# ClaudePublishPost

Publicação automática de posts e carrosséis no Instagram via Meta Graph API,
para uso por sessões do Claude Code (incluindo sessões agendadas na nuvem).

## Configuração

1. Copie `.env.example` para `.env` e preencha:
   - `INSTAGRAM_BUSINESS_ID` — ID da conta profissional do Instagram
   - `FACEBOOK_PAGE_ID` — ID da Página do Facebook vinculada
   - `INSTAGRAM_ACCESS_TOKEN` — token da Meta Graph API (permissões
     `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`)
   - `META_API_VERSION` — versão da API (padrão `v19.0`)

   Para obter essas credenciais, use a skill `setup-instagram` do Claude Code
   (ela guia todo o processo, do Graph API Explorer até o token de longa duração).

2. **Para publicar a partir de uma sessão na nuvem** (como esta), as
   credenciais precisam existir no ambiente remoto — não basta configurar o
   `.env` na sua máquina local. Configure `INSTAGRAM_BUSINESS_ID`,
   `INSTAGRAM_ACCESS_TOKEN` etc. como variáveis de ambiente do ambiente/sessão
   remota (ou faça uma sessão local salvar o `.env` diretamente neste
   repositório, fora do controle de versão).

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

```bash
# Post único
python scripts/publish_instagram.py --images foto.png --caption "Legenda aqui #hashtag"

# Carrossel (2 a 10 imagens)
python scripts/publish_instagram.py --images slide1.png slide2.png --caption "Legenda aqui"

# Testar sem publicar de verdade
python scripts/publish_instagram.py --images foto.png --caption "teste" --dry-run
```

## Importante

- Toda legenda publicada pelo script recebe automaticamente um aviso de
  transparência ("Post gerado por IA — imagem e texto criados com Claude
  Code."), inserido antes do bloco final de hashtags. Não é preciso escrevê-lo
  na legenda; se ele já estiver lá, o script não duplica. Para mudar o texto do
  aviso, edite `AI_DISCLOSURE` em `scripts/publish_instagram.py`.
- A Graph API não permite editar a legenda de um post já publicado — o aviso só
  vale para publicações novas.
- O token gerado pelo Graph API Explorer expira em 1 hora. Para uso
  contínuo (ex.: publicações agendadas), gere um token de longa duração —
  veja a etapa final da skill `setup-instagram`.
- Nunca faça commit do arquivo `.env` (já está no `.gitignore`).
- Existem dois tipos de token/API, e o `INSTAGRAM_BUSINESS_ID` é diferente
  em cada um:
  - Token começando com `EAA...` (fluxo via Página do Facebook) → API em
    `graph.facebook.com`, ID vem de `me/accounts?fields=instagram_business_account`.
  - Token começando com `IGAA...` (Instagram Login direto) → API em
    `graph.instagram.com`, ID vem de `graph.instagram.com/me`.
  O script detecta o host automaticamente pelo prefixo do token, mas o
  `INSTAGRAM_BUSINESS_ID` no `.env` precisa ser o ID correto para o tipo
  de token usado — confirme com uma chamada a `.../me` antes de publicar.
