---
name: gpt-image-2-api
description: Use this skill whenever the user asks how to call GPT-Image-2 image generation or editing APIs, mentions gpt-image-2, /v1/images/generations, /v1/images/edits, response_format, b64_json, url image output, or asks for curl examples for image generation. Prefer this skill even if the user only says "生图怎么调", "测试生图", "图片接口", "生成图片", or "OpenAI 图片接口".
---

# GPT-Image-2 API Calls

Use this skill to answer or generate commands for GPT-Image-2 image generation and image editing through an OpenAI-compatible API gateway.

## Core endpoints

- Generate image: `POST /v1/images/generations`
- Edit image: `POST /v1/images/edits`

Prefer `/v1/...` endpoint paths unless the target service explicitly documents root-path aliases such as `/images/generations`.

## Image generation request

Required:

- `prompt`

Recommended:

- `model`: `gpt-image-2`
- `size`: commonly `1024x1024`
- `response_format`: `b64_json` or `url`

Compatibility notes:

- Some gateways accept `n`, but GPT-Image-2 compatibility layers may ignore it or not forward it upstream.
- `response_format: "url"` may return a data URL rather than a remotely hosted URL, depending on the gateway.

## Basic curl example

When the user asks for environment setup or reusable commands, use the env examples in `references/env-config.md`.

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

## Save b64_json output to a file

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

On macOS, if `base64 --decode` is not supported:

```bash
jq -r '.data[0].b64_json' image_response.json | base64 -D > image.png
```

## URL response format

```bash
curl "$BASE_URL/v1/images/generations" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "蓝色机器人头像，白底，图标风格",
    "size": "1024x1024",
    "response_format": "url"
  }'
```

Read the image from:

- `data[0].url` when `response_format` is `url`
- `data[0].b64_json` when `response_format` is `b64_json`

## Image editing request

Use this when the target gateway supports JSON image edit requests.

Required:

- `prompt`
- `image` or `images`

Common accepted image inputs:

- HTTP/HTTPS image URL
- data URL: `data:image/png;base64,...`
- raw base64, if the gateway documents that it accepts it

Example:

```bash
export BASE_URL="http://<api-host>:<port>"
export API_KEY="<API_KEY>"

curl "$BASE_URL/v1/images/edits" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "把图片改成赛博朋克霓虹风，保留主体轮廓",
    "image": "https://example.com/input.png",
    "size": "1024x1024",
    "response_format": "b64_json"
  }'
```

Base64 input example:

```json
{
  "model": "gpt-image-2",
  "prompt": "把背景改成透明",
  "image": "data:image/png;base64,<BASE64_IMAGE>",
  "response_format": "b64_json"
}
```

## Env configuration

For shell, `.env`, Docker Compose, and Node.js examples, read `references/env-config.md`.

Default variable names:

- `BASE_URL`
- `API_KEY`
- `IMAGE_MODEL`
- `IMAGE_SIZE`
- `IMAGE_RESPONSE_FORMAT`
- `IMAGE_OUTPUT`

## Troubleshooting

If image generation fails:

1. Confirm the endpoint is `/v1/images/generations`, not a text-only endpoint.
2. Confirm the request contains `model: "gpt-image-2"` and a non-empty `prompt`.
3. Try `response_format: "b64_json"` first; it is easiest to verify locally.
4. Remove optional fields such as `n`, `quality`, `background`, or `output_compression` and retry with the minimal body.
5. If the gateway returns "did not return image output", inspect upstream logs for:
   - `response.failed`
   - `image_generation_call`
   - upstream HTTP status
   - selected account/key/model

## Minimal known-good body

Use this as the first reproduction case:

```json
{
  "model": "gpt-image-2",
  "prompt": "一只戴墨镜的橘猫，赛博朋克风",
  "size": "1024x1024",
  "response_format": "b64_json"
}
```
