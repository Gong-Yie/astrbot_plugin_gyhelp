<div align="center">

![astrbot_plugin_gyhelp](https://count.getloli.com/@astrbot_plugin_gyhelp?name=astrbot_plugin_gyhelp&theme=original-new&padding=7&offset=0&align=center&scale=1&pixelated=1&darkmode=auto)

# astrbot_plugin_gyhelp

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-4.0%2B-orange.svg)](https://github.com/Soulter/AstrBot)
[![GitHub](https://img.shields.io/badge/作者-Gong_Yie-blue)](https://github.com/Gong-Yie)

</div>

不再单纯发送枯燥的长文本帮助菜单，而是将所有已安装插件的指令自动读取、排版，并渲染成一张精美的**图片**发送给用户。支持自定义背景、字体、分页显示。

---

## ✨ 核心特性

- **可视化渲染**：将指令列表生成为图片，阅读体验更佳。
- **智能分页**：根据背景图片的高度和指令数量，自动计算每页显示的条目数。
- **高度自定义**：
  - 支持自定义**背景图片**
  - 支持自定义**字体文件**（打造个性化风格）。
  - 支持自定义**主标题**和**副标题**。
  - 支持自定义**字体颜色**和**遮罩透明度**。
- **系统指令管理**：一键隐藏/显示 AstrBot 自带的系统指令

---

## 📥 安装方法

### 手动安装

1.  进入 AstrBot 的插件目录：
    ```bash
    cd data/plugins
    ```
2.  克隆本仓库（或将插件文件夹上传至此目录）：
    ```bash
    git clone https://github.com/Gong-Yie/astrbot_plugin_gyhelp.git
    ```
3.  安装依赖库（通常 AstrBot 环境已包含 PIL，若无请安装）：
    ```bash
    pip install Pillow
    ```
4.  **重启 AstrBot**。

---

## 📂 目录结构与资源放置

插件启动后，会自动在 AstrBot 根目录的 `data` 文件夹下生成以下结构。**请务必将您的自定义资源放入对应文件夹中**：

```text
AstrBot根目录/
├── data/
│   └── astrbot_plugin_gyhelp/       <-- 插件数据主目录
│       ├── background/              <-- 【在此放入背景图片】(.jpg, .png)
│       ├── font/                    <-- 【在此放入字体文件】(.ttf, .ttc)
│       ├── cache/                   <-- 存放生成的帮助图缓存（可定期清理）
│       └── config.json              <-- 自动生成的配置文件（建议通过WebUI修改）
```

## ⚙️ 配置说明 (WebUI)

请在 AstrBot 管理面板 -> **插件** -> **astrbot_plugin_gyhelp** -> **配置** 中进行设置。

| 配置项 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| **主标题文字** | String | AstrBot 指令菜单 | 图片最上方显示的大标题。 |
| **副标题文字** | String | (空) | 显示在标题下方的文字。留空则不占用空间。 |
| **显示系统指令** | Bool | False | 是否显示 AstrBot 内置指令。默认关闭。 |
| **背景图片文件名** | String | (空) | **重点**：填写 `data/astrbot_plugin_gyhelp/background/` 下的文件名（包含后缀），例如 `bg.jpg`。留空则使用纯白背景。 |
| **强制拉伸背景** | Bool | False | 开启后，图片将被强制拉伸至 1000x1400。关闭则使用图片原始尺寸作为画布。 |
| **遮罩透明度** | Int | 230 | 范围 0-255。0为全透，255为纯白。用于在花哨背景上增加一层半透明蒙版，确保文字清晰可见。 |
| **字体文件名** | String | (空) | **重点**：填写 `data/astrbot_plugin_gyhelp/font/` 下的文件名，例如 `myfont.ttf`。留空则尝试使用系统字体。 |
| **字体颜色** | String | #333333 | 主标题和正文的颜色（Hex 格式）。 |
| **排除插件名** | List | [] | 在此列表中填入的插件名（如 `astrbot_plugin_test`），其指令将不会显示。 |

---

## 🎮 指令使用

### 1. 查看帮助
- **指令**：`/help`
- **作用**：发送帮助菜单的第一页。
- **翻页**：`/help 2` 
- **作用**：查看第二页（如果有），以此类推。

### 2. 快速切换模式
- **指令**：`/gyhelp_switch`
- **作用**：快速开启或关闭“显示系统指令”功能（无需进入 WebUI）。

---

## ⚠️ 注意事项与常见问题 (FAQ)

### Q1: 与内置的`help`指令冲突？
我不太喜欢astrbot内置的help指令，感觉又臭又长，所以禁用了astrbot自带的系统指令。
* **解决**：
    禁用astrbot自带的系统指令。  
    或者修改astrbot_plugin_gyhelp的help指令名称

### Q2: 背景图片或字体不生效？
* **解决**：
    1. 确保文件已放入 `data/astrbot_plugin_gyhelp/background/` 或 `font/` 目录。
    2. 确保 WebUI 配置中填写的文件名（包含后缀，如 `.jpg`）与实际文件名完全一致。
    3. 修改配置后，建议重新发送一次指令。

### Q3: 图片里的文字被背景挡住了，看不清？
* **解决**：请在配置中调高 `overlay_opacity` (遮罩透明度) 的值（例如设为 240 或 250），或者更换一张颜色较浅的背景图。

### Q4: 如何修改图片生成的尺寸？
* **解决**：图片的尺寸由**背景图片**决定。
    * 如果您希望图片大一点，请找一张高分辨率的背景图，并关闭“强制拉伸”。
    * 如果您开启“强制拉伸”，图片将固定为 1000x1400 像素。

---

## 📝 免责声明

- 使用目的：本插件仅供学习交流，使用者不得用于非法或侵权行为，否则自行承担全部责任。

- 功能限制：本插件仅通过 onebot 协议获取公开信息，作者不对数据的准确性、完整性负责。

- 禁止非法修改：严禁私自魔改本插件（如接入社工库等违规操作），违者自行承担法律责任。

- 风险自担：使用者应自行评估使用风险，作者不对使用过程中产生的任何损失或风险承担责任。

- 法律适用：本声明适用中华人民共和国法律，争议由作者所在地法院管辖。

- 声明解释权：作者保留对本声明的最终解释权，并有权随时修改。
