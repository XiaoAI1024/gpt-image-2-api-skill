---
name: gpt-image-2-api
description: Use this skill whenever the user asks how to call or run GPT-Image-2 image generation or editing APIs, mentions gpt-image-2, /v1/images/generations, /v1/images/edits, response_format, b64_json, url image output, multipart image edits, or asks for curl/script examples for image generation. Prefer this skill even if the user only says "生图怎么调", "测试生图", "图片接口", "生成图片", "画图", "改图", "修图", "图片合成", "生成海报", "生成头像", or "OpenAI 图片接口".
---

# GPT-Image-2 API Calls

Use this skill to answer or generate commands for GPT-Image-2 image generation and image editing through an OpenAI-compatible API gateway.

## Core endpoints

- Generate image: `POST /v1/images/generations`
- Edit image: `POST /v1/images/edits`

Prefer `/v1/...` endpoint paths unless the target service explicitly documents root-path aliases such as `/images/generations`.

## Executable script workflow

Use `scripts/generate_image.py` when the user wants the image generated or edited now. Use curl examples when the user asks for API documentation, request bodies, or copy-paste gateway tests.

First-run check:

```bash
python3 scripts/check_environment.py
```

Text-to-image:

```bash
python3 scripts/generate_image.py \
  --prompt "一只戴墨镜的橘猫，赛博朋克风" \
  --output image.png \
  --retries 2
```

Image edit:

```bash
python3 scripts/generate_image.py \
  --image input.png \
  --prompt "把图片改成赛博朋克霓虹风，保留主体轮廓" \
  --output edited.png \
  --retries 2
```

Masked edit or multi-image composition:

```bash
python3 scripts/generate_image.py \
  --image subject.png \
  --image background.png \
  --mask mask.png \
  --prompt "把主体自然合成到背景中，匹配光线和透视" \
  --output composited.png \
  --size 1536x1024 \
  --quality high \
  --output-format png \
  --retries 2
```

## Image generation request

Required:

- `prompt`

Recommended:

- `model`: `gpt-image-2`
- `size`: `auto` by default, or a valid `WIDTHxHEIGHT` such as `1024x1024`
- `quality`: `auto` by default, or `low`, `medium`, `high`
- `output_format`: `png`, `jpeg`, or `webp`
- `output_compression`: `0` through `100`, only useful for JPEG/WebP
- `moderation`: `auto` or `low`
- `response_format`: `b64_json` or `url`

Compatibility notes:

- Some gateways accept `n`, but GPT-Image-2 compatibility layers may ignore it or not forward it upstream.
- `response_format: "url"` may return a data URL rather than a remotely hosted URL, depending on the gateway.
- The official Image API returns `data[0].b64_json`; keep `response_format` only when the target gateway documents or accepts it.
- `gpt-image-2` does not currently support transparent backgrounds; do not set `background: "transparent"` for this model.

## Size and quality options

For `gpt-image-2`, use these current output controls:

- `size`: `auto` (default) or any `WIDTHxHEIGHT` that satisfies all constraints below.
- Popular sizes:
  - `1024x1024` square, usually fastest
  - `1536x1024` landscape
  - `1024x1536` portrait
  - `2048x2048` 2K square
  - `2048x1152` 2K landscape
  - `3840x2160` 4K landscape
  - `2160x3840` 4K portrait
- Size constraints:
  - max edge length `<= 3840px`
  - both edges must be multiples of `16px`
  - long edge / short edge ratio must be `<= 3:1`
  - total pixels must be from `655360` through `8294400`
- `quality`: `auto` (default), `low`, `medium`, or `high`
- Use `quality: "low"` for fast drafts, thumbnails, and quick iterations.
- Treat outputs larger than `2560x1440` total pixels as experimental.

## Output controls

- `output_format`: use `png` by default. Use `jpeg` or `webp` when file size matters.
- `output_compression`: use only with `jpeg` or `webp`; range is `0` through `100`.
- `moderation`: use `auto` unless the user explicitly asks for lower filtering and the gateway/model supports `low`.
- `response_format` is a compatibility option for gateways that still expose `b64_json`/`url`; the official Images API returns base64 image data by default.

## Basic curl example

When the user asks for environment setup or reusable commands, use the env examples in `references/env-config.md`.

```bash
export GPT_IMAGE_2_BASE_URL="http://<api-host>:<port>"
export BASE_URL_API_KEY="<API_KEY>"

curl "$GPT_IMAGE_2_BASE_URL/v1/images/generations" \
  -H "Authorization: Bearer $BASE_URL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "一只戴墨镜的橘猫，赛博朋克风",
    "size": "1024x1024",
    "quality": "auto",
    "output_format": "png",
    "response_format": "b64_json"
  }'
```

## Save b64_json output to a file

```bash
curl "$GPT_IMAGE_2_BASE_URL/v1/images/generations" \
  -H "Authorization: Bearer $BASE_URL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "一只戴墨镜的橘猫，赛博朋克风",
    "size": "1024x1024",
    "quality": "auto",
    "output_format": "png",
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
curl "$GPT_IMAGE_2_BASE_URL/v1/images/generations" \
  -H "Authorization: Bearer $BASE_URL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "蓝色机器人头像，白底，图标风格",
    "size": "1024x1024",
    "quality": "auto",
    "output_format": "png",
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
export GPT_IMAGE_2_BASE_URL="http://<api-host>:<port>"
export BASE_URL_API_KEY="<API_KEY>"

curl "$GPT_IMAGE_2_BASE_URL/v1/images/edits" \
  -H "Authorization: Bearer $BASE_URL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "把图片改成赛博朋克霓虹风，保留主体轮廓",
    "image": "https://example.com/input.png",
    "size": "1024x1024",
    "quality": "auto",
    "output_format": "png",
    "response_format": "b64_json"
  }'
```

Base64 input example:

```json
{
  "model": "gpt-image-2",
  "prompt": "把背景改成纯白色",
  "image": "data:image/png;base64,<BASE64_IMAGE>",
  "response_format": "b64_json"
}
```

## Official multipart image edit example

Use multipart/form-data for official-style image edits, masks, and multi-image composition:

```bash
curl "$GPT_IMAGE_2_BASE_URL/v1/images/edits" \
  -H "Authorization: Bearer $BASE_URL_API_KEY" \
  -F model="gpt-image-2" \
  -F prompt="把主体自然合成到背景中，匹配光线和透视" \
  -F "image[]=@subject.png" \
  -F "image[]=@background.png" \
  -F "mask=@mask.png" \
  -F size="1536x1024" \
  -F quality="high" \
  -F output_format="png"
```

## Env configuration

For shell, `.env`, Docker Compose, and Node.js examples, read `references/env-config.md`.

Default variable names:

- `GPT_IMAGE_2_BASE_URL`
- `BASE_URL_API_KEY`
- `IMAGE_MODEL`
- `IMAGE_SIZE`
- `IMAGE_QUALITY`
- `IMAGE_OUTPUT_FORMAT`
- `IMAGE_OUTPUT_COMPRESSION`
- `IMAGE_MODERATION`
- `IMAGE_RESPONSE_FORMAT`
- `IMAGE_OUTPUT`

## Troubleshooting

If image generation fails:

1. Confirm the endpoint is `/v1/images/generations`, not a text-only endpoint.
2. Confirm the request contains `model: "gpt-image-2"` and a non-empty `prompt`.
3. Try `response_format: "b64_json"` first; it is easiest to verify locally.
4. Run `python3 scripts/check_environment.py` to confirm Python and API config.
5. If a gateway rejects the request, remove optional fields such as `n`, `quality`, `background`, `output_format`, `output_compression`, or `moderation` and retry with the minimal body.
6. If the gateway returns "did not return image output", inspect upstream logs for:
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
  "quality": "auto",
  "response_format": "b64_json"
}
```
