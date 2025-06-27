import asyncio
import aiofiles
import argparse

import logging
import os

from aiohttp import web
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('download-server')

INTERVAL_SECS = 0
CHUNK_SIZE = 100
BASE_DIR = 'test_photos'


async def archive(request):
    archive_hash = request.match_info['archive_hash']
    path_to_files = f'{args.folder_path}/{archive_hash}/'
    delay = args.delay
    chunk_size = args.chunk_size*1024

    if not os.path.exists(path_to_files):
        raise web.HTTPNotFound(reason='Архив не существует или перемещен.')

    response = web.StreamResponse()
    response.headers[
        'Content-Disposition'] = 'attachment; filename=archive.zip'
    await response.prepare(request)

    proc = await asyncio.create_subprocess_exec(
            'zip',
            *('-r', '-', '.'),
            cwd=path_to_files,
            stdout=asyncio.subprocess.PIPE)
    try:
        while not proc.stdout.at_eof():
            logger.info(
                f'{archive_hash}: Подготовка архива к скачиванию ...')
            chunk = await proc.stdout.read(chunk_size)
            await response.write(chunk)
            await asyncio.sleep(delay)
            print(delay)
            print(chunk_size)
        return response
    except ConnectionResetError:
        logger.info(f'{archive_hash}: Загрузка была прервана')
    finally:
        if proc.returncode == 0:
            logger.info('Архив успешно загружен')
        if proc.returncode is None:
            logger.info('Загрузка архива прервана')
            proc.kill()
            await proc.communicate()


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':

    load_dotenv()

    parser = argparse.ArgumentParser(
                    description='Программа для скачивания архива')

    parser.add_argument('--make_logging', '-l',
                        help='Включить логирование',
                        action='store_true')
    parser.add_argument('--delay', '-d',
                        help='Включить задержку ответа при скачивании архива',
                        default=INTERVAL_SECS,
                        type=int)
    parser.add_argument('--folder_path', '-fp',
                        help='Указать путь к папке с файлами',
                        default=BASE_DIR,
                        type=str)
    parser.add_argument(
        '--chunk_size', '-cs',
        help='Определить размер части архива при скачивании в кБ',
        default=INTERVAL_SECS,
        type=int)

    args = parser.parse_args()

    if not args.make_logging:
        logging.disable

    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)
