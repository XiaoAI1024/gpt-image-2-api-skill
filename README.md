# gpt-image-2-api Skill

This skill provides reusable examples for calling GPT-Image-2 through an OpenAI-compatible image API.

## Trigger examples

- `gpt-image-2 怎么调用`
- `生图接口 curl`
- `图片生成怎么保存成 png`
- `/v1/images/generations`
- `/v1/images/edits`
- `response_format=b64_json`
- `给我一个 env 配置示例`

## Main files

- `SKILL.md` - skill instructions loaded by Codex
- `references/env-config.md` - shell, `.env`, Docker Compose, and Node.js env examples
- `.env.example` - copy this to `.env` and fill in real values locally

## Default API shape

```bash
curl "$BASE_URL/v1/images/generations" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "一只戴墨镜的橘猫，赛博朋克风",
    "size": "1024x1024",
    "response_format": "b64_json"
  }'
```

## Env variables

```dotenv
BASE_URL=http://<api-host>:<port>
API_KEY=<API_KEY>
IMAGE_MODEL=gpt-image-2
IMAGE_SIZE=1024x1024
IMAGE_RESPONSE_FORMAT=b64_json
IMAGE_OUTPUT=image.png
```

Keep real API keys out of committed files.
