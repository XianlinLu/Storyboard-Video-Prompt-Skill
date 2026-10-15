# 分镜视频提示词 Skill

[English](README.md) | [简体中文](README.zh-CN.md)

这是一个不绑定具体平台的通用 Skill，可将剧本、电子表格、镜头清单、参考图片和已有分镜文档转化为可直接执行的视频生成提示词。

它固化了完整的分镜提示词工作流：

- 按场景组织输出；
- 在连续性允许时，合并 4 秒以内（含 4 秒）的相邻片段；
- 完整保留台词、景别、镜头动作、人物动作和画面描述；
- 使用四舍五入（`.5` 进位）把所有提示词时长转成连续的整数秒；
- 同一场景内，把上一条生成视频作为下一条输入；
- 到新场景时重置视频续写链；
- 放置参考图/视频并对最终文档做回读校验；
- 用户用中文提问时输出简体中文，用英文提问时输出英文。

Skill 不依赖特定厂商的工具名。只要 Agent 具备文档或文件处理能力，就可以在飞书/Lark、本地 Markdown/JSON 或其他表格与文档系统中使用。

## 快速开始

### 导入 Agent 界面

只导入以下目录：

```text
portable/storyboard-video-prompt-skill/
```

便携包只包含 `.md`、`.json` 和 `.txt` 文件，特意排除了 `.skillignore`、`.py` 文件和 Git 仓库元数据。校验器会以兼容 Python 的 `.txt` 文件保存，仍可通过 `python3` 执行。

### 从 Git 仓库使用

让 Agent 的 Skill 加载器读取仓库根目录，或把根目录中的 Skill 文件复制到 Agent 的技能目录。入口文件是 `SKILL.md`，详细规则位于 `references/`。

示例请求：

```text
从第 5 行开始，根据台词、景别、镜头动作、人物动作、画面描述和时长，
生成对应的分镜视频提示词。按场景分组；4 秒以内的镜头在满足连续性的前提下
与相邻镜头合并；同一场景内使用上一条生成视频续写，新场景重新开始。
```

除非用户明确指定语言，Skill 会自动跟随用户最新有效请求所使用的语言。

## 为什么提供便携导入包

部分导入器会对以下两种情况报错或警告：

1. `SKILL.md` 超过 20,000 个字符；
2. 文件不是 `.md`、`.txt`、`.json`、`.yaml` 或 `.yml`，例如 `.skillignore`。

本仓库通过以下方式避免这两类问题：

- 自动检查标准 `SKILL.md` 不超过 20,000 个字符；
- `portable/storyboard-video-prompt-skill/` 只包含导入器支持的格式；
- 仓库内置的便携包检查器会验证文件是否与标准版本同步，以及是否混入不支持的格式。

不要把整个仓库上传到有文件格式限制的导入器，请上传便携目录。

## 校验

校验仓库内的示例分镜计划：

```bash
python3 scripts/validate_storyboard_plan.py references/storyboard-plan-example.json
```

重新生成并检查便携包：

```bash
python3 scripts/build_portable.py
python3 scripts/build_portable.py --check
```

分镜计划校验器会检查整数时长、连续时间轴、总时长、源表行唯一性、输入素材、场景边界重置和本地化续写指令。

## 仓库结构

```text
SKILL.md                                  标准 Agent 指令
references/prompt-spec.md                 提示词、合并、时长和续写规范
references/quality-checklist.md           人工验收清单
references/storyboard-plan-example.json   结构化校验示例
scripts/validate_storyboard_plan.py       确定性分镜计划校验器
scripts/build_portable.py                  便携包生成与检查脚本
portable/storyboard-video-prompt-skill/   可直接导入的纯文本包
```

## 核心视频续写规则

同一场景中，除第一条外的每一条分镜都使用上一条生成视频，并以对应语言的指令开头：

- 中文：`续写这个@视频。`
- 英文：`Continue this @video.`

每个新场景的第一条分镜使用新场景参考素材，不使用这句续写指令。
