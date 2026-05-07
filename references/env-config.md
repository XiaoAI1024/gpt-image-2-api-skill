# GPT-Image-2 Env Configuration Examples

Use these examples when the user wants a reusable image-generation setup instead of a one-off curl command.

## Shell env

```bash
export GPT_IMAGE_2_BASE_URL="http://<api-host>:<port>"
export BASE_URL_API_KEY="<API_KEY>"
export IMAGE_MODEL="gpt-image-2"
export IMAGE_SIZE="1024x1024"
export IMAGE_QUALITY="auto"
export IMAGE_OUTPUT_FORMAT="png"
export IMAGE_OUTPUT_COMPRESSION=""
export IMAGE_MODERATION=""
export IMAGE_RESPONSE_FORMAT="b64_json"
export IMAGE_OUTPUT="image.png"
```

Generate and save:

```bash
curl "$GPT_IMAGE_2_BASE_URL/v1/images/generations" \
  -H "Authorization: Bearer $BASE_URL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$IMAGE_MODEL\",
    \"prompt\": \"一只戴墨镜的橘猫，赛博朋克风\",
    \"size\": \"$IMAGE_SIZE\",
    \"quality\": \"$IMAGE_QUALITY\",
    \"output_format\": \"$IMAGE_OUTPUT_FORMAT\",
    \"response_format\": \"$IMAGE_RESPONSE_FORMAT\"
  }" > image_response.json

jq -r '.data[0].b64_json' image_response.json | base64 --decode > "$IMAGE_OUTPUT"
```

On macOS, if `base64 --decode` is unavailable:

```bash
jq -r '.data[0].b64_json' image_response.json | base64 -D > "$IMAGE_OUTPUT"
```

## .env example

Copy `.env.example` to `.env` and fill in real values locally.

```dotenv
GPT_IMAGE_2_BASE_URL=http://<api-host>:<port>
BASE_URL_API_KEY=<API_KEY>
IMAGE_MODEL=gpt-image-2
IMAGE_SIZE=1024x1024
IMAGE_QUALITY=auto
IMAGE_OUTPUT_FORMAT=png
IMAGE_OUTPUT_COMPRESSION=
IMAGE_MODERATION=
IMAGE_RESPONSE_FORMAT=b64_json
IMAGE_OUTPUT=image.png
```

Do not commit real API keys. Commit this as `.env.example`; keep real values in `.env`.

## Docker Compose env example

```yaml
services:
  image-client:
    image: curlimages/curl:latest
    environment:
      GPT_IMAGE_2_BASE_URL: "http://<api-host>:<port>"
      BASE_URL_API_KEY: "<API_KEY>"
      IMAGE_MODEL: "gpt-image-2"
      IMAGE_SIZE: "1024x1024"
      IMAGE_QUALITY: "auto"
      IMAGE_OUTPUT_FORMAT: "png"
      IMAGE_OUTPUT_COMPRESSION: ""
      IMAGE_MODERATION: ""
      IMAGE_RESPONSE_FORMAT: "b64_json"
```

## Node.js env example

```js
const baseURL = process.env.GPT_IMAGE_2_BASE_URL;
const apiKey = process.env.BASE_URL_API_KEY;

const res = await fetch(`${baseURL}/v1/images/generations`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${apiKey}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: process.env.IMAGE_MODEL || "gpt-image-2",
    prompt: "一只戴墨镜的橘猫，赛博朋克风",
    size: process.env.IMAGE_SIZE || "1024x1024",
    quality: process.env.IMAGE_QUALITY || "auto",
    output_format: process.env.IMAGE_OUTPUT_FORMAT || "png",
    output_compression: process.env.IMAGE_OUTPUT_COMPRESSION
      ? Number(process.env.IMAGE_OUTPUT_COMPRESSION)
      : undefined,
    moderation: process.env.IMAGE_MODERATION || undefined,
    response_format: process.env.IMAGE_RESPONSE_FORMAT || "b64_json",
  }),
});

const json = await res.json();
console.log(json.data?.[0]?.b64_json || json.data?.[0]?.url);
```

## Variable reference

| Variable | Required | Example | Meaning |
| --- | --- | --- | --- |
| `GPT_IMAGE_2_BASE_URL` | Yes | `http://<api-host>:<port>` | API gateway base URL without trailing slash |
| `BASE_URL_API_KEY` | Yes | `<API_KEY>` | Bearer token |
| `IMAGE_MODEL` | No | `gpt-image-2` | Image model ID |
| `IMAGE_SIZE` | No | `1024x1024` | Requested image size: `auto` or constrained `WIDTHxHEIGHT` |
| `IMAGE_QUALITY` | No | `auto` | `auto`, `low`, `medium`, or `high` |
| `IMAGE_OUTPUT_FORMAT` | No | `png` | `png`, `jpeg`, or `webp` |
| `IMAGE_OUTPUT_COMPRESSION` | No | `50` | JPEG/WebP compression from `0` to `100` |
| `IMAGE_MODERATION` | No | `auto` | `auto` or `low` |
| `IMAGE_RESPONSE_FORMAT` | No | `b64_json` | `b64_json` or `url` |
| `IMAGE_OUTPUT` | No | `image.png` | Local output filename |

## Size and quality quick reference

- `size`: `auto` by default, or a `WIDTHxHEIGHT` value.
- Common sizes: `1024x1024`, `1536x1024`, `1024x1536`, `2048x2048`, `2048x1152`, `3840x2160`, `2160x3840`.
- Constraints: max edge `<= 3840px`; both edges are multiples of `16px`; aspect ratio `<= 3:1`; total pixels `655360` through `8294400`.
- `quality`: `auto`, `low`, `medium`, or `high`; use `low` for fast drafts.
- Outputs larger than `2560x1440` total pixels are experimental.

## Script examples

Check setup:

```bash
python3 scripts/check_environment.py
```

Generate and save:

```bash
python3 scripts/generate_image.py \
  --prompt "一只戴墨镜的橘猫，赛博朋克风" \
  --output "$IMAGE_OUTPUT" \
  --size "$IMAGE_SIZE" \
  --quality "$IMAGE_QUALITY" \
  --output-format "$IMAGE_OUTPUT_FORMAT" \
  --retries 2
```

Official-style multipart edit:

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
