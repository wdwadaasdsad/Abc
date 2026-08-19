# -*- coding: utf-8 -*-
"""扫描 D:/Software/workbuddy-空间/新建文件夹/电商 真实目录，
按用户命名规则配对 颜色主图 + A+，规范化复制到 作品集/images/电商/，生成 ecom_products.js。
规则：
  - 主图文件夹里 1.png = 白底图 = 切换缩略图（始终第一张）
  - 有 A+ 的产品 -> type=variant（颜色 swatch 切换主图 + 该色 A+ 配对）
  - 无 A+ 的产品 -> type=flat（主图直接铺开）
"""
import os, re, shutil, json
from urllib.parse import quote

SRC = "D:/Software/workbuddy-空间/新建文件夹/电商"
DST = "D:/Software/workbuddy-空间/任务1/任务1/设计/作品集/images/电商"
OUT_JS = "D:/Software/workbuddy-空间/任务1/任务1\设计/作品集/ecom_products.js"

# 基于真实目录树精确配置（颜色 -> 主图目录 / A+ 目录）
CONFIG = {
    "儿童打印相机": {
        "id": 10, "type": "variant",
        "intro": "专为儿童设计的即时打印相机，2.5K 高清录像 + 前后双摄，拍立得式无墨热敏打印，内置趣味贴纸、滤镜与益智游戏。圆润防摔机身，激发孩子观察与记录世界的兴趣，是 3–12 岁寓教于乐的创意礼物。",
        "colors": [
            {"name": "粉色", "main": "儿童打印相机/粉色-儿童打印相机", "aplus": "儿童打印相机/粉色A+"},
            {"name": "绿色", "main": "儿童打印相机/绿色-儿童打印相机", "aplus": "儿童打印相机/绿色A+"},
            {"name": "青色", "main": "儿童打印相机/青色-儿童打印相机", "aplus": "儿童打印相机/青色A+"},
        ],
    },
    "卡片相机": {
        "id": 12, "type": "variant",
        "intro": "信用卡尺寸口袋相机，超薄便携随行记录，48MP 自动对焦前后双摄，多种复古滤镜，支持即时打印与手机互传。复古外形搭配现代功能，旅行街拍必备。",
        "colors": [
            {"name": "白色", "main": "卡片相机/白色", "aplus": "卡片相机/A+白色卡片相机"},
            {"name": "粉色", "main": "卡片相机/粉色", "aplus": "卡片相机/A+粉色卡片相机"},
            {"name": "黑色", "main": "卡片相机/黑色", "aplus": "卡片相机/A+黑色卡片相机"},
        ],
    },
    "早读机": {
        "id": 13, "type": "variant",
        "intro": "早教点读跟读学习机，冰墩墩、小猫、米奇多款 IP 造型，中英文双语儿歌、故事与识字卡片，护眼大按键设计，寓教于乐，0–6 岁启蒙好帮手。",
        "colors": [
            {"name": "冰墩墩", "main": "早读机/冰墩墩/主图", "aplus": "早读机/冰墩墩/A+"},
            {"name": "小猫", "main": "早读机/小猫/1000x1000", "aplus": None},
            {"name": "米奇-粉色", "main": "早读机/米奇/1000x1000-双语-粉色-560", "aplus": "早读机/米奇/A+", "aplus_filter": "粉色"},
            {"name": "米奇-蓝色", "main": "早读机/米奇/1000x1000-双语-蓝色-560", "aplus": "早读机/米奇/A+", "aplus_filter": "蓝色"},
        ],
    },
    "车载婴儿监视器": {
        "id": 16, "type": "variant",
        "intro": "车用婴儿后视镜监视器，广角高清摄像头实时查看宝宝状态，红外夜视清晰，4.3 英寸大屏，防眩光设计，绑带式一秒安装牢固不遮挡视线，开车带娃更安心。",
        "colors": [
            {"name": "颜色1", "main": "车载婴儿监视器/主图1-颜色1", "aplus": "车载婴儿监视器/颜色1A+"},
            {"name": "颜色2", "main": "车载婴儿监视器/主图2-颜色2", "aplus": None},
        ],
    },
    # ---- 无 A+：按颜色 / 形状分组铺开（居中排版，每组单独成行）----
    "前后屏相机": {
        "id": 11, "type": "flat",
        "intro": "前后双屏自拍相机，前置自拍屏 + 后置取景屏，4K 高清录像与一键美颜，轻巧便携。无墨热敏打印即拍即印，多种创意滤镜与拍摄模式，记录生活每一刻。",
        "groups": [
            {"name": "白色", "dir": "前后屏相机/白色"},
            {"name": "粉色", "dir": "前后屏相机/粉色"},
            {"name": "黑色", "dir": "前后屏相机/黑色"},
        ],
    },
    "同屏器": {
        "id": 17, "type": "flat",
        "intro": "手机同屏器，一键将手机画面无线投射到大屏，游戏、观影、会议演示低延迟共享，即插即用免驱动。",
        "groups": [{"name": "", "dir": "同屏器/2"}],
    },
    "夜视仪": {
        "id": 18, "type": "flat",
        "intro": "便携数码夜视观察仪，弱光 / 全黑环境清晰成像，1080P 录像与拍照，户外探险、夜间观察、安防巡检多场景适用。",
        "groups": [
            {"name": "白", "dir": "夜视仪/白"},
            {"name": "紫", "dir": "夜视仪/紫"},
        ],
    },
    "硅胶感官板": {
        "id": 14, "type": "flat",
        "intro": "蒙特梭利硅胶感官训练板，食品级软硅胶多种造型（心型、恐龙、方形、独角兽、长方形、套装），可啃咬可水洗，锻炼宝宝抓握、触觉与专注力，安全放心。",
        "groups": [
            {"name": "心型", "dir": "硅胶感官板/1000-心型"},
            {"name": "恐龙", "dir": "硅胶感官板/1000-恐龙"},
            {"name": "正方行", "dir": "硅胶感官板/1000-正方行"},
            {"name": "独角兽", "dir": "硅胶感官板/1000-独角兽"},
            {"name": "长方行", "dir": "硅胶感官板/1000-长方行"},
            {"name": "套装", "dir": "硅胶感官板/套装"},
        ],
    },
    "美甲刀": {
        "id": 15, "type": "flat",
        "intro": "专业美甲修护套装，多规格指甲刀、死皮剪、磨甲锉与电动打磨头，不锈钢锋利耐用，便携收纳盒设计，居家旅行美甲一站式，干净利落不伤甲。",
        "groups": [
            {"name": "605", "dir": "美甲刀/605"},
            {"name": "606", "dir": "美甲刀/606"},
        ],
    },
    "亚马逊": {
        "id": 19, "type": "flat",
        "intro": "跨境电商品牌视觉全案，覆盖多平台 Listing 主图、A+ 详情与品牌视觉规范，从卖点提炼到转化排版的一体化设计。",
        "groups": [{"name": "", "dir": "亚马逊"}],
    },
}

IMG_EXT = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp')

def num_of(name):
    m = re.search(r'(\d+)', name)
    return int(m.group(1)) if m else 999

def collect_images(d):
    """递归收集目录下所有图片，返回按 (层级, 数字, 路径) 排序的绝对路径列表"""
    if not os.path.isdir(d):
        return []
    out = []
    for root, _, files in os.walk(d):
        depth = root[len(d):].count(os.sep)
        for f in files:
            if f.lower().endswith(IMG_EXT):
                out.append((depth, num_of(f), os.path.join(root, f)))
    out.sort()
    return [p for _, _, p in out]

def safe_name(fname):
    base, ext = os.path.splitext(fname)
    s = re.sub(r'[^A-Za-z0-9._-]', '_', base)
    return s + ext.lower()

def copy_group(src_dir, dst_dir, prefix, name_filter=None):
    """复制一组图片到 dst_dir，重命名为 prefix_01..，1.png 永远第一。
    name_filter: 仅收集文件名含该子串的图片（用于同目录按前缀拆分 A+）。
    返回相对 url 列表（已编码）"""
    os.makedirs(dst_dir, exist_ok=True)
    imgs = collect_images(src_dir)
    if name_filter:
        imgs = [p for p in imgs if name_filter in os.path.basename(p)]
    # 排序：base=='1' 的第一张（白底），其余按数字
    def key(p):
        b = os.path.splitext(os.path.basename(p))[0]
        if re.fullmatch(r'1', b):
            return (0, 0, p)
        return (1, num_of(os.path.basename(p)), p)
    imgs.sort(key=key)
    rels = []
    for i, src in enumerate(imgs, 1):
        ext = os.path.splitext(src)[1].lower()
        newname = f"{prefix}_{i:02d}{ext}"
        shutil.copy2(src, os.path.join(dst_dir, newname))
        rel = os.path.relpath(os.path.join(dst_dir, newname), "D:/Software/workbuddy-空间/任务1/任务1/设计/作品集").replace("\\", "/")
        rels.append(quote(rel, safe='/_'))
    return rels

def main():
    os.makedirs(DST, exist_ok=True)

    products = []
    for pname, cfg in CONFIG.items():
        pdir = os.path.join(DST, pname)
        if cfg["type"] == "variant":
            colors = []
            for c in cfg["colors"]:
                mdir = os.path.join(pdir, c["name"])
                mains = copy_group(os.path.join(SRC, c["main"]), mdir, "main")
                aplus = []
                if c.get("aplus"):
                    adir = os.path.join(pdir, c["name"] + "_A+")
                    aplus = copy_group(os.path.join(SRC, c["aplus"]), adir, "aplus", c.get("aplus_filter"))
                colors.append({
                    "name": c["name"],
                    "thumb": mains[0] if mains else "",
                    "main": mains,
                    "aplus": aplus,
                })
            cover = colors[0]["thumb"] if colors else ""
            products.append({
                "id": cfg["id"], "name": pname, "type": "variant",
                "category": "ecom", "catName": "电商设计", "role": "独立设计", "tools": [],
                "desc": cfg.get("intro", ""),
                "intro": cfg.get("intro", ""),
                "cover": cover, "colors": colors,
            })
            print(f"[variant] {pname}: {len(colors)} 色 | 封面={cover}")
            for c in colors:
                print(f"    - {c['name']}: 主图{len(c['main'])} A+{len(c['aplus'])} 缩略={c['thumb']}")
        else:
            # flat：按 groups（颜色/形状）分组铺开，每组单独子目录
            groups = []
            for g in cfg["groups"]:
                gdir = os.path.join(pdir, g["name"] or "set")
                imgs = copy_group(os.path.join(SRC, g["dir"]), gdir, "img")
                groups.append({"name": g["name"], "images": imgs})
            cover = groups[0]["images"][0] if groups and groups[0]["images"] else ""
            products.append({
                "id": cfg["id"], "name": pname, "type": "flat",
                "category": "ecom", "catName": "电商设计", "role": "独立设计", "tools": [],
                "desc": cfg.get("intro", ""),
                "intro": cfg.get("intro", ""),
                "cover": cover, "groups": groups,
            })
            total = sum(len(g["images"]) for g in groups)
            print(f"[flat]    {pname}: {len(groups)} 组 共 {total} 张 | 封面={cover}")

    # 写 JS
    js = "window.ECOM_PRODUCTS = " + json.dumps(products, ensure_ascii=False, indent=2) + ";\n"
    with open(OUT_JS, "w", encoding="utf-8") as f:
        f.write(js)
    print(f"\n生成 {OUT_JS} (共 {len(products)} 个电商产品)")

if __name__ == "__main__":
    main()
