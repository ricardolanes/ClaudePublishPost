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

- O token gerado pelo Graph API Explorer expira em 1 hora. Para uso
  contínuo (ex.: publicações agendadas), gere um token de longa duração —
  veja a etapa final da skill `setup-instagram`.
- Nunca faça commit do arquivo `.env` (já está no `.gitignore`).
