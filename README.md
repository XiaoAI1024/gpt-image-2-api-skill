# gpt-image-2-api Skill

用于调用 GPT-Image-2 图片生成 / 图片编辑接口的 Codex Skill。

This Codex skill provides reusable examples for calling GPT-Image-2 image generation and image editing through an OpenAI-compatible image API.

## 中文说明

这个 skill 适合在以下场景使用：

- 询问 `gpt-image-2` 怎么调用
- 需要 `/v1/images/generations` 生图示例
- 需要 `/v1/images/edits` 图片编辑示例
- 需要 `curl`、`.env`、Docker Compose 或 Node.js 调用模板
- 需要把 `b64_json` 图片结果保存为本地图片文件

默认调用方式：

```bash
export BASE_URL="http://<api-host>:<port>"
export API_KEY="<API_KEY>"

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

环境变量示例：

```dotenv
BASE_URL=http://<api-host>:<port>
API_KEY=<API_KEY>
IMAGE_MODEL=gpt-image-2
IMAGE_SIZE=1024x1024
IMAGE_RESPONSE_FORMAT=b64_json
IMAGE_OUTPUT=image.png
```

可以复制 `.env.example` 为 `.env`，然后填入自己的真实地址和密钥。

注意：

- 不要把真实 API Key 提交到 GitHub。
- `response_format` 常用 `b64_json` 或 `url`。
- 如果使用 `b64_json`，可以通过 `jq` + `base64` 解码保存成图片。

## English

This skill is useful when you need:

- GPT-Image-2 image generation examples
- `/v1/images/generations` curl requests
- `/v1/images/edits` image editing examples
- `.env`, Docker Compose, shell, or Node.js configuration templates
- A way to decode `b64_json` output into a local image file

Default request:

```bash
export BASE_URL="http://<api-host>:<port>"
export API_KEY="<API_KEY>"

curl "$BASE_URL/v1/images/generations" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "A cyberpunk orange cat wearing sunglasses",
    "size": "1024x1024",
    "response_format": "b64_json"
  }'
```

Environment variables:

```dotenv
BASE_URL=http://<api-host>:<port>
API_KEY=<API_KEY>
IMAGE_MODEL=gpt-image-2
IMAGE_SIZE=1024x1024
IMAGE_RESPONSE_FORMAT=b64_json
IMAGE_OUTPUT=image.png
```

Copy `.env.example` to `.env` and fill in your real local values.

Notes:

- Do not commit real API keys.
- `response_format` is usually `b64_json` or `url`.
- For `b64_json`, decode the result with `jq` and `base64` to save a local image.

## Trigger examples / 触发示例

- `gpt-image-2 怎么调用`
- `生图接口 curl`
- `图片生成怎么保存成 png`
- `/v1/images/generations`
- `/v1/images/edits`
- `response_format=b64_json`
- `给我一个 env 配置示例`

## Main files / 主要文件

- `SKILL.md` - skill instructions loaded by Codex / Codex 加载的 skill 指令
- `references/env-config.md` - shell, `.env`, Docker Compose, and Node.js env examples / 多种环境配置示例
- `.env.example` - copy this to `.env` and fill in real values locally / 复制为 `.env` 后填入真实配置

## Save b64_json output / 保存 b64_json 图片

```bash
curl "$BASE_URL/v1/images/generations" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "一只戴墨镜的橘猫，赛博朋克风",
    "size": "1024x1024",
    "response_format": "b64_json"
  }' > image_response.json

jq -r '.data[0].b64_json' image_response.json | base64 --decode > image.png
```

## Community / 社区

Community: https://linux.do
