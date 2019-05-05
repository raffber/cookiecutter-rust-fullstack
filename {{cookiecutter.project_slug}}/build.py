import wasp
from wasp import shell, chain, Task
from wasp.fs import copy, directory
from wasp import ctx
from wasp.main import run_command
from subprocess import call
from shutil import make_archive
from os.path import relpath, abspath
from wasp.util import is_iterable
import threading
from subprocess import Popen


def flatten(lst_of_lst):
    from itertools import chain
    return list(chain.from_iterable(lst_of_lst))


def _list_files_in_dirs(dirs):
    return [str(x) for x in flatten([directory(x).list(recursive=True) for x in dirs])]


def zip_release(t):
    bd = ctx.builddir
    prod_dir = bd.join('prod')
    make_archive(str(prod_dir), 'zip', str(prod_dir))


@wasp.command("setup")
def setup():
    yield shell('npm install', cwd='frontend', pretty=False, always=True)
    yield shell('cargo install wasm-pack', pretty=False, always=True)


@wasp.command('build-backend')
def build_backend():
    yield shell('cargo build', cwd='backend', pretty=False, always=True)


def copy_html(target_dir):
    html_files = directory('frontend/html/').glob(r'.*\.html$')
    for f in html_files:
        yield copy(f, target_dir)


@wasp.command('build-frontend')
def build_frontend():
    bd = ctx.builddir
    js = bd.join('static')
    pkg = directory('frontend/pkg')

    # webpack is not designed with explicit dependency tracking
    # which is why we help a bit to speed up the whole build process
    # and only run webpack in case some files have changed
    frontend_files = _list_files_in_dirs(['frontend/html', 'frontend/scss'])
    webpack_srcs = [pkg.join('frontend_bg.wasm'), pkg.join('frontend.js')]
    webpack_srcs.extend(frontend_files)
    webpack_tgts = [js.join('0.app.js'), js.join('app.js'), js.join('app.wasm')]

    ch = chain()
    ch += shell('wasm-pack build', cwd='frontend', pretty=False, always=True)
    ch += shell('node_modules/.bin/webpack --config webpack.dev.config.js', cwd='frontend', pretty=False, sources=webpack_srcs, targets=webpack_tgts)
    for task in copy_html(bd.join('static/html')):
        yield task
    yield ch


@wasp.command('build', depends=['build-frontend', 'build-backend'])
def build():
    pass


@wasp.command("run", depends="build")
def run():
    call('cargo run', cwd='backend', shell=True)


@wasp.command("release")
def release():
    bd = ctx.builddir
    prod_dir = bd.join('prod')
    ch = chain()
    ch += shell('cargo build --release', cwd='backend', pretty=False, always=True)
    ch += shell('wasm-pack build --release', cwd='frontend', pretty=False, always=True)
    ch += shell('node_modules/.bin/webpack --config webpack.prod.config.js', cwd='frontend', pretty=False, always=True)
    ch += copy('backend/target/release/backend', prod_dir)
    ch += copy('backend/Rocket.toml', prod_dir)
    ch += Task(fun=zip_release, always=True)
    for task in copy_html(prod_dir.join('static/html')):
        yield task
    yield ch


server_proc = None

@wasp.command('run-async')
def run_async():
    global server_proc
    if server_proc is not None:
        server_proc.terminate()
        server_proc.wait()
    server_proc = Popen('target/debug/backend', cwd='backend', shell=True)


@wasp.command('watch', depends=['build', 'run-async'])
def watch():
    frontend_dirs = ['frontend/src', 'frontend/html', 'frontend/scss']
    backend_dirs = ['backend/src']
    shared_dirs = ['shared/src']

    all_dirs = flatten([frontend_dirs, backend_dirs, shared_dirs])
    frontend_files = _list_files_in_dirs(frontend_dirs)
    backend_files = _list_files_in_dirs(backend_dirs)
    shared_files = _list_files_in_dirs(shared_dirs)
    all_files = flatten([frontend_files, backend_files, shared_files])

    thread = TaskRunThread()
    thread.start()
    
    def callback(path):
        if path in frontend_files:
            thread.mark('build-frontend')
        elif path in backend_files:
            thread.mark('build-backend')
            thread.mark('run-async')
        elif path in shared_files:
            thread.mark('build')
            thread.mark('run-async')
    monitor = MonitorDaemon(files=all_files, dirs=all_dirs, callback=callback)
    monitor.run()
    thread.cancel()
    server_proc.terminate()
    server_proc.wait()


class TaskRunThread(object):
    def __init__(self):
        self._cancel = False
        self._evt = threading.Event()
        self._thread = threading.Thread(target=self._run)
        self._lock = threading.Lock()
        self._tasks = []
    
    def start(self):
        self._thread.start()

    def cancel(self):
        self._cancel = True
        self._evt.set()

    def mark(self, task):
        with self._lock:
            self._tasks.append(task)

    def _loop(self):
        with self._lock:
            tasks = list(self._tasks)
        run_tasks = set()
        for task in tasks:
            if task in run_tasks:
                continue
            run_command(task)
            run_tasks.add(task)
        with self._lock:
            for task in run_tasks:
                self._tasks = [x for x in self._tasks if x != task]
        
    def _run(self):
        while True:
            self._evt.wait(0.3)
            if self._evt.is_set():
                break
            self._loop()


class MonitorDaemon(object):
    import pyinotify

    class Handler(pyinotify.ProcessEvent):
        def process_default(self, event):
            if self._callback is None:
                return
            if event.pathname in self._files:
                self._callback(relpath(event.pathname, str(ctx.topdir)))

        def my_init(self, callback=None, files=None):
            self._callback = callback
            assert files is not None
            self._files = files

    def __init__(self, files, dirs, callback):
        import pyinotify
        self._watchmanager = pyinotify.WatchManager()
        self._files = [abspath(f) for f in files]
        self._dirs = set(dirs)
        self._callback = callback
        assert self._callback is not None

    def run(self):
        import pyinotify
        for d in self._dirs:
            # would it be better to watch  IN_CLOSE_WRITE?! maybe sth leaves a file permanently
            # open, such as a log file => no CLOSE_WRITE event is triggered
            # what about IN_CREATE?!
            self._watchmanager.add_watch(d, mask=pyinotify.IN_MODIFY | pyinotify.IN_MOVED_TO)
        handler = MonitorDaemon.Handler(callback=self._callback, files=self._files)
        notifier = pyinotify.Notifier(self._watchmanager, handler)
        try:
            notifier.loop()
        except KeyboardInterrupt:
            notifier.stop()

