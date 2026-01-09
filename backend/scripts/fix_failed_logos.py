"""
修复失败的 Logo URL 并重新下载
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import httpx
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.software import Software


async def download_logo(url: str, software_id: int, software_name: str) -> str:
    """下载 Logo 图片到本地"""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

            # 确定文件扩展名
            content_type = response.headers.get('content-type', '')
            if 'png' in content_type or url.endswith('.png'):
                ext = '.png'
            elif 'svg' in content_type or url.endswith('.svg'):
                ext = '.svg'
            elif 'ico' in content_type or url.endswith('.ico'):
                ext = '.ico'
            else:
                ext = '.jpg'

            # 创建 logo 目录
            logo_dir = os.path.join(settings.STORAGE_PATH, "logos")
            os.makedirs(logo_dir, exist_ok=True)

            # 生成文件名
            filename = f"software_{software_id}{ext}"
            file_path = os.path.join(logo_dir, filename)

            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(response.content)

            # 返回访问路径
            return f"/api/software/logos/{filename}"
    except Exception as e:
        print(f"Failed to download logo for {software_name}: {e}")
        return None


async def main():
    """主函数"""
    db = SessionLocal()

    # 失败的软件 Logo URL 修复
    logo_fixes = {
        "PyCharm": "https://resources.jetbrains.com/storage/products/pycharm/img/pycharm_logo.svg",
        "IntelliJ IDEA": "https://resources.jetbrains.com/storage/products/intellij-idea/img/intellij-idea_logo.svg",
        "Figma": "https://static.figma.com/app/icon/1/favicon-32x32.png",
        "VMware Workstation": "https://www.vmware.com/content/dam/digitalmarketing/vmware/en_US/logos/vmware-workstation-pro-logo.svg",
        "Node.js": "https://nodejs.org/static/images/logo.svg",
    }

    try:
        for software_name, logo_url in logo_fixes.items():
            software = db.query(Software).filter(Software.name == software_name).first()
            if software:
                print(f"Updating logo for: {software_name}...")
                new_logo_path = await download_logo(logo_url, software.id, software_name)

                if new_logo_path:
                    software.logo = new_logo_path
                    db.commit()
                    print(f"  + Saved to: {new_logo_path}")
                else:
                    print(f"  - Failed, clearing logo field")
                    software.logo = None
                    db.commit()

        print("\nFailed logos fixed!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
