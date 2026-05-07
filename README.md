# gpt-image-2-api Skill

用于调用 GPT-Image-2 图片生成 / 图片编辑接口的 Codex Skill。

This Codex skill provides reusable examples for calling GPT-Image-2 image generation and image editing through an OpenAI-compatible image API.

## 中文说明

这个 skill 适合在以下场景使用：

- 询问 `gpt-image-2` 怎么调用
- 需要 `/v1/images/generations` 生图示例
- 需要 `/v1/images/edits` 图片编辑示例
- 需要直接运行脚本生成图片或编辑图片
- 需要官方 multipart/form-data 图片编辑示例
- 需要 `curl`、`.env`、Docker Compose 或 Node.js 调用模板
- 需要把 `b64_json` 图片结果保存为本地图片文件

默认调用方式：

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

环境变量示例：

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

可以复制 `.env.example` 为 `.env`，然后填入自己的真实地址和密钥。

注意：

- 不要把真实 API Key 提交到 GitHub。
- `response_format` 常用 `b64_json` 或 `url`。
- `size` 可用 `auto` 或满足约束的 `WIDTHxHEIGHT`；`quality` 可用 `auto`、`low`、`medium`、`high`。
- `output_format` 可用 `png`、`jpeg`、`webp`；`output_compression` 仅用于 JPEG/WebP，范围 `0` 到 `100`；`moderation` 可用 `auto` 或 `low`。
- 如果使用 `b64_json`，可以通过 `jq` + `base64` 解码保存成图片。

常用尺寸：

- `1024x1024`：方图，通常最快
- `1536x1024`：横图
- `1024x1536`：竖图
- `2048x2048`：2K 方图
- `2048x1152`：2K 横图
- `3840x2160`：4K 横图
- `2160x3840`：4K 竖图

尺寸约束：最大边不超过 `3840px`；宽高都必须是 `16px` 的倍数；长边/短边比例不超过 `3:1`；总像素数在 `655360` 到 `8294400` 之间。超过 `2560x1440` 总像素的输出按实验性能力处理。

脚本调用：

```bash
python3 scripts/check_environment.py

python3 scripts/generate_image.py \
  --prompt "一只戴墨镜的橘猫，赛博朋克风" \
  --output image.png \
  --retries 2
```

官方 multipart 编辑示例：

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

## English

This skill is useful when you need:

- GPT-Image-2 image generation examples
- `/v1/images/generations` curl requests
- `/v1/images/edits` image editing examples
- executable generation/editing scripts
- official-style multipart image editing examples
- `.env`, Docker Compose, shell, or Node.js configuration templates
- A way to decode `b64_json` output into a local image file

Default request:

```bash
export GPT_IMAGE_2_BASE_URL="http://<api-host>:<port>"
export BASE_URL_API_KEY="<API_KEY>"

curl "$GPT_IMAGE_2_BASE_URL/v1/images/generations" \
  -H "Authorization: Bearer $BASE_URL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "A cyberpunk orange cat wearing sunglasses",
    "size": "1024x1024",
    "quality": "auto",
    "output_format": "png",
    "response_format": "b64_json"
  }'
```

Environment variables:

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

Copy `.env.example` to `.env` and fill in your real local values.

Notes:

- Do not commit real API keys.
- `response_format` is usually `b64_json` or `url`.
- `size` can be `auto` or a constrained `WIDTHxHEIGHT`; `quality` can be `auto`, `low`, `medium`, or `high`.
- `output_format` can be `png`, `jpeg`, or `webp`; `output_compression` is `0` through `100` for JPEG/WebP; `moderation` can be `auto` or `low`.
- For `b64_json`, decode the result with `jq` and `base64` to save a local image.

## Trigger examples / 触发示例

- `gpt-image-2 怎么调用`
- `生图接口 curl`
- `画图`
- `改图`
- `修图`
- `图片合成`
- `生成海报`
- `生成头像`
- `图片生成怎么保存成 png`
- `/v1/images/generations`
- `/v1/images/edits`
- `response_format=b64_json`
- `给我一个 env 配置示例`

## Main files / 主要文件

- `SKILL.md` - skill instructions loaded by Codex / Codex 加载的 skill 指令
- `scripts/generate_image.py` - generate/edit images and save output / 生成或编辑图片并保存输出
- `scripts/check_environment.py` - check Python and API config / 检查 Python 与 API 配置
- `references/env-config.md` - shell, `.env`, Docker Compose, and Node.js env examples / 多种环境配置示例
- `.env.example` - copy this to `.env` and fill in real values locally / 复制为 `.env` 后填入真实配置

## Save b64_json output / 保存 b64_json 图片

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

## Community / 社区

Community: https://linux.do
