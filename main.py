import os
import math
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 导入 AstrBot 组件
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

# 尝试导入官方指令管理器
try:
    from astrbot.core.star import command_management
except ImportError:
    command_management = None
    logger.error("[GYHelp] 严重错误: 无法导入 astrbot.core.star.command_management")


@register("gyhelp", "工一阵", "GYHelp图片帮助菜单", "1.0.0")
class GyHelpPlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config

        # --- 路径配置 ---
        self.plugin_dir = Path(__file__).parent
        self.plugin_data_dir = Path("data/astrbot_plugin_gyhelp")
        self.bg_dir = self.plugin_data_dir / "background"
        self.font_dir = self.plugin_data_dir / "font"
        self.cache_dir = self.plugin_data_dir / "cache"

        # 确保目录结构存在
        self._ensure_dirs()

        logger.info("[GYHelp] 插件加载成功! 注册指令: help")

    def _ensure_dirs(self):
        """初始化目录结构"""
        for p in [self.plugin_data_dir, self.bg_dir, self.font_dir, self.cache_dir]:
            if not p.exists():
                p.mkdir(parents=True, exist_ok=True)

    def _get_font_path(self):
        """获取当前配置的字体路径"""
        selection = self.config.get("font_file", "")
        if selection:
            custom_font = self.font_dir / selection
            if custom_font.exists():
                return str(custom_font)
            else:
                logger.warning(f"[GYHelp] 未找到字体文件: {selection}，将使用默认字体")

        local_font = self.plugin_dir / "font.ttf"
        if local_font.exists():
            return str(local_font)

        system_fonts = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "arial.ttf",
        ]
        for f in system_fonts:
            if os.path.exists(f):
                return f
        return "arial.ttf"

    async def _fetch_commands(self):
        """获取指令列表"""
        if not command_management:
            return []
        try:
            raw_list = await command_management.list_commands()
        except Exception as e:
            logger.error(f"[GYHelp] 获取指令列表失败: {e}")
            return []

        commands_list = []
        show_sys = self.config.get("show_system_commands", False)
        exclude_list = self.config.get("exclude_plugins", [])

        for item in raw_list:
            if not item.get("enabled", True):
                continue

            cmd = item.get("effective_command") or item.get("original_command")
            if not cmd:
                continue

            desc = item.get("description", "暂无描述")
            is_reserved = item.get("reserved", False)
            plugin_name = item.get("plugin_name") or (
                "System" if is_reserved else "UserPlugin"
            )

            if is_reserved and not show_sys:
                continue
            if plugin_name in exclude_list:
                continue

            if not any(x[0] == cmd for x in commands_list):
                commands_list.append((cmd, desc, plugin_name))

        return sorted(commands_list, key=lambda x: (x[2], x[0]))

    def _draw_page_image(self, commands, page):
        """绘制单页图片"""
        # 1. 基础配置
        canvas_width = 1000
        canvas_height = 1400

        # 动态布局参数
        base_padding_top = 180  # 默认没有副标题时的起始高度
        padding_bottom = 80
        line_height = 70
        side_padding = 50

        # 获取文本配置
        main_title = self.config.get("menu_title", "AstrBot 指令菜单")
        sub_title_text = self.config.get("menu_sub_title", "")  # 获取副标题

        # 如果有副标题，整体内容下移 50 像素
        extra_offset = 50 if sub_title_text else 0
        padding_top = base_padding_top + extra_offset

        # 颜色
        main_color = self.config.get("font_color", "#333333")
        plugin_color = "#888888"
        desc_color = "#555555"

        # 2. 背景加载
        bg_selection = self.config.get("background_image", "")
        bg_image = None

        if bg_selection:
            bg_path = self.bg_dir / bg_selection
            if bg_path.exists():
                try:
                    bg_image = Image.open(bg_path).convert("RGBA")
                except Exception as e:
                    logger.error(f"[GYHelp] 背景加载失败: {e}")
            else:
                logger.warning(f"[GYHelp] 未找到背景图片: {bg_selection}")

        if bg_image:
            if not self.config.get("force_stretch", False):
                canvas_width, canvas_height = bg_image.size
            else:
                bg_image = bg_image.resize((canvas_width, canvas_height))
        else:
            bg_image = Image.new("RGBA", (canvas_width, canvas_height), "#F5F5F5")

        if canvas_height < 600:
            canvas_height = 600
        if canvas_width < 600:
            canvas_width = 600

        # 3. 分页计算
        content_height = canvas_height - padding_top - padding_bottom
        items_per_page = max(1, content_height // line_height)

        real_total_pages = math.ceil(len(commands) / items_per_page)
        if page > real_total_pages:
            page = 1

        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(commands))
        current_page_data = commands[start_idx:end_idx]

        # 4. 绘图
        final_img = Image.new("RGBA", (canvas_width, canvas_height))
        final_img.paste(bg_image, (0, 0))

        # 遮罩
        overlay_alpha = int(self.config.get("overlay_opacity", 230))
        overlay = Image.new(
            "RGBA", (canvas_width, canvas_height), (255, 255, 255, overlay_alpha)
        )
        final_img = Image.alpha_composite(final_img, overlay)

        draw = ImageDraw.Draw(final_img)
        font_path = self._get_font_path()

        def get_font(size):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                return ImageFont.load_default()

        # --- 绘制头部信息 ---

        # 1. 主标题 (y=50)
        draw.text((side_padding, 50), main_title, fill=main_color, font=get_font(60))

        # 2. 副标题 (y=120) - 如果有
        current_y_cursor = 130  # 下一个元素的起始 Y 坐标

        if sub_title_text:
            draw.text(
                (side_padding, 120), sub_title_text, fill=main_color, font=get_font(32)
            )
            current_y_cursor += extra_offset  # 下推

        # 3. 页码信息 (动态位置)
        page_info = f"Page {page} / {real_total_pages} | 共 {len(commands)} 个指令"
        draw.text(
            (side_padding, current_y_cursor),
            page_info,
            fill=plugin_color,
            font=get_font(24),
        )

        # 4. 分割线 (再往下一点)
        line_y = current_y_cursor + 35
        draw.line(
            [(side_padding, line_y), (canvas_width - side_padding, line_y)],
            fill="#BBBBBB",
            width=2,
        )

        # --- 列表内容 ---
        # 列表起始位置 = 动态计算的 padding_top
        list_start_y = padding_top + 10
        current_y = list_start_y

        for cmd, desc, plugin in current_page_data:
            clean_cmd = cmd.lstrip("/")

            # 指令名
            draw.text(
                (side_padding, current_y), clean_cmd, fill="#0066CC", font=get_font(36)
            )

            # 插件标签
            try:
                cmd_bbox = draw.textbbox((0, 0), clean_cmd, font=get_font(36))
                cmd_w = cmd_bbox[2] - cmd_bbox[0]
            except:
                cmd_w = len(clean_cmd) * 20

            draw.text(
                (side_padding + cmd_w + 15, current_y + 12),
                f"[{plugin}]",
                fill="#AAAAAA",
                font=get_font(20),
            )

            # 描述
            try:
                desc_bbox = draw.textbbox((0, 0), desc, font=get_font(28))
                desc_w = desc_bbox[2] - desc_bbox[0]
            except:
                desc_w = len(desc) * 15

            desc_x = canvas_width - side_padding - desc_w
            limit_x = side_padding + 400
            if desc_x < limit_x:
                desc_x = limit_x

            draw.text((desc_x, current_y + 5), desc, fill=desc_color, font=get_font(28))
            current_y += line_height

        # 底部
        footer_text = "Generated by astrbot_plugin_gyhelp"
        draw.text(
            (side_padding, canvas_height - 40),
            footer_text,
            fill="#CCCCCC",
            font=get_font(30),
        )

        if page < real_total_pages:
            hint = f"下一页: help {page + 1}"
            try:
                hint_w = draw.textbbox((0, 0), hint, font=get_font(20))[2]
                draw.text(
                    (canvas_width - side_padding - hint_w, canvas_height - 40),
                    hint,
                    fill="#999999",
                    font=get_font(20),
                )
            except:
                pass

        save_path = self.cache_dir / f"help_page_{page}.png"
        final_img.convert("RGB").save(save_path)

        return str(save_path), (page < real_total_pages), page, real_total_pages

    @filter.command("help")
    async def help(self, event: AstrMessageEvent, page: str = "1"):
        """查看指令帮助菜单。用法: /help 或 /help 2"""
        try:
            page_num = int(page)
        except ValueError:
            page_num = 1
        if page_num < 1:
            page_num = 1

        commands = await self._fetch_commands()
        if not commands:
            yield event.plain_result("未找到指令。")
            return

        loop = asyncio.get_running_loop()

        try:
            img_path, has_next, real_page, total_pages = await loop.run_in_executor(
                None, self._draw_page_image, commands, page_num
            )
        except Exception as e:
            logger.error(f"绘图失败: {e}")
            yield event.plain_result(f"帮助图生成出错: {e}")
            return

        yield event.image_result(img_path)

    @filter.command("gyhelp_switch")
    async def switch_mode(self, event: AstrMessageEvent):
        """切换是否显示astrbot内置指令"""
        current = self.config.get("show_system_commands", False)
        yield event.plain_result(
            f"当前状态: {'显示' if current else '隐藏'}内置指令。\n请在 WebUI 修改配置以切换。"
        )
