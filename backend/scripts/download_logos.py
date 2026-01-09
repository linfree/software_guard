"""
下载软件 Logo 到本地存储
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import httpx
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.software import Software


async def download_logo(url: str, software_id: int, software_name: str) -> str:
    """下载 Logo 图片到本地"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
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

    try:
        # 获取所有有 logo URL 的软件
        softwares = db.query(Software).filter(
            Software.logo.isnot(None),
            Software.logo != ''
        ).all()

        print(f"Found {len(softwares)} software with logo URLs")

        for software in softwares:
            if software.logo and not software.logo.startswith('/api/'):
                print(f"Downloading logo for: {software.name}...")
                new_logo_path = await download_logo(software.logo, software.id, software.name)

                if new_logo_path:
                    # 更新数据库
                    software.logo = new_logo_path
                    db.commit()
                    print(f"  + Saved to: {new_logo_path}")
                else:
                    # 下载失败，清空 logo 字段
                    software.logo = None
                    db.commit()

        print("\nLogo download completed!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
