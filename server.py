import asyncio
import aiofiles

import logging
import os

from aiohttp import web


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('download-server')

INTERVAL_SECS = 1
CHUNK_SIZE = 102400


async def archive(request):
    base_dir = 'test_photos'
    archive_hash = request.match_info['archive_hash']
    path_to_files = f'{base_dir}/{archive_hash}/'

    if not os.path.exists(path_to_files):
        raise web.HTTPNotFound(reason='Архив не существует или перемещен.')

    
    
    response = web.StreamResponse()
    response.headers['Content-Disposition'] = 'attachment; filename=archive.zip'
    await response.prepare(request)
    
    proc = await asyncio.create_subprocess_exec(
            "zip",
            *("-r", "-", "."),
            cwd = path_to_files,
            stdout=asyncio.subprocess.PIPE)
    while not proc.stdout.at_eof():
        logger.info(f'{archive_hash}: Подготовка архива к скачиванию ...')
        chunk = await proc.stdout.read(CHUNK_SIZE)
        await response.write(chunk)
        await asyncio.sleep(INTERVAL_SECS)
    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        #web.get('/', uptime_handler),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)
