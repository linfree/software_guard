"""
数据重置脚本
清空所有数据（保留用户），然后创建演示数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.software import Software, SoftwareVersion
from app.models.download import DownloadLog
from app.models.request import SoftwareRequest
from app.models.vulnerability import Vulnerability
from app.models.audit import AuditLog


def clear_data(db: Session):
    """清空所有数据（保留用户表）"""
    print("Starting data cleanup...")

    # 按依赖顺序删除 - 必须先删除引用了 software 的表
    db.query(DownloadLog).delete()
    db.query(SoftwareRequest).delete()
    db.query(Vulnerability).delete()  # 必须在 Software 之前删除
    db.query(SoftwareVersion).delete()
    db.query(Software).delete()
    db.query(AuditLog).delete()

    db.commit()
    print("Data cleared successfully")


def create_demo_software(db: Session):
    """创建演示软件数据"""
    print("\nCreating demo software data...")

    demo_softwares = [
        {
            "name": "Visual Studio Code",
            "description": "一款轻量级但功能强大的源代码编辑器，支持多种编程语言",
            "category": "开发",
            "logo": "https://code.visualstudio.com/favicon.ico",
            "official_url": "https://code.visualstudio.com/",
            "versions": [
                {"version": "1.86.0", "file_size": 95420416, "release_notes": "修复了多个 bug，性能优化"},
                {"version": "1.85.0", "file_size": 94886416, "release_notes": "新增 AI 辅助编程功能"},
            ]
        },
        {
            "name": "PyCharm",
            "description": "JetBrains 开发的 Python IDE，提供智能代码补全、实时错误检查和快速修复",
            "category": "开发",
            "logo": "https://www.jetbrains.com/pycharm/favicon.ico",
            "official_url": "https://www.jetbrains.com/pycharm/",
            "versions": [
                {"version": "2023.3", "file_size": 524288000, "release_notes": "支持 Python 3.12"},
                {"version": "2023.2", "file_size": 511180800, "release_notes": "性能优化和新功能"},
            ]
        },
        {
            "name": "IntelliJ IDEA",
            "description": "JetBrains 开发的 Java 集成开发环境，支持 Java、Kotlin 等多种语言",
            "category": "开发",
            "logo": "https://www.jetbrains.com/idea/favicon.ico",
            "official_url": "https://www.jetbrains.com/idea/",
            "versions": [
                {"version": "2023.3", "file_size": 629145600, "release_notes": "Ultimate 版本更新"},
                {"version": "2023.2", "file_size": 616038400, "release_notes": "Community 版本更新"},
            ]
        },
        {
            "name": "Docker Desktop",
            "description": "容器化应用程序开发工具，支持构建、共享和运行容器化应用",
            "category": "开发",
            "logo": "https://www.docker.com/favicon.ico",
            "official_url": "https://www.docker.com/products/docker-desktop",
            "versions": [
                {"version": "4.27.0", "file_size": 52428800, "release_notes": "Docker Engine 更新"},
                {"version": "4.26.0", "file_size": 51380224, "release_notes": "安全修复"},
            ]
        },
        {
            "name": "Microsoft Office",
            "description": "微软办公套件，包含 Word、Excel、PowerPoint 等办公软件",
            "category": "办公",
            "logo": "https://www.microsoft.com/favicon.ico",
            "official_url": "https://www.microsoft.com/office",
            "versions": [
                {"version": "2021", "file_size": 2097152000, "release_notes": "经典版 Office"},
                {"version": "2019", "file_size": 1992294400, "release_notes": "稳定版本"},
            ]
        },
        {
            "name": "WPS Office",
            "description": "金山办公软件，兼容 Microsoft Office 格式",
            "category": "办公",
            "logo": "https://www.wps.cn/favicon.ico",
            "official_url": "https://www.wps.cn/",
            "versions": [
                {"version": "2019", "file_size": 104857600, "release_notes": "个人版免费"},
            ]
        },
        {
            "name": "Adobe Photoshop",
            "description": "Adobe 公司的专业图像编辑软件",
            "category": "设计",
            "logo": "https://www.adobe.com/favicon.ico",
            "official_url": "https://www.adobe.com/products/photoshop",
            "versions": [
                {"version": "2024", "file_size": 2097152000, "release_notes": "新增 AI 功能"},
                {"version": "2023", "file_size": 1992294400, "release_notes": "稳定版本"},
            ]
        },
        {
            "name": "Figma",
            "description": "基于浏览器的协作界面设计工具",
            "category": "设计",
            "logo": "https://www.figma.com/favicon.ico",
            "official_url": "https://www.figma.com/",
            "versions": [
                {"version": "116.0", "file_size": 15728640, "release_notes": "性能优化"},
                {"version": "115.0", "file_size": 15204352, "release_notes": "新功能发布"},
            ]
        },
        {
            "name": "Sketch",
            "description": "macOS 平台的矢量图形设计工具",
            "category": "设计",
            "logo": "https://www.sketch.com/favicon.ico",
            "official_url": "https://www.sketch.com/",
            "versions": [
                {"version": "83.1", "file_size": 13631488, "release_notes": "macOS 原生应用"},
            ]
        },
        {
            "name": "Wireshark",
            "description": "网络协议分析工具，用于网络故障排除和分析",
            "category": "安全",
            "logo": "https://www.wireshark.org/favicon.ico",
            "official_url": "https://www.wireshark.org/",
            "versions": [
                {"version": "4.2.0", "file_size": 62914560, "release_notes": "最新稳定版"},
                {"version": "4.0.0", "file_size": 62914560, "release_notes": "长期支持版本"},
            ]
        },
        {
            "name": "Burp Suite",
            "description": "Web 应用程序安全测试工具",
            "category": "安全",
            "logo": "https://portswigger.net/favicon.ico",
            "official_url": "https://portswigger.net/burp",
            "versions": [
                {"version": "2023.10", "file_size": 32440320, "release_notes": "新增扫描功能"},
            ]
        },
        {
            "name": "VMware Workstation",
            "description": "虚拟机软件，支持在单个计算机上运行多个操作系统",
            "category": "开发",
            "logo": "https://www.vmware.com/favicon.ico",
            "official_url": "https://www.vmware.com/products/workstation-pro",
            "versions": [
                {"version": "17.5", "file_size": 734003200, "release_notes": "支持 Windows 11"},
            ]
        },
        {
            "name": "Postman",
            "description": "API 开发和测试工具，支持 API 设计、文档、测试",
            "category": "开发",
            "logo": "https://www.postman.com/favicon.ico",
            "official_url": "https://www.postman.com/",
            "versions": [
                {"version": "10.18", "file_size": 12582912, "release_notes": "新增 Collections 功能"},
            ]
        },
        {
            "name": "Git",
            "description": "分布式版本控制系统",
            "category": "开发",
            "logo": "https://git-scm.com/favicon.ico",
            "official_url": "https://git-scm.com/",
            "versions": [
                {"version": "2.43.0", "file_size": 52428800, "release_notes": "最新稳定版"},
                {"version": "2.42.0", "file_size": 51380224, "release_notes": "安全更新"},
            ]
        },
        {
            "name": "Node.js",
            "description": "基于 Chrome V8 引擎的 JavaScript 运行环境",
            "category": "开发",
            "logo": "https://nodejs.org/favicon.ico",
            "official_url": "https://nodejs.org/",
            "versions": [
                {"version": "20.10.0", "file_size": 35651584, "release_notes": "LTS 版本"},
                {"version": "18.19.0", "file_size": 34603008, "release_notes": "旧版 LTS"},
            ]
        },
        {
            "name": "7-Zip",
            "description": "高压缩比归档工具",
            "category": "办公",
            "logo": "https://www.7-zip.org/favicon.ico",
            "official_url": "https://www.7-zip.org/",
            "versions": [
                {"version": "23.01", "file_size": 1572864, "release_notes": "最新版本"},
            ]
        },
        {
            "name": "Notepad++",
            "description": "Windows 文本编辑器，支持多种编程语言语法高亮",
            "category": "开发",
            "logo": "https://notepad-plus-plus.org/favicon.ico",
            "official_url": "https://notepad-plus-plus.org/",
            "versions": [
                {"version": "8.6.0", "file_size": 4194304, "release_notes": "新增功能"},
            ]
        },
        {
            "name": "VLC Media Player",
            "description": "免费开源的多媒体播放器",
            "category": "其他",
            "logo": "https://www.videolan.org/favicon.ico",
            "official_url": "https://www.videolan.org/vlc/",
            "versions": [
                {"version": "3.0.20", "file_size": 41943040, "release_notes": "最新版本"},
            ]
        },
    ]

    for sw_data in demo_softwares:
        # 创建软件
        software = Software(
            name=sw_data["name"],
            description=sw_data["description"],
            category=sw_data["category"],
            logo=sw_data.get("logo"),
            official_url=sw_data.get("official_url"),
            created_by=1  # admin 用户
        )
        db.add(software)
        db.flush()

        # 创建版本
        for i, ver_data in enumerate(sw_data["versions"]):
            import hashlib
            import os

            # 模拟文件路径（实际文件不存在，但路径需要设置）
            storage_path = os.path.join("storage", str(software.id))
            os.makedirs(storage_path, exist_ok=True)

            # 模拟文件名
            file_name = f"{sw_data['name'].replace(' ', '_')}_{ver_data['version']}.exe"

            # 模拟文件路径
            file_path = os.path.join(storage_path, file_name)

            # 创建空文件占位
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(b'')

            # 计算文件哈希
            sha256_hash = hashlib.sha256()
            sha256_hash.update(b'placeholder')
            file_hash = sha256_hash.hexdigest()

            software_version = SoftwareVersion(
                software_id=software.id,
                version=ver_data["version"],
                file_path=file_path,
                file_name=file_name,
                file_size=ver_data["file_size"],
                file_hash=file_hash,
                uploader_id=1,
                release_notes=ver_data.get("release_notes", ""),
                download_count=0
            )
            db.add(software_version)

            # 为第一个版本添加一些下载量
            if i == 0:
                software_version.download_count = __import__('random').randint(50, 500)

        db.commit()
        print(f"+ Created software: {sw_data['name']}")

    print(f"\nTotal created: {len(demo_softwares)} software")


if __name__ == "__main__":
    db = SessionLocal()

    try:
        clear_data(db)
        create_demo_software(db)
        print("\nData reset completed successfully!")
    except Exception as e:
        print(f"\nError: {e}")
        db.rollback()
    finally:
        db.close()
