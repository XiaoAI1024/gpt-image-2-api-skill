# GPT-Image-2 Env Configuration Examples

Use these examples when the user wants a reusable image-generation setup instead of a one-off curl command.

## Shell env

```bash
export BASE_URL="http://<api-host>:<port>"
export API_KEY="<API_KEY>"
export IMAGE_MODEL="gpt-image-2"
export IMAGE_SIZE="1024x1024"
export IMAGE_RESPONSE_FORMAT="b64_json"
export IMAGE_OUTPUT="image.png"
```

Generate and save:

```bash
curl "$BASE_URL/v1/images/generations" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$IMAGE_MODEL\",
    \"prompt\": \"一只戴墨镜的橘猫，赛博朋克风\",
    \"size\": \"$IMAGE_SIZE\",
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
BASE_URL=http://<api-host>:<port>
API_KEY=<API_KEY>
IMAGE_MODEL=gpt-image-2
IMAGE_SIZE=1024x1024
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
      BASE_URL: "http://<api-host>:<port>"
      API_KEY: "<API_KEY>"
      IMAGE_MODEL: "gpt-image-2"
      IMAGE_SIZE: "1024x1024"
      IMAGE_RESPONSE_FORMAT: "b64_json"
```

## Node.js env example

```js
const baseURL = process.env.BASE_URL;
const apiKey = process.env.API_KEY;

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
    response_format: process.env.IMAGE_RESPONSE_FORMAT || "b64_json",
  }),
});

const json = await res.json();
console.log(json.data?.[0]?.b64_json || json.data?.[0]?.url);
```

## Variable reference

| Variable | Required | Example | Meaning |
| --- | --- | --- | --- |
| `BASE_URL` | Yes | `http://<api-host>:<port>` | API gateway base URL without trailing slash |
| `API_KEY` | Yes | `<API_KEY>` | Bearer token |
| `IMAGE_MODEL` | No | `gpt-image-2` | Image model ID |
| `IMAGE_SIZE` | No | `1024x1024` | Requested image size |
| `IMAGE_RESPONSE_FORMAT` | No | `b64_json` | `b64_json` or `url` |
| `IMAGE_OUTPUT` | No | `image.png` | Local output filename |
